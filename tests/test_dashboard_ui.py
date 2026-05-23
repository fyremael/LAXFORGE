import json
from pathlib import Path

from laxforge.ui.dashboard import (
    build_dashboard_payload,
    write_dashboard_data,
    write_dashboard_data_js,
)


FORBIDDEN_PROMOTION_TERMS = ("novel", "publishable", "publication")


def _item(payload, item_id):
    return next(item for item in payload["items"] if item["id"] == item_id)


def test_dashboard_payload_tracks_m0_calibration_and_discovery_items():
    payload = build_dashboard_payload()

    assert payload["schema_version"] == 7
    assert payload["metrics"]["tracked_items_total"] == 145
    assert payload["metrics"]["proof_artifact_count"] == 1
    assert payload["metrics"]["discovery_candidate_count"] == 143
    assert payload["metrics"]["dis001_candidate_count"] == 4
    assert payload["metrics"]["dis002_candidate_count"] == 4
    assert payload["metrics"]["dis003_candidate_count"] == 3
    assert payload["metrics"]["dis004_candidate_count"] == 2
    assert payload["metrics"]["dis005_candidate_count"] == 2
    assert payload["metrics"]["dis006_candidate_count"] == 128
    assert payload["metrics"]["frontier_count"] == 134
    assert payload["metrics"]["promising_potential_count"] == 0
    assert payload["metrics"]["blocked_frontier_count"] == 3
    assert payload["metrics"]["ansatz_blocked_count"] == 1
    assert payload["metrics"]["serious_cycle_status"] == "blocked"
    assert payload["metrics"]["full_scale_status"] == "frontier_active"
    assert payload["metrics"]["full_scale_candidate_count"] == 143
    assert payload["metrics"]["full_scale_action_queue_count"] == 25
    assert payload["metrics"]["procedure_audit_status"] == "pass"
    assert payload["metrics"]["procedure_check_count"] == 8
    assert payload["metrics"]["procedure_failure_count"] == 0
    assert payload["metrics"]["validated_zcr_count"] == 2
    assert payload["iterative_process"]["run_id"] == "ITER-001"
    assert payload["procedure_audit"]["procedure_id"] == "PROC-001"
    assert payload["serious_cycle"]["cycle_id"] == "SERIOUS-001"
    assert payload["full_scale_search"]["run_id"] == "FULL-001"
    assert [item["id"] for item in payload["items"][:10]] == [
        "m0-pure-gauge-flatness-audit",
        "second-jet-nilpotent-mkdv",
        "semidirect-zero-connection-control",
        "semidirect-split-nilpotent-mkdv-lift-control",
        "semidirect-rescaled-perturbation-parameter-control",
        "semidirect-non-split-product-deformation-probe",
        "sphere-zero-flow-zero-connection-control",
        "sphere-s-cross-s-x-tangent-candidate",
        "sphere-s-cross-s-xx-heisenberg-shaped-candidate",
        "sphere-s-cross-s-xxx-exploratory-candidate",
    ]
    assert payload["items"][10]["id"] == "density-matrix-zero-commutator-control"
    assert payload["items"][-1]["lane"] == "DIS-006"


def test_every_dashboard_item_has_normalized_audit_fields():
    payload = build_dashboard_payload()

    for item in payload["items"]:
        assert item["item_type"] in {"candidate", "calibration", "proof_artifact"}
        assert item["lane"]
        assert item["gate_summary"]
        assert item["recommendation"] in {
            "audit",
            "blocked",
            "calibration",
            "discard",
            "needs_human_review",
        }
        assert item["disposition"] == item["recommendation"]
        assert item["detail"]
        assert item["surprisal"]["drivers"]
        assert {gate["key"] for gate in item["gates"]} == set(payload["gate_order"])


