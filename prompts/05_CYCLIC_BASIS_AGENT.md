# Codex Prompt 05 — Cyclic Basis Agent

Implement cyclic-basis fingerprints for zero-curvature representations.

## Scope

Work in:

```text
src/laxforge/core/cyclic_basis.py
src/laxforge/core/invariants.py
tests/
```

## Mathematical task

For a scalar evolution equation with a matrix `X` in the spatial spectral problem, compute the characteristic matrix `C`, the covariant derivative

```text
nabla_x(Y) = D_x(Y) - [X, Y]
```

and the cyclic basis

```text
C, nabla_x C, nabla_x^2 C, ...
```

until closure.

## Required output

`CyclicBasisReport` with:

- basis dimension,
- closure relation,
- closure coefficients,
- lambda dependence of closure coefficients,
- simplified fingerprint string.

## Tests

- Known scalar examples with stable fingerprints.
- Gauge-related examples should produce matching or transform-consistent fingerprints.

## Definition of done

The report should help distinguish true parameter-dependent pairs from fake or gauge-trivial pairs in small examples.

