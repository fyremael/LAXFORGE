import json

import sympy as sp

from laxforge.search.overnight import (
    OvernightSearchConfig,
    run_overnight_search,
    write_overnight_data_js,
    write_overnight_search_report,
)


FORBIDDEN_PROMOTION_TERMS = ("novel", "publishable", "publication")


def test_overnight_search_generates_plethora_of_candidates():
    report = run_overnight_search()

    assert report.run_id == "OVERNIGHT-001"
    assert report.status == "frontier_active"
    assert len(report.candidates) == 1024
    assert len({candidate.name for candidate in report.candidates}) == 1024
    assert report.candidates[0].name == "overnight sphere zero-flow zero-connection control"
    assert report.recommendation_counts == {"discard": 1, "needs_human_review": 1023}
    assert len(report.family_counts) >= 3


def test_overnight_candidates_are_tangent_and_conservative():
    report = run_overnight_search()

    for candidate in report.candidates[1:]:
        assert sp.simplify(candidate.tangent_condition) == 0
        assert candidate.tangent_status == "tangent"
        assert candidate.connection_status == "not_constructed_overnight_triage"
        assert candidate.dossier.recommendation == "needs_human_review"
        assert candidate.failure_reasons
        assert "curvature_validation" in candidate.gate_summary
        assert "audit_surprisal" in candidate.gate_summary

    zero_control = report.candidates[0]
    assert zero_control.dossier.recommendation == "discard"
    assert zero_control.connection_status == "validated_zero_control"


def test_overnight_action_queue_is_ranked_and_auditable():
    report = run_overnight_search()

    assert len(report.action_queue) == 80
    scores = [candidate.audit_surprisal["score"] for candidate in report.action_queue]
    assert scores == sorted(scores, reverse=True)
    assert all(candidate.dossier.recommendation == "needs_human_review" for candidate in report.action_queue)
    assert report.analysis_notes
    assert report.next_actions


def test_overnight_search_rejects_too_small_runs():
    try:
        run_overnight_search(OvernightSearchConfig(target_count=200))
    except ValueError as exc:
        assert "at least 500 candidates" in str(exc)
    else:
        raise AssertionError("Expected overnight search to reject an underfilled run")


def test_overnight_report_avoids_promotion_language():
    report = run_overnight_search()
    rendered = json.dumps(report.as_dict(), sort_keys=True).lower() + report.to_markdown().lower()

    assert all(term not in rendered for term in FORBIDDEN_PROMOTION_TERMS)


def test_write_overnight_search_report_emits_json_markdown_and_data_js(tmp_path):
    report = run_overnight_search()
    output_dir = tmp_path / "overnight"

    written_path = write_overnight_search_report(report, output_dir)
    assert written_path == output_dir
    data = json.loads((output_dir / "overnight_search.json").read_text(encoding="utf-8"))
    assert data["run_id"] == "OVERNIGHT-001"
    assert data["candidate_count"] == 1024
    assert (output_dir / "overnight_search.md").read_text(encoding="utf-8").startswith(
        "# OVERNIGHT-001"
    )

    js_path = write_overnight_data_js(tmp_path / "overnight_data.js", report=report)
    assert js_path.read_text(encoding="utf-8").startswith("window.LAXFORGE_OVERNIGHT_DATA = ")


def test_write_overnight_search_report_refuses_overwrite_when_requested(tmp_path):
    report = run_overnight_search()
    output_dir = tmp_path / "overnight"
    write_overnight_search_report(report, output_dir)

    try:
        write_overnight_search_report(report, output_dir, overwrite=False)
    except FileExistsError as exc:
        assert "Refusing to overwrite" in str(exc)
    else:
        raise AssertionError("Expected overwrite refusal")