def test_dashboard_payload_includes_plain_lay_summary():
    payload = build_dashboard_payload()
    summary = payload["plain_summary"]

    assert "active evidence search" in summary["headline"]
    assert "auditing 145 items" in summary["lede"]
    assert "active frontier has 134 queued candidates" in summary["lede"]
    assert len(summary["bullets"]) == 10
    assert "pure-gauge proof artifact passes" in summary["bullets"][0]
    assert "formal procedure audit passes" in summary["bullets"][1]
    assert "DIS-001 has 4 semidirect probes" in summary["bullets"][2]
    assert "DIS-003 through DIS-005 add 3 density-matrix" in summary["bullets"][4]
    assert "DIS-006 adds 128 scaled sphere-tangent triage candidates" in summary["bullets"][5]
    assert "SERIOUS-001 leaves 1 third-order candidate blocked" in summary["bullets"][7]
    assert "FULL-001 evaluates 143 discovery candidates" in summary["bullets"][-1]
    assert "process console" in summary["bottom_line"]


def test_dashboard_pure_gauge_artifact_records_proof_summary():
    payload = build_dashboard_payload()
    item = _item(payload, "m0-pure-gauge-flatness-audit")
    proof = item["proof_summary"]

    assert item["item_type"] == "proof_artifact"
    assert item["curvature_residual_zero"] is True
    assert proof["curvature_convention"] == "U_t - V_x + [U,V]"
    assert proof["matrix_shape"] == [2, 2]
    assert proof["coefficient_basis"] == ["1", "eps", "eps^2"]
    assert proof["entry_status_grid"] == [["OK", "OK"], ["OK", "OK"]]
    assert proof["markdown_ready"] is True


def test_dashboard_heisenberg_candidate_surfaces_known_zcr_collision():
    payload = build_dashboard_payload()
    item = _item(payload, "sphere-s-cross-s-xx-heisenberg-shaped-candidate")

    assert item["zcr_validated"] is True
    assert item["zcr_solution"] == {"alpha": "-1", "beta": "1"}
    assert item["classification"] == "known"
    assert item["recommendation"] == "discard"
    assert "Heisenberg / symmetric-space" in item["collision_families"]
    assert "AKNS" in item["collision_families"]
    assert "validated ZCR evidence" in item["surprisal"]["drivers"]


def test_dashboard_semidirect_search_surfaces_started_dis001_lane():
    payload = build_dashboard_payload()
    split_control = _item(payload, "semidirect-split-nilpotent-mkdv-lift-control")
    non_split_probe = _item(payload, "semidirect-non-split-product-deformation-probe")

    assert split_control["lane"] == "DIS-001"
    assert split_control["zcr_validated"] is True
    assert split_control["recommendation"] == "discard"
    assert "semidirect coupling" in split_control["collision_families"]
    assert non_split_probe["recommendation"] == "needs_human_review"
    assert non_split_probe["connection_status"] == "not_constructed"
    assert non_split_probe["frontier_status"] == "blocked_by_missing_capability"


def test_dashboard_frontier_process_tracks_queued_next_actions():
    payload = build_dashboard_payload()
    frontier = payload["iterative_process"]["frontier"]
    frontier_ids = {record["item_id"] for record in frontier}

    assert {
        "semidirect-non-split-product-deformation-probe",
        "sphere-s-cross-s-x-tangent-candidate",
        "sphere-s-cross-s-xxx-exploratory-candidate",
    } <= frontier_ids
    assert len(frontier) == 134
    assert any(record["lane"] == "DIS-003" for record in frontier)
    assert any(record["lane"] == "DIS-006" for record in frontier)
    assert all(record["next_action"] for record in frontier)
    assert _item(payload, "sphere-s-cross-s-x-tangent-candidate")[
        "frontier_status"
    ] == "blocked_by_first_potential_gate"
    assert _item(payload, "sphere-s-cross-s-xxx-exploratory-candidate")[
        "frontier_status"
    ] == "blocked_by_ansatz_obstruction"


def test_dashboard_serious_cycle_surfaces_sxxx_obstruction():
    payload = build_dashboard_payload()
    item = _item(payload, "sphere-s-cross-s-xxx-exploratory-candidate")
    cycle = payload["serious_cycle"]

    assert cycle["result_status"] == "blocked"
    assert cycle["baseline_process"]["frontier"][0]["item_id"] == item["id"]
    assert item["recommendation"] == "blocked"
    assert item["connection_status"] == "ansatz_obstruction_current_family"
    assert item["zcr_validated"] is False
    assert item["zcr_obstruction_basis"]


