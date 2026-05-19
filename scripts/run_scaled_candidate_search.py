#!/usr/bin/env python
"""Run DIS-006 scaled candidate triage without writing artifacts."""

from __future__ import annotations

from collections import Counter

from laxforge.search.bulk import run_scaled_candidate_search


def main() -> None:
    """Print a compact scaled-search summary."""
    report = run_scaled_candidate_search()
    recommendations = Counter(candidate.dossier.recommendation for candidate in report.candidates)
    families = Counter(candidate.family for candidate in report.candidates)
    print("LAXFORGE DIS-006 scaled candidate triage")
    print(f"Run: {report.run_id}")
    print(f"Arena: {report.arena}")
    print(f"Candidates: {len(report.candidates)}")
    print(f"Recommendations: {dict(sorted(recommendations.items()))}")
    print(f"Families: {dict(sorted(families.items()))}")
    print("Top priority records:")
    for candidate in sorted(
        report.candidates,
        key=lambda candidate: (-candidate.priority_score, candidate.name),
    )[:12]:
        print(
            "  - "
            f"{candidate.name}: "
            f"priority {candidate.priority_score}, "
            f"{candidate.dossier.recommendation}, "
            f"{candidate.connection_status}"
        )


if __name__ == "__main__":
    main()
