import json

from laxforge.search.full_scale import (
    FullScaleSearchConfig,
    run_full_scale_search,
    write_full_scale_search_report,
)


FORBIDDEN_PROMOTION_TERMS = ("novel", "publishable", "publication")


def test_full_scale_search_runs_current_scaled_frontier():
    report = run_full_scale_search()

    assert report.run_id == "FULL-001"
    assert report.status == "frontier_active"
    assert report.generated_candidate_count == 143
    assert report.frontier_count == 134
    assert report.discard_count == 9
    assert report.lane_counts == {
        "DIS-001": 4,
        "DIS-002": 4,
        "DIS-003": 3,
        "DIS-004": 2,
        "DIS-005": 2,
        "DIS-006": 128,
    }
    assert report.recommendation_counts == {
        "blocked": 2,
        "discard": 9,
        "needs_human_review": 132,
    }
    assert report.procedure_audit.status == "pass"


def test_full_scale_action_queue_is_prioritized_and_conservative():
    report = run_full_scale_search()

    assert len(report.action_queue) == 25
    assert report.action_queue[0].item_id == "semidirect-non-split-product-deformation-probe"
    assert report.action_queue[1].item_id == "scaled-sphere-jerk-sq-blend-sx-sxxx"
    assert report.action_queue[2].item_id == "scaled-sphere-jerk-sq-blend-sx-sxxxx"
    assert any(record.lane == "DIS-006" for record in report.action_queue)
    assert any("non-split semidirect gauge" in item for item in report.blocked_capabilities)
    assert any("formal-tower evidence" in item for item in report.blocked_capabilities)
    assert all(
        record.recommendation in {"needs_human_review", "blocked"}
        for record in report.action_queue
    )


def test_full_scale_search_rejects_underfilled_runs():
    try:
        run_full_scale_search(FullScaleSearchConfig(minimum_candidates=200))
    except RuntimeError as exc:
        assert "requires at least 200 candidates" in str(exc)
    else:
        raise AssertionError("Expected underfilled full-scale run to fail")


def test_full_scale_report_avoids_promotion_language():
    report = run_full_scale_search()
    rendered = json.dumps(report.as_dict(), sort_keys=True).lower() + report.to_markdown().lower()

    assert all(term not in rendered for term in FORBIDDEN_PROMOTION_TERMS)


def test_write_full_scale_search_report_emits_json_and_markdown(tmp_path):
    report = run_full_scale_search()
    output_dir = tmp_path / "full"

    written_path = write_full_scale_search_report(report, output_dir)

    assert written_path == output_dir
    data = json.loads((output_dir / "full_scale_search.json").read_text(encoding="utf-8"))
    assert data["run_id"] == "FULL-001"
    assert data["generated_candidate_count"] == 143
    assert (output_dir / "full_scale_search.md").read_text(encoding="utf-8").startswith(
        "# Full-Scale Search FULL-001"
    )


def test_write_full_scale_search_report_refuses_overwrite_when_requested(tmp_path):
    report = run_full_scale_search()
    output_dir = tmp_path / "full"
    write_full_scale_search_report(report, output_dir)

    try:
        write_full_scale_search_report(report, output_dir, overwrite=False)
    except FileExistsError as exc:
        assert "Refusing to overwrite" in str(exc)
    else:
        raise AssertionError("Expected FileExistsError when overwrite is disabled")
