"""Formal discovery procedures and audit checks."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from laxforge.search.iterative import IterativeDiscoveryReport, run_iterative_discovery


FORBIDDEN_PROMOTION_TERMS = ("novel", "publishable", "publication")
FRONTIER_STATUSES = {
    "promising_potential",
    "blocked_by_first_potential_gate",
    "blocked_by_recursive_nonlocal_tower",
    "formal_nonlocal_tower_validated",
    "blocked_by_missing_capability",
    "blocked_by_ansatz_obstruction",
    "needs_review",
    "density_matrix_pending",
    "nonlocal_covering_pending",
    "cohomology_pending",
    "batch_triage_pending",
}
FRONTIER_RECOMMENDATIONS = {"needs_human_review", "blocked"}
DISCARD_CLASSES = {"fake", "known", "known_mechanism_new_presentation", "known_mechanism"}


@dataclass(frozen=True)
class ProcedureStep:
    """One formal step in the discovery procedure."""

    step_id: str
    label: str
    owner: str
    objective: str
    required_evidence: tuple[str, ...]
    completion_rule: str

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-compatible procedure step."""
        return {
            "step_id": self.step_id,
            "label": self.label,
            "owner": self.owner,
            "objective": self.objective,
            "required_evidence": list(self.required_evidence),
            "completion_rule": self.completion_rule,
        }


@dataclass(frozen=True)
class ProcedureAuditCheck:
    """One procedure audit result."""

    check_id: str
    label: str
    status: str
    detail: str
    severity: str = "info"
    item_ids: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-compatible audit check."""
        return {
            "check_id": self.check_id,
            "label": self.label,
            "status": self.status,
            "detail": self.detail,
            "severity": self.severity,
            "item_ids": list(self.item_ids),
        }


@dataclass(frozen=True)
class ProcedureAuditReport:
    """Formal procedure audit for the current discovery frontier."""

    procedure_id: str
    title: str
    version: int
    status: str
    passed: bool
    failure_count: int
    warning_count: int
    summary: str
    procedure_steps: tuple[ProcedureStep, ...]
    checks: tuple[ProcedureAuditCheck, ...]

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-compatible procedure audit report."""
        return {
            "procedure_id": self.procedure_id,
            "title": self.title,
            "version": self.version,
            "status": self.status,
            "passed": self.passed,
            "failure_count": self.failure_count,
            "warning_count": self.warning_count,
            "summary": self.summary,
            "procedure_steps": [step.as_dict() for step in self.procedure_steps],
            "checks": [check.as_dict() for check in self.checks],
        }

    def to_markdown(self) -> str:
        """Render a concise procedure audit."""
        lines = [
            f"# {self.title}",
            "",
            f"- Procedure ID: `{self.procedure_id}`",
            f"- Version: {self.version}",
            f"- Status: `{self.status}`",
            f"- Failures: {self.failure_count}",
            f"- Warnings: {self.warning_count}",
            "",
            "## Formal Steps",
            "",
            "| Step | Owner | Completion Rule |",
            "|---|---|---|",
        ]
        for step in self.procedure_steps:
            lines.append(f"| {step.step_id}: {step.label} | {step.owner} | {step.completion_rule} |")
        lines.extend(["", "## Audit Checks", "", "| Check | Status | Detail |", "|---|---|---|"])
        for check in self.checks:
            lines.append(f"| {check.check_id}: {check.label} | `{check.status}` | {check.detail} |")
        return "\n".join(lines).rstrip() + "\n"


