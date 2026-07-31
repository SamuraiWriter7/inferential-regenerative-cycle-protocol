# Security Considerations

## 1. Planning must not grant authority

The most important v0.3 rule is:

> The document that proposes an action must not authorize that action.

The schema therefore rejects an authorization status such as `authorized`.

## 2. Target substitution

An attacker may try to replace an approved target with a more valuable or less controlled destination.

The validator requires an exact match against the assessment-approved target type, ID, and reuse mode.

## 3. Provenance stripping

Reintegrated content may appear harmless after Origin or Trace information has been removed.

Every plan must:

- preserve all Origin references exactly,
- retain all residual Trace references,
- prohibit Origin modification,
- prohibit Trace removal,
- halt when the Origin chain breaks.

## 4. Integrity substitution

A plan can be redirected to altered content while keeping the original residual ID.

The plan therefore binds to the original digest and algorithm.

## 5. Recursive contamination

A low-risk residual can become dangerous after repeated circulation or transformation.

Plans must limit:

- total uses,
- lineage depth,
- target scope,
- transformation scope.

Plans with repeated use or depth greater than one must include corresponding halt conditions.

## 6. Restricted and secret content

Restricted residuals must not move directly into controlled production.

Residuals containing secrets cannot enter reintegration planning. They require removal, rotation, redaction, or separate secure handling.

## 7. Physical recovery risks

Thermal recovery plans may affect pumps, valves, exchangers, buildings, or industrial systems.

Controlled production therefore requires human review and requested authorization.

## 8. Economic recovery risks

Economic residuals may represent unallocated value rather than free value.

A future royalty or settlement layer must verify beneficiaries, disputes, holds, and authorization before transfer.

## 9. Expiration

A plan becomes unsafe when target state, policy, or infrastructure has changed.

Every plan therefore expires. An expired plan must be reassessed rather than silently renewed.

## Runtime authorization drift

A valid authorization can still be misused if runtime operations, target, environment, node, geography, use count, or cycle depth expand beyond the plan. v0.4 compares all observed execution fields against both the plan and the authorization snapshot.

## Safe halt integrity

A receipt claiming `halted` must name a halt condition already declared by the plan. A receipt claiming `completed` must not contain a halt condition, a failed contamination scan, or unauthorized effects.
