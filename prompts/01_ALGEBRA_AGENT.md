# Codex Prompt 01 — Algebra Agent

Implement and harden coefficient algebra support for LAXFORGE.

## Scope

Work in:

```text
src/laxforge/algebra/
tests/
```

## Required features

1. Keep `TruncatedPoly` simple and auditable.
2. Support addition, subtraction, multiplication, powers, differentiation, simplification, expansion, and coefficient extraction.
3. Support matrix addition, subtraction, multiplication, commutator, and differentiation over truncated-polynomial entries.
4. Add tests for:
   - associativity of multiplication,
   - distributivity,
   - `eps^order = 0`,
   - derivative acts componentwise,
   - matrix commutator is zero for identical matrices.

## Constraints

- Do not introduce a heavy custom CAS.
- Use SymPy expressions as coefficients.
- Do not add noncommutative support yet. That is a future module.

## Definition of done

`pytest -q` passes, and `scripts/run_mkdv_validation.py` passes.

