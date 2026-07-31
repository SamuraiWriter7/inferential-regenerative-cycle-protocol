# Changelog

All notable changes to the Inferential Regenerative Cycle Protocol are documented in this file.

The project develops the protocol incrementally from residual recording to closed-loop audit, stability assessment, and authoritative cycle control.

## [0.5.0] - 2026-07-31

### Added

* `Regenerative Cycle Audit Record` JSON Schema
* `Cycle Stability Assessment` JSON Schema
* `Regenerative Cycle Control Receipt` JSON Schema
* Audit verification for:

  * authorization-request matching,
  * authorization-receipt verification,
  * authorization-decision validity,
  * authorized-scope matching,
  * authorization-time validity,
  * plan matching,
  * target matching,
  * operation matching,
  * provenance matching,
  * integrity matching,
  * execution-status matching,
  * contamination propagation,
  * isolation status,
  * realized-benefit evidence,
  * unresolved findings.
* Audit results:

  * `passed`,
  * `passed_with_conditions`,
  * `failed`,
  * `inconclusive`.
* Stability evaluation for:

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
* Stability states:

  * `stable`,
  * `conditionally_stable`,
  * `unstable`,
  * `critical`.
* Final cycle-control decisions:

  * `continue`,
  * `suspend`,
  * `roll_back`,
  * `close`.
* State-transition records for post-assessment control.
* Required control actions for monitoring, suspension, rollback, archival, and resource release.
* Separate authorization binding for rollback execution.
* Passing end-to-end examples for:

  * audited and stable cache reuse,
  * audited safe halt and cycle closure,
  * audited thermal recovery with conditional continuation.
* Failing examples for contradictory audit, stability, and control records.
* Seven-record cross-reference indexing in the Python reference validator.
* Documentation for:

  * closed-loop audit,
  * stability assessment,
  * cycle control,
  * control-plane separation,
  * failure and safe halt as evidence.

### Changed

* Updated all protocol schemas to `schema_version: "0.5.0"`.
* Updated all active passing examples to `schema_version: "0.5.0"`.
* Normalized legacy failing examples so they test their intended schema or semantic violation rather than failing only because of an obsolete version number.
* Extended the evidence chain from execution recording to authoritative cycle control.
* Extended the validator registry from four record types to seven.
* Added cross-record validation across:

  * residual records,
  * classification assessments,
  * reintegration plans,
  * execution receipts,
  * audit records,
  * stability assessments,
  * control receipts.
* Added validation of audit and control time ordering.
* Added validation that control decisions preserve the recommendation of the referenced stability assessment.
* Expanded the reference suite to:

  * 27 passing examples,
  * 49 failing examples.

### Security

* Passed audits require valid authorization and complete execution verification.
* A passed audit is prohibited when:

  * authorization does not match,
  * scope does not match,
  * target or operation evidence does not match,
  * provenance does not match,
  * integrity does not match,
  * contamination is confirmed.
* Confirmed contamination requires:

  * a failed audit,
  * isolation evidence,
  * suspension or rollback.
* Broken provenance continuity requires `critical` stability status.
* Broken authorization continuity requires `critical` stability status.
* Severe feedback amplification prohibits `stable` classification.
* Severe resource pressure prohibits `stable` classification.
* Detected cycle-depth and reuse-count violations must be declared.
* Critical cycles cannot receive a `continue` recommendation.
* Conditional continuation requires monitoring or reassessment conditions.
* Rollback requires separate execution authorization.
* Suspension requires:

  * reintegration freeze,
  * authorization revocation.
* Closure requires:

  * cycle archival,
  * resource release.
* Final control decisions must match the referenced stability recommendation.

---

## [0.4.0] - 2026-07-31

### Added

* `Regenerative Cycle Execution Receipt` JSON Schema
* Runtime authorization binding for:

  * authorization request,
  * authorization receipt,
  * authorization decision,
  * authorized operations,
  * authorized environment.
* Execution states:

  * `completed`,
  * `partially_completed`,
  * `halted`,
  * `rolled_back`,
  * `failed`.
* Runtime observations for:

  * target state,
  * performed operations,
  * input integrity,
  * Origin preservation,
  * Trace preservation,
  * execution-generated Trace references,
  * node scope,
  * geographic scope,
  * contamination checks,
  * triggered halt conditions,
  * rollback state,
  * realized benefits,
  * execution outcome,
  * receipt integrity.
* Safe-halt evidence handling.
* Passing examples for:

  * completed cache-seed execution,
  * safely halted route-boundary execution,
  * completed thermal-recovery execution.
* Failing examples for:

  * unknown plans,
  * mismatched authorization requests,
  * expired plans,
  * expired authorization,
  * operations outside the plan,
  * operations outside authorization,
  * target substitution,
  * node-scope violations,
  * integrity mismatch,
  * exceeded use limits,
  * completed execution with an active halt condition,
  * halted execution without a halt condition,
  * contamination failure reported as completed,
  * unauthorized effects,
  * missing human review in controlled production.

### Changed

* Updated active schemas and examples to `schema_version: "0.4.0"`.
* Extended the evidence chain from planning to authorized execution.
* Added execution-receipt indexing to the Python validator.
* Added semantic comparison between:

  * planned operations,
  * authorized operations,
  * executed operations.
* Added validation of actual runtime environment, node, geographic scope, target, use count, and cycle depth.
* Separated expected benefits from observed benefits.

### Security

* Enforced:

```text
Executed Operations
    ⊆ Authorized Operations
    ⊆ Planned Operations
```