def test_dashboard_procedure_audit_tracks_formal_checks():
    payload = build_dashboard_payload()
    audit = payload["procedure_audit"]

    assert audit["status"] == "pass"
    assert len(audit["procedure_steps"]) == 10
    assert len(audit["checks"]) == 8
    assert all(check["status"] == "pass" for check in audit["checks"])
    assert audit["checks"][0]["check_id"] == "A0"


def test_dashboard_surprisal_is_a_triage_signal_not_a_promotion_claim():
    payload = build_dashboard_payload()

    for item in payload["items"]:
        surprisal = item["surprisal"]
        assert 0 <= surprisal["score"] <= 100
        assert surprisal["band"] in {"baseline", "watch", "inspect", "escalate"}
        assert surprisal["drivers"]

    rendered = json.dumps(payload, sort_keys=True).lower()
    assert all(term not in rendered for term in FORBIDDEN_PROMOTION_TERMS)


def test_dashboard_collision_family_map_connects_known_families():
    payload = build_dashboard_payload()
    families = {entry["family"]: entry["item_ids"] for entry in payload["collision_family_map"]}

    assert "AKNS" in families
    assert "Heisenberg / symmetric-space" in families
    assert "scalar hierarchy" in families
    assert "nilpotent / perturbation" in families
    assert "sphere-s-cross-s-xx-heisenberg-shaped-candidate" in families["AKNS"]


def test_dashboard_writer_emits_json_and_static_js(tmp_path):
    payload = build_dashboard_payload()
    json_path = write_dashboard_data(tmp_path / "dashboard.json", payload=payload)
    js_path = write_dashboard_data_js(tmp_path / "dashboard_data.js", payload=payload)

    assert json.loads(json_path.read_text(encoding="utf-8"))["schema_version"] == 7
    js_text = js_path.read_text(encoding="utf-8")
    assert js_text.startswith("window.LAXFORGE_DASHBOARD_DATA = ")
    assert '"LAXFORGE Evidence Console"' in js_text


def test_dashboard_writer_refuses_overwrite_when_requested(tmp_path):
    output_path = tmp_path / "dashboard_data.js"
    write_dashboard_data_js(output_path)

    try:
        write_dashboard_data_js(output_path, overwrite=False)
    except FileExistsError as exc:
        assert "Refusing to overwrite" in str(exc)
    else:
        raise AssertionError("Expected FileExistsError when overwrite is disabled")


def test_static_web_dashboard_assets_cover_full_console():
    root = Path(__file__).resolve().parents[1]
    index_text = (root / "web" / "index.html").read_text(encoding="utf-8")
    app_text = (root / "web" / "app.js").read_text(encoding="utf-8")
    css_text = (root / "web" / "styles.css").read_text(encoding="utf-8")
    combined = "\n".join([index_text, app_text, css_text]).lower()

    for panel in (
        "tab-overview",
        "tab-candidates",
        "tab-frontier",
        "tab-procedures",
        "tab-gates",
        "tab-artifacts",
        "tab-collisions",
    ):
        assert panel in index_text
    assert "plain-summary" in index_text
    for renderer in (
        "renderTabs",
        "renderPlainSummary",
        "renderGateHeatmap",
        "renderCandidateBoard",
        "renderFrontierList",
        "renderProcedureAudit",
        "renderArtifactList",
        "renderCollisionMap",
        "renderDetails",
    ):
        assert renderer in app_text
    for selector in (
        ".metric-grid",
        ".plain-summary",
        ".frontier-list",
        ".procedure-list",
        ".heatmap-slot",
        ".board-panel",
        ".detail-panel",
        "@media",
    ):
        assert selector in css_text
    assert all(term not in combined for term in FORBIDDEN_PROMOTION_TERMS)
