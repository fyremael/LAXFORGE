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

## FULL-001 Full-Scale Search Cycle

Added a conservative full-scale orchestration layer over the current discovery lanes. The run evaluates
136 discovery candidates across DIS-001, DIS-002, and DIS-003, keeps 130 candidates in the active
frontier, and records a 25-item solver action queue. The result is a process state, not a stronger
interpretation: every candidate remains discard, needs-human-review, or blocked according to the
documented gates.

```text
$ python scripts\run_full_scale_search.py
LAXFORGE full-scale search
Run: FULL-001
Status: frontier_active
Generated candidates: 136
Frontier: 130
Discarded: 6
Lane counts: {'DIS-001': 4, 'DIS-002': 4, 'DIS-003': 128}
Recommendations: {'blocked': 1, 'discard': 6, 'needs_human_review': 129}
Action queue: 25 records retained for candidate-specific solver work
```

```text
$ python scripts\run_prompt_pack_validation.py
LAXFORGE prompt-pack validation
Scaled discovery phase: DIS-003, 128 candidates, 1 discard, 127 review
Iterative discovery frontier: ITER-001, frontier_active, 130 queued records
Procedure audit: PROC-001, pass, 8 checks, 0 failures, 0 warnings
Serious cycle: SERIOUS-001, blocked, target sphere-s-cross-s-xxx-exploratory-candidate
Full-scale search: FULL-001, frontier_active, 136 generated candidates, 130 frontier records, 25 action-queue records
```

```text
$ python scripts\run_procedure_audit.py
LAXFORGE procedure audit
Procedure: PROC-001 v1
Status: pass
Summary: 130 frontier records, 6 discard records, 0 failures, 0 warnings
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
$ python -m ruff check .
All checks passed!
```

```text
$ python -m pytest -q
........................................................................ [ 64%]
.......................................                                  [100%]
111 passed in 127.47s (0:02:07)
```

```text
$ python scripts\run_mkdv_validation.py
All symbolic checks passed.
```

```text
$ python scripts\run_discovery_search.py
DIS-001: 4 candidates
DIS-002: 4 candidates
DIS-003: 128 candidates, 116 summarized after the first 12 displayed
ITER-001: frontier_active, 130 active frontier records
```

```text
$ python scripts\run_scaled_candidate_search.py
LAXFORGE DIS-003 scaled candidate triage
Run: DIS-003
Candidates: 128
Recommendations: {'discard': 1, 'needs_human_review': 127}
Families: {'control': 1, 'single_factor_cross': 60, 'two_atom_blend': 67}
```

```text
$ python scripts\build_dashboard_data.py
Wrote dashboard data: F:\_codex\LAXFORGE\web\dashboard_data.js
```

```text
$ node --check web\app.js
$ node --check web\research_report.js
```

```text
$ browser smoke for http://127.0.0.1:8765/research_report.html?v=4#report-readout
desktop: 8 metric tiles, 8 dossier cards, 828 gate cells, 138 ledger rows, readout visible
mobile: readout visible, 8 dossier cards, 138 ledger rows, text wraps without obvious overlap
```

```text
$ browser smoke for http://127.0.0.1:8765/index.html?v=4
dashboard: 14 metric cards, 8 run pills, 138 candidate cards, 5 board columns, 1656 gate cells
mobile: filters stack, run pills wrap, candidate board remains scrollable
```

## OVERNIGHT-001 Wide Candidate Evidence Run

Added and executed a wide deterministic overnight-style search over sphere-tangent descriptors. The
run generated 1024 candidate records, all conservative: 1023 remain `needs_human_review`, and the
single zero-flow control is `discard`. The batch is intentionally broad but shallow. It verifies
tangent construction for the generated descriptors, records prior-family collision pressure, and leaves
matrix-pair, spectral, gauge, cyclic, conservation, and Hamiltonian gates open until candidate-specific
solver passes are run.

```text
$ python scripts\run_overnight_search.py
LAXFORGE overnight candidate search
Run: OVERNIGHT-001
Status: frontier_active
Candidates: 1024
Action queue: 80
Families: {'control': 1, 'cross_atom_blend': 386, 'scalar_weighted_cross': 385, 'two_atom_blend': 252}
Orders: {'0': 1, '2': 4, '3': 14, '4': 30, '5': 78, '6': 268, '7': 629}
Recommendations: {'discard': 1, 'needs_human_review': 1023}
```

