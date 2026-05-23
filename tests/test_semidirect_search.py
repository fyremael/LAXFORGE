import json

from laxforge.core.prior_art import CandidateClassification
from laxforge.search.semidirect import (
    SemidirectSearchConfig,
    run_semidirect_deformation_search,
    write_semidirect_discovery_run,
)


EXPECTED_CANDIDATE_NAMES = (
    "semidirect zero-connection control",
    "semidirect split nilpotent mKdV lift control",
    "semidirect rescaled perturbation parameter control",
    "semidirect non-split product deformation probe",
)


def test_semidirect_search_generates_fixed_candidate_set():
    report = run_semidirect_deformation_search()

    assert report.run_id == "DIS-001"
    assert tuple(candidate.name for candidate in report.candidates) == EXPECTED_CANDIDATE_NAMES


def test_every_semidirect_candidate_has_dossier_gates_and_recommendation():
    report = run_semidirect_deformation_search()
    required_gates = {
        "curvature_validation",
        "solve_status",
        "gauge_risk_score",
        "spectral_parameter_status",
        "conservation_evidence",
        "collision_classification",
        "recommendation",
    }

    for candidate in report.candidates:
        assert candidate.dossier is not None
        assert required_gates <= set(candidate.gate_summary)
        assert candidate.dossier.collision_report
        assert candidate.dossier.recommendation in {"discard", "needs_human_review"}
        assert candidate.failure_reasons


def test_split_nilpotent_semidirect_control_validates_known_flow_equations():
    candidate = run_semidirect_deformation_search().candidates[1]
    checks = candidate.evidence["checks"]

    assert candidate.dossier.classification == CandidateClassification.KNOWN_MECHANISM_NEW_PRESENTATION
    assert candidate.dossier.recommendation == "discard"
    assert candidate.connection_status == "validated_known_semidirect_zcr"
    assert candidate.evidence["validated_as_flow_equations"] is True
    assert all(checks.values())
    assert candidate.dossier.curvature_summary["matrix_shape"] == (2, 2)


def test_rescaled_parameter_control_is_discarded_as_fake():
    candidate = run_semidirect_deformation_search().candidates[2]

    assert candidate.dossier.classification == CandidateClassification.FAKE
    assert candidate.dossier.recommendation == "discard"
    assert candidate.evidence["rescaling_parameter_status"] == "removable"


def test_non_split_probe_constructs_non_split_curvature_evidence():
    candidate = run_semidirect_deformation_search().candidates[3]

    assert candidate.dossier.classification == CandidateClassification.NEEDS_HUMAN_REVIEW
    assert candidate.dossier.recommendation == "needs_human_review"
    assert candidate.connection_status == "constructed_non_split_curvature"
    assert candidate.solve_status == "residuals_unresolved_non_split_product"
    assert candidate.evidence["matrix_pair_constructed"] is True
    assert candidate.evidence["associative"] is True
    assert candidate.dossier.curvature_summary["basis_split_complete"] is True
    assert candidate.dossier.curvature_summary["curvature_terms_nonzero"] > 0
    assert "non-split multiplication table is implemented" in candidate.failure_reasons[0]


def test_semidirect_search_config_can_limit_orders():
    report = run_semidirect_deformation_search(SemidirectSearchConfig(max_order=1))

    assert tuple(candidate.order for candidate in report.candidates) == (0, 1, 1)


def test_semidirect_candidate_markdown_avoids_promotion_language():
    forbidden = ("novel", "publishable", "publication")

    for candidate in run_semidirect_deformation_search().candidates:
        markdown = candidate.to_markdown().lower()
        assert all(term not in markdown for term in forbidden)


def test_write_semidirect_discovery_run_emits_json_and_markdown(tmp_path):
    report = run_semidirect_deformation_search()
    output_dir = tmp_path / "dis001"

    written_path = write_semidirect_discovery_run(report, output_dir)

    assert written_path == output_dir
    run_json = json.loads((output_dir / "run.json").read_text(encoding="utf-8"))
    assert run_json["run_id"] == "DIS-001"
    assert (output_dir / "run.md").read_text(encoding="utf-8").startswith("# Discovery Run DIS-001")
    assert len(list((output_dir / "candidates").glob("*.json"))) == 4
    assert len(list((output_dir / "candidates").glob("*.md"))) == 4


def test_write_semidirect_discovery_run_refuses_overwrite_when_requested(tmp_path):
    report = run_semidirect_deformation_search()
    output_dir = tmp_path / "dis001"
    write_semidirect_discovery_run(report, output_dir)

    try:
        write_semidirect_discovery_run(report, output_dir, overwrite=False)
    except FileExistsError as exc:
        assert "Refusing to overwrite" in str(exc)
    else:
        raise AssertionError("Expected FileExistsError when overwrite is disabled")
