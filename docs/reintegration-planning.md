# Reintegration Planning

## 1. A plan is not reuse

A recoverable residual has passed classification, but it has not yet been connected to a target.

A reintegration plan answers:

1. Which residual is being proposed?
2. Which assessment approved planning?
3. Which exact target was approved?
4. Which operations are allowed?
5. Which operations are forbidden?
6. How many times may the residual be used?
7. How deep may the circulation continue?
8. Which safety conditions stop the process?
9. What authorization scope will be required?
10. How will recovered value be measured?

## 2. Target selection

A plan must not broaden the assessment decision.

If the assessment approved:

```yaml
target_type: retrieval_cache
target_id: cache:regional-route-features-01
reuse_mode: cache_seed

then the plan must use the same tuple.

Changing only the target ID is still a scope change.

3. Transformation

Transformations may include:

redaction,

compression,

summarization,

normalization,

aggregation,

format conversion.

A transformation policy should state which information may be changed and which semantics must remain invariant.

4. Use count and cycle depth

maximum_uses limits how many target operations may consume the residual.

maximum_cycle_depth limits how many regenerative generations may follow from the residual.

These controls are different.

maximum_uses       = horizontal reuse count
maximum_cycle_depth = vertical lineage depth

5. Controlled production

Plans targeting a live physical or production system require stronger controls.

The reference validator requires:

human review,

requested authorization,

rollback planning,

mandatory stop conditions.

6. Benefit measurement

Regeneration should produce evidence of value rather than merely moving waste elsewhere.

Possible benefits include:

reduced computation,

reduced latency,

improved safety,

improved reliability,

thermal recovery,

economic recovery,

knowledge preservation.

Each plan links to at least one measurement plan or metric.
