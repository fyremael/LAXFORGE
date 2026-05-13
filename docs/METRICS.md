# METRICS.md — LAXFORGE Candidate Metrics

## Algebraic correctness metrics

- `curvature_residual_zero`: Boolean after coefficient splitting and simplification.
- `curvature_terms_total`: Number of coefficient equations before simplification.
- `curvature_terms_nonzero`: Number of unresolved residual terms.
- `basis_split_complete`: Boolean confirming all algebra/Lie/λ/derivative bases were split.

## Gauge and novelty-risk metrics

- `lambda_essential`: true / false / unknown.
- `cyclic_basis_dimension`: integer or null.
- `cyclic_closure_order`: integer or null.
- `block_reducible`: true / false / unknown.
- `known_projection_detected`: true / false.
- `spectral_curve_repeated`: true / false / unknown.
- `gauge_risk_score`: 0 to 1, where 1 means high risk of known or fake equivalence.

## Integrability evidence metrics

- `num_conservation_laws_found`: integer.
- `recursion_operator_found`: true / false / unknown.
- `hamiltonian_form_found`: true / false / unknown.
- `second_hamiltonian_found`: true / false / unknown.
- `commuting_flows_found`: integer.

## Publishability score

LAXFORGE should not compute a magical novelty score. It may compute a triage score:

```text
publishability_score =
  correctness_gate
  × gauge_gate
  × structure_gate
  × collision_gate
```

Where each gate is documented separately. A low score means “do not claim novelty.” A high score means “prepare for human expert review,” not “publish automatically.”

