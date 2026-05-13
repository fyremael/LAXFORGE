from laxforge.core.dossier import build_mkdv_second_jet_dossier
from laxforge.core.prior_art import CandidateClassification, classify_candidate
from laxforge.search.controlled import run_sphere_tangent_projection_search


def test_second_jet_nilpotent_mkdv_classifies_as_known_mechanism():
    report = classify_candidate("second-jet nilpotent mKdV", metadata={"nilpotent_lift": True})

    assert report.classification == CandidateClassification.KNOWN_MECHANISM_NEW_PRESENTATION
    assert report.novelty_status == "collision_detected"
    assert any("Projection recovers" in item for item in report.checklist)


def test_mkdv_dossier_has_conservation_and_hamiltonian_evidence_without_novelty_claim():
    dossier = build_mkdv_second_jet_dossier()

    assert dossier.classification == CandidateClassification.KNOWN_MECHANISM_NEW_PRESENTATION
    assert dossier.conservation_report["num_conservation_laws_found"] >= 3
    assert dossier.hamiltonian_report["verified"]
    assert dossier.novelty_status == "collision_detected"


def test_controlled_discovery_run_records_discarded_fake_candidate():
    report = run_sphere_tangent_projection_search()
    candidate = report.candidates[0]

    assert report.run_id == "DIS-002-control"
    assert candidate.tangent_condition == 0
    assert candidate.dossier.classification == CandidateClassification.FAKE
    assert candidate.dossier.recommendation == "discard"
    assert candidate.failure_reasons
