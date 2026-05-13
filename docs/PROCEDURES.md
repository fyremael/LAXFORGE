# LAXFORGE Procedures

This document fixes the current discovery and audit procedure. The code authority
is `src/laxforge/core/procedures.py`; this file is the human-readable version.

## Operating Rule

LAXFORGE produces evidence. It does not promote a candidate automatically. Every
candidate starts in a conservative state and must move through formal gates before
it can leave the frontier.

## Discovery Procedure

| Step | Owner | Evidence Required | Completion Rule |
|---|---|---|---|
| P0 Scope and posture | Orchestrator | lane id, candidate defaults, promotion guard | scope recorded before candidates enter the queue |
| P1 Generate | Discovery Agent | candidate name, order, target flow or ansatz shape | candidate set is reproducible and includes controls |
| P2 Solve | Ansatz Solver Agent | unknowns, solution status, residual basis | residuals are solved, falsified, or explicitly blocked |
| P3 Reduce | Gauge Agent | gauge-risk score, spectral status, block report | reduction evidence is recorded or marked unsupported |
| P4 Fingerprint | Cyclic Basis Agent | basis dimension, closure relation, lambda dependence | fingerprint is recorded or the missing matrix reason is explicit |
| P5 Extract structure | Conservation/Hamiltonian Agent | conservation count, Hamiltonian status | structure evidence is recorded or left as an open gate |
| P6 Collision check | Prior-Art Agent | classification, collisions, checklist | known collisions force discard or review status |
| P7 Classify | Orchestrator | recommendation, failure reasons, gate summary | candidate is discard, review, audit, or calibration |
| P8 Queue next action | Discovery Agent | priority, gate gaps, next action | frontier records have actionable next tests |
| P9 Emit explicit artifacts | Zero Curvature Agent | writer helper, overwrite guard, validation result | no validation or search script writes proof files implicitly |

## Audit Procedure

The audit checks the current iterative frontier with these gates:

| Check | Purpose |
|---|---|
| A0 | Confirm the formal procedure has all ordered steps. |
| A1 | Confirm every search record is either frontier or discard, with no overlap. |
| A2 | Confirm discard records carry discard disposition and recommendation. |
| A3 | Confirm frontier records remain conservative review or blocked work. |
| A4 | Confirm frontier records have next actions, gate gaps, and evidence summaries. |
| A5 | Confirm process status matches frontier contents. |
| A6 | Confirm every record has base evidence fields. |
| A7 | Confirm the promotion-language guard passes. |

Run the audit without writing artifacts:

```bash
python scripts/run_procedure_audit.py
```

Write an audit artifact only through the explicit helper:

```python
from laxforge.core.procedures import build_procedure_audit_report, write_procedure_audit_report

report = build_procedure_audit_report()
write_procedure_audit_report(report, "audit-output")
```