```text
$ python scripts\build_overnight_report_data.py
Wrote overnight report data: F:\_codex\LAXFORGE\web\overnight_data.js
```

```text
$ python scripts\run_prompt_pack_validation.py
Overnight search:
{'action_queue': 80,
 'candidate_count': 1024,
 'recommendations': {'discard': 1, 'needs_human_review': 1023},
 'run_id': 'OVERNIGHT-001',
 'status': 'frontier_active'}
```

```text
$ python -m ruff check .
All checks passed!
```

```text
$ python -m pytest -q
........................................................................ [ 60%]
................................................                         [100%]
120 passed in 129.61s (0:02:09)
```

```text
$ python scripts\run_mkdv_validation.py
All symbolic checks passed.
```

```text
$ python scripts\run_discovery_search.py
DIS-001: 4 candidates
DIS-002: 4 candidates
DIS-003: 128 candidates, 116 summarized after the first 12 displayed
ITER-001: frontier_active, 130 active frontier records
```

```text
$ python scripts\run_procedure_audit.py
LAXFORGE procedure audit
Procedure: PROC-001 v1
Status: pass
Summary: 130 frontier records, 6 discard records, 0 failures, 0 warnings
```

```text
$ python scripts\run_serious_cycle_001.py
LAXFORGE serious cycle
Cycle: SERIOUS-001
Target: sphere s_cross_s_xxx exploratory candidate
Result: blocked
Procedure audit: pass
```

```text
$ python scripts\run_full_scale_search.py
LAXFORGE full-scale search
Run: FULL-001
Status: frontier_active
Generated candidates: 136
Frontier: 130
Discarded: 6
```

```text
$ python scripts\build_dashboard_data.py
Wrote dashboard data: F:\_codex\LAXFORGE\web\dashboard_data.js
```

```text
$ node --check web\app.js
$ node --check web\research_report.js
$ node --check web\overnight_report.js
```

```text
$ browser smoke for http://127.0.0.1:8765/overnight_report.html?v=3
desktop: 12 metric cards, 4 family bars, 7 order bars, 7 gate tiles, 24 queue cards, 180 table rows
mobile: readout wraps cleanly, 12 metric cards, 24 queue cards, 180 table rows
```

## SOLVER-CAMPAIGN-001 24-Hour Campaign Launch

Added a checkpointed solver campaign runner for the current supported sphere ZCR machinery. The
campaign repeatedly expands the overnight action queue by derivative order, records every attempted
candidate gate, and stops only on wall-clock expiry or an automated survivor requiring human prior-art
review. The stop condition is not an automated novelty claim.

Initial smoke evidence before launch:

```text
$ python scripts\run_solver_campaign.py --hours 0.01 --target-count 600 --max-derivative-order 5 --action-queue-limit 30
LAXFORGE solver campaign
Run: SOLVER-CAMPAIGN-001
Status: candidate_queue_exhausted_without_survivor
Attempts: 33 / 33
Automated survivor: none
```

The smoke campaign rediscovered the known Heisenberg case as `validated_known_collision`, kept
`unit times sxxx` as `blocked_current_ansatz_family`, and marked `unit times sx` as
`blocked_first_potential_gate`.

24-hour campaign launched explicitly:

```text
Process ID: 9380
Output directory: F:\_codex\LAXFORGE\runs\solver_campaign_24h_20260517_034143
Started: 2026-05-17T03:41:43.4898003-07:00
```

Early checkpoint:

```text
attempt_count: 8600
candidate_count: 8623
rounds_completed: 16
status: running
survivor: null
updated_at: 2026-05-17T03:42:04.888001-07:00
```

Validation after adding the campaign runner:

```text
$ python -m ruff check .
All checks passed!
```

```text
$ python -m pytest -q
........................................................................ [ 58%]
...................................................                      [100%]
123 passed in 136.45s (0:02:16)
```

## Expanded Formal Ansatz Solver Remediation

