#!/usr/bin/env python3
"""Validate Inferential Regenerative Cycle Protocol v0.2 examples."""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT_DIR = Path(__file__).resolve().parents[1]
PASS_DIR = ROOT_DIR / "examples" / "pass"
FAIL_DIR = ROOT_DIR / "examples" / "fail"

SCHEMA_PATHS = {
    "inference_residual_record": (
        ROOT_DIR / "schemas" / "inference-residual-record.schema.json"
    ),
    "residual_classification_assessment": (
        ROOT_DIR / "schemas" / "residual-classification-assessment.schema.json"
    ),
}


def load_yaml_or_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as stream:
            document = yaml.safe_load(stream)
    except OSError as exc:
        raise RuntimeError(f"could not read {path}: {exc}") from exc
    except yaml.YAMLError as exc:
        raise RuntimeError(f"invalid YAML in {path}: {exc}") from exc

    if not isinstance(document, dict):
        raise RuntimeError(f"{path}: document root must be an object")

    return document


def discover_examples(directory: Path) -> list[Path]:
    return sorted([*directory.glob("*.yaml"), *directory.glob("*.yml")])


def format_json_path(error: Any) -> str:
    if not error.absolute_path:
        return "<root>"
    return ".".join(str(part) for part in error.absolute_path)


def collect_schema_errors(
    validator: Draft202012Validator,
    document: dict[str, Any],
) -> list[str]:
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
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError):
        errors.append(f"{field_name}: must be a valid ISO 8601 datetime")
        return None

    if parsed.tzinfo is None:
        errors.append(f"{field_name}: timezone information is required")
        return None

    return parsed


def load_validators() -> dict[str, Draft202012Validator]:
    validators: dict[str, Draft202012Validator] = {}

    for record_type, schema_path in SCHEMA_PATHS.items():
        schema = load_yaml_or_json(schema_path)
        Draft202012Validator.check_schema(schema)
        validators[record_type] = Draft202012Validator(
            schema,
            format_checker=FormatChecker(),
        )

    return validators


def validator_for_document(
    document: dict[str, Any],
    validators: dict[str, Draft202012Validator],
) -> Draft202012Validator | None:
    record_type = document.get("record_type")
    return validators.get(record_type)


