# VALIDATION_LOG.md

Local scaffold validation completed and M0 algebra/report hardening verified.
Zero-curvature M0 completion added pure-gauge flatness coverage and explicit proof-artifact emission.
Curvature proof artifacts now include a visual residual summary grid for fast audit triage.
Prompt-pack scaffolding now covers ansatz solving, gauge-risk reports, cyclic-basis
fingerprints, conservation/Hamiltonian checks, prior-art dossiers, and a controlled
discard-path discovery run.
DIS-002 now runs a fixed low-order sphere-valued search with zero-control discard,
three tangent cross-product candidates, conservative gate summaries, and optional
explicit JSON/Markdown artifact writing.
The `s × s_xx` DIS-002 candidate now has a real `so(3)` Heisenberg-shaped ZCR
ansatz solve with `{alpha: -1, beta: 1}`, zero residual modulo explicit unit-sphere
constraints, gauge/cyclic evidence, known-family collision classification, and a
discard recommendation for discovery purposes.
A static evidence dashboard now tracks M0 proof-artifact readiness, the calibration
dossier, and DIS-002 candidates. It includes tabbed overview/candidate/gate/artifact/
collision views, metric cards, gate heatmaps, residual grids, collision-family maps,
and audit-surprisal scores. Dashboard data is generated only through the explicit
`scripts/build_dashboard_data.py` writer.
The overview now includes a generated plain-language summary for lay viewers, with
current counts, passed evidence, open review items, discard-path items, and a
conservative bottom line.
DIS-001 has begun as a controlled semidirect deformation lane with four deterministic
records: a zero-connection control, a known split nilpotent mKdV semidirect control,
a removable rescaling control, and a non-split product probe queued for review until
the coefficient algebra can construct that product honestly. No automatic discovery
conclusions are emitted.
ITER-001 now turns the lane snapshots into an iterative discovery frontier. It keeps
discarded controls and known-family collisions out of the active queue, tracks three
frontier records with explicit next actions, and exposes process status in the static
dashboard Frontier tab.
PROC-001 now formalizes the discovery procedure as ten ordered steps and audits the
current frontier with eight checks: clean frontier/discard partition, discard
discipline, conservative frontier status, next-action evidence, status consistency,
base evidence fields, and language guard. The static dashboard now includes a
Procedures tab and schema version 3 payload with procedure-audit metrics.
SERIOUS-001 froze the pre-attempt ITER/PROC state, attempted a low-order real
`so(3)` ansatz for the DIS-002 `s × s_xxx` sphere candidate, and recorded a
current-family obstruction rather than a global falsification. The candidate is now
classified as `blocked` with `ansatz_obstruction_current_family`; ITER-001 advances
`s × s_x` as the next queued sphere candidate while retaining the obstruction
evidence. The dashboard payload is now schema version 4 with SERIOUS-001 metrics.

```text
$ python -m ruff check .
All checks passed!
```

```text
$ python -m pytest -q
........................................................................ [ 75%]
.......................                                                  [100%]
95 passed in 96.70s
```

```text
$ python scripts/run_mkdv_validation.py
LAXFORGE calibration: second-jet nilpotent mKdV
Checks:
{'diag_00_zero': True,
 'diag_11_zero': True,
 'lower_left_negative_expected': True,
 'upper_right_expected': True}

All symbolic checks passed.
```

```text
$ python scripts/run_prompt_pack_validation.py
LAXFORGE prompt-pack validation
Scalar mKdV V recovery: solved
Second-jet mKdV dossier: known_mechanism_new_presentation, 9 conservation laws, Hamiltonian verified
Controlled discovery run: DIS-002, 4 fixed candidates, 2 discard, 1 review, 1 blocked
Iterative discovery frontier: ITER-001, frontier_active, 3 queued records
Procedure audit: PROC-001, pass, 8 checks, 0 failures, 0 warnings
Serious cycle: SERIOUS-001, blocked, target sphere-s-cross-s-xxx-exploratory-candidate
```