* Prohibited execution after plan expiration.
* Prohibited execution after authorization expiration.
* Prohibited execution outside declared node and geographic scope.
* Required input integrity to match both the residual record and reintegration plan.
* Required safe halt when mandatory halt conditions were triggered.
* Required prohibited effects to remain unapplied after a halt.
* Required controlled-production execution to preserve human-review requirements.

---

## [0.3.0] - 2026-07-31

### Added

* `Residual Reintegration Plan` JSON Schema
* Reintegration target definition.
* Reuse-mode definition.
* Residual and integrity binding.
* Origin and Trace preservation.
* Transformation requirements.
* Scope controls for:

  * operations,
  * environment,
  * nodes,
  * geographic regions,
  * maximum reuse count,
  * maximum cycle depth.
* Safety controls.
* Mandatory halt conditions.
* Authorization gate.
* Expected-benefit declarations.
* Plan lifecycle and expiration.
* Passing examples for:

  * cache-seed planning,
  * route-boundary planning,
  * thermal-recovery planning.
* Failing examples for:

  * authorization bypass,
  * planning before assessment,
  * planning from a dormant assessment,
  * controlled production without human review,
  * expired plans,
  * integrity mismatch,
  * missing halt conditions,
  * Origin mismatch,
  * requested authorization without a reference,
  * self-targeting,
  * unapproved targets,
  * unknown assessments.

### Changed

* Updated active schemas and examples to `schema_version: "0.3.0"`.
* Extended the evidence chain from classification to bounded reintegration planning.
* Added assessment and plan cross-reference indexes to the Python validator.
* Required reintegration targets to match a candidate target approved by the referenced assessment.
* Required plan Origin references to preserve the residual Origin chain.
* Required residual digests to match across the residual record and plan.
* Clarified that a plan may request authorization but cannot authorize itself.

### Security

* Added mandatory prohibited operations:

```text
execute_without_authorization
modify_origin
remove_trace
expand_scope
```

* Added mandatory halt conditions for:

  * Origin-chain breaks,
  * integrity mismatch,
  * missing authorization,
  * scope violations.
* Prohibited plans for Dormant, Hazardous, and Discardable residuals.
* Prohibited target substitution.
* Prohibited residual self-targeting.
* Required bounded use counts and cycle depths.
* Required additional halt conditions when higher reuse counts or cycle depths were permitted.

---

## [0.2.0] - 2026-07-31

### Added

* `Residual Classification Assessment` JSON Schema
* Formal residual classifications:

  * `recoverable`,
  * `dormant`,
  * `hazardous`,
  * `discardable`.
* Assessment fields for:

  * assessor identity,
  * assessor independence,
  * assessment time,
  * classification confidence,
  * rationale,
  * evidence references,
  * hazard level,
  * contamination risk,
  * provenance status,
  * integrity status,
  * policy compatibility,
  * candidate reuse targets,
  * required action,
  * human-review requirement,
  * lifecycle state,
  * reassessment time.
* Cross-reference validation between residual records and classification assessments.
* Passing examples for each classification.
* Failing examples for:

  * recoverable residuals with high hazard,
  * Dormant residuals without reassessment,
  * Hazardous residuals with reuse targets,
  * Discardable residuals with reuse targets,
  * unknown residual references,
  * source-inference mismatch,
  * missing provenance,
  * disposal under legal hold.

### Changed

* Updated active schemas and examples to `schema_version: "0.2.0"`.
* Renamed the preliminary field:

```text
reuse_eligible
```

to:

```text
classification_eligible
```

* Clarified that preliminary eligibility permits formal classification, not reuse.
* Added lifecycle states for active, awaiting-review, quarantined, and awaiting-disposal assessments.
* Added time-order validation between residual creation and assessment.

### Security

* Required Recoverable residuals to have:

  * `none` or `low` hazard,
  * `none` or `low` contamination risk,
  * verified provenance,
  * verified integrity,
  * at least one candidate reuse target.
* Required Dormant residuals to declare a reassessment time.
* Required Hazardous residuals to:

  * prohibit reuse planning,
  * require human review,
  * remain quarantined.
* Required Discardable residuals to:

  * prohibit reuse targets,
  * respect legal holds,
  * proceed through controlled disposal.

---

## [0.1.0] - 2026-07-31

### Added

* Initial Inferential Regenerative Cycle Protocol repository.
* `Inference Residual Record` JSON Schema.
* Residual identity.
* Source-inference binding.
* Required Origin references.
* Optional Trace references.
* Producer identity.
* Residual category taxonomy.
* Logical and physical residual forms.
* Content-reference structure.
* Sensitivity classification.
* SHA-256 and SHA-512 integrity records.
* Retention and review policy.
* Preliminary safety observations.
* Preliminary processing disposition.
* Extension namespace support.
* Passing examples for:

  * rejected inference candidates,
  * quarantined safety observations.
* Failing examples for:

  * missing Origin references,
  * high-risk residuals marked reusable,
  * restricted inline content,
  * thermal category and form mismatch.
* Python reference validator.
* JSON Schema validation.
* Protocol-specific semantic validation.
* GitHub Actions validation workflow.
* Architecture documentation.
* Residual taxonomy documentation.
* Security considerations.

### Security

* Required high- and critical-hazard residuals to be quarantined.
* Prohibited high- and critical-hazard residuals from being marked reusable.
* Required human review for high- and critical-hazard residuals.
* Prohibited restricted residuals from storing inline content.
* Prohibited secret-containing residuals from storing inline content.
* Required quarantined records to include a quarantine reason.
* Required integrity digests for every residual record.
* Required review and expiration times to occur after residual creation.
