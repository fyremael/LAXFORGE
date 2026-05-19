#!/usr/bin/env python
"""Run the current controlled discovery lanes without writing artifacts."""

from __future__ import annotations

from laxforge.search.bulk import run_scaled_candidate_search
from laxforge.search.iterative import run_iterative_discovery
from laxforge.search.run_matrix import (
    run_cohomological_deformation_search,
    run_density_matrix_search,
    run_nonlocal_covering_search,
)
from laxforge.search.semidirect import run_semidirect_deformation_search
from laxforge.search.sphere import run_sphere_low_order_search


def _print_run_summary(report, limit: int | None = None) -> None:
    print(f"{report.run_id}: {report.arena}")
    candidates = report.candidates if limit is None else report.candidates[:limit]
    for candidate in candidates:
        print(
            "  - "
            f"{candidate.name}: "
            f"{candidate.dossier.classification.value}, "
            f"{candidate.dossier.recommendation}, "
            f"{candidate.connection_status}"
        )
    if limit is not None and len(report.candidates) > limit:
        print(f"  - ... {len(report.candidates) - limit} additional candidates retained in report")


def main() -> None:
    """Print a compact conservative discovery summary."""
    print("LAXFORGE controlled discovery search")
    print("No automatic discovery conclusions are emitted.")
    _print_run_summary(run_semidirect_deformation_search())
    _print_run_summary(run_sphere_low_order_search())
    _print_run_summary(run_density_matrix_search())
    _print_run_summary(run_nonlocal_covering_search())
    _print_run_summary(run_cohomological_deformation_search())
    _print_run_summary(run_scaled_candidate_search(), limit=12)
    iterative = run_iterative_discovery()
    print(f"{iterative.run_id}: iterative discovery frontier")
    print(f"  - process status: {iterative.process_status}")
    print(f"  - active frontier: {len(iterative.frontier)}")
    for record in iterative.frontier[:12]:
        print(
            "    * "
            f"{record.name}: "
            f"{record.potential_status}, "
            f"priority {record.priority}, "
            f"next={record.next_action}"
        )
    if len(iterative.frontier) > 12:
        print(f"    * ... {len(iterative.frontier) - 12} additional frontier records retained")
    print(f"  - stop reason: {iterative.stop_reason}")


if __name__ == "__main__":
    main()
