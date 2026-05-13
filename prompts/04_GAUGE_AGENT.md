# Codex Prompt 04 — Gauge Agent

Implement the first gauge transformation and reducibility tests.

## Scope

Work in:

```text
src/laxforge/core/gauge.py
src/laxforge/core/invariants.py
tests/
```

## Required features

1. Implement finite gauge transform:

```text
U -> G U G^{-1} + G_x G^{-1}
V -> G V G^{-1} + G_t G^{-1}
```

2. Implement block-reducibility detection for explicit matrix pairs.
3. Implement a basic spectral-parameter removal heuristic:
   - try gauges from a restricted ansatz,
   - detect whether lambda dependence can be eliminated.
4. Emit `GaugeReport`.

## Tests

- Gauge-transform a known pair and verify curvature transforms covariantly.
- Detect direct block sum reducibility.
- Flag fake lambda in a constructed trivial pair.

## Definition of done

The gauge layer must never certify novelty. It may only report risk, invariants, and unresolved status.

