# Audit, Stability, and Control

## Audit

Audit asks whether the execution receipt is supported by external evidence.

A passed audit requires:

- valid authorization,
- exact plan and target matching,
- operations within scope,
- intact provenance,
- matching integrity digests,
- clean contamination assessment,
- no unresolved severe findings,
- verified or partially verified benefits.

## Stability

Audit verifies an execution event. Stability evaluates the wider cycle.

A cycle may have a valid execution and still be unstable because of:

- repeated self-reuse,
- excessive cycle depth,
- resource pressure,
- feedback amplification,
- weakening provenance,
- expired or broken authorization continuity,
- unresolved disputes,
- benefits that do not persist.

## Control

The control receipt converts the stability recommendation into an authoritative state transition.

```text
stable               → continue or close
conditionally_stable → continue, close, or human review
unstable             → suspend, roll back, or human review
critical             → suspend or roll back
```

A human-review recommendation is not itself a final control decision. A later authorized controller must issue the final receipt.

## Why three records

Combining audit, stability, and control into one object would let the evaluator silently become the authority. Separation preserves accountability:

```text
Auditor reports evidence.
Stability assessor interprets system condition.
Controller applies an authorized state transition.
