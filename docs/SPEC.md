# SPEC.md — LAXFORGE: Gauge-Aware Discovery Engine for Lax Pairs

## 1. Mission

LAXFORGE is a methodical discovery system for zero-curvature representations, Lax pairs, and integrable hierarchies. Its purpose is to generate, validate, reduce, classify, and document candidate Lax pairs in a way that is mathematically auditable.

The system must never treat symbolic compatibility as sufficient novelty. It must distinguish:

- true Lax pairs from fake or gauge-trivial pairs,
- new presentations from new mathematics,
- known hierarchy members from genuinely new reductions or deformations,
- isolated compatibility identities from structure-rich integrable systems.

The central equation is

```text
U_t - V_x + [U,V] = 0.
```

The central standard is:

```text
generate → solve → reduce → falsify → extract structure → publish only what survives
```

## 2. Core deliverables

LAXFORGE must produce a candidate dossier for every generated pair:

1. Definition of fields, base variables, and coefficient algebra.
2. Connection pair `(U, V)`.
3. Generated PDE or target PDE.
4. Full zero-curvature expansion.
5. Coefficient-splitting proof.
6. Gauge/fake-pair assessment.
7. Cyclic-basis fingerprint where applicable.
8. Essential spectral-parameter test.
9. Conservation-law mining results.
10. Hamiltonian and bi-Hamiltonian attempts.
11. Known-hierarchy collision report.
12. Publishability classification.

## 3. Candidate classes

Every candidate receives one of the following classifications.

### Class 0: fake

Gauge-trivial, field-removable, or parameter-spurious.

### Class 1: known

Directly equivalent to a known Lax pair, hierarchy member, or standard reduction.

### Class 2: known mechanism, new presentation

Useful for pedagogy, implementation, or exposition but not a major mathematical contribution.

### Class 3: known hierarchy, new reduction or extension

Potentially publishable if the reduction or extension has nontrivial structure.

### Class 4: new Lax representation for a known PDE

Potentially publishable if gauge-inequivalence and essential parameter status are established.

### Class 5: new integrable PDE or system with strong Lax structure

A high-value discovery candidate.

### Class 6: new hierarchy or family with recursion, Hamiltonian, and spectral theory

The strongest target class.

## 4. Initial calibration target

The first implementation target is the second-jet nilpotent mKdV lift. This is deliberately not the flagship novelty claim. It is a calibration target for symbolic infrastructure.

Let

```text
Q = u + eps v + eps^2 w, eps^3 = 0.
```

Use the AKNS/mKdV pair

```text
U = [[lambda, Q], [-Q, -lambda]]
```

with

```text
A = -4 lambda^3 - 2 lambda Q^2
B = -4 lambda^2 Q - 2 lambda Q_x - Q_xx - 2 Q^3
C =  4 lambda^2 Q - 2 lambda Q_x + Q_xx + 2 Q^3
V = [[A, B], [C, -A]]
```

The zero-curvature condition must reduce to

```text
Q_t + Q_xxx + 6 Q^2 Q_x = 0.
```

Expanding in powers of eps gives:

```text
u_t + u_xxx + 6 u^2 u_x = 0
v_t + v_xxx + 6 u^2 v_x + 12 u u_x v = 0
w_t + w_xxx + 6 u^2 w_x + 12 u v v_x + 6 v^2 u_x + 12 u w u_x = 0
```

This example validates:

- truncated coefficient algebra,
- matrix arithmetic over symbolic algebras,
- curvature expansion,
- coefficient extraction,
- proof-report emission,
- baseline Hamiltonian-dossier scaffolding.

## 5. Architecture

### 5.1 `algebra`

Provides coefficient algebras:

- truncated polynomial algebras,
- matrix coefficient algebras,
- graded/super algebras,
- semidirect product algebras,
- loop-algebra helpers.

Current implementation includes `TruncatedPoly` and finite structure-constant
algebra support for the DIS-001 non-split product probe.

### 5.2 `core.zero_curvature`

Computes

```text
U_t - V_x + [U,V]
```

over supported coefficient algebras.

Must support:

- symbolic derivatives,
- matrix commutators,
- basis coefficient splitting,
- report generation.

### 5.3 `core.ansatz`

Creates structured symbolic ansatzes for `U`, `V`, and candidate PDEs.

Must support:

- polynomial spectral-parameter dependence,
- homogeneous weight assignments,
- derivative-order constraints,
- field-valued and algebra-valued coefficients.

### 5.4 `core.solver`

Solves the coefficient equations obtained by curvature splitting.

Must support:

- linear solve for ansatz coefficients,
- nonlinear symbolic constraints where tractable,
- fallback to Gröbner-style or SAT-style simplification in small examples,
- JSON-compatible result objects.

### 5.5 `core.gauge`

Implements gauge transformations:

```text
U ↦ G U G^{-1} + G_x G^{-1}
V ↦ G V G^{-1} + G_t G^{-1}
```

Must support:

- parameter-removal tests,
- block-reduction tests,
- algebra-preserving gauges,
- finite-dimensional matrix gauges.

### 5.6 `core.cyclic_basis`

Implements the cyclic-basis machinery for gauge-invariant fingerprints.

Must compute:

- characteristic element,
- covariant derivative operator,
- cyclic basis closure,
- closure coefficients,
- dimension and closure fingerprint.

### 5.7 `core.invariants`

Computes fingerprints for candidate comparison:

- cyclic-basis data,
- spectral parameter essentiality flags,
- trace invariants,
- block-decomposition signatures,
- grading signatures,
- generated PDE canonical form.

### 5.8 `core.conservation`

Mines conservation laws from:

- trace/monodromy expansions,
- Riccati expansions,
- inherited scalar hierarchy formulas,
- homotopy operator methods where implemented.

### 5.9 `core.hamiltonian`

Attempts to represent candidate PDEs as

```text
q_t = J δH/δq.
```

Must support:

- variational derivatives,
- skew-adjointness checks,
- constant-coefficient Poisson operators,
- Jacobi checks for simple operators,
- compatibility attempts for operator pairs.

### 5.10 `core.prior_art`

A structured registry, not an automated truth oracle.

Initial version should include manually curated fingerprints and notes for:

- AKNS,
- KdV,
- mKdV,
- NLS,
- sine-Gordon,
- Toda,
- KP/Gelfand-Dickey,
- Drinfel'd-Sokolov,
- vector/matrix mKdV,
- integrable couplings,
- nilpotent and perturbation extensions.

## 6. Search strategy

The first serious novelty search should avoid saturated scalar AKNS variants. Priority territories:

1. Non-semisimple, non-split, cohomologically nontrivial algebra deformations.
2. Nonlocal coverings and pseudopotential-dependent connections.
3. Geometry-constrained fields on spheres, Stiefel manifolds, coadjoint orbits, and density-operator spaces.
4. Operator-valued connections with noncommutative coefficients.
5. Cohomological deformations of known zero-curvature representations modulo gauge coboundaries.

## 7. Definition of done

A candidate reaches publication consideration only if it has:

- a validated zero-curvature proof,
- an essential spectral parameter or justified parameter-free formulation,
- evidence of nontrivial gauge class,
- at least three nontrivial conservation laws or a recursion/hierarchy mechanism,
- a known-hierarchy collision report,
- a clear mathematical interpretation,
- a concise falsifiability statement.
