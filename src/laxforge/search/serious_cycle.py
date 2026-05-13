"""Controlled serious discovery cycles."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from laxforge.core.procedures import ProcedureAuditReport, build_procedure_audit_report
from laxforge.search.iterative import (
    DiscoveryIterationConfig,
    IterativeDiscoveryReport,
    run_iterative_discovery,
)
from laxforge.search.sphere_zcr import SphereSxxxZCRAttemptReport, solve_sxxx_zcr_ansatz


@dataclass(frozen=True)
class SeriousCycleReport:
    """A controlled evidence-cycle report."""

    cycle_id: str
    target_item_id: str
    target_name: str
    result_status: str
    recommendation: str
    baseline_process: IterativeDiscoveryReport
    baseline_procedure: ProcedureAuditReport
    attempt_report: SphereSxxxZCRAttemptReport
    refreshed_process: IterativeDiscoveryReport
    refreshed_procedure: ProcedureAuditReport
    next_action: str

    def as_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible serious-cycle report."""
        return {
            "cycle_id": self.cycle_id,
            "target_item_id": self.target_item_id,
            "target_name": self.target_name,
            "result_status": self.result_status,
            "recommendation": self.recommendation,
            "baseline_process": self.baseline_process.as_dict(),
            "baseline_procedure": self.baseline_procedure.as_dict(),
            "attempt_report": self.attempt_report.as_dict(),
            "refreshed_process": self.refreshed_process.as_dict(),
            "refreshed_procedure": self.refreshed_procedure.as_dict(),
            "next_action": self.next_action,
        }

    def to_markdown(self) -> str:
        """Render a concise serious-cycle report."""
        baseline_target = next(
            record
            for record in self.baseline_process.frontier
            if record.item_id == self.target_item_id
        )
        refreshed_target = next(
            record
            for record in self.refreshed_process.frontier
            if record.item_id == self.target_item_id
        )
        lines = [
            f"# Serious Cycle {self.cycle_id}",
            "",
            f"- Target: {self.target_name}",
            f"- Result: `{self.result_status}`",
            f"- Recommendation: `{self.recommendation}`",
            f"- Baseline target status: `{baseline_target.potential_status}`",
            f"- Refreshed target status: `{refreshed_target.potential_status}`",
            f"- Procedure status: `{self.refreshed_procedure.status}`",
            "",
            "## Obstruction Evidence",
            "",
        ]
        lines.extend(f"- {term}" for term in self.attempt_report.obstruction_basis)
        lines.extend(["", "## Next Action", "", self.next_action])
        return "\n".join(lines).rstrip() + "\n"


def run_serious_cycle_001() -> SeriousCycleReport:
    """Run SERIOUS-001 without writing artifacts."""
    baseline_process = run_iterative_discovery(
        DiscoveryIterationConfig(attempt_sxxx_ansatz=False)
    )
    baseline_procedure = build_procedure_audit_report(baseline_process)
    attempt_report = solve_sxxx_zcr_ansatz()
    refreshed_process = run_iterative_discovery(
        DiscoveryIterationConfig(attempt_sxxx_ansatz=True)
    )
    refreshed_procedure = build_procedure_audit_report(refreshed_process)
    return SeriousCycleReport(
        cycle_id="SERIOUS-001",
        target_item_id="sphere-s-cross-s-xxx-exploratory-candidate",
        target_name="sphere s_cross_s_xxx exploratory candidate",
        result_status="blocked",
        recommendation="blocked",
        baseline_process=baseline_process,
        baseline_procedure=baseline_procedure,
        attempt_report=attempt_report,
        refreshed_process=refreshed_process,
        refreshed_procedure=refreshed_procedure,
        next_action=(
            "Advance to the next queued frontier candidate while retaining the "
            "s_cross_s_xxx obstruction for a broader ansatz-family expansion."
        ),
    )


def write_serious_cycle_report(
    report: SeriousCycleReport, output_dir: str | Path, overwrite: bool = True
) -> Path:
    """Write serious-cycle JSON and Markdown only when explicitly requested."""
    output_path = Path(output_dir)
    if output_path.exists() and any(output_path.iterdir()) and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing serious-cycle output: {output_path}")
    output_path.mkdir(parents=True, exist_ok=True)
    (output_path / "serious_cycle.json").write_text(
        json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_path / "serious_cycle.md").write_text(report.to_markdown(), encoding="utf-8")
    return output_path
