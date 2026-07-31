# Inferential Regenerative Cycle Protocol

A protocol for recording, classifying, planning, authorizing, executing, auditing, stabilizing, and controlling the reuse of residual value produced by AI inference cycles.

**Current specification version:** `0.5.0`

## Overview

Most AI systems use a one-directional resource flow:

```text
Electricity, data, and computation
              ↓
          Inference
              ↓
        Primary output
              ↓
Rejected candidates, intermediate results, idle capacity,
failure observations, thermal output, and unallocated value
are discarded
```

The Inferential Regenerative Cycle Protocol introduces a bounded alternative.

It treats unused outputs, byproducts, and unrealized value as **residuals** that may become resources only after their Origin, integrity, safety, authorization, execution, and stability have been verified.

```text
Origin
  ↓
Inference Residual Record
  ↓
Residual Classification Assessment
  ↓
Residual Reintegration Plan
  ↓
External Authorization
  ↓
Regenerative Cycle Execution Receipt
  ↓
Regenerative Cycle Audit Record
  ↓
Cycle Stability Assessment
  ↓
Regenerative Cycle Control Receipt
```

The protocol does not claim that AI systems can create physical energy from nothing.

In this specification, **regenerative** means recovering usable value from resources that have already been consumed, produced, or left disconnected.

Examples include:

* reusing verified intermediate computation,
* converting failure observations into safety controls,
* routing idle capacity to bounded low-priority work,
* recovering thermal output from compute infrastructure,
* preserving dormant evidence for later reassessment,
* returning unallocated economic value to an authorized allocation process.

A residual is not automatically a resource.

It becomes reusable only when a safe, authorized, traceable, and reversible next connection has been established.

---

## Core separation principle

```text
Record ≠ Classification
Classification ≠ Plan
Plan ≠ Authorization
Authorization ≠ Execution
Execution ≠ Audit
Audit ≠ Stability
Stability ≠ Control Authority
```

Each stage has a separate responsibility.

No record may silently grant the authority of a later stage.

In particular:

* recording a residual does not classify it,
* classifying a residual as recoverable does not authorize reuse,
* creating a reintegration plan does not authorize execution,
* receiving authorization does not prove that execution was correct,
* recording an execution does not constitute an audit,
* passing an audit does not prove that repeated circulation is stable,
* recommending a control action does not grant unlimited control authority.

---

## Seven-record evidence chain

Version `0.5.0` defines seven protocol records.

| Stage | Record                                 | Purpose                                                                                       |
| ----- | -------------------------------------- | --------------------------------------------------------------------------------------------- |
| 1     | `Inference Residual Record`            | Records what remained after inference and where it originated                                 |
| 2     | `Residual Classification Assessment`   | Classifies the residual as Recoverable, Dormant, Hazardous, or Discardable                    |
| 3     | `Residual Reintegration Plan`          | Defines the target, purpose, scope, limits, and safety conditions of proposed reuse           |
| 4     | `Regenerative Cycle Execution Receipt` | Records what was actually executed under external authorization                               |
| 5     | `Regenerative Cycle Audit Record`      | Verifies authorization, execution, provenance, integrity, contamination, and claimed benefits |
| 6     | `Cycle Stability Assessment`           | Evaluates whether repeated circulation remains bounded and safe                               |
| 7     | `Regenerative Cycle Control Receipt`   | Applies the final Continue, Suspend, Roll Back, or Close decision                             |

---

## 1. Inference Residual Record

The `Inference Residual Record` identifies a residual produced by an inference cycle.

It records:

* residual identity,
* source inference identity,
* Origin references,
* Trace references,
* producer identity,
* residual category,
* physical or logical form,
* content location,
* sensitivity,
* integrity digest,
* retention conditions,
* preliminary safety observations,
* eligibility for formal classification.

Supported residual categories include:

```text
rejected_candidate
intermediate_result
failed_attempt
unused_evidence
discovered_constraint
safety_observation
cache_candidate
idle_capacity
thermal_byproduct
unallocated_value
other
```

Supported residual forms include:

```text
data
computation
thermal
temporal
economic
operational
```

The record may describe logical AI artifacts as well as physical or economic byproducts.

---

