#!/usr/bin/env python
"""Run FULL-001 full-scale conservative search without writing artifacts."""

from __future__ import annotations

from laxforge.search.full_scale import run_full_scale_search


def main() -> None:
    """Print a compact full-scale search summary."""
    report = run_full_scale_search()
    print("LAXFORGE full-scale search")
    print(f"Run: {report.run_id}")
    print(f"Status: {report.status}")
    print(f"Generated candidates: {report.generated_candidate_count}")
    print(f"Frontier: {report.frontier_count}")
    print(f"Discarded: {report.discard_count}")
    print(f"Lane counts: {report.lane_counts}")
    print(f"Recommendations: {report.recommendation_counts}")
    print("Outcome:")
    for item in report.outcome_summary:
        print(f"  - {item}")
    print("Action queue:")
    for record in report.action_queue[:15]:
        print(
            "  - "
            f"{record.name}: "
            f"{record.lane}, "
            f"{record.potential_status}, "
            f"priority {record.priority}"
        )


if __name__ == "__main__":
    main()