```text
$ python scripts/run_discovery_search.py
LAXFORGE controlled discovery search
No automatic discovery conclusions are emitted.
DIS-001: small semidirect deformation search around mKdV AKNS
  - semidirect zero-connection control: fake, discard, validated_zero_control
  - semidirect split nilpotent mKdV lift control: known_mechanism_new_presentation, discard, validated_known_semidirect_zcr
  - semidirect rescaled perturbation parameter control: fake, discard, field_rescaling_control
  - semidirect non-split product deformation probe: needs_human_review, needs_human_review, not_constructed
DIS-002: sphere-valued tangent-projected low-order flow search
  - sphere zero-flow zero-connection control: fake, discard, validated_zero_control
  - sphere s_cross_s_x tangent candidate: needs_human_review, needs_human_review, no_validated_zcr
  - sphere s_cross_s_xx Heisenberg-shaped candidate: known, discard, validated_known_zcr
  - sphere s_cross_s_xxx exploratory candidate: needs_human_review, blocked, ansatz_obstruction_current_family
ITER-001: iterative discovery frontier
  - process status: frontier_active
  - active frontier: 3
    * sphere s_cross_s_x tangent candidate: promising_potential, priority 58, next=Run a minimal so(3) ansatz falsification pass with spectral and gauge checks.
    * semidirect non-split product deformation probe: blocked_by_missing_capability, priority 54, next=Implement non-split coefficient multiplication, then construct zero-curvature equations.
    * sphere s_cross_s_xxx exploratory candidate: blocked_by_ansatz_obstruction, priority 36, next=Current low-order so(3) ansatz family is obstructed; expand the ansatz family after the next queued candidate.
  - stop reason: active frontier awaits next ansatz, gauge, cyclic, conservation, or algebra gate
```

```text
$ python scripts/run_procedure_audit.py
LAXFORGE procedure audit
Procedure: PROC-001 v1
Status: pass
Summary: 3 frontier records, 5 discard records, 0 failures, 0 warnings
  - A0 pass: ten ordered procedure steps are defined
  - A1 pass: all records partition into frontier or discard
  - A2 pass: discard records carry discard disposition and recommendation
  - A3 pass: frontier records remain review or blocked work
  - A4 pass: frontier records include next actions, gate gaps, and evidence summaries
  - A5 pass: process status matches the current frontier state
  - A6 pass: all records include name, lane, classification, and connection status
  - A7 pass: promotion-language guard passed
```

```text
$ python scripts/run_serious_cycle_001.py
LAXFORGE serious cycle
Cycle: SERIOUS-001
Target: sphere s_cross_s_xxx exploratory candidate
Result: blocked
Baseline status: promising_potential
Refreshed status: blocked_by_ansatz_obstruction
Procedure audit: pass
Obstruction evidence:
  - lambda residual remains s cross s_xxx - b*s_xxx after high-order consistency
  - generic sphere data does not make s cross s_xxx a scalar multiple of s_xxx
  - current low-order so(3) ansatz family is obstructed
Next action: Advance to the next queued frontier candidate while retaining the s_cross_s_xxx obstruction for a broader ansatz-family expansion.
```

```text
$ node --check web/app.js
```

```text
$ browser smoke check for file:///F:/_codex/LAXFORGE/web/index.html
browser smoke passed for desktop and mobile
```

```text
$ plain summary browser smoke for file:///F:/_codex/LAXFORGE/web/index.html
plain summary browser smoke passed for desktop and mobile
```

```text
$ DIS-001 dashboard browser smoke for file:///F:/_codex/LAXFORGE/web/index.html
DIS-001 dashboard browser smoke passed for desktop and mobile
```

```text
$ iterative frontier browser smoke for file:///F:/_codex/LAXFORGE/web/index.html
iterative frontier browser smoke passed for desktop and mobile
```

```text
$ procedure dashboard browser smoke for file:///F:/_codex/LAXFORGE/web/index.html
procedure dashboard browser smoke passed for desktop and mobile
```

```text
$ serious cycle dashboard browser smoke for file:///F:/_codex/LAXFORGE/web/index.html
serious cycle dashboard browser smoke passed for desktop and mobile
```

```text
$ python scripts/build_dashboard_data.py
Wrote dashboard data: F:\_codex\LAXFORGE\web\dashboard_data.js
```

## Research Progress Report Refresh

