# CODEX_MASTER_PROMPT.md — LAXFORGE Build Directive

You are implementing LAXFORGE, a gauge-aware discovery engine for zero-curvature representations and Lax pairs.

The project exists to discover and validate mathematically meaningful Lax pairs, not to produce unsupported novelty claims. Treat every candidate as non-novel until it passes a validation pipeline:

```text
zero curvature → coefficient proof → gauge reduction → cyclic-basis fingerprint → conservation/Hamiltonian evidence → prior-art collision report → human review
```

## Immediate command sequence

```bash
pip install -e '.[dev]'
pytest -q
python scripts/run_mkdv_validation.py
```

## First task

Make the existing calibration target robust. The nilpotent second-jet mKdV construction is intentionally a known-mechanism calibration target. Do not turn it into the flagship novelty claim.

## Build order

1. Harden coefficient algebra.
2. Harden zero-curvature reports.
3. Add structured candidate dossiers.
4. Implement ansatz generation and solving.
5. Implement gauge transforms and reducibility tests.
6. Implement cyclic-basis fingerprints.
7. Implement conservation-law and Hamiltonian checks.
8. Implement prior-art collision registry.
9. Run controlled discovery experiments in underexplored geometry-constrained and cohomological deformation spaces.

## Non-negotiable rules

- Never add a function that declares a candidate mathematically novel.
- Never hide unresolved symbolic residuals.
- Never omit gauge-risk status.
- Never present a block/Jordan/nilpotent lift as novel without collision warnings.
- Prefer complete dossiers over exciting fragments.

