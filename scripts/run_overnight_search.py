#!/usr/bin/env python
"""Run OVERNIGHT-001 wide candidate triage without writing artifacts."""

from __future__ import annotations

from laxforge.search.overnight import run_overnight_search


def main() -> None:
    """Print a compact overnight-search summary."""
    report = run_overnight_search()
    print("LAXFORGE overnight candidate search")
    print(f"Run: {report.run_id}")
    print(f"Status: {report.status}")
    print(f"Candidates: {len(report.candidates)}")
    print(f"Action queue: {len(report.action_queue)}")
    print(f"Families: {report.family_counts}")
    print(f"Orders: {report.order_counts}")
    print(f"Recommendations: {report.recommendation_counts}")
    print("Analysis:")
    for note in report.analysis_notes:
        print(f"  - {note}")
    print("Top action queue:")
    for candidate in report.action_queue[:20]:
        print(
            "  - "
            f"{candidate.name}: "
            f"{candidate.family}, "
            f"order {candidate.order}, "
            f"priority {candidate.priority_score}, "
            f"surprisal {candidate.audit_surprisal['score']}"
        )


if __name__ == "__main__":
    main()
