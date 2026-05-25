import json

from laxforge.search.iterative import (
    DiscoveryIterationConfig,
    run_iterative_discovery,
    write_iterative_discovery_report,
)


FORBIDDEN_PROMOTION_TERMS = ("novel", "publishable", "publication")


def test_iterative_discovery_builds_repeatable_frontier():
    report = run_iterative_discovery()

    assert report.run_id == "ITER-001"
    assert report.process_status == "frontier_active"
    assert [iteration.index for iteration in report.iterations] == [1, 2]
    assert [record.item_id for record in report.frontier[:3]] == [
        "scaled-sphere-unit-times-sxxxxx",
        "semidirect-non-split-product-deformation-probe",
        "scaled-sphere-jerk-sq-blend-sx-sxxx",
    ]
    assert len(report.all_records) == 143
    assert len(report.frontier) == 134


def test_iterative_discovery_discards_controls_and_known_collisions():
    report = run_iterative_discovery()
    discarded_ids = {record.item_id for record in report.discarded}

    assert "semidirect-zero-connection-control" in discarded_ids
    assert "sphere-zero-flow-zero-connection-control" in discarded_ids
    assert "scaled-sphere-zero-flow-zero-connection-control" in discarded_ids
    assert "sphere-s-cross-s-xx-heisenberg-shaped-candidate" in discarded_ids
    assert all(record.recommendation == "discard" for record in report.discarded)


def test_iterative_frontier_records_next_gate_gaps():
    report = run_iterative_discovery()

    for record in report.frontier:
        assert record.process_disposition == "frontier"
        assert record.recommendation in {"needs_human_review", "blocked"}
        assert record.next_action
        assert record.gate_gaps
        assert record.evidence_summary
        assert record.potential_status in {
            "promising_potential",
            "blocked_by_first_potential_gate",
            "blocked_by_recursive_nonlocal_tower",
            "formal_nonlocal_tower_validated",
            "formal_tower_downstream_gates_recorded",
            "blocked_by_missing_capability",
            "blocked_by_ansatz_obstruction",
            "needs_review",
            "validated_non_split_flow_equations",
            "density_matrix_pending",
            "nonlocal_covering_pending",
            "cohomology_pending",
            "batch_triage_pending",
        }


def test_iterative_baseline_freeze_can_leave_sxxx_as_promising_potential():
    report = run_iterative_discovery(DiscoveryIterationConfig(attempt_sxxx_ansatz=False))

    assert report.frontier[0].item_id == "sphere-s-cross-s-xxx-exploratory-candidate"
    assert report.frontier[0].potential_status == "promising_potential"


def test_iterative_serious_attempt_blocks_sxxx_and_advances_next_candidate():
    report = run_iterative_discovery()

    assert report.frontier[0].item_id == "scaled-sphere-unit-times-sxxxxx"
    sx = next(
        record
        for record in report.frontier
        if record.item_id == "sphere-s-cross-s-x-tangent-candidate"
    )
    non_split = next(
        record
        for record in report.frontier
        if record.item_id == "semidirect-non-split-product-deformation-probe"
    )
    sxxx = next(
        record
        for record in report.frontier
        if record.item_id == "sphere-s-cross-s-xxx-exploratory-candidate"
    )
    assert sx.recommendation == "needs_human_review"
    assert sx.potential_status == "formal_tower_downstream_gates_recorded"
    assert sx.connection_status == "validated_formal_infinite_nonlocal_tower"
    assert "downstream" in sx.potential_status
    assert non_split.potential_status == "validated_non_split_flow_equations"
    assert non_split.connection_status == "validated_non_split_flow_equations"
    assert sxxx.recommendation == "blocked"
    assert sxxx.potential_status == "blocked_by_ansatz_obstruction"
    assert any(record.lane == "DIS-003" for record in report.frontier)
    assert any(record.lane == "DIS-006" for record in report.frontier)


def test_iterative_config_can_disable_one_lane_and_limit_iterations():
    report = run_iterative_discovery(
        DiscoveryIterationConfig(
            max_iterations=1,
            include_dis001=False,
            include_dis003=False,
            include_dis004=False,
            include_dis005=False,
            include_dis006=False,
        )
    )

    assert len(report.iterations) == 1
    assert {record.lane for record in report.all_records} == {"DIS-002"}


def test_iterative_report_avoids_promotion_language():
    report = run_iterative_discovery()
    rendered = json.dumps(report.as_dict(), sort_keys=True).lower() + report.to_markdown().lower()

    assert all(term not in rendered for term in FORBIDDEN_PROMOTION_TERMS)


def test_write_iterative_discovery_report_emits_json_and_markdown(tmp_path):
    report = run_iterative_discovery()
    output_dir = tmp_path / "iter"

    written_path = write_iterative_discovery_report(report, output_dir)

    assert written_path == output_dir
    run_json = json.loads((output_dir / "run.json").read_text(encoding="utf-8"))
    assert run_json["run_id"] == "ITER-001"
    assert (output_dir / "run.md").read_text(encoding="utf-8").startswith(
        "# Discovery Process ITER-001"
    )


def test_write_iterative_discovery_report_refuses_overwrite_when_requested(tmp_path):
    report = run_iterative_discovery()
    output_dir = tmp_path / "iter"
    write_iterative_discovery_report(report, output_dir)

    try:
        write_iterative_discovery_report(report, output_dir, overwrite=False)
    except FileExistsError as exc:
        assert "Refusing to overwrite" in str(exc)
    else:
        raise AssertionError("Expected FileExistsError when overwrite is disabled")