## 2. Residual Classification Assessment

The `Residual Classification Assessment` determines the residual's permitted lifecycle.

```text
Recoverable
Dormant
Hazardous
Discardable
```

### Recoverable

A residual that may proceed to bounded reintegration planning.

Recoverable does not mean automatically reusable.

A recoverable residual still requires:

```text
Plan
  ↓
Authorization
  ↓
Execution
  ↓
Audit
  ↓
Stability Assessment
```

### Dormant

A residual that is not currently reusable but may become valuable under future conditions.

Dormant records require:

* a declared retention state,
* a reassessment time,
* preservation of Origin and integrity,
* no execution before reassessment.

### Hazardous

A residual that may contaminate, compromise, or destabilize future inference cycles.

Hazardous residuals must be:

* quarantined,
* prohibited from reintegration,
* reviewed under an appropriate authority,
* isolated from ordinary inference contexts.

### Discardable

A residual with no legitimate future use under the current assessment.

Discardable residuals may proceed to controlled disposal only when:

* no legal hold prevents disposal,
* required evidence has been preserved,
* disposal is authorized,
* disposal does not break an active Trace or audit chain.

---

## 3. Residual Reintegration Plan

The `Residual Reintegration Plan` defines how a recoverable residual may be reused.

It records:

* the referenced residual,
* the referenced classification assessment,
* the source inference,
* the proposed target,
* the proposed reuse mode,
* residual integrity binding,
* Origin and Trace preservation,
* required transformation,
* permitted operations,
* prohibited operations,
* geographic and node scope,
* maximum reuse count,
* maximum cycle depth,
* safety controls,
* halt conditions,
* expected benefits,
* authorization requirements,
* plan lifecycle.

A plan is not an execution command.

```text
Plan ≠ Authorization
```

The authorization gate supports only pre-execution states such as:

```text
not_requested
requested
```

A plan cannot declare itself authorized.

### Mandatory prohibited operations

A valid plan must prohibit at least:

```text
execute_without_authorization
modify_origin
remove_trace
expand_scope
```

### Mandatory halt conditions

A valid plan must stop when conditions such as the following occur:

```text
origin_chain_break
integrity_mismatch
authorization_missing
scope_violation
```

Plans with higher reuse counts or cycle depths must also include bounded termination conditions.

---

## 4. Regenerative Cycle Execution Receipt

The `Regenerative Cycle Execution Receipt` records what happened when an authorized plan was executed.

Supported execution states include:

```text
completed
partially_completed
halted
rolled_back
failed
```

The receipt records:

* authorization request and receipt references,
* authorization decision,
* authorized operations,
* authorized environment,
* execution start and completion times,
* performed operations,
* target observations,
* input integrity,
* Origin and Trace observations,
* execution-generated Trace references,
* actual node and geographic scope,
* safety observations,
* triggered halt conditions,
* rollback state,
* realized benefits,
* execution outcome,
* receipt integrity.

The validator enforces:

```text
Executed Operations
    ⊆ Authorized Operations
    ⊆ Planned Operations
```

An execution may not expand the plan or authorization scope.

### Safe halt

A halted execution is not automatically a failed execution.

A safe halt can be a valid outcome when:

* the target changed after authorization,
* integrity no longer matches,
* authorization expired,
* a scope violation was detected,
* contamination was detected,
* a mandatory halt condition became true.

The receipt must show that prohibited effects were not applied.

---

## 5. Regenerative Cycle Audit Record

The `Regenerative Cycle Audit Record` independently verifies the execution evidence.

Audit verification covers:

### Authorization

* authorization request match,
* authorization receipt verification,
* authorization decision validity,
* authorized scope,
* authorization time validity.

### Execution

* plan match,
* target match,
* operation match,
* provenance match,
* integrity match,
* execution-status match.

### Contamination

* contamination state,
* propagation scope,
* isolation state,
* unresolved contamination findings.

### Benefit realization

* claimed benefit evidence,
* observed metrics,
* measurement references,
* unverifiable or overstated benefit claims.

Supported audit results are:

```text
passed
passed_with_conditions
failed
inconclusive
```

A passed audit requires complete authorization and execution consistency.

Confirmed contamination cannot produce a passed audit.