The first 24-hour campaign exposed a real solver limitation: high-order sphere candidates were being
queued because the implemented solver only covered the hand-built low-order `U = lambda*hat(s)` cases.
Remediation added a formal local-vector ansatz layer for sphere-valued flows. The new layer represents
sphere derivative atoms, scalar invariants `<s_i,s_j>`, cross atoms, unit-sphere reductions for
`<s,s_k>`, and coefficient splitting for polynomial-in-lambda local-vector ansatzes.

New campaign launched with the expanded formal solver:

```text
Process ID: 40372
Output directory: F:\_codex\LAXFORGE\runs\solver_campaign_24h_expanded_20260517_035240
Started: 2026-05-17T03:52:40-07:00
Solver: formal_sphere_ansatz_v1_fsync
```

Early expanded-solver checkpoint:

```text
attempt_count: 300
candidate_count: 515
rounds_completed: 0
status: running
survivor: null
attempt statuses:
  formal_ansatz_obstruction_or_gap: 297
  blocked_current_ansatz_family: 1
  blocked_first_potential_gate: 1
  validated_known_collision: 1
formal ansatz statuses:
  no_formal_solution: 297
```

Validation after remediation:

```text
$ python -m ruff check .
All checks passed!
```

```text
$ python -m pytest -q
........................................................................ [ 57%]
......................................................                   [100%]
126 passed in 140.86s (0:02:20)
```

## Bounded Solver Campaign Scheduler Restart

The expanded formal-solver campaign did not reach the 24-hour wall-clock budget. It stopped after
35,759 JSONL attempts when the next high-order overnight candidate batch exhausted memory while
materializing blend descriptors. No automated survivor was recorded before the stop.

Crash snapshot:

```text
Process ID: 40372
Output directory: F:\_codex\LAXFORGE\runs\solver_campaign_24h_expanded_20260517_035240
Last checkpoint: 2026-05-17T09:04:39.828268-07:00
attempt_count: 35750
attempts_jsonl_count: 35759
rounds_completed: 69
survivor: null
attempt statuses:
  formal_ansatz_obstruction_or_gap: 35756
  blocked_current_ansatz_family: 1
  blocked_first_potential_gate: 1
  validated_known_collision: 1
formal ansatz statuses:
  skipped_too_many_unknowns: 32256
  no_formal_solution: 3500
```

The scheduler was remediated to use bounded deterministic frontier pools instead of materializing the
entire high-order descriptor universe each round. The ansatz gates and conservative classifications
are unchanged.

Validation after bounded-scheduler remediation:

```text
$ python -m ruff check src\laxforge\search\solver_campaign.py scripts\run_solver_campaign.py tests\test_solver_campaign.py
All checks passed!
```

```text
$ python -m pytest tests\test_solver_campaign.py -q
....                                                                     [100%]
4 passed in 5.35s
```

Replacement 24-hour campaign launched explicitly:

```text
Process ID: 13884
Output directory: F:\_codex\LAXFORGE\runs\solver_campaign_24h_bounded_20260518_004842
Started: 2026-05-18T00:48:42-07:00
Solver: formal_sphere_ansatz_v1_bounded_frontier
```

Early bounded-scheduler checkpoint:

```text
attempt_count: 50
candidate_count: 515
rounds_completed: 0
status: running
survivor: null
attempt statuses:
  formal_ansatz_obstruction_or_gap: 53
  blocked_current_ansatz_family: 1
  blocked_first_potential_gate: 1
  validated_known_collision: 1
formal ansatz statuses:
  no_formal_solution: 53
```

## Monitored Solver Campaign Restart

The bounded scheduler was extended with a compact live-monitor snapshot writer. The monitor writes
`web/campaign_monitor_data.json` at checkpoint cadence and the static page
`web/campaign_monitor.html` polls that file from the local web server.

Validation after monitor integration:

```text
$ python -m ruff check src\laxforge\search\solver_campaign.py scripts\run_solver_campaign.py tests\test_solver_campaign.py
All checks passed!
```

```text
$ python -m pytest tests\test_solver_campaign.py -q
.....                                                                    [100%]
5 passed in 7.10s
```

```text
$ node --check web\campaign_monitor.js
```

Monitored 24-hour campaign launched explicitly:

```text
Process ID: 38032
Output directory: F:\_codex\LAXFORGE\runs\solver_campaign_24h_monitored_20260518_005647
Monitor URL: http://127.0.0.1:8765/campaign_monitor.html
Monitor snapshot: F:\_codex\LAXFORGE\web\campaign_monitor_data.json
Started: 2026-05-18T00:56:47-07:00
Solver: formal_sphere_ansatz_v1_bounded_frontier_monitored
Checkpoint cadence: 10 attempts
```

Browser smoke check:

```text
status: running
attempts: 170
candidates seen: 515
survivors: 0
known collisions: 1
validated ZCR: 1
```

## Fresh Overnight Campaign Reset

The monitored lane was reset on user request. Prior monitored/bounded campaign processes were stopped,
the monitor snapshot was cleared, and a fresh 24-hour campaign was launched from the initial low-order
sphere candidates.

Fresh monitored campaign:

```text
Process ID: 39244
Output directory: F:\_codex\LAXFORGE\runs\solver_campaign_overnight_fresh_20260518_013445
Monitor URL: http://127.0.0.1:8765/campaign_monitor.html
Monitor snapshot: F:\_codex\LAXFORGE\web\campaign_monitor_data.json
Started: 2026-05-18T01:34:45-07:00
Solver: formal_sphere_ansatz_v1_bounded_frontier_monitored
Session: fresh_overnight_from_first_candidates
```

First-candidate verification:

```text
attempt 1: overnight sphere unit times sxxx -> blocked_current_ansatz_family
attempt 2: overnight sphere unit times sxx -> validated_known_collision
attempt 3: overnight sphere unit times sx -> blocked_first_potential_gate
```

Browser smoke check after reset:

```text
status: running
attempts: 110
candidates seen: 515
survivors: 0
known collisions: 1
validated ZCR: 1
```

## Full-Spec Remediation Closure

Implemented canonical Pydantic evidence models, complete candidate dossier serialization,
explicit candidate artifact bundles, strategy-based symbolic constraint solving, expanded
gauge/invariant/conservation/Hamiltonian evidence reports, broadened prior-art coverage,
and the functional-completeness audit command.

Run-matrix parity was restored: DIS-003 is now the density-matrix lane, DIS-004 covers
nonlocal coverings, DIS-005 covers cohomological deformations, and the scaled sphere
triage lane is now DIS-006. FULL-001 now evaluates 143 discovery candidates across
DIS-001 through DIS-006, with 134 frontier records and 9 discard records.

Monitor snapshot writes now use best-effort atomic temp-file replacement, so live-monitor
filesystem failures do not abort solver campaigns.

```text
$ python -m ruff check .
All checks passed!
```

```text
$ python -m pytest -q
........................................................................ [ 50%]
......................................................................   [100%]
142 passed in 142.75s (0:02:22)
```

```text
$ python scripts/run_prompt_pack_validation.py
Restored run-matrix discovery lanes:
{'cohomology': ('DIS-005', 2),
 'density': ('DIS-003', 3),
 'nonlocal': ('DIS-004', 2)}
Scaled discovery phase:
{'candidate_count': 128,
 'discard_count': 1,
 'review_count': 127,
 'run_id': 'DIS-006'}
Iterative discovery frontier: ITER-001, frontier_active, 134 queued records
Procedure audit: PROC-001, pass, 8 checks, 0 failures, 0 warnings
Full-scale search: FULL-001, frontier_active, 143 generated candidates, 134 frontier records
```

```text
$ python scripts/run_functional_completeness_audit.py
Functional Completeness Audit FUNC-COMP-001
Status: pass
FC-001 canonical dossier model: pass
FC-002 dossier JSON serialization: pass
FC-003 artifact bundle filenames: pass
FC-004 run-matrix parity: pass
FC-005 density and scaled lane split: pass
FC-006 prior-art registry breadth: pass
FC-007 runtime language guard: pass
```

```text
$ python scripts/build_dashboard_data.py
Wrote dashboard data: F:\_codex\LAXFORGE\web\dashboard_data.js
```

```text
$ node --check web\app.js
$ node --check web\research_report.js
$ node --check web\campaign_monitor.js
$ node --check web\overnight_report.js
```
