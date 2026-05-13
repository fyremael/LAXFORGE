#!/usr/bin/env python
"""Run SERIOUS-001 without writing artifacts."""

from __future__ import annotations

from laxforge.search.serious_cycle import run_serious_cycle_001


def main() -> None:
    """Print the SERIOUS-001 summary."""
    report = run_serious_cycle_001()
    baseline_target = next(
        record
        for record in report.baseline_process.frontier
        if record.item_id == report.target_item_id
    )
    refreshed_target = next(
        record
        for record in report.refreshed_process.frontier
        if record.item_id == report.target_item_id
    )
    print("LAXFORGE serious cycle")
    print(f"Cycle: {report.cycle_id}")
    print(f"Target: {report.target_name}")
    print(f"Result: {report.result_status}")
    print(f"Baseline status: {baseline_target.potential_status}")
    print(f"Refreshed status: {refreshed_target.potential_status}")
    print(f"Procedure audit: {report.refreshed_procedure.status}")
    print("Obstruction evidence:")
    for term in report.attempt_report.obstruction_basis:
        print(f"  - {term}")
    print(f"Next action: {report.next_action}")
    if report.refreshed_procedure.status != "pass":
        raise SystemExit("Procedure audit failed after SERIOUS-001")


if __name__ == "__main__":
    main()
