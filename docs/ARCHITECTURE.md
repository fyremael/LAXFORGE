# ARCHITECTURE.md — LAXFORGE System Architecture

## 1. Design philosophy

LAXFORGE is not a single symbolic script. It is a pipeline with falsification gates. Each module should produce structured, serializable outputs that can be inspected by another module and by a human mathematician.

Every function should prefer explicit data structures over hidden global symbolic state.

## 2. Data model

Future agents should implement Pydantic models for:

```python
FieldSpec
DerivativeSpec
CoefficientAlgebraSpec
ConnectionSpec
CurvatureReport
GaugeReport
CyclicBasisReport
ConservationReport
HamiltonianReport
PriorArtCollisionReport
CandidateDossier
```

The initial scaffold uses direct symbolic functions, but the end-state should be model-driven.

## 3. Pipeline

```text
Input: arena + ansatz family + constraints
  ↓
Ansatz generation
  ↓
Curvature expansion
  ↓
Coefficient splitting
  ↓
Constraint solving
  ↓
Candidate PDE/pair extraction
  ↓
Gauge reduction
  ↓
Invariant fingerprinting
  ↓
Conservation-law mining
  ↓
Hamiltonian testing
  ↓
Prior-art collision report
  ↓
Candidate dossier
```

## 4. Output artifacts

Every run should produce:

```text
candidate.json
curvature_report.md
proof_sketch.md
gauge_report.md
invariants.json
conservation_report.md
hamiltonian_report.md
prior_art_report.md
publishability_classification.md
```

## 5. Reliability rules

1. Do not simplify away assumptions silently.
2. Always show coefficient-splitting basis.
3. Always record gauge choices.
4. Treat `lambda` as non-essential until tested.
5. Treat novelty as false until collision checks are done.
6. Prefer small auditable examples over huge opaque symbolic searches.

## 6. Implementation milestones

### M0: calibration

- Implement truncated algebra.
- Validate nilpotent mKdV second-jet example.
- Emit coefficient-level curvature reports.

### M1: ansatz solver

- Generate homogeneous polynomial ansatzes.
- Solve coefficient constraints for small scalar/vector systems.

### M2: gauge layer

- Implement finite gauge transformations.
- Implement simple parameter-removal tests.
- Implement block-reducibility checks.

### M3: cyclic basis

- Implement covariant derivative.
- Compute cyclic-basis closure.
- Emit gauge-invariant fingerprints.

### M4: conservation/Hamiltonian layer

- Mine simple conservation laws.
- Implement variational derivative helper.
- Validate constant Poisson operators.

### M5: first novelty search

- Search non-split semidirect deformations.
- Search constrained sphere-valued flows.
- Produce candidate dossiers, not claims.