---

## 6. Cycle Stability Assessment

A correct single execution does not prove that repeated circulation is safe.

The `Cycle Stability Assessment` evaluates the cycle as a continuing system.

It examines:

* cycle depth,
* reuse count,
* resource pressure,
* feedback amplification,
* confidence trends,
* provenance continuity,
* authorization continuity,
* contamination state,
* benefit persistence,
* unresolved disputes,
* audit failures.

Supported stability states are:

```text
stable
conditionally_stable
unstable
critical
```

### Stable

The cycle remains within all declared safety and resource thresholds.

### Conditionally stable

The cycle may continue only under declared monitoring, reassessment, or reduced-scope conditions.

### Unstable

The cycle has exceeded one or more limits and should be suspended or rolled back.

### Critical

The cycle has a severe structural failure, such as:

* broken Origin continuity,
* broken authorization continuity,
* confirmed contamination,
* severe feedback amplification,
* uncontrolled propagation.

Critical cycles cannot continue.

### Thresholds

A stability assessment may define limits such as:

```yaml
thresholds:
  maximum_cycle_depth: 1
  maximum_reuse_count: 1
  maximum_resource_pressure: moderate
  maximum_feedback_amplification: low
```

Detected violations must be declared explicitly.

An assessment cannot hide a threshold violation while reporting the cycle as stable.

---

## 7. Regenerative Cycle Control Receipt

The `Regenerative Cycle Control Receipt` applies the authoritative post-assessment decision.

Supported decisions are:

```text
continue
suspend
roll_back
close
```

### Continue

Continuation requires monitoring.

Typical required action:

```text
monitor
```

A conditionally stable cycle may also require a declared reassessment time or measurement window.

### Suspend

Suspension requires control actions such as:

```text
freeze_reintegration
revoke_authorization
```

Suspension prevents additional residual reuse while preserving evidence for investigation.

### Roll back

Rollback is a new execution action.

It therefore requires separate authorization.

Typical actions include:

```text
execute_rollback
freeze_reintegration
revoke_authorization
```

An audit or stability assessor cannot silently grant itself rollback authority.

### Close

Closure ends the cycle and releases its resources.

Typical required actions include:

```text
archive_cycle
release_resources
```

Closure must preserve the audit trail before operational resources are released.

---

## Safety invariants

The reference validator rejects, among other conditions:

* a residual without an Origin reference,
* a high-risk residual that is not quarantined,
* a hazardous residual with a reuse target,
* a dormant residual without a reassessment time,
* a recoverable classification with unverified provenance,
* a reintegration plan for a non-recoverable residual,
* a target not approved by the referenced assessment,
* Origin replacement or Trace removal,
* execution without external authorization,
* execution outside planned operations,
* execution outside authorized node or geographic scope,
* execution after plan expiration,
* execution after authorization expiration,
* a completed execution with an active halt condition,
* a passed audit with authorization or scope mismatch,
* a passed audit with confirmed contamination,
* continuation after a failed audit,
* a stable assessment with broken provenance,
* undeclared cycle-depth or reuse-count violations,
* continuation of a critical cycle,
* suspension without freezing reintegration,
* rollback without separate authorization,
* closure without archival and resource release,
* a final control decision that contradicts the referenced stability assessment.

---

## End-to-end examples

### Cache reuse

```text
Intermediate route features
  ↓
Inference Residual Record
  ↓
Recoverable classification
  ↓
Bounded cache-seed plan
  ↓
External authorization
  ↓
Completed execution
  ↓
Verified latency and computation savings
  ↓
Passed audit
  ↓
Stable assessment
  ↓
Continue with monitoring
```

### Safe halt

```text
Rejected route candidate
  ↓
Recoverable classification
  ↓
Boundary-registry plan
  ↓
External authorization
  ↓
Target changes before modification
  ↓
Execution halts safely
  ↓
Audit confirms that no unauthorized effect occurred
  ↓
Conditionally stable
  ↓
Close and release resources
```

### Thermal recovery

```text
GPU thermal byproduct
  ↓
Recoverable classification
  ↓
Physical heat-recovery plan
  ↓
Human-authorized transfer
  ↓
Measured thermal recovery
  ↓
Passed audit
  ↓
Conditionally stable
  ↓
Continue for another measurement window
```