def collect_residual_semantic_errors(
    document: dict[str, Any],
) -> list[str]:
    errors: list[str] = []

    created_at = parse_datetime(document["created_at"], "created_at", errors)
    retention = document["retention"]
    processing = document["preliminary_processing"]
    safety = document["safety"]
    content_reference = document["content_reference"]
    integrity = document["integrity"]

    review_at = None
    expires_at = None
    next_assessment_after = None

    if "review_at" in retention:
        review_at = parse_datetime(
            retention["review_at"], "retention.review_at", errors
        )
    if "expires_at" in retention:
        expires_at = parse_datetime(
            retention["expires_at"], "retention.expires_at", errors
        )
    if "next_assessment_after" in processing:
        next_assessment_after = parse_datetime(
            processing["next_assessment_after"],
            "preliminary_processing.next_assessment_after",
            errors,
        )

    if created_at and review_at and review_at <= created_at:
        errors.append("retention.review_at: must be later than created_at")
    if created_at and expires_at and expires_at <= created_at:
        errors.append("retention.expires_at: must be later than created_at")
    if review_at and expires_at and review_at >= expires_at:
        errors.append("retention.review_at: must be earlier than expires_at")
    if created_at and next_assessment_after and next_assessment_after <= created_at:
        errors.append(
            "preliminary_processing.next_assessment_after: "
            "must be later than created_at"
        )

    hazard = safety["potential_hazard"]
    disposition = processing["disposition"]

    if hazard in {"high", "critical"}:
        if disposition != "quarantined":
            errors.append(
                "preliminary_processing.disposition: "
                f"{hazard}-hazard residuals must be quarantined"
            )
        if not safety["requires_human_review"]:
            errors.append(
                "safety.requires_human_review: "
                f"must be true for {hazard}-hazard residuals"
            )

    if disposition == "quarantined" and not safety.get("quarantine_reason"):
        errors.append(
            "safety.quarantine_reason: required when disposition is quarantined"
        )

    if not processing["classification_eligible"]:
        if disposition == "pending_assessment":
            errors.append(
                "preliminary_processing.classification_eligible: "
                "pending_assessment residuals must be classification eligible"
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

    expected_digest_length = {"sha256": 64, "sha512": 128}[
        integrity["algorithm"]
    ]
    if len(integrity["digest"]) != expected_digest_length:
        errors.append(
            "integrity.digest: "
            f"{integrity['algorithm']} digests must contain "
            f"{expected_digest_length} hexadecimal characters"
        )

    if reference_type == "digest_only":
        if content_reference["value"].lower() != integrity["digest"].lower():
            errors.append(
                "content_reference.value: "
                "digest_only references must equal integrity.digest"
            )

    category = document["residual_category"]
    residual_form = document["residual_form"]
    required_forms: dict[str, set[str]] = {
        "thermal_byproduct": {"thermal"},
        "unallocated_value": {"economic"},
        "idle_capacity": {"computation", "temporal", "operational"},
    }
    allowed_forms = required_forms.get(category)
    if allowed_forms is not None and residual_form not in allowed_forms:
        errors.append(
            "residual_form: "
            f"{category} requires one of: {', '.join(sorted(allowed_forms))}"
        )

    if document["residual_id"] == document["source_inference_id"]:
        errors.append("residual_id: must differ from source_inference_id")

    return errors


def collect_assessment_semantic_errors(
    document: dict[str, Any],
    residual_index: dict[str, dict[str, Any]],
) -> list[str]:
    errors: list[str] = []

    assessed_at = parse_datetime(document["assessed_at"], "assessed_at", errors)
    lifecycle = document["lifecycle"]
    decision = document["decision"]
    risk = document["risk_evaluation"]
    classification = document["classification"]
    confidence = document["confidence"]
    targets = document.get("candidate_reuse_targets", [])

    review_at = None
    expires_at = None
    if "review_at" in lifecycle:
        review_at = parse_datetime(
            lifecycle["review_at"], "lifecycle.review_at", errors
        )
    if "expires_at" in lifecycle:
        expires_at = parse_datetime(
            lifecycle["expires_at"], "lifecycle.expires_at", errors
        )

    if assessed_at and review_at and review_at <= assessed_at:
        errors.append("lifecycle.review_at: must be later than assessed_at")
    if assessed_at and expires_at and expires_at <= assessed_at:
        errors.append("lifecycle.expires_at: must be later than assessed_at")
    if review_at and expires_at and review_at >= expires_at:
        errors.append("lifecycle.review_at: must be earlier than expires_at")

    residual_id = document["residual_id"]
    residual = residual_index.get(residual_id)

    if residual is None:
        errors.append(
            f"residual_id: unknown referenced residual '{residual_id}'"
        )
    else:
        if document["source_inference_id"] != residual["source_inference_id"]:
            errors.append(
                "source_inference_id: must match the referenced residual record"
            )

        residual_created_at = parse_datetime(
            residual["created_at"], "referenced_residual.created_at", errors
        )
        if assessed_at and residual_created_at and assessed_at < residual_created_at:
            errors.append(
                "assessed_at: cannot be earlier than referenced residual creation"
            )

        if not residual["preliminary_processing"]["classification_eligible"]:
            errors.append(
                "residual_id: referenced residual is not classification eligible"
            )

        source_hazard = residual["safety"]["potential_hazard"]
        if classification == "recoverable" and source_hazard in {"high", "critical"}:
            errors.append(
                "classification: high or critical source residuals cannot be recoverable"
            )

        source_disposition = residual["preliminary_processing"]["disposition"]
        if classification == "recoverable" and source_disposition != "pending_assessment":
            errors.append(
                "classification: recoverable residuals must originate from pending_assessment"
            )
        if classification == "hazardous" and source_disposition != "quarantined":
            errors.append(
                "classification: hazardous residuals must originate from quarantine"
            )

    eligible = decision["eligible_for_reintegration_planning"]
    action = decision["required_action"]
    human_review = decision["human_review_required"]
    status = lifecycle["status"]

    if classification == "recoverable":
        if confidence < 0.60:
            errors.append("confidence: recoverable classification requires at least 0.60")
        if risk["hazard_level"] not in {"none", "low"}:
            errors.append(
                "risk_evaluation.hazard_level: recoverable residuals require none or low"
            )
        if risk["contamination_risk"] not in {"none", "low"}:
            errors.append(
                "risk_evaluation.contamination_risk: "
                "recoverable residuals require none or low"
            )
        if risk["provenance_status"] != "verified":
            errors.append(
                "risk_evaluation.provenance_status: "
                "recoverable residuals require verified provenance"
            )
        if risk["integrity_status"] != "verified":
            errors.append(
                "risk_evaluation.integrity_status: "
                "recoverable residuals require verified integrity"
            )
        if risk["policy_compatibility"] not in {"compatible", "conditional"}:
            errors.append(
                "risk_evaluation.policy_compatibility: "
                "recoverable residuals must be compatible or conditional"
            )
        if not targets:
            errors.append(
                "candidate_reuse_targets: required for recoverable classification"
            )
        if not eligible:
            errors.append(
                "decision.eligible_for_reintegration_planning: "
                "must be true for recoverable classification"
            )
        if action != "approve_for_planning":
            errors.append(
                "decision.required_action: recoverable classification requires approve_for_planning"
            )
        if status != "active":
            errors.append("lifecycle.status: recoverable classification requires active")

    elif classification == "dormant":
        if eligible:
            errors.append(
                "decision.eligible_for_reintegration_planning: "
                "must be false for dormant classification"
            )
        if action != "retain_dormant":
            errors.append(
                "decision.required_action: dormant classification requires retain_dormant"
            )
        if status != "awaiting_review":
            errors.append(
                "lifecycle.status: dormant classification requires awaiting_review"
            )
        if review_at is None:
            errors.append("lifecycle.review_at: required for dormant classification")

    elif classification == "hazardous":
        if risk["hazard_level"] not in {"medium", "high", "critical"} and risk[
            "contamination_risk"
        ] not in {"high", "critical"}:
            errors.append(
                "risk_evaluation: hazardous classification requires material hazard or contamination risk"
            )
        if eligible:
            errors.append(
                "decision.eligible_for_reintegration_planning: "
                "must be false for hazardous classification"
            )
        if action != "quarantine":
            errors.append(
                "decision.required_action: hazardous classification requires quarantine"
            )
        if not human_review:
            errors.append(
                "decision.human_review_required: must be true for hazardous classification"
            )
        if not decision.get("quarantine_reason"):
            errors.append(
                "decision.quarantine_reason: required for hazardous classification"
            )
        if status != "quarantined":
            errors.append(
                "lifecycle.status: hazardous classification requires quarantined"
            )
        if targets:
            errors.append(
                "candidate_reuse_targets: prohibited for hazardous classification"
            )

    elif classification == "discardable":
        if eligible:
            errors.append(
                "decision.eligible_for_reintegration_planning: "
                "must be false for discardable classification"
            )
        if action != "discard":
            errors.append(
                "decision.required_action: discardable classification requires discard"
            )
        if not decision.get("discard_reason"):
            errors.append(
                "decision.discard_reason: required for discardable classification"
            )
        if status != "awaiting_disposal":
            errors.append(
                "lifecycle.status: discardable classification requires awaiting_disposal"
            )
        if targets:
            errors.append(
                "candidate_reuse_targets: prohibited for discardable classification"
            )

    if risk["integrity_status"] == "mismatch" and classification in {
        "recoverable",
        "dormant",
    }:
        errors.append(
            "classification: integrity mismatch cannot be recoverable or dormant"
        )

    if risk["provenance_status"] in {"missing", "conflicted"} and classification == "recoverable":
        errors.append(
            "classification: missing or conflicted provenance cannot be recoverable"
        )

    return errors


def collect_semantic_errors(
    document: dict[str, Any],
    residual_index: dict[str, dict[str, Any]],
) -> list[str]:
    record_type = document["record_type"]
    if record_type == "inference_residual_record":
        return collect_residual_semantic_errors(document)
    if record_type == "residual_classification_assessment":
        return collect_assessment_semantic_errors(document, residual_index)
    return [f"record_type: unsupported record type '{record_type}'"]


def print_errors(label: str, errors: list[str]) -> None:
    print(label)
    for error in errors:
        print(f"  - {error}")


def load_pass_documents() -> list[tuple[Path, dict[str, Any]]]:
    documents: list[tuple[Path, dict[str, Any]]] = []
    for path in discover_examples(PASS_DIR):
        documents.append((path, load_yaml_or_json(path)))
    return documents


def build_residual_index(
    documents: list[tuple[Path, dict[str, Any]]],
) -> tuple[dict[str, dict[str, Any]], list[str]]:
    residual_index: dict[str, dict[str, Any]] = {}
    errors: list[str] = []

    for path, document in documents:
        if document.get("record_type") != "inference_residual_record":
            continue
        residual_id = document.get("residual_id")
        if not isinstance(residual_id, str):
            continue
        if residual_id in residual_index:
            errors.append(
                f"{path.relative_to(ROOT_DIR)}: duplicate residual_id '{residual_id}'"
            )
            continue
        residual_index[residual_id] = document

    return residual_index, errors


def validate_pass_examples(
    validators: dict[str, Draft202012Validator],
    pass_documents: list[tuple[Path, dict[str, Any]]],
    residual_index: dict[str, dict[str, Any]],
) -> int:
    failures = 0

    for path, document in pass_documents:
        relative_path = path.relative_to(ROOT_DIR)
        print(f"\n[validate-pass] {relative_path}")

        validator = validator_for_document(document, validators)
        if validator is None:
            print_errors(
                "[schema-error]",
                [f"record_type: unsupported or missing type '{document.get('record_type')}'"],
            )
            failures += 1
            continue

        schema_errors = collect_schema_errors(validator, document)
        if schema_errors:
            print_errors("[schema-error]", schema_errors)
            failures += 1
            continue

        print("[schema-ok]")
        semantic_errors = collect_semantic_errors(document, residual_index)
        if semantic_errors:
            print_errors("[semantic-error]", semantic_errors)
            failures += 1
            continue

        print("[semantic-ok]")

    return failures


def validate_fail_examples(
    validators: dict[str, Draft202012Validator],
    residual_index: dict[str, dict[str, Any]],
) -> int:
    failures = 0

    for path in discover_examples(FAIL_DIR):
        relative_path = path.relative_to(ROOT_DIR)
        print(f"\n[validate-fail] {relative_path}")

        try:
            document = load_yaml_or_json(path)
        except RuntimeError as exc:
            print_errors("[expected-load-error]", [str(exc)])
            continue

        validator = validator_for_document(document, validators)
        if validator is None:
            print_errors(
                "[expected-schema-error]",
                [f"record_type: unsupported or missing type '{document.get('record_type')}'"],
            )
            continue

        schema_errors = collect_schema_errors(validator, document)
        if schema_errors:
            print_errors("[expected-schema-error]", schema_errors)
            continue

        print("[schema-ok]")
        semantic_errors = collect_semantic_errors(document, residual_index)
        if semantic_errors:
            print_errors("[expected-semantic-error]", semantic_errors)
            continue

        print("[unexpected-pass] example passed all validation")
        failures += 1

    return failures


def main() -> int:
    print("=== Inferential Regenerative Cycle Protocol v0.2 Validation ===")
    print(
        "schema [inference-residual-record]: "
        "schemas/inference-residual-record.schema.json"
    )
    print(
        "schema [residual-classification-assessment]: "
        "schemas/residual-classification-assessment.schema.json"
    )

    try:
        validators = load_validators()
        pass_documents = load_pass_documents()
    except (RuntimeError, Exception) as exc:
        print(f"[fatal] {exc}", file=sys.stderr)
        return 1

    residual_index, index_errors = build_residual_index(pass_documents)
    if index_errors:
        print_errors("[fatal-index-error]", index_errors)
        return 1

    pass_failures = validate_pass_examples(
        validators, pass_documents, residual_index
    )
    fail_failures = validate_fail_examples(validators, residual_index)

    print("\n=== Validation Summary ===")
    print(f"pass example failures: {pass_failures}")
    print(f"fail example failures: {fail_failures}")

    if pass_failures + fail_failures:
        print("Validation failed.")
        return 1

    print("All examples behaved as expected.")
    return 0


if __name__ == "__main__":
