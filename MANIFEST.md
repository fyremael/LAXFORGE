# MANIFEST.md

## Top-level files

- `README.md` — project overview and quick start.
- `CODEX_MASTER_PROMPT.md` — master implementation directive.
- `AGENTS.md` — multi-agent role map.
- `VALIDATION_LOG.md` — local validation results.
- `pyproject.toml` — package metadata and test configuration.

## Documentation

- `docs/SPEC.md` — formal implementation specification.
- `docs/ARCHITECTURE.md` — system architecture and milestones.
- `docs/RUN_MATRIX.md` — calibration, gauge, and discovery runs.
- `docs/METRICS.md` — candidate validation metrics.
- `docs/PRIOR_ART_REGISTRY.md` — initial known-family collision checklist.
- `docs/PROCEDURES.md` — formal discovery and procedure-audit checklist.

## Static UI

- `web/index.html` — static evidence console entrypoint.
- `web/app.js` — evidence console renderer.
- `web/styles.css` — evidence console styling.
- `web/dashboard_data.js` — explicitly generated dashboard payload.
- `web/research_report.html` — visually rich research progress report.
- `web/research_report.js` — research report renderer.
- `web/research_report.css` — research report styling.

## Prompts

- `prompts/00_ORCHESTRATOR.md`
- `prompts/01_ALGEBRA_AGENT.md`
- `prompts/02_ZERO_CURVATURE_AGENT.md`
- `prompts/03_ANSATZ_SOLVER_AGENT.md`
- `prompts/04_GAUGE_AGENT.md`
- `prompts/05_CYCLIC_BASIS_AGENT.md`
- `prompts/06_CONSERVATION_HAMILTONIAN_AGENT.md`
- `prompts/07_PRIOR_ART_AGENT.md`
- `prompts/08_DISCOVERY_AGENT.md`

## Source scaffold

- `src/laxforge/algebra/truncated_poly.py`
- `src/laxforge/core/zero_curvature.py`
- `src/laxforge/core/procedures.py`
- `src/laxforge/search/bulk.py`
- `src/laxforge/search/serious_cycle.py`
- `src/laxforge/examples/mkdv_second_jet.py`

## Tests and scripts

- `tests/test_mkdv_second_jet.py`
- `tests/test_bulk_search.py`
- `tests/test_procedures.py`
- `tests/test_research_report_ui.py`
- `scripts/run_mkdv_validation.py`
- `scripts/run_procedure_audit.py`
- `scripts/run_scaled_candidate_search.py`
- `scripts/run_serious_cycle_001.py`
