#!/usr/bin/env python
"""Run a checkpointed solver campaign."""

from __future__ import annotations

import argparse
from pathlib import Path

from laxforge.search.solver_campaign import SolverCampaignConfig, run_solver_campaign


def main() -> None:
    """Run the campaign and print the final summary."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hours", type=float, default=24.0, help="Wall-clock budget in hours.")
    parser.add_argument("--target-count", type=int, default=4096, help="Candidate count to generate.")
    parser.add_argument("--max-derivative-order", type=int, default=9)
    parser.add_argument("--max-expansion-order", type=int, default=45)
    parser.add_argument("--action-queue-limit", type=int, default=512)
    parser.add_argument("--checkpoint-every", type=int, default=25)
    parser.add_argument("--candidate-pool-limit", type=int, default=4096)
    parser.add_argument("--frontier-vector-limit", type=int, default=192)
    parser.add_argument("--blend-pair-window", type=int, default=24)
    parser.add_argument(
        "--monitor-json",
        type=Path,
        default=None,
        help="Optional compact JSON snapshot written at checkpoint cadence for a live monitor.",
    )
    parser.add_argument("--monitor-recent-attempts", type=int, default=50)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("runs") / "solver_campaign_latest",
        help="Checkpoint/output directory.",
    )
    args = parser.parse_args()
    report = run_solver_campaign(
        SolverCampaignConfig(
            wall_seconds=max(1, int(args.hours * 60 * 60)),
            target_count=args.target_count,
            max_derivative_order=args.max_derivative_order,
            max_expansion_order=args.max_expansion_order,
            action_queue_limit=args.action_queue_limit,
            output_dir=args.output_dir,
            checkpoint_every=args.checkpoint_every,
            candidate_pool_limit=args.candidate_pool_limit,
            frontier_vector_limit=args.frontier_vector_limit,
            blend_pair_window=args.blend_pair_window,
            monitor_json_path=args.monitor_json,
            monitor_recent_attempts=args.monitor_recent_attempts,
        )
    )
    print("LAXFORGE solver campaign")
    print(f"Run: {report.run_id}")
    print(f"Status: {report.status}")
    print(f"Attempts: {len(report.attempts)} / {report.candidate_count}")
    print(f"Output: {report.output_dir}")
    if report.survivor:
        print(f"Automated survivor: {report.survivor.candidate_name}")
    else:
        print("Automated survivor: none")


if __name__ == "__main__":
    main()
