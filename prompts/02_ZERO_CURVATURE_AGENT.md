# Codex Prompt 02 — Zero Curvature Agent

Implement the zero-curvature computation and reporting layer.

## Scope

Work in:

```text
src/laxforge/core/zero_curvature.py
src/laxforge/core/reports.py
tests/
```

## Required features

1. Compute `U_t - V_x + [U,V]` over supported coefficient algebras.
2. Split every matrix entry by coefficient-algebra basis.
3. Emit a structured `CurvatureReport` with:
   - matrix shape,
   - coefficient basis,
   - raw coefficients,
   - simplified coefficients,
   - zero/nonzero flags,
   - unresolved terms.
4. Add Markdown report generation.

## Tests

- Scalar mKdV calibration if available.
- Second-jet nilpotent mKdV example.
- Zero curvature of a pure gauge pair should vanish.

## Definition of done

The curvature report should make it possible to reproduce the algebraic proof line by line.

