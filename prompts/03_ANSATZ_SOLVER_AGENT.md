# Codex Prompt 03 — Ansatz and Solver Agent

Build the first structured ansatz generator and coefficient solver.

## Scope

Work in:

```text
src/laxforge/core/ansatz.py
src/laxforge/core/solver.py
tests/
```

## Required features

1. Define `WeightSpec` for symbolic weights.
2. Generate homogeneous monomials in fields and derivatives up to a prescribed order.
3. Generate polynomial-in-lambda matrix ansatzes.
4. Split zero-curvature equations into algebraic constraints on unknown coefficients.
5. Solve linear systems for unknown coefficients using SymPy.

## Initial target

Rediscover the scalar mKdV AKNS `V` from fixed `U` and a homogeneous ansatz.

## Non-goals

- Do not attempt broad nonlinear solving yet.
- Do not implement ML-guided search yet.

## Definition of done

Given the scalar mKdV `U`, the solver can recover a compatible `V` up to known normalizations and gauge choices.

