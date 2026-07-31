#!/usr/bin/env python3
"""Validate Inferential Regenerative Cycle Protocol v0.3 examples."""

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
    "residual_reintegration_plan": (
        ROOT_DIR / "schemas" / "residual-reintegration-plan.schema.json"
    ),
    "regenerative_cycle_execution_receipt": (
        ROOT_DIR / "schemas" / "regenerative-cycle-execution-receipt.schema.json"
    ),
}


def load_yaml_or_json(path: Path) -> dict[str, Any]:
    """Load a YAML or JSON object."""
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
    return [f"{format_json_path(error)}: {error.message}" for error in errors]


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
    return validators.get(document.get("record_type"))


def collect_residual_semantic_errors(document: dict[str, Any]) -> list[str]:
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

    if (
        disposition == "pending_assessment"
        and not processing["classification_eligible"]
    ):
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
        errors.append(f"residual_id: unknown referenced residual '{residual_id}'")
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
        if classification == "recoverable" and source_hazard in {
            "high",
            "critical",
        }:
            errors.append(
                "classification: high or critical source residuals cannot be recoverable"
            )

        source_disposition = residual["preliminary_processing"]["disposition"]
        if (
            classification == "recoverable"
            and source_disposition != "pending_assessment"
        ):
            errors.append(
                "classification: recoverable residuals must originate from "
                "pending_assessment"
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
            errors.append(
                "confidence: recoverable classification requires at least 0.60"
            )
        if risk["hazard_level"] not in {"none", "low"}:
            errors.append(
                "risk_evaluation.hazard_level: "
                "recoverable residuals require none or low"
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
                "decision.required_action: recoverable classification "
                "requires approve_for_planning"
            )
        if status != "active":
            errors.append(
                "lifecycle.status: recoverable classification requires active"
            )

    elif classification == "dormant":
        if eligible:
            errors.append(
                "decision.eligible_for_reintegration_planning: "
                "must be false for dormant classification"
            )
        if action != "retain_dormant":
            errors.append(
                "decision.required_action: dormant classification "
                "requires retain_dormant"
            )
        if status != "awaiting_review":
            errors.append(
                "lifecycle.status: dormant classification requires awaiting_review"
            )
        if review_at is None:
            errors.append("lifecycle.review_at: required for dormant classification")

    elif classification == "hazardous":
        material_hazard = risk["hazard_level"] in {"medium", "high", "critical"}
        material_contamination = risk["contamination_risk"] in {
            "high",
            "critical",
        }
        if not material_hazard and not material_contamination:
            errors.append(
                "risk_evaluation: hazardous classification requires material "
                "hazard or contamination risk"
            )
        if eligible:
            errors.append(
                "decision.eligible_for_reintegration_planning: "
                "must be false for hazardous classification"
            )
        if action != "quarantine":
            errors.append(
                "decision.required_action: hazardous classification "
                "requires quarantine"
            )
        if not human_review:
            errors.append(
                "decision.human_review_required: "
                "must be true for hazardous classification"
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
                "decision.required_action: discardable classification "
                "requires discard"
            )
        if not decision.get("discard_reason"):
            errors.append(
                "decision.discard_reason: required for discardable classification"
            )
        if status != "awaiting_disposal":
            errors.append(
                "lifecycle.status: discardable classification "
                "requires awaiting_disposal"
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

    if (
        risk["provenance_status"] in {"missing", "conflicted"}
        and classification == "recoverable"
    ):
        errors.append(
            "classification: missing or conflicted provenance cannot be recoverable"
        )

    return errors


def target_signature(target: dict[str, Any]) -> tuple[str, str, str]:
    return (
        target["target_type"],
        target["target_id"],
        target["reuse_mode"],
    )


def collect_plan_semantic_errors(
    document: dict[str, Any],
    residual_index: dict[str, dict[str, Any]],
    assessment_index: dict[str, dict[str, Any]],
) -> list[str]:
    errors: list[str] = []

    planned_at = parse_datetime(document["planned_at"], "planned_at", errors)
    lifecycle = document["lifecycle"]
    scope = document["scope_control"]
    controls = document["safety_controls"]
    gate = document["authorization_gate"]
    target = document["target"]
    binding = document["residual_binding"]
    provenance = document["provenance_binding"]
    transformation = document["transformation"]
    expected_benefit = document["expected_benefit"]

    review_at = None
    expires_at = parse_datetime(
        lifecycle["expires_at"], "lifecycle.expires_at", errors
    )
    if "review_at" in lifecycle:
        review_at = parse_datetime(
            lifecycle["review_at"], "lifecycle.review_at", errors
        )

    if planned_at and review_at and review_at <= planned_at:
        errors.append("lifecycle.review_at: must be later than planned_at")
    if planned_at and expires_at and expires_at <= planned_at:
        errors.append("lifecycle.expires_at: must be later than planned_at")
    if review_at and expires_at and review_at >= expires_at:
        errors.append("lifecycle.review_at: must be earlier than expires_at")

    residual = residual_index.get(document["residual_id"])
    assessment = assessment_index.get(document["assessment_id"])

    if residual is None:
        errors.append(
            f"residual_id: unknown referenced residual '{document['residual_id']}'"
        )
    if assessment is None:
        errors.append(
            "assessment_id: unknown referenced assessment "
            f"'{document['assessment_id']}'"
        )

    if residual is not None:
        if document["source_inference_id"] != residual["source_inference_id"]:
            errors.append(
                "source_inference_id: must match the referenced residual record"
            )

        residual_integrity = residual["integrity"]
        if binding["algorithm"] != residual_integrity["algorithm"]:
            errors.append(
                "residual_binding.algorithm: must match referenced residual integrity"
            )
        if binding["digest"].lower() != residual_integrity["digest"].lower():
            errors.append(
                "residual_binding.digest: must match referenced residual integrity"
            )

        if set(provenance["origin_refs"]) != set(residual["origin_refs"]):
            errors.append(
                "provenance_binding.origin_refs: must exactly preserve residual Origin references"
            )

        residual_traces = set(residual.get("trace_refs", []))
        plan_traces = set(provenance["trace_refs"])
        if not residual_traces.issubset(plan_traces):
            errors.append(
                "provenance_binding.trace_refs: must include every residual Trace reference"
            )

        if target["target_id"] in {
            document["residual_id"],
            document["source_inference_id"],
        }:
            errors.append(
                "target.target_id: cannot be the residual or source inference identifier"
            )

        if residual["sensitivity"] == "restricted":
            if scope["environment"] == "controlled_production":
                errors.append(
                    "scope_control.environment: restricted residuals cannot be planned directly for controlled_production"
                )
            if not controls["human_review_required"]:
                errors.append(
                    "safety_controls.human_review_required: required for restricted residuals"
                )

        if residual["safety"]["contains_secrets"]:
            errors.append(
                "residual_id: residuals containing secrets cannot enter reintegration planning"
            )

        target_type = target["target_type"]
        reuse_mode = target["reuse_mode"]
        residual_form = residual["residual_form"]
        residual_category = residual["residual_category"]

        if target_type == "physical_recovery_system":
            if residual_form != "thermal":
                errors.append(
                    "target.target_type: physical_recovery_system requires a thermal residual"
                )
            if reuse_mode != "thermal_recovery":
                errors.append(
                    "target.reuse_mode: physical_recovery_system requires thermal_recovery"
                )
        if target_type == "royalty_pool":
            if residual_form != "economic":
                errors.append(
                    "target.target_type: royalty_pool requires an economic residual"
                )
            if reuse_mode != "economic_reallocation":
                errors.append(
                    "target.reuse_mode: royalty_pool requires economic_reallocation"
                )
        if target_type == "retrieval_cache":
            if residual_category not in {"cache_candidate", "intermediate_result"}:
                errors.append(
                    "target.target_type: retrieval_cache requires cache_candidate or intermediate_result"
                )
            if reuse_mode != "cache_seed":
                errors.append(
                    "target.reuse_mode: retrieval_cache requires cache_seed"
                )
        if target_type == "boundary_condition_registry" and reuse_mode != "constraint":
            errors.append(
                "target.reuse_mode: boundary_condition_registry requires constraint"
            )

    if assessment is not None:
        if assessment["residual_id"] != document["residual_id"]:
            errors.append(
                "residual_id: must match the referenced assessment"
            )
        if assessment["source_inference_id"] != document["source_inference_id"]:
            errors.append(
                "source_inference_id: must match the referenced assessment"
            )

        assessed_at = parse_datetime(
            assessment["assessed_at"], "referenced_assessment.assessed_at", errors
        )
        if planned_at and assessed_at and planned_at < assessed_at:
            errors.append(
                "planned_at: cannot be earlier than referenced assessment"
            )

        if assessment["classification"] != "recoverable":
            errors.append(
                "assessment_id: referenced assessment must classify the residual as recoverable"
            )
        decision = assessment["decision"]
        if not decision["eligible_for_reintegration_planning"]:
            errors.append(
                "assessment_id: referenced assessment is not eligible for reintegration planning"
            )
        if decision["required_action"] != "approve_for_planning":
            errors.append(
                "assessment_id: referenced assessment must require approve_for_planning"
            )
        if assessment["lifecycle"]["status"] != "active":
            errors.append(
                "assessment_id: referenced assessment lifecycle must be active"
            )

        approved_targets = {
            target_signature(candidate)
            for candidate in assessment.get("candidate_reuse_targets", [])
        }
        if target_signature(target) not in approved_targets:
            errors.append(
                "target: must exactly match a candidate_reuse_target in the referenced assessment"
            )

        if decision["human_review_required"] and not controls["human_review_required"]:
            errors.append(
                "safety_controls.human_review_required: required by the referenced assessment"
            )

    if binding["binding_mode"] == "verified_derivative":
        if not binding.get("derivative_artifact_ref"):
            errors.append(
                "residual_binding.derivative_artifact_ref: required for verified_derivative"
            )
        if transformation["mode"] == "none":
            errors.append(
                "transformation.mode: verified_derivative requires a transformation"
            )
    elif binding.get("derivative_artifact_ref"):
        errors.append(
            "residual_binding.derivative_artifact_ref: prohibited for exact_content"
        )

    mandatory_prohibited = {
        "execute_without_authorization",
        "modify_origin",
        "remove_trace",
        "expand_scope",
    }
    missing_prohibited = mandatory_prohibited - set(scope["prohibited_operations"])
    for operation in sorted(missing_prohibited):
        errors.append(
            f"scope_control.prohibited_operations: missing mandatory prohibition '{operation}'"
        )

    mandatory_halts = {
        "origin_chain_break",
        "integrity_mismatch",
        "authorization_missing",
        "scope_violation",
    }
    missing_halts = mandatory_halts - set(controls["halt_conditions"])
    for condition in sorted(missing_halts):
        errors.append(
            f"safety_controls.halt_conditions: missing mandatory halt condition '{condition}'"
        )

    if scope["maximum_uses"] > 1 and "maximum_use_exceeded" not in controls["halt_conditions"]:
        errors.append(
            "safety_controls.halt_conditions: maximum_use_exceeded is required when maximum_uses exceeds 1"
        )
    if scope["maximum_cycle_depth"] > 1 and "maximum_cycle_depth_exceeded" not in controls["halt_conditions"]:
        errors.append(
            "safety_controls.halt_conditions: maximum_cycle_depth_exceeded is required when maximum_cycle_depth exceeds 1"
        )

    if scope["environment"] == "controlled_production":
        if not controls["human_review_required"]:
            errors.append(
                "safety_controls.human_review_required: controlled_production plans require human review"
            )
        if gate["status"] != "requested":
            errors.append(
                "authorization_gate.status: controlled_production plans must have a requested authorization"
            )

    gate_status = gate["status"]
    lifecycle_status = lifecycle["status"]
    request_ref = gate.get("authorization_request_ref")

    if gate_status == "not_requested":
        if request_ref:
            errors.append(
                "authorization_gate.authorization_request_ref: prohibited when status is not_requested"
            )
        if lifecycle_status != "draft":
            errors.append(
                "lifecycle.status: not_requested plans must remain draft"
            )
    elif gate_status == "requested":
        if not request_ref:
            errors.append(
                "authorization_gate.authorization_request_ref: required when status is requested"
            )
        if lifecycle_status != "ready_for_authorization":
            errors.append(
                "lifecycle.status: requested plans must be ready_for_authorization"
            )

    benefit_types = set(expected_benefit["benefit_types"])
    if target["target_type"] == "physical_recovery_system" and "thermal_recovery" not in benefit_types:
        errors.append(
            "expected_benefit.benefit_types: thermal target requires thermal_recovery"
        )
    if target["target_type"] == "royalty_pool" and "economic_recovery" not in benefit_types:
        errors.append(
            "expected_benefit.benefit_types: royalty target requires economic_recovery"
        )
    if target["target_type"] == "retrieval_cache" and not benefit_types.intersection(
        {"reduced_computation", "reduced_latency"}
    ):
        errors.append(
            "expected_benefit.benefit_types: retrieval cache requires reduced_computation or reduced_latency"
        )

    return errors



def collect_execution_receipt_semantic_errors(
    document: dict[str, Any],
    residual_index: dict[str, dict[str, Any]],
    assessment_index: dict[str, dict[str, Any]],
    plan_index: dict[str, dict[str, Any]],
) -> list[str]:
    """Validate an authorized regenerative execution receipt."""
    errors: list[str] = []

    recorded_at = parse_datetime(document["recorded_at"], "recorded_at", errors)
    auth = document["authorization_binding"]
    execution = document["execution"]
    target = document["target_observation"]
    provenance = document["provenance_observation"]
    scope_observation = document["scope_observation"]
    safety = document["safety_observation"]
    benefit = document["benefit_realization"]
    outcome = document["outcome"]

    authorized_at = parse_datetime(auth["authorized_at"], "authorization_binding.authorized_at", errors)
    authorization_expires_at = parse_datetime(auth["expires_at"], "authorization_binding.expires_at", errors)
    started_at = parse_datetime(execution["started_at"], "execution.started_at", errors)
    completed_at = parse_datetime(execution["completed_at"], "execution.completed_at", errors)

    if authorized_at and started_at and authorized_at > started_at:
        errors.append("authorization_binding.authorized_at: must not be later than execution.started_at")
    if started_at and completed_at and started_at > completed_at:
        errors.append("execution.completed_at: must not be earlier than execution.started_at")
    if completed_at and recorded_at and completed_at > recorded_at:
        errors.append("recorded_at: must not be earlier than execution.completed_at")
    if authorization_expires_at and completed_at and authorization_expires_at < completed_at:
        errors.append("authorization_binding.expires_at: authorization must remain valid through execution completion")

    residual = residual_index.get(document["residual_id"])
    assessment = assessment_index.get(document["assessment_id"])
    plan = plan_index.get(document["plan_id"])

    if residual is None:
        errors.append(f"residual_id: unknown referenced residual '{document['residual_id']}'")
    if assessment is None:
        errors.append(f"assessment_id: unknown referenced assessment '{document['assessment_id']}'")
    if plan is None:
        errors.append(f"plan_id: unknown referenced plan '{document['plan_id']}'")

    if plan is not None:
        if plan["residual_id"] != document["residual_id"]:
            errors.append("residual_id: must match the referenced plan")
        if plan["assessment_id"] != document["assessment_id"]:
            errors.append("assessment_id: must match the referenced plan")
        if plan["source_inference_id"] != document["source_inference_id"]:
            errors.append("source_inference_id: must match the referenced plan")

        planned_at = parse_datetime(plan["planned_at"], "referenced_plan.planned_at", errors)
        plan_expires_at = parse_datetime(plan["lifecycle"]["expires_at"], "referenced_plan.lifecycle.expires_at", errors)
        if planned_at and authorized_at and authorized_at < planned_at:
            errors.append("authorization_binding.authorized_at: cannot be earlier than referenced plan")
        if plan_expires_at and started_at and started_at > plan_expires_at:
            errors.append("execution.started_at: cannot occur after referenced plan expiration")
        if plan_expires_at and completed_at and completed_at > plan_expires_at:
            errors.append("execution.completed_at: cannot occur after referenced plan expiration")

        gate = plan["authorization_gate"]
        if gate["status"] != "requested":
            errors.append("plan_id: referenced plan must have requested execution authorization")
        if gate.get("authorization_request_ref") != auth["authorization_request_ref"]:
            errors.append("authorization_binding.authorization_request_ref: must match the referenced plan")
        if not set(gate["required_scope"]).issubset(set(auth["authorized_scope"])):
            errors.append("authorization_binding.authorized_scope: must include every scope required by the referenced plan")

        plan_ops = set(plan["scope_control"]["allowed_operations"])
        auth_ops = set(auth["authorized_operations"])
        executed_ops = set(execution["operations_performed"])
        if not auth_ops.issubset(plan_ops):
            errors.append("authorization_binding.authorized_operations: must remain within plan allowed_operations")
        if not executed_ops.issubset(plan_ops):
            errors.append("execution.operations_performed: contains an operation outside the referenced plan")
        if not executed_ops.issubset(auth_ops):
            errors.append("execution.operations_performed: contains an operation outside the authorization receipt")

        plan_environment = plan["scope_control"]["environment"]
        if auth["authorized_environment"] != plan_environment:
            errors.append("authorization_binding.authorized_environment: must match the referenced plan")
        if scope_observation["environment"] != plan_environment:
            errors.append("scope_observation.environment: must match the referenced plan")

        if target_signature(target) != target_signature(plan["target"]):
            errors.append("target_observation: must exactly match the referenced plan target")

        plan_binding = plan["residual_binding"]
        input_integrity = execution["input_integrity"]
        if input_integrity["algorithm"] != plan_binding["algorithm"]:
            errors.append("execution.input_integrity.algorithm: must match the referenced plan residual binding")
        if input_integrity["digest"].lower() != plan_binding["digest"].lower():
            errors.append("execution.input_integrity.digest: must match the referenced plan residual binding")

        if set(provenance["origin_refs"]) != set(plan["provenance_binding"]["origin_refs"]):
            errors.append("provenance_observation.origin_refs: must preserve the referenced plan Origin chain")
        if not set(plan["provenance_binding"]["trace_refs"]).issubset(set(provenance["trace_refs"])):
            errors.append("provenance_observation.trace_refs: must include every referenced plan Trace")
        if set(provenance["generated_trace_refs"]).intersection(set(provenance["trace_refs"])):
            errors.append("provenance_observation.generated_trace_refs: must be new execution traces")

        if execution["use_count"] > plan["scope_control"]["maximum_uses"]:
            errors.append("execution.use_count: exceeds referenced plan maximum_uses")
        if execution["cycle_depth"] > plan["scope_control"]["maximum_cycle_depth"]:
            errors.append("execution.cycle_depth: exceeds referenced plan maximum_cycle_depth")

        plan_nodes = set(plan["scope_control"].get("node_scope", []))
        observed_node = scope_observation["node_id"]
        if plan_nodes and observed_node not in plan_nodes:
            errors.append("scope_observation.node_id: outside referenced plan node_scope")
        if execution["executor"]["node_id"] != observed_node:
            errors.append("execution.executor.node_id: must match scope_observation.node_id")

        plan_geo = set(plan["scope_control"].get("geographic_scope", []))
        observed_geo = set(scope_observation.get("geographic_scope", []))
        if plan_geo and not observed_geo:
            errors.append("scope_observation.geographic_scope: required by referenced plan")
        if observed_geo and plan_geo and not observed_geo.issubset(plan_geo):
            errors.append("scope_observation.geographic_scope: outside referenced plan geographic_scope")

        controls = plan["safety_controls"]
        if controls["contamination_scan_required"] and safety["contamination_scan_result"] == "not_applicable":
            errors.append("safety_observation.contamination_scan_result: scan is required by referenced plan")
        if controls["rollback_required"] and safety["rollback_status"] == "not_required":
            errors.append("safety_observation.rollback_status: rollback capability is required by referenced plan")
        if controls["human_review_required"] and not safety.get("human_review_ref"):
            errors.append("safety_observation.human_review_ref: required by referenced plan")

        triggered = set(safety["triggered_halt_conditions"])
        plan_halts = set(controls["halt_conditions"])
        if not triggered.issubset(plan_halts):
            errors.append("safety_observation.triggered_halt_conditions: contains a condition not defined by the referenced plan")

        expected_benefits = set(plan["expected_benefit"]["benefit_types"])
        observed_benefits = set(benefit["benefit_types"])
        if not observed_benefits.issubset(expected_benefits):
            errors.append("benefit_realization.benefit_types: must remain within referenced plan expected benefits")

    if residual is not None:
        input_integrity = execution["input_integrity"]
        if input_integrity["algorithm"] != residual["integrity"]["algorithm"]:
            errors.append("execution.input_integrity.algorithm: must match referenced residual integrity")
        if input_integrity["digest"].lower() != residual["integrity"]["digest"].lower():
            errors.append("execution.input_integrity.digest: must match referenced residual integrity")
        if set(provenance["origin_refs"]) != set(residual["origin_refs"]):
            errors.append("provenance_observation.origin_refs: must exactly preserve residual Origin references")

    if assessment is not None:
        if assessment["classification"] != "recoverable":
            errors.append("assessment_id: execution requires a recoverable assessment")
        if assessment["lifecycle"]["status"] != "active":
            errors.append("assessment_id: execution requires an active assessment")

    status = execution["status"]
    update_status = target["target_update_status"]
    triggered = safety["triggered_halt_conditions"]
    next_action = outcome["next_action"]

    if status == "completed":
        if update_status != "applied":
            errors.append("target_observation.target_update_status: completed execution requires applied")
        if triggered:
            errors.append("safety_observation.triggered_halt_conditions: completed execution cannot contain a halt condition")
        if safety["contamination_scan_result"] == "failed":
            errors.append("execution.status: cannot be completed when contamination scan failed")
        if safety["unauthorized_effects_detected"]:
            errors.append("execution.status: cannot be completed when unauthorized effects were detected")
        if next_action != "submit_for_audit":
            errors.append("outcome.next_action: completed execution must submit_for_audit")
    elif status == "partially_completed":
        if update_status != "partially_applied":
            errors.append("target_observation.target_update_status: partially_completed requires partially_applied")
        if next_action not in {"submit_for_audit", "investigate", "suspend_cycle"}:
            errors.append("outcome.next_action: invalid for partially_completed execution")
    elif status == "halted":
        if not triggered:
            errors.append("safety_observation.triggered_halt_conditions: halted execution requires at least one halt condition")
        if update_status not in {"not_applied", "partially_applied"}:
            errors.append("target_observation.target_update_status: halted execution cannot be applied")
        if next_action not in {"investigate", "suspend_cycle", "close_without_target_update"}:
            errors.append("outcome.next_action: halted execution requires investigation, suspension, or safe closure")
    elif status == "rolled_back":
        if safety["rollback_status"] != "executed":
            errors.append("safety_observation.rollback_status: rolled_back execution requires executed")
        if update_status != "reverted":
            errors.append("target_observation.target_update_status: rolled_back execution requires reverted")
        if next_action not in {"confirm_rollback", "submit_for_audit"}:
            errors.append("outcome.next_action: rolled_back execution requires rollback confirmation or audit")
    elif status == "failed":
        if update_status == "applied":
            errors.append("target_observation.target_update_status: failed execution cannot remain applied")
        if next_action not in {"investigate", "suspend_cycle"}:
            errors.append("outcome.next_action: failed execution requires investigate or suspend_cycle")

    if safety["unauthorized_effects_detected"]:
        if status == "completed":
            errors.append("safety_observation.unauthorized_effects_detected: completed status is prohibited")
        if next_action not in {"investigate", "suspend_cycle"}:
            errors.append("outcome.next_action: unauthorized effects require investigate or suspend_cycle")

    if safety["contamination_scan_result"] == "failed":
        if status == "completed":
            errors.append("safety_observation.contamination_scan_result: failed scan prohibits completed status")
        if next_action not in {"investigate", "suspend_cycle", "confirm_rollback"}:
            errors.append("outcome.next_action: failed contamination scan requires containment action")

    benefit_types = set(benefit["benefit_types"])
    if target["target_type"] == "physical_recovery_system" and "thermal_recovery" not in benefit_types:
        errors.append("benefit_realization.benefit_types: physical recovery requires thermal_recovery")
    if target["target_type"] == "retrieval_cache" and not benefit_types.intersection({"reduced_computation", "reduced_latency"}):
        errors.append("benefit_realization.benefit_types: retrieval cache requires reduced_computation or reduced_latency")
    if target["target_type"] == "royalty_pool" and "economic_recovery" not in benefit_types:
        errors.append("benefit_realization.benefit_types: royalty pool requires economic_recovery")

    for field_name, integrity in (
        ("execution.input_integrity", execution["input_integrity"]),
        ("execution.output_integrity", execution["output_integrity"]),
        ("receipt_integrity", document["receipt_integrity"]),
    ):
        expected_length = 64 if integrity["algorithm"] == "sha256" else 128
        if len(integrity["digest"]) != expected_length:
            errors.append(f"{field_name}.digest: invalid digest length for {integrity['algorithm']}")

    return errors

def collect_semantic_errors(
    document: dict[str, Any],
    residual_index: dict[str, dict[str, Any]],
    assessment_index: dict[str, dict[str, Any]],
    plan_index: dict[str, dict[str, Any]],
) -> list[str]:
    record_type = document["record_type"]
    if record_type == "inference_residual_record":
        return collect_residual_semantic_errors(document)
    if record_type == "residual_classification_assessment":
        return collect_assessment_semantic_errors(document, residual_index)
    if record_type == "residual_reintegration_plan":
        return collect_plan_semantic_errors(
            document,
            residual_index,
            assessment_index,
        )
    if record_type == "regenerative_cycle_execution_receipt":
        return collect_execution_receipt_semantic_errors(
            document, residual_index, assessment_index, plan_index
        )
    return [f"record_type: unsupported record type '{record_type}'"]


def print_errors(label: str, errors: list[str]) -> None:
    print(label)
    for error in errors:
        print(f"  - {error}")


def load_pass_documents() -> list[tuple[Path, dict[str, Any]]]:
    return [
        (path, load_yaml_or_json(path))
        for path in discover_examples(PASS_DIR)
    ]


def build_indexes(
    documents: list[tuple[Path, dict[str, Any]]],
) -> tuple[
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
    list[str],
]:
    residual_index: dict[str, dict[str, Any]] = {}
    assessment_index: dict[str, dict[str, Any]] = {}
    plan_index: dict[str, dict[str, Any]] = {}
    receipt_index: dict[str, dict[str, Any]] = {}
    errors: list[str] = []

    configs = {
        "inference_residual_record": ("residual_id", residual_index),
        "residual_classification_assessment": ("assessment_id", assessment_index),
        "residual_reintegration_plan": ("plan_id", plan_index),
        "regenerative_cycle_execution_receipt": ("receipt_id", receipt_index),
    }

    for path, document in documents:
        record_type = document.get("record_type")
        config = configs.get(record_type)
        if config is None:
            continue
        id_field, index = config
        record_id = document.get(id_field)
        if not isinstance(record_id, str):
            continue
        if record_id in index:
            errors.append(
                f"{path.relative_to(ROOT_DIR)}: duplicate {id_field} '{record_id}'"
            )
            continue
        index[record_id] = document

    return residual_index, assessment_index, plan_index, receipt_index, errors


def validate_pass_examples(
    validators: dict[str, Draft202012Validator],
    pass_documents: list[tuple[Path, dict[str, Any]]],
    residual_index: dict[str, dict[str, Any]],
    assessment_index: dict[str, dict[str, Any]],
    plan_index: dict[str, dict[str, Any]],
) -> int:
    failures = 0

    for path, document in pass_documents:
        relative_path = path.relative_to(ROOT_DIR)
        print(f"\n[validate-pass] {relative_path}")

        validator = validator_for_document(document, validators)
        if validator is None:
            print_errors(
                "[schema-error]",
                [
                    "record_type: unsupported or missing type "
                    f"'{document.get('record_type')}'"
                ],
            )
            failures += 1
            continue

        schema_errors = collect_schema_errors(validator, document)
        if schema_errors:
            print_errors("[schema-error]", schema_errors)
            failures += 1
            continue

        print("[schema-ok]")
        semantic_errors = collect_semantic_errors(
            document,
            residual_index,
            assessment_index,
            plan_index,
        )
        if semantic_errors:
            print_errors("[semantic-error]", semantic_errors)
            failures += 1
            continue

        print("[semantic-ok]")

    return failures


def validate_fail_examples(
    validators: dict[str, Draft202012Validator],
    residual_index: dict[str, dict[str, Any]],
    assessment_index: dict[str, dict[str, Any]],
    plan_index: dict[str, dict[str, Any]],
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
                [
                    "record_type: unsupported or missing type "
                    f"'{document.get('record_type')}'"
                ],
            )
            continue

        schema_errors = collect_schema_errors(validator, document)
        if schema_errors:
            print_errors("[expected-schema-error]", schema_errors)
            continue

        print("[schema-ok]")
        semantic_errors = collect_semantic_errors(
            document,
            residual_index,
            assessment_index,
            plan_index,
        )
        if semantic_errors:
            print_errors("[expected-semantic-error]", semantic_errors)
            continue

        print("[unexpected-pass] example passed all validation")
        failures += 1

    return failures


def main() -> int:
    print("=== Inferential Regenerative Cycle Protocol v0.4 Validation ===")
    print(
        "schema [inference-residual-record]: "
        "schemas/inference-residual-record.schema.json"
    )
    print(
        "schema [residual-classification-assessment]: "
        "schemas/residual-classification-assessment.schema.json"
    )
    print(
        "schema [residual-reintegration-plan]: "
        "schemas/residual-reintegration-plan.schema.json"
    )
    print(
        "schema [regenerative-cycle-execution-receipt]: "
        "schemas/regenerative-cycle-execution-receipt.schema.json"
    )

    try:
        validators = load_validators()
        pass_documents = load_pass_documents()
    except (RuntimeError, yaml.YAMLError, ValueError) as exc:
        print(f"[fatal] {exc}", file=sys.stderr)
        return 1

    residual_index, assessment_index, plan_index, _receipt_index, index_errors = build_indexes(
        pass_documents
    )
    if index_errors:
        print_errors("[fatal-index-error]", index_errors)
        return 1

    pass_failures = validate_pass_examples(
        validators,
        pass_documents,
        residual_index,
        assessment_index,
        plan_index,
    )
    fail_failures = validate_fail_examples(
        validators,
        residual_index,
        assessment_index,
        plan_index,
    )

    print("\n=== Validation Summary ===")
    print(f"pass example failures: {pass_failures}")
    print(f"fail example failures: {fail_failures}")

    if pass_failures + fail_failures:
        print("Validation failed.")
        return 1

    print("All examples behaved as expected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