def discovery_procedure_steps() -> tuple[ProcedureStep, ...]:
    """Return the formal discovery procedure."""
    return (
        ProcedureStep(
            step_id="P0",
            label="Scope and posture",
            owner="Orchestrator",
            objective="Fix the lane, constraints, and conservative disposition rules.",
            required_evidence=("lane id", "candidate defaults", "promotion guard"),
            completion_rule="scope recorded before candidates enter the queue",
        ),
        ProcedureStep(
            step_id="P1",
            label="Generate",
            owner="Discovery Agent",
            objective="Create deterministic candidates with controls included.",
            required_evidence=("candidate name", "order", "target flow or ansatz shape"),
            completion_rule="candidate set is reproducible and includes controls",
        ),
        ProcedureStep(
            step_id="P2",
            label="Solve",
            owner="Ansatz Solver Agent",
            objective="Attempt zero-curvature construction using supported algebra.",
            required_evidence=("unknowns", "solution status", "residual basis"),
            completion_rule="residuals are solved, falsified, or explicitly blocked",
        ),
        ProcedureStep(
            step_id="P3",
            label="Reduce",
            owner="Gauge Agent",
            objective="Identify fake, trivial, removable, or reducible pairs.",
            required_evidence=("gauge-risk score", "spectral status", "block report"),
            completion_rule="reduction evidence is recorded or marked unsupported",
        ),
        ProcedureStep(
            step_id="P4",
            label="Fingerprint",
            owner="Cyclic Basis Agent",
            objective="Record gauge-invariant cyclic evidence when a spatial matrix exists.",
            required_evidence=("basis dimension", "closure relation", "lambda dependence"),
            completion_rule="fingerprint is recorded or the missing matrix reason is explicit",
        ),
        ProcedureStep(
            step_id="P5",
            label="Extract structure",
            owner="Conservation/Hamiltonian Agent",
            objective="Mine conservation and Hamiltonian evidence supported by the lane.",
            required_evidence=("conservation count", "Hamiltonian status"),
            completion_rule="structure evidence is recorded or left as an open gate",
        ),
        ProcedureStep(
            step_id="P6",
            label="Collision check",
            owner="Prior-Art Agent",
            objective="Compare against known families and collision zones.",
            required_evidence=("classification", "collisions", "checklist"),
            completion_rule="known collisions force discard or review status",
        ),
        ProcedureStep(
            step_id="P7",
            label="Classify",
            owner="Orchestrator",
            objective="Assign only conservative dispositions.",
            required_evidence=("recommendation", "failure reasons", "gate summary"),
            completion_rule="candidate is discard, review, audit, or calibration",
        ),
        ProcedureStep(
            step_id="P8",
            label="Queue next action",
            owner="Discovery Agent",
            objective="Keep surviving work as a frontier with the next honest test.",
            required_evidence=("priority", "gate gaps", "next action"),
            completion_rule="frontier records have actionable next tests",
        ),
        ProcedureStep(
            step_id="P9",
            label="Emit explicit artifacts",
            owner="Zero Curvature Agent",
            objective="Write JSON, Markdown, or dashboard data only through explicit writers.",
            required_evidence=("writer helper", "overwrite guard", "validation result"),
            completion_rule="no validation or search script writes proof files implicitly",
        ),
    )


def _check(
    check_id: str,
    label: str,
    ok: bool,
    pass_detail: str,
    fail_detail: str,
    item_ids: tuple[str, ...] = (),
    warning: bool = False,
) -> ProcedureAuditCheck:
    if ok:
        return ProcedureAuditCheck(check_id, label, "pass", pass_detail, "info", item_ids)
    status = "warn" if warning else "fail"
    severity = "warn" if warning else "fail"
    return ProcedureAuditCheck(check_id, label, status, fail_detail, severity, item_ids)