Added a static, file-openable visual report at `web/research_report.html`, backed by the same explicit
`web/dashboard_data.js` payload used by the evidence console. The report summarizes M0 proof-artifact
readiness, prompt-pack calibration, DIS-001/DIS-002 candidates, ITER-001 frontier state, PROC-001 audit
state, SERIOUS-001 obstruction evidence, gate heatmaps, collision-family mapping, residual grids, and the
technical ledger.

```text
$ python -m ruff check .
All checks passed!
```

```text
$ python -m pytest -q
........................................................................ [ 74%]
.........................                                                [100%]
97 passed in 109.93s (0:01:49)
```

```text
$ python scripts/run_mkdv_validation.py
LAXFORGE calibration: second-jet nilpotent mKdV
All symbolic checks passed.
```

```text
$ python scripts/run_prompt_pack_validation.py
LAXFORGE prompt-pack validation
Scalar mKdV V recovery: solved
Second-jet mKdV dossier: known_mechanism_new_presentation, 9 conservation laws, Hamiltonian verified
Controlled discovery run: DIS-002, 4 fixed candidates, 2 discard, 1 review, 1 blocked
Iterative discovery frontier: ITER-001, frontier_active, 3 queued records
Procedure audit: PROC-001, pass, 8 checks, 0 failures, 0 warnings
Serious cycle: SERIOUS-001, blocked, target sphere-s-cross-s-xxx-exploratory-candidate
```

```text
$ python scripts/run_discovery_search.py
LAXFORGE controlled discovery search
DIS-001: 4 candidates
DIS-002: 4 candidates
ITER-001: frontier_active, 3 active frontier records
```

```text
$ python scripts/run_procedure_audit.py
LAXFORGE procedure audit
Procedure: PROC-001 v1
Status: pass
Summary: 3 frontier records, 5 discard records, 0 failures, 0 warnings
```

```text
$ python scripts/run_serious_cycle_001.py
LAXFORGE serious cycle
Cycle: SERIOUS-001
Target: sphere s_cross_s_xxx exploratory candidate
Result: blocked
Baseline status: promising_potential
Refreshed status: blocked_by_ansatz_obstruction
Procedure audit: pass
```

```text
$ node --check web/app.js
$ node --check web/research_report.js
```

```text
$ python scripts/build_dashboard_data.py
Wrote dashboard data: F:\_codex\LAXFORGE\web\dashboard_data.js
```

```text
$ in-app browser automation for file:///F:/_codex/LAXFORGE/web/research_report.html
Blocked by Browser Use URL policy for file:// navigation; no alternate browser-surface smoke was attempted.
Static DOM/CSS/JS tests and syntax checks passed.
```

## Research Report Narrative Revision

Client-facing report presentation was revised from a dashboard-like point summary into a fuller research
readout. The report now includes an executive narrative, research-question framing, method explanation,
lane-by-lane evidence dossiers, and the existing supporting visual/audit sections. The static assets still
avoid promotion conclusions and remain backed by the explicit dashboard payload.

```text
$ python -m ruff check .
All checks passed!
```

```text
$ python -m pytest -q
........................................................................ [ 74%]
.........................                                                [100%]
97 passed in 103.87s (0:01:43)
```

```text
$ python -m pytest tests\test_research_report_ui.py -q
..                                                                       [100%]
2 passed in 5.45s
```

```text
$ node --check web\app.js
$ node --check web\research_report.js
```

```text
$ python scripts\run_prompt_pack_validation.py
LAXFORGE prompt-pack validation
Scalar mKdV V recovery: solved
Second-jet mKdV dossier: known_mechanism_new_presentation, 9 conservation laws, Hamiltonian verified
Controlled discovery run: DIS-002, 4 fixed candidates, 2 discard, 1 review, 1 blocked
Iterative discovery frontier: ITER-001, frontier_active, 3 queued records
Procedure audit: PROC-001, pass, 8 checks, 0 failures, 0 warnings
Serious cycle: SERIOUS-001, blocked, target sphere-s-cross-s-xxx-exploratory-candidate
```

```text
$ python scripts\run_serious_cycle_001.py
LAXFORGE serious cycle
Cycle: SERIOUS-001
Target: sphere s_cross_s_xxx exploratory candidate
Result: blocked
Baseline status: promising_potential
Refreshed status: blocked_by_ansatz_obstruction
Procedure audit: pass
```

