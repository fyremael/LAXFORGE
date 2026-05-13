# Codex Prompt 08 — Discovery Agent

Implement the first controlled discovery runs.

## Scope

Work in:

```text
src/laxforge/search/
scripts/
experiments/
```

## Initial discovery territories

1. Non-split semidirect algebra deformations.
2. Sphere-valued tangent-projected flows.
3. First-order cohomological deformations of known pairs.

## Requirements

1. Use small ansatz spaces first.
2. Emit complete dossiers for every candidate.
3. Never suppress failed candidates; record why they failed.
4. Rank candidates by validation status, not by excitement.

## First concrete target

Search for a low-order zero-curvature representation for a norm-preserving field `s(x,t)` with `s·s=1`, using tangent-projected flow ansatzes.

## Definition of done

At least one discovery run produces:

- a candidate dossier,
- a curvature report,
- a gauge-risk report,
- a collision report,
- and a recommendation: discard / investigate / prepare note.