def audit_iterative_discovery(
    report: IterativeDiscoveryReport | None = None,
) -> ProcedureAuditReport:
    """Audit the current iterative discovery frontier against the formal procedure."""
    report = report or run_iterative_discovery()
    steps = discovery_procedure_steps()
    all_ids = {record.item_id for record in report.all_records}
    frontier_ids = {record.item_id for record in report.frontier}
    discarded_ids = {record.item_id for record in report.discarded}
    partition_ok = all_ids == frontier_ids | discarded_ids and not (frontier_ids & discarded_ids)
    discarded_ok = all(
        record.process_disposition == "discard" and record.recommendation == "discard"
        for record in report.discarded
    )
    frontier_conservative = all(
        record.recommendation in FRONTIER_RECOMMENDATIONS
        and record.potential_status in FRONTIER_STATUSES
        and record.classification not in DISCARD_CLASSES
        for record in report.frontier
    )
    frontier_actionable = all(
        record.next_action and record.gate_gaps and record.evidence_summary
        for record in report.frontier
    )
    status_ok = (
        bool(report.frontier) and report.process_status == "frontier_active"
    ) or (not report.frontier and report.process_status == "all_candidates_discarded")
    base_fields_ok = all(
        record.name and record.lane and record.classification and record.connection_status
        for record in report.all_records
    )
    rendered = (json.dumps(report.as_dict(), sort_keys=True) + report.to_markdown()).lower()
    language_ok = not any(term in rendered for term in FORBIDDEN_PROMOTION_TERMS)

    checks = (
        _check(
            "A0",
            "formal steps present",
            len(steps) == 10,
            "ten ordered procedure steps are defined",
            "procedure step list is incomplete",
        ),
        _check(
            "A1",
            "frontier partition",
            partition_ok,
            "all records partition into frontier or discard",
            "frontier and discard records do not form a clean partition",
            tuple(sorted(all_ids)),
        ),
        _check(
            "A2",
            "discard discipline",
            discarded_ok,
            "discard records carry discard disposition and recommendation",
            "discard records contain inconsistent disposition data",
            tuple(sorted(discarded_ids)),
        ),
        _check(
            "A3",
            "frontier conservatism",
            frontier_conservative,
            "frontier records remain review or blocked work",
            "frontier contains a record that should not remain queued",
            tuple(sorted(frontier_ids)),
        ),
        _check(
            "A4",
            "frontier actionability",
            frontier_actionable,
            "frontier records include next actions, gate gaps, and evidence summaries",
            "frontier records are missing next-action evidence",
            tuple(sorted(frontier_ids)),
        ),
        _check(
            "A5",
            "process status",
            status_ok,
            "process status matches the current frontier state",
            "process status does not match frontier contents",
        ),
        _check(
            "A6",
            "base evidence fields",
            base_fields_ok,
            "all records include name, lane, classification, and connection status",
            "one or more records are missing base evidence fields",
            tuple(sorted(all_ids)),
        ),
        _check(
            "A7",
            "language guard",
            language_ok,
            "promotion-language guard passed",
            "promotion-language guard failed",
        ),
    )
    failure_count = sum(1 for check in checks if check.status == "fail")
    warning_count = sum(1 for check in checks if check.status == "warn")
    passed = failure_count == 0
    status = "pass" if passed else "fail"
    summary = (
        f"{len(report.frontier)} frontier records, {len(report.discarded)} discard records, "
        f"{failure_count} failures, {warning_count} warnings"
    )
    return ProcedureAuditReport(
        procedure_id="PROC-001",
        title="LAXFORGE Discovery Procedure Audit",
        version=1,
        status=status,
        passed=passed,
        failure_count=failure_count,
        warning_count=warning_count,
        summary=summary,
        procedure_steps=steps,
        checks=checks,
    )


def build_procedure_audit_report(
    report: IterativeDiscoveryReport | None = None,
) -> ProcedureAuditReport:
    """Build the current procedure audit report."""
    return audit_iterative_discovery(report)


def write_procedure_audit_report(
    report: ProcedureAuditReport, output_dir: str | Path, overwrite: bool = True
) -> Path:
    """Write procedure audit JSON and Markdown only when explicitly requested."""
    output_path = Path(output_dir)
    if output_path.exists() and any(output_path.iterdir()) and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing procedure audit output: {output_path}")
    output_path.mkdir(parents=True, exist_ok=True)
    (output_path / "procedure_audit.json").write_text(
        json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_path / "procedure_audit.md").write_text(report.to_markdown(), encoding="utf-8")
    return output_path
