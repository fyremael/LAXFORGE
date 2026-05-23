# LAXFORGE Codex Pack

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Python >=3.10](https://img.shields.io/badge/python-%3E%3D3.10-blue)
![Version 0.1.0](https://img.shields.io/badge/version-0.1.0-informational)

**LAXFORGE** is a gauge-aware discovery engine for zero-curvature representations and Lax pairs. Its purpose is not to generate decorative symbolic coincidences, but to produce candidates that survive algebraic validation, gauge/fake-pair reduction, invariant comparison, hierarchy extraction, and prior-art collision checks.

This repository scaffold is designed for incremental implementation by Codex-style coding agents. It includes:

- A formal implementation specification.
- Module boundaries and function contracts.
- Agent prompts for staged implementation.
- A first calibration example: the second-jet nilpotent mKdV lift.
- A minimal symbolic validation script and pytest target.

The philosophical rule is simple:

> A pair is not new because we have not seen it before. It is new only after it survives zero-curvature validation, gauge reduction, invariant comparison, and serious prior-art collision.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest -q
python scripts/run_mkdv_validation.py
```

To emit a LAXCERT-ingestable calibration artifact:

```bash
python scripts/export_laxcert_calibration.py runs/laxcert_calibration --overwrite
```

The output directory contains `laxforge_manifest.json`, `candidate.json`, and
`source_report.json`. The default candidate is the LAXCERT section-10
`LaxforgeAKNSD2TransportZero` calibration with second-order diagonal operators
and paired-field off-diagonal entries. LAXCERT can certify that directory
directly.

## First milestone

The first milestone is **not** to claim novelty. It is to calibrate the symbolic engine on a known-valid construction:

\[
Q = u + \epsilon v + \epsilon^2 w, \qquad \epsilon^3=0,
\]

with the AKNS/mKdV pair lifted into the truncated algebra \(\mathbb{R}[\epsilon]/(\epsilon^3)\). This validates the algebra, curvature expansion, coefficient extraction, and proof-emission pipeline.

## Repository layout

```text
src/laxforge/
  algebra/              # coefficient algebras, truncated and finite-table arithmetic
  core/                 # curvature, ansatz, gauge, cyclic basis, invariants
  examples/             # verified examples and calibration targets
tests/                  # pytest suite
scripts/                # runnable demos and validation reports
docs/                   # formal specs, architecture, metrics, run matrix
prompts/                # Codex agent prompts by module
```

## Grand Challenge posture

LAXFORGE should act like a mathematical clean room. Every candidate receives a structured dossier:

1. Candidate pair \((U,V)\).
2. Generated PDE or target PDE.
3. Zero-curvature proof.
4. Gauge/fake-pair tests.
5. Cyclic-basis fingerprint.
6. Essential spectral-parameter test.
7. Conservation-law extraction.
8. Hamiltonian/bi-Hamiltonian attempts.
9. Known-hierarchy collision search.
10. Publishability classification.
