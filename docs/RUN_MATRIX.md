# RUN_MATRIX.md — LAXFORGE Experiments and Validation Runs

## Calibration runs

| Run ID | Purpose | Expected class | Required pass condition |
|---|---|---:|---|
| CAL-001 | Scalar mKdV AKNS pair | Known | Curvature reduces to scalar mKdV |
| CAL-002 | Second-jet nilpotent mKdV | Known mechanism / new presentation | Curvature reduces to three-component jet system |
| CAL-003 | KdV scalar operator Lax pair | Known | Commutator form produces KdV |
| CAL-004 | NLS AKNS pair | Known | Curvature produces focusing/defocusing NLS with sign convention explicit |

## Gauge test runs

| Run ID | Purpose | Required pass condition |
|---|---|---|
| GAU-001 | Gauge-transform known pair | Invariant fingerprint unchanged |
| GAU-002 | Fake spectral parameter insertion | Parameter-removal test detects fake lambda |
| GAU-003 | Block-diagonal direct sum | Reducibility test detects decomposition |
| GAU-004 | Nilpotent Jordan lift | Reports repeated spectral curve and perturbation data |

## Discovery runs

| Run ID | Arena | Ansatz | Goal |
|---|---|---|---|
| DIS-001 | non-split semidirect algebra | polynomial λ, order ≤ 3 | find nontrivial deformation candidates |
| DIS-002 | sphere-valued field | tangent-projected order ≤ 3 flow | find norm-preserving zero-curvature systems |
| DIS-003 | density-matrix field | commutator + dissipative tangent terms | identify isospectral or constrained flows |
| DIS-004 | nonlocal covering | one pseudopotential variable | test for nonlocal Lax representations |
| DIS-005 | cohomological deformation | first-order deformation of known pair | classify nontrivial cocycles modulo gauge |

## Acceptance gates

A discovery run is successful only if at least one candidate has:

1. Valid zero curvature.
2. Nontrivial gauge fingerprint.
3. Essential spectral parameter.
4. At least preliminary conserved quantities.
5. Collision report showing no immediate known equivalence.

