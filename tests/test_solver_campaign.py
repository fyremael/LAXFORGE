import json

from laxforge.search.solver_campaign import SolverCampaignConfig, run_solver_campaign


def test_solver_campaign_records_supported_attempts(tmp_path):
    report = run_solver_campaign(
        SolverCampaignConfig(
            wall_seconds=1,
            target_count=520,
            max_derivative_order=4,
            action_queue_limit=12,
            output_dir=tmp_path / "campaign",
            checkpoint_every=3,
        )
    )

    assert report.run_id == "SOLVER-CAMPAIGN-001"
    assert report.status in {
        "candidate_queue_exhausted_without_survivor",
        "automated_survivor_found",
        "time_budget_exhausted",
    }
    assert report.attempts
    assert (tmp_path / "campaign" / "attempts.jsonl").exists()
    assert (tmp_path / "campaign" / "checkpoint.json").exists()
    assert (tmp_path / "campaign" / "summary.json").exists()


def test_solver_campaign_hits_known_heisenberg_collision(tmp_path):
    report = run_solver_campaign(
        SolverCampaignConfig(
            wall_seconds=1,
            target_count=520,
            max_derivative_order=4,
            action_queue_limit=12,
            output_dir=tmp_path / "campaign",
        )
    )

    known = [
        attempt
        for attempt in report.attempts
        if attempt.attempt_status == "validated_known_collision"
    ]
    assert known
    assert known[0].validated_zcr
    assert known[0].known_collision
    assert known[0].recommendation == "discard"


def test_solver_campaign_summary_avoids_promotion_language(tmp_path):
    report = run_solver_campaign(
        SolverCampaignConfig(
            wall_seconds=1,
            target_count=520,
            max_derivative_order=4,
            action_queue_limit=12,
            output_dir=tmp_path / "campaign",
        )
    )
    rendered = json.dumps(report.as_dict(), sort_keys=True).lower()

    assert "publishable" not in rendered
    assert "publication" not in rendered


def test_solver_campaign_uses_bounded_high_order_generation(tmp_path):
    report = run_solver_campaign(
        SolverCampaignConfig(
            wall_seconds=1,
            target_count=540,
            max_derivative_order=24,
            max_expansion_order=30,
            action_queue_limit=16,
            output_dir=tmp_path / "campaign",
            candidate_pool_limit=180,
            frontier_vector_limit=32,
            blend_pair_window=6,
        )
    )

    assert report.attempts
    assert report.status in {
        "candidate_queue_exhausted_without_survivor",
        "automated_survivor_found",
        "time_budget_exhausted",
    }


def test_solver_campaign_writes_monitor_snapshot(tmp_path):
    monitor_json = tmp_path / "monitor" / "campaign_monitor_data.json"
    report = run_solver_campaign(
        SolverCampaignConfig(
            wall_seconds=1,
            target_count=520,
            max_derivative_order=4,
            action_queue_limit=12,
            output_dir=tmp_path / "campaign",
            monitor_json_path=monitor_json,
            monitor_recent_attempts=8,
        )
    )

    payload = json.loads(monitor_json.read_text(encoding="utf-8"))
    rendered = json.dumps(payload, sort_keys=True).lower()

    assert payload["schema"] == "laxforge.campaign_monitor.v1"
    assert payload["run_id"] == report.run_id
    assert payload["attempt_count"] == len(report.attempts)
    assert "attempt_status" in payload["counts"]
    assert len(payload["latest_attempts"]) <= 8
    assert "publishable" not in rendered
    assert "publication" not in rendered


def test_solver_campaign_monitor_write_failure_does_not_abort(tmp_path):
    blocked_parent = tmp_path / "monitor-file"
    blocked_parent.write_text("not a directory", encoding="utf-8")
    monitor_json = blocked_parent / "campaign_monitor_data.json"

    report = run_solver_campaign(
        SolverCampaignConfig(
            wall_seconds=1,
            target_count=520,
            max_derivative_order=4,
            action_queue_limit=12,
            output_dir=tmp_path / "campaign",
            monitor_json_path=monitor_json,
            checkpoint_every=2,
        )
    )

    assert report.attempts
    assert (tmp_path / "campaign" / "checkpoint.json").exists()
    assert (tmp_path / "campaign" / "summary.json").exists()
