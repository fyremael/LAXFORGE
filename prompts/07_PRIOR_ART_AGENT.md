# Codex Prompt 07 — Prior-Art and Collision Agent

Implement the prior-art collision registry and candidate classification scaffolding.

## Scope

Work in:

```text
src/laxforge/core/prior_art.py
src/laxforge/core/dossier.py
docs/PRIOR_ART_REGISTRY.md
tests/
```

## Required features

1. Create a structured registry of known family names, fingerprints, and collision notes.
2. Implement `CandidateClassification` enum:
   - FAKE
   - KNOWN
   - KNOWN_MECHANISM_NEW_PRESENTATION
   - KNOWN_HIERARCHY_NEW_REDUCTION
   - NEW_PAIR_FOR_KNOWN_PDE
   - NEW_SYSTEM_STRONG_LAX
   - NEW_HIERARCHY
   - NEEDS_HUMAN_REVIEW
3. Implement a conservative classifier that defaults to `NEEDS_HUMAN_REVIEW` or known-risk labels.
4. Add a collision checklist for nilpotent/jet/integrable-coupling constructions.

## Important rule

The code must not claim mathematical novelty automatically.

## Definition of done

The second-jet nilpotent mKdV example is classified conservatively as `KNOWN_MECHANISM_NEW_PRESENTATION` unless a human overrides it.