---

## Repository structure

```text
README.md
CHANGELOG.md
LICENSE
requirements.txt

.github/
└── workflows/
    └── validate.yml

schemas/
├── inference-residual-record.schema.json
├── residual-classification-assessment.schema.json
├── residual-reintegration-plan.schema.json
├── regenerative-cycle-execution-receipt.schema.json
├── regenerative-cycle-audit-record.schema.json
├── cycle-stability-assessment.schema.json
└── regenerative-cycle-control-receipt.schema.json

scripts/
└── validate_examples.py

docs/
├── architecture.md
├── audit-stability-control.md
├── execution-receipts.md
├── reintegration-planning.md
└── security-considerations.md

examples/
├── pass/
│   └── Valid records expected to pass schema and semantic validation
└── fail/
    └── Invalid records expected to be rejected
```

---

## Validation

### Requirements

The reference validator uses:

```text
jsonschema
PyYAML
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the validator:

```bash
python scripts/validate_examples.py
```

GitHub Actions runs the same validation process with Python `3.12`.

Expected result:

```text
=== Validation Summary ===
pass example failures: 0
fail example failures: 0
All examples behaved as expected.
```

The v0.5 reference suite contains:

```text
27 passing examples
49 failing examples
7 cross-referenced record types
```

Passing examples must satisfy both JSON Schema and semantic validation.

Failing examples must be rejected by at least one of those layers.

### Validation layers

```text
JSON Schema validation
          ↓
Record-type semantic validation
          ↓
Cross-record reference validation
          ↓
Lifecycle and time-order validation
          ↓
Authorization, scope, and integrity validation
          ↓
Audit, stability, and control consistency validation
```

---

## Five-Phase relationship

The protocol is implementation-neutral, but it can be mapped to a Yin-Yang Five-Phase operational model.

| Phase | Infrastructure role                                      |
| ----- | -------------------------------------------------------- |
| Wood  | participation, growth, capability activation             |
| Fire  | inference, execution, computation, thermal output        |
| Earth | state, Trace, data, retention                            |
| Metal | classification, authorization, audit, stability, control |
| Water | cooling, resource movement, reward, liquidity            |

A typical regenerative flow is:

```text
Wood
  ↓
New capability or node participation

Fire
  ↓
Inference, execution, and residual generation

Earth
  ↓
Residual recording, Trace preservation, and retention

Metal
  ↓
Classification, authorization, audit, and control

Water
  ↓
Resource recovery, redistribution, and renewed circulation

Wood
```

In v0.5, Audit, Stability, and Control form the Metal function that prevents regenerative circulation from becoming self-contamination.

Yin and Yang may be applied as operating modes within every phase:

* Yang activates, expands, executes, and distributes.
* Yin cools, pauses, compresses, reviews, and preserves.

---

## Interoperability boundaries

This repository defines the regenerative-cycle evidence chain.

It does not define a universal authorization system.

Authorization receipts are expected to be produced by an external authorization protocol or equivalent trusted authority.

The protocol may interoperate with systems that provide:

* Origin registration,
* Trace relay,
* action authorization receipts,
* execution evidence,
* audit records,
* structural precedence,
* royalty allocation,
* human-axis binding,
* protocol interoperability profiles.

External references must remain verifiable and must not be replaced by local self-authorization.

---

## Version history

| Version | Primary addition                                 |
| ------- | ------------------------------------------------ |
| `v0.1`  | Inference Residual Record                        |
| `v0.2`  | Residual Classification Assessment               |
| `v0.3`  | Residual Reintegration Plan                      |
| `v0.4`  | Regenerative Cycle Execution Receipt             |
| `v0.5`  | Audit, Stability Assessment, and Control Receipt |

---

## Design principles

> A resource becomes waste when no safe next connection exists.

> A reusable residual is not an authorized residual.

> A completed execution is not a verified execution.

> A verified execution is not necessarily a stable cycle.

> A cycle becomes dangerous when it cannot prove when to stop.

The protocol therefore treats stopping, suspending, rolling back, and closing as first-class capabilities rather than exceptional failures.

---

## License

MIT License.
