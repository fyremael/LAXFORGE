"""Full-scale conservative search orchestration."""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from laxforge.core.procedures import ProcedureAuditReport, build_procedure_audit_report
from laxforge.search.iterative import (
    DiscoveryIterationConfig,
    FrontierCandidate,
    IterativeDiscoveryReport,
    run_iterative_discovery,
)


@dataclass(frozen=True)
class FullScaleSearchConfig:
    """Configuration for a full-scale evidence pass."""

    minimum_candidates: int = 100
    frontier_limit: int = 160
    action_queue_limit: int = 25
    include_dis001: bool = True
    include_dis002: bool = True
    include_dis003: bool = True
    include_dis004: bool = True
    include_dis005: bool = True
    include_dis006: bool = True


@dataclass(frozen=True)
class FullScaleSearchReport:
    """Conservative report for a full-scale discovery pass."""

    run_id: str
    status: str
    generated_candidate_count: int
    frontier_count: int
    discard_count: int
    lane_counts: dict[str, int]
    recommendation_counts: dict[str, int]
    action_queue: tuple[FrontierCandidate, ...]
    supported_gates: tuple[str, ...]
    blocked_capabilities: tuple[str, ...]
    outcome_summary: tuple[str, ...]
    iterative_report: IterativeDiscoveryReport
    procedure_audit: ProcedureAuditReport

    def as_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible full-scale report."""
        return {
            "run_id": self.run_id,
            "status": self.status,
            "generated_candidate_count": self.generated_candidate_count,
            "frontier_count": self.frontier_count,
            "discard_count": self.discard_count,
            "lane_counts": dict(self.lane_counts),
            "recommendation_counts": dict(self.recommendation_counts),
            "action_queue": [record.as_dict() for record in self.action_queue],
            "supported_gates": list(self.supported_gates),
            "blocked_capabilities": list(self.blocked_capabilities),
            "outcome_summary": list(self.outcome_summary),
            "iterative_report": self.iterative_report.as_dict(),
            "procedure_audit": self.procedure_audit.as_dict(),
        }

    def to_markdown(self) -> str:
        """Render a concise full-scale search report."""
        lines = [
            f"# Full-Scale Search {self.run_id}",
            "",
            f"- Status: `{self.status}`",
            f"- Generated candidates: {self.generated_candidate_count}",
            f"- Active frontier: {self.frontier_count}",
            f"- Discarded records: {self.discard_count}",
            f"- Procedure audit: `{self.procedure_audit.status}`",
            "",
            "## Outcome Summary",
            "",
        ]
        lines.extend(f"- {item}" for item in self.outcome_summary)
        lines.extend(
            [
                "",
                "## Action Queue",
                "",
                "| Candidate | Lane | Status | Priority | Next Action |",
                "|---|---|---|---:|---|",
            ]
        )
        for record in self.action_queue:
            lines.append(
                "| "
                f"{record.name} | "
                f"{record.lane} | "
                f"`{record.potential_status}` | "
                f"{record.priority} | "
                f"{record.next_action} |"
            )
        lines.extend(["", "## Blocked Capabilities", ""])
        lines.extend(f"- {item}" for item in self.blocked_capabilities)
        return "\n".join(lines).rstrip() + "\n"


def _count_by(records: tuple[FrontierCandidate, ...], field: str) -> dict[str, int]:
    counts = Counter(str(getattr(record, field)) for record in records)
    return dict(sorted(counts.items()))


def run_full_scale_search(config: FullScaleSearchConfig | None = None) -> FullScaleSearchReport:
    """Run the current full-scale search through all supported gates."""
    config = config or FullScaleSearchConfig()
    iterative = run_iterative_discovery(
        DiscoveryIterationConfig(
            frontier_limit=config.frontier_limit,
            include_dis001=config.include_dis001,
            include_dis002=config.include_dis002,
            include_dis003=config.include_dis003,
            include_dis004=config.include_dis004,
            include_dis005=config.include_dis005,
            include_dis006=config.include_dis006,
        )
    )
    procedure_audit = build_procedure_audit_report(iterative)
    lane_counts = _count_by(iterative.all_records, "lane")
    generated_candidate_count = len(iterative.all_records)
    if generated_candidate_count < config.minimum_candidates:
        raise RuntimeError(
            f"FULL-001 requires at least {config.minimum_candidates} candidates; "
            f"only {generated_candidate_count} were generated"
        )

    recommendation_counts = _count_by(iterative.all_records, "recommendation")
    action_queue = tuple(iterative.frontier[: config.action_queue_limit])
    blocked_capabilities = (
        "DIS-003 density-matrix ZCR matrices are not constructed in this pass",
        "DIS-004 nonlocal-covering ZCR matrices are not constructed in this pass",
        "DIS-005 cohomology quotient gates are scaffolded but not solved in this pass",
        "non-split semidirect coefficient multiplication remains unsupported",
        "s_cross_s_xxx is blocked only for the current low-order so(3) ansatz family",
        "conservation and Hamiltonian mining are not yet run for DIS-006 scaled descriptors",
    )
    supported_gates = (
        "deterministic candidate generation",
        "sphere tangent construction",
        "zero-control discard check",
        "known Heisenberg ZCR collision check",
        "s_cross_s_xxx low-order ansatz obstruction",
        "prior-art collision registry",
        "procedure partition audit",
        "dashboard/report evidence emission",
    )
    outcome_summary = (
        f"Full-scale pass evaluated {generated_candidate_count} candidate records across "
        f"{len(lane_counts)} discovery lanes.",
        f"DIS-003 contributes {lane_counts.get('DIS-003', 0)} density-matrix probes.",
        f"DIS-006 contributes {lane_counts.get('DIS-006', 0)} scaled sphere-tangent descriptors.",
        f"The active frontier contains {len(iterative.frontier)} records; "
        f"{len(iterative.discarded)} records are discarded controls or known-family collisions.",
        "No DIS-006 scaled batch candidate has a constructed ZCR matrix pair in this pass.",
        "The next honest work is solver selection from the action queue, not a stronger conclusion.",
    )
    status = "frontier_active" if iterative.frontier and procedure_audit.passed else "blocked"
    return FullScaleSearchReport(
        run_id="FULL-001",
        status=status,
        generated_candidate_count=generated_candidate_count,
        frontier_count=len(iterative.frontier),
        discard_count=len(iterative.discarded),
        lane_counts=lane_counts,
        recommendation_counts=recommendation_counts,
        action_queue=action_queue,
        supported_gates=supported_gates,
        blocked_capabilities=blocked_capabilities,
        outcome_summary=outcome_summary,
        iterative_report=iterative,
        procedure_audit=procedure_audit,
    )


def write_full_scale_search_report(
    report: FullScaleSearchReport, output_dir: str | Path, overwrite: bool = True
) -> Path:
    """Write full-scale JSON and Markdown only when explicitly requested."""
    output_path = Path(output_dir)
    if output_path.exists() and any(output_path.iterdir()) and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing full-scale output: {output_path}")
    output_path.mkdir(parents=True, exist_ok=True)
    (output_path / "full_scale_search.json").write_text(
        json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_path / "full_scale_search.md").write_text(report.to_markdown(), encoding="utf-8")
    return output_path