```text
$ python scripts\build_dashboard_data.py
Wrote dashboard data: F:\_codex\LAXFORGE\web\dashboard_data.js
```

## Localhost Browser Smoke Repair

Served the static `web/` directory over localhost so Browser Use can inspect the report without the
blocked `file://` URL policy. The report is available at
`http://127.0.0.1:8765/research_report.html?v=2#report-readout` while the local Python static server is
running.

During live browser inspection, the report shell loaded but dynamic sections did not render. Browser console
evidence identified an SVG title-node assignment error in `web/research_report.js`; the report script was
patched and cache-busted from `web/research_report.html`.

```text
$ Invoke-WebRequest http://127.0.0.1:8765/research_report.html
StatusCode: 200
```

```text
$ browser smoke for http://127.0.0.1:8765/research_report.html?v=2#report-readout
desktop: h1 visible, readout visible, 6 dossier cards, 8 metric tiles, 60 gate cells
mobile: h1 visible, readout visible, 6 dossier cards, 8 metric tiles, 60 gate cells
```

```text
$ node --check web\research_report.js
```

```text
$ python -m pytest tests\test_research_report_ui.py -q
..                                                                       [100%]
2 passed in 5.35s
```

```text
$ python -m ruff check .
All checks passed!
```

```text
$ python -m pytest -q
........................................................................ [ 74%]
.........................                                                [100%]
97 passed in 102.26s (0:01:42)
```

## DIS-003 Scaled Candidate Phase

Added a deterministic scaled triage phase with 128 sphere-tangent candidates. The batch is intentionally
conservative: one zero-control candidate is classified fake/discard, and 127 generated candidates remain
`needs_human_review` with ZCR, spectral, gauge, cyclic, conservation, Hamiltonian, and collision gates open.
No generated candidate is promoted by the automated phase.

```text
$ python scripts\run_scaled_candidate_search.py
LAXFORGE DIS-003 scaled candidate triage
Run: DIS-003
Arena: scaled deterministic sphere-tangent triage search
Candidates: 128
Recommendations: {'discard': 1, 'needs_human_review': 127}
Families: {'control': 1, 'single_factor_cross': 60, 'two_atom_blend': 67}
```

```text
$ python scripts\run_discovery_search.py
LAXFORGE controlled discovery search
DIS-001: 4 candidates
DIS-002: 4 candidates
DIS-003: 128 candidates, 116 summarized after the first 12 displayed
ITER-001: frontier_active, 130 active frontier records
```

```text
$ python scripts\run_prompt_pack_validation.py
LAXFORGE prompt-pack validation
Scalar mKdV V recovery: solved
Second-jet mKdV dossier: known_mechanism_new_presentation, 9 conservation laws, Hamiltonian verified
Controlled discovery run: DIS-002, 4 fixed candidates, 2 discard, 1 review, 1 blocked
Scaled discovery phase: DIS-003, 128 candidates, 1 discard, 127 review
Iterative discovery frontier: ITER-001, frontier_active, 130 queued records
Procedure audit: PROC-001, pass, 8 checks, 0 failures, 0 warnings
Serious cycle: SERIOUS-001, blocked, target sphere-s-cross-s-xxx-exploratory-candidate
```

```text
$ python scripts\run_procedure_audit.py
LAXFORGE procedure audit
Procedure: PROC-001 v1
Status: pass
Summary: 130 frontier records, 6 discard records, 0 failures, 0 warnings
```

```text
$ python -m ruff check .
All checks passed!
```

```text
$ python -m pytest -q
........................................................................ [ 68%]
.................................                                        [100%]
105 passed in 102.68s (0:01:42)
```

```text
$ node --check web\app.js
$ node --check web\research_report.js
```

```text
$ python scripts\build_dashboard_data.py
Wrote dashboard data: F:\_codex\LAXFORGE\web\dashboard_data.js
```

```text
$ browser smoke for http://127.0.0.1:8765/research_report.html?v=3#report-readout
desktop: 8 metric tiles, 7 dossier cards, 828 gate cells, 138 ledger rows, readout visible
mobile: readout visible, 7 dossier cards, 138 ledger rows
```

```text
$ browser smoke for http://127.0.0.1:8765/index.html?v=3
dashboard: 13 metric cards, 7 run pills, 138 candidate cards, 1656 gate cells
```
