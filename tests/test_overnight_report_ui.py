import json

from laxforge.search.overnight import run_overnight_search


FORBIDDEN_PROMOTION_TERMS = ("novel", "publishable", "publication")


def test_overnight_static_report_assets_exist_and_render_contracts():
    html = open("web/overnight_report.html", encoding="utf-8").read()
    js = open("web/overnight_report.js", encoding="utf-8").read()
    css = open("web/overnight_report.css", encoding="utf-8").read()

    for required_id in (
        "executive-readout",
        "metric-grid",
        "family-bars",
        "order-bars",
        "gate-grid",
        "action-queue",
        "candidate-table",
    ):
        assert required_id in html

    for function_name in (
        "renderReadout",
        "renderMetrics",
        "renderBars",
        "renderGates",
        "renderQueue",
        "renderTable",
    ):
        assert f"function {function_name}" in js

    assert "@media" in css
    assert ".metric-grid" in css
    assert ".gate-grid" in css
    assert ".queue-grid" in css
    assert ".candidate-table" in css

    rendered = f"{html}\n{js}\n{css}".lower()
    assert all(term not in rendered for term in FORBIDDEN_PROMOTION_TERMS)


def test_overnight_report_payload_contains_expected_analysis_shape():
    report = run_overnight_search()
    payload = report.as_dict()
    rendered = json.dumps(payload, sort_keys=True).lower()

    assert payload["run_id"] == "OVERNIGHT-001"
    assert payload["candidate_count"] == 1024
    assert payload["action_queue_count"] == 80
    assert payload["gate_counts"]["tangent"]["pass"] == 1024
    assert payload["gate_counts"]["curvature"]["warn"] == 1023
    assert payload["analysis_notes"]
    assert payload["next_actions"]
    assert all(term not in rendered for term in FORBIDDEN_PROMOTION_TERMS)
