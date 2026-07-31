# Architecture

## 1. Purpose

The Inferential Regenerative Cycle Protocol governs the path from residual observation to controlled reuse.

Version 0.3 introduces the first forward-moving artifact in that path: the Residual Reintegration Plan.

## 2. Three-record chain

```text
Inference Residual Record
  identifies what remains

Residual Classification Assessment
  decides whether the residual is recoverable, dormant, hazardous, or discardable

Residual Reintegration Plan
  proposes one bounded future use for a recoverable residual

Each stage has a different authority.

Record       = observation
Assessment   = classification
Plan         = proposal

None of these records authorizes execution.

3. Cross-record invariants

A valid plan must preserve the following chain:

plan.residual_id
  = assessment.residual_id
  = residual.residual_id

plan.source_inference_id
  = assessment.source_inference_id
  = residual.source_inference_id

The plan must also be created after the assessment, and the assessment after the residual.

4. Approved target rule

The classification assessment defines candidate targets.

The plan may select exactly one of those targets, but it cannot invent a new target.

Assessment candidate target
        ↓ exact type, ID, and mode match
Reintegration plan target

This prevents a safe classification from being reused as permission for an unrelated destination.

5. Integrity binding

The plan binds to the residual digest.

Two modes are supported:

exact_content

The plan references the exact residual content recorded in the residual record.

verified_derivative

The plan references a derivative artifact produced under a declared transformation policy.

A verified derivative still preserves the original Origin chain and must not erase the source digest.

6. Scope control

Every plan defines:

allowed operations,

prohibited operations,

maximum uses,

maximum cycle depth,

execution environment,

optional geographic scope,

optional node scope.

The maximum circulation depth prevents a residual from being copied indefinitely through recursive inference loops.

7. Authorization boundary

Version 0.3 supports only two authorization states:

not_requested
requested

A plan can request future authority, but cannot contain an authorized state.

Execution authority must come from a separate authorization artifact.

8. Physical and logical reintegration

The same plan model supports:

data and computation reuse,

safety and boundary updates,

agent handoffs,

routing policy updates,

physical heat recovery,

economic reallocation.

The validator checks that the target is compatible with the residual form.

9. Future execution layer

Version 0.4 will record what actually happened.

Plan
  ↓
Authorization
  ↓
Execution Receipt
  ↓
Audit

The execution receipt must not merely cite the plan. It must prove that actual operations stayed within the plan and authorization scopes.

