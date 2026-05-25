from pathlib import Path

from laxforge.ui.dashboard import build_dashboard_payload


FORBIDDEN_PROMOTION_TERMS = ("novel", "publishable", "publication")


def test_research_report_payload_supports_progress_digest():
    payload = build_dashboard_payload()
    target = next(
        item for item in payload["items"] if item["id"] == "sphere-s-cross-s-xxx-exploratory-candidate"
    )
    artifact = next(item for item in payload["items"] if item["item_type"] == "proof_artifact")

    assert payload["run_ids"] == [
        "M0",
        "PROMPT-PACK",
        "DIS-001",
        "DIS-002",
        "DIS-003",
        "DIS-004",
        "DIS-005",
        "DIS-006",
        "ITER-001",
        "PROC-001",
        "SERIOUS-001",
        "FULL-001",
    ]
    assert payload["metrics"]["tracked_items_total"] == 145
    assert payload["metrics"]["dis003_candidate_count"] == 3
    assert payload["metrics"]["dis006_candidate_count"] == 128
    assert payload["metrics"]["validated_zcr_count"] == 4
    assert payload["metrics"]["serious_cycle_status"] == "blocked"
    assert payload["metrics"]["full_scale_status"] == "frontier_active"
    assert payload["procedure_audit"]["status"] == "pass"
    assert target["recommendation"] == "blocked"
    assert target["zcr_obstruction_basis"]
    assert artifact["proof_summary"]["entry_status_grid"] == [["OK", "OK"], ["OK", "OK"]]


def test_static_research_report_assets_cover_visual_report_sections():
    root = Path(__file__).resolve().parents[1]
    html = (root / "web" / "research_report.html").read_text(encoding="utf-8")
    script = (root / "web" / "research_report.js").read_text(encoding="utf-8")
    css = (root / "web" / "research_report.css").read_text(encoding="utf-8")
    combined = "\n".join([html, script, css]).lower()

    for element_id in (
        "report-summary",
        "report-readout",
        "report-readout-copy",
        "report-question",
        "report-methods",
        "report-dossiers",
        "report-metrics",
        "report-timeline",
        "report-disposition",
        "report-gates",
        "report-surprisal",
        "report-frontier",
        "report-cycle",
        "report-procedure",
        "report-artifacts",
        "report-residual",
        "report-collisions",
        "report-ledger",
    ):
        assert element_id in html

    for renderer in (
        "renderInstrumentRing",
        "renderReportMetrics",
        "renderSummary",
        "renderReadout",
        "renderQuestion",
        "renderMethods",
        "renderDossiers",
        "renderTimeline",
        "renderDispositionMix",
        "renderGateHeatmap",
        "renderAuditSurprisal",
        "renderFrontier",
        "renderSeriousCycle",
        "renderProcedureAudit",
        "renderArtifacts",
        "renderCollisionMap",
        "renderTechnicalLedger",
    ):
        assert renderer in script

    for selector in (
        ".report-hero",
        ".narrative-section",
        ".readout-copy",
        ".prose-panel",
        ".dossier-grid",
        ".dossier-card",
        ".metric-strip",
        ".timeline",
        ".gate-matrix",
        ".frontier-cards",
        ".cycle-panel",
        ".residual-grid",
        ".collision-radar",
        ".ledger-table",
        "@media",
    ):
        assert selector in css

    for narrative_phrase in (
        "controlled evidence machine",
        "what are we trying to separate",
        "the progress story by lane",
        "blocked is a valid outcome",
        "scaled triage now carries 100+ candidates",
        "full-scale pass has been carried out",
    ):
        assert narrative_phrase in combined

    assert all(term not in combined for term in FORBIDDEN_PROMOTION_TERMS)
