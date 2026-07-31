#!/usr/bin/env python3
"""
Validate Inferential Regenerative Cycle Protocol examples.

Validation is performed in two layers:

1. JSON Schema validation
2. Protocol-specific semantic validation

Files under examples/pass must pass both layers.
Files under examples/fail must fail at least one layer.
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker


ROOT_DIR = Path(__file__).resolve().parents[1]

SCHEMA_PATH = (
    ROOT_DIR
    / "schemas"
    / "inference-residual-record.schema.json"
)

PASS_DIR = ROOT_DIR / "examples" / "pass"
FAIL_DIR = ROOT_DIR / "examples" / "fail"


def load_yaml_or_json(path: Path) -> dict[str, Any]:
    """Load a YAML or JSON document and require an object root."""

    try:
        with path.open("r", encoding="utf-8") as stream:
            document = yaml.safe_load(stream)
    except OSError as exc:
        raise RuntimeError(f"could not read {path}: {exc}") from exc
    except yaml.YAMLError as exc:
        raise RuntimeError(f"invalid YAML in {path}: {exc}") from exc

    if not isinstance(document, dict):
        raise RuntimeError(
            f"{path}: document root must be an object"
        )

    return document


def format_json_path(error: Any) -> str:
    """Return a readable path for a jsonschema validation error."""

    if not error.absolute_path:
        return "<root>"

    return ".".join(str(part) for part in error.absolute_path)


def collect_schema_errors(
    validator: Draft202012Validator,
    document: dict[str, Any],
) -> list[str]:
    """Collect JSON Schema validation errors."""

    errors = sorted(
        validator.iter_errors(document),
        key=lambda error: list(error.absolute_path),
    )

    return [
        f"{format_json_path(error)}: {error.message}"
        for error in errors
    ]


def parse_datetime(
    value: str,
    field_name: str,
    errors: list[str],
) -> datetime | None:
    """Parse an ISO 8601 datetime and require timezone information."""

    try:
        parsed = datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )
    except (TypeError, ValueError):
        errors.append(
            f"{field_name}: must be a valid ISO 8601 datetime"
        )
        return None

    if parsed.tzinfo is None:
        errors.append(
            f"{field_name}: timezone information is required"
        )
        return None

    return parsed


def collect_semantic_errors(
    document: dict[str, Any],
) -> list[str]:
    """Apply protocol-level semantic validation."""

    errors: list[str] = []

    created_at = parse_datetime(
        document["created_at"],
        "created_at",
        errors,
    )

    retention = document["retention"]
    processing = document["preliminary_processing"]
    safety = document["safety"]
    content_reference = document["content_reference"]
    integrity = document["integrity"]

    review_at: datetime | None = None
    expires_at: datetime | None = None
    next_assessment_after: datetime | None = None

    if "review_at" in retention:
        review_at = parse_datetime(
            retention["review_at"],
            "retention.review_at",
            errors,
        )

    if "expires_at" in retention:
        expires_at = parse_datetime(
            retention["expires_at"],
            "retention.expires_at",
            errors,
        )

    if "next_assessment_after" in processing:
        next_assessment_after = parse_datetime(
            processing["next_assessment_after"],
            "preliminary_processing.next_assessment_after",
            errors,
        )

    if created_at is not None and review_at is not None:
        if review_at <= created_at:
            errors.append(
                "retention.review_at: must be later than created_at"
            )

    if created_at is not None and expires_at is not None:
        if expires_at <= created_at:
            errors.append(
                "retention.expires_at: must be later than created_at"
            )

    if (
        review_at is not None
        and expires_at is not None
        and review_at >= expires_at
    ):
        errors.append(
            "retention.review_at: must be earlier than expires_at"
        )

    if (
        created_at is not None
        and next_assessment_after is not None
        and next_assessment_after <= created_at
    ):
        errors.append(
            "preliminary_processing.next_assessment_after: "
            "must be later than created_at"
        )

    hazard = safety["potential_hazard"]
    disposition = processing["disposition"]
    reuse_eligible = processing["reuse_eligible"]

    if hazard in {"high", "critical"}:
        if disposition != "quarantined":
            errors.append(
                "preliminary_processing.disposition: "
                f"{hazard}-hazard residuals must be quarantined"
            )

        if reuse_eligible:
            errors.append(
                "preliminary_processing.reuse_eligible: "
                f"{hazard}-hazard residuals cannot be reusable"
            )

        if not safety["requires_human_review"]:
            errors.append(
                "safety.requires_human_review: "
                f"must be true for {hazard}-hazard residuals"
            )

    if disposition == "quarantined":
        if reuse_eligible:
            errors.append(
                "preliminary_processing.reuse_eligible: "
                "quarantined residuals cannot be reusable"
            )

        if not safety.get("quarantine_reason"):
            errors.append(
                "safety.quarantine_reason: "
                "required when disposition is quarantined"
            )

    if disposition == "discard_requested" and reuse_eligible:
        errors.append(
            "preliminary_processing.reuse_eligible: "
            "discard-requested residuals cannot be reusable"
        )

    reference_type = content_reference["reference_type"]
    sensitivity = document["sensitivity"]

    if sensitivity == "restricted" and reference_type == "inline_text":
        errors.append(
            "content_reference.reference_type: "
            "restricted residuals cannot use inline_text"
        )

    if safety["contains_secrets"] and reference_type == "inline_text":
        errors.append(
            "content_reference.reference_type: "
            "residuals containing secrets cannot use inline_text"
        )

    algorithm = integrity["algorithm"]
    digest = integrity["digest"]

    expected_digest_length = {
        "sha256": 64,
        "sha512": 128,
    }[algorithm]

    if len(digest) != expected_digest_length:
        errors.append(
            "integrity.digest: "
            f"{algorithm} digests must contain "
            f"{expected_digest_length} hexadecimal characters"
        )

    if reference_type == "digest_only":
        if content_reference["value"].lower() != digest.lower():
            errors.append(
                "content_reference.value: "
                "digest_only references must equal integrity.digest"
            )

    category = document["residual_category"]
    residual_form = document["residual_form"]

    required_forms: dict[str, set[str]] = {
        "thermal_byproduct": {"thermal"},
        "unallocated_value": {"economic"},
        "idle_capacity": {
            "computation",
            "temporal",
            "operational",
        },
    }

    allowed_forms = required_forms.get(category)

    if allowed_forms is not None and residual_form not in allowed_forms:
        readable_forms = ", ".join(sorted(allowed_forms))
        errors.append(
            "residual_form: "
            f"{category} requires one of: {readable_forms}"
        )

    residual_id = document["residual_id"]
    source_inference_id = document["source_inference_id"]

    if residual_id == source_inference_id:
        errors.append(
            "residual_id: must differ from source_inference_id"
        )

    return errors


def discover_examples(directory: Path) -> list[Path]:
    """Return all YAML example files in deterministic order."""

    return sorted(
        [
            *directory.glob("*.yaml"),
            *directory.glob("*.yml"),
        ]
    )


def print_errors(
    label: str,
    errors: list[str],
) -> None:
    """Print a validation error group."""

    print(label)

    for error in errors:
        print(f"  - {error}")


def validate_pass_examples(
    validator: Draft202012Validator,
) -> int:
    """Validate examples expected to pass."""

    failures = 0

    for path in discover_examples(PASS_DIR):
        relative_path = path.relative_to(ROOT_DIR)
        print(f"\n[validate-pass] {relative_path}")

        try:
            document = load_yaml_or_json(path)
        except RuntimeError as exc:
            print_errors("[load-error]", [str(exc)])
            failures += 1
            continue

        schema_errors = collect_schema_errors(
            validator,
            document,
        )

        if schema_errors:
            print_errors("[schema-error]", schema_errors)
            failures += 1
            continue

        print("[schema-ok]")

        semantic_errors = collect_semantic_errors(document)

        if semantic_errors:
            print_errors("[semantic-error]", semantic_errors)
            failures += 1
            continue

        print("[semantic-ok]")

    return failures


def validate_fail_examples(
    validator: Draft202012Validator,
) -> int:
    """Validate examples expected to fail."""

    failures = 0

    for path in discover_examples(FAIL_DIR):
        relative_path = path.relative_to(ROOT_DIR)
        print(f"\n[validate-fail] {relative_path}")

        try:
            document = load_yaml_or_json(path)
        except RuntimeError as exc:
            print_errors("[expected-load-error]", [str(exc)])
            continue

        schema_errors = collect_schema_errors(
            validator,
            document,
        )

        if schema_errors:
            print_errors(
                "[expected-schema-error]",
                schema_errors,
            )
            continue

        print("[schema-ok]")

        semantic_errors = collect_semantic_errors(document)

        if semantic_errors:
            print_errors(
                "[expected-semantic-error]",
                semantic_errors,
            )
            continue

        print(
            "[unexpected-pass] example was expected to fail "
            "but passed all validation"
        )
        failures += 1

    return failures


def main() -> int:
    """Run all example validations."""

    print(
        "=== Inferential Regenerative Cycle Protocol "
        "v0.1 Validation ==="
    )
    print(
        "schema [inference-residual-record]: "
        "schemas/inference-residual-record.schema.json"
    )

    try:
        schema = load_yaml_or_json(SCHEMA_PATH)
    except RuntimeError as exc:
        print(f"[fatal] {exc}", file=sys.stderr)
        return 1

    try:
        Draft202012Validator.check_schema(schema)
    except Exception as exc:
        print(
            f"[fatal] invalid JSON Schema: {exc}",
            file=sys.stderr,
        )
        return 1

    validator = Draft202012Validator(
        schema,
        format_checker=FormatChecker(),
    )

    pass_failures = validate_pass_examples(validator)
    fail_failures = validate_fail_examples(validator)

    total_failures = pass_failures + fail_failures

    print("\n=== Validation Summary ===")
    print(f"pass example failures: {pass_failures}")
    print(f"fail example failures: {fail_failures}")

    if total_failures:
        print("Validation failed.")
        return 1

    print("All examples behaved as expected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
