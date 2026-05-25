"""Conservative prior-art collision registry and classification helpers."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Sequence


class CandidateClassification(str, Enum):
    """Conservative candidate classes; none declares novelty automatically."""

    FAKE = "fake"
    KNOWN = "known"
    KNOWN_MECHANISM_NEW_PRESENTATION = "known_mechanism_new_presentation"
    KNOWN_HIERARCHY_NEW_REDUCTION = "known_hierarchy_new_reduction"
    NEW_PAIR_FOR_KNOWN_PDE = "new_pair_for_known_pde"
    NEW_SYSTEM_STRONG_LAX = "new_system_strong_lax"
    NEW_HIERARCHY = "new_hierarchy"
    NEEDS_HUMAN_REVIEW = "needs_human_review"


@dataclass(frozen=True)
class PriorArtFamily:
    """Known-family registry entry."""

    name: str
    fingerprints: tuple[str, ...]
    collision_notes: str


@dataclass(frozen=True)
class PriorArtCollisionReport:
    """Conservative collision report for a candidate."""

    candidate_name: str
    classification: CandidateClassification
    collisions: tuple[str, ...]
    checklist: tuple[str, ...]
    novelty_status: str = "unassessed"

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-compatible collision report."""
        return {
            "candidate_name": self.candidate_name,
            "classification": self.classification.value,
            "collisions": list(self.collisions),
            "checklist": list(self.checklist),
            "novelty_status": self.novelty_status,
        }


def default_prior_art_registry() -> tuple[PriorArtFamily, ...]:
    """Return the built-in conservative known-family registry."""
    return (
        PriorArtFamily(
            "AKNS / Zakharov-Shabat",
            ("akns", "sl2", "spectral-parameter"),
            "standard source of mKdV/NLS pairs",
        ),
        PriorArtFamily(
            "KdV and mKdV scalar hierarchies",
            ("mkdv", "kdv", "scalar-hierarchy"),
            "direct hierarchy collision zone",
        ),
        PriorArtFamily(
            "Nonlinear Schrodinger hierarchy",
            ("nls", "akns", "schrodinger"),
            "AKNS reduction collision zone",
        ),
        PriorArtFamily(
            "sine-Gordon and affine Toda systems",
            ("sine-gordon", "toda", "affine-toda"),
            "standard zero-curvature hierarchy collision zone",
        ),
        PriorArtFamily(
            "KP and Gelfand-Dickey hierarchies",
            ("kp", "gelfand-dickey", "pseudo-differential"),
            "scalar operator hierarchy collision zone",
        ),
        PriorArtFamily(
            "Drinfeld-Sokolov reductions",
            ("drinfeld-sokolov", "ds-reduction"),
            "graded Lie algebra reduction collision zone",
        ),
        PriorArtFamily(
            "Vector and matrix mKdV systems",
            ("vector-mkdv", "matrix-mkdv"),
            "possible multicomponent collision zone",
        ),
        PriorArtFamily(
            "Integrable couplings via semidirect products",
            ("integrable-coupling", "semidirect"),
            "common source of triangular or perturbative lifts",
        ),
        PriorArtFamily(
            "Nilpotent and perturbation extensions",
            ("nilpotent-lift", "jet-extension"),
            "known mechanism for coupled perturbation systems",
        ),
        PriorArtFamily(
            "Supersymmetric and graded extensions",
            ("supersymmetric", "graded", "super"),
            "graded extension collision zone",
        ),
        PriorArtFamily(
            "Nonlocal coverings and pseudopotentials",
            ("nonlocal", "covering", "pseudopotential"),
            "nonlocal Lax representation collision zone",
        ),
        PriorArtFamily(
            "Principal chiral model and Heisenberg ferromagnet families",
            ("principal-chiral", "heisenberg", "sphere"),
            "sphere and chiral-model collision zone",
        ),
        PriorArtFamily(
            "Coadjoint-orbit and symmetric-space hierarchies",
            ("coadjoint-orbit", "symmetric-space", "stiefel"),
            "geometry-constrained hierarchy collision zone",
        ),
    )


def nilpotent_collision_checklist() -> tuple[str, ...]:
    """Return the checklist for nilpotent/jet/integrable-coupling constructions."""
    return (
        "Projection recovers a known scalar mKdV AKNS pair.",
        "Construction is a nilpotent or jet lift of a known pair.",
        "Field content includes perturbation equations around the scalar flow.",
        "Spectral curve may repeat known scalar data.",
        "Gauge and cyclic-basis checks remain required before any external claim.",
    )


def classify_candidate(
    candidate_name: str,
    metadata: Mapping[str, object] | None = None,
    registry: Sequence[PriorArtFamily] | None = None,
) -> PriorArtCollisionReport:
    """Classify conservatively from explicit metadata and known collision zones."""
    metadata = metadata or {}
    registry = tuple(registry or default_prior_art_registry())
    lowered_name = candidate_name.lower()
    collisions: list[str] = []
    checklist: tuple[str, ...] = ()

    if metadata.get("fake_pair"):
        return PriorArtCollisionReport(
            candidate_name=candidate_name,
            classification=CandidateClassification.FAKE,
            collisions=("Constructed or detected fake/trivial pair.",),
            checklist=("Discard unless used as a pipeline control.",),
            novelty_status="collision_detected",
        )

    if metadata.get("known_heisenberg_zcr"):
        collisions.extend(family.name for family in registry if "heisenberg" in family.fingerprints)
        collisions.extend(family.name for family in registry if "akns" in family.fingerprints)
        return PriorArtCollisionReport(
            candidate_name=candidate_name,
            classification=CandidateClassification.KNOWN,
            collisions=tuple(dict.fromkeys(collisions)),
            checklist=(
                "Validated ZCR matches a Heisenberg/symmetric-space known-family template.",
                "Sphere-valued cross-product flow is tangent by construction.",
                "Record gauge, cyclic, and spectral evidence for audit only.",
                "Recommendation remains discard for discovery purposes.",
            ),
            novelty_status="collision_detected",
        )

    if metadata.get("field_rescaling_control"):
        return PriorArtCollisionReport(
            candidate_name=candidate_name,
            classification=CandidateClassification.FAKE,
            collisions=("Field-rescaling parameter control.",),
            checklist=("Discard unless used as a parameter-removal control.",),
            novelty_status="collision_detected",
        )

    if metadata.get("semidirect_lift"):
        collisions.extend(family.name for family in registry if "integrable-coupling" in family.fingerprints)
        collisions.extend(family.name for family in registry if "nilpotent-lift" in family.fingerprints)
        collisions.extend(family.name for family in registry if "mkdv" in family.fingerprints)
        return PriorArtCollisionReport(
            candidate_name=candidate_name,
            classification=CandidateClassification.KNOWN_MECHANISM_NEW_PRESENTATION,
            collisions=tuple(dict.fromkeys(collisions)),
            checklist=(
                "Construction is a semidirect or perturbative lift of a known mKdV pair.",
                "Projection recovers the scalar mKdV AKNS pair.",
                "Treat as calibration or known-mechanism evidence unless extra structure survives.",
                "Gauge, cyclic, conservation, and collision evidence remain audit requirements.",
            ),
            novelty_status="collision_detected",
        )

    if metadata.get("non_split_semidirect_probe"):
        collisions.extend(family.name for family in registry if "integrable-coupling" in family.fingerprints)
        collisions.extend(family.name for family in registry if "nilpotent-lift" in family.fingerprints)
        return PriorArtCollisionReport(
            candidate_name=candidate_name,
            classification=CandidateClassification.NEEDS_HUMAN_REVIEW,
            collisions=tuple(dict.fromkeys(collisions)),
            checklist=(
                "Non-split product data must be checked against integrable-coupling families.",
                "Do not promote without a solved zero-curvature proof and structure evidence.",
                "Known integrable-coupling and perturbation families are collision zones.",
            ),
            novelty_status="needs_human_review",
        )

    if metadata.get("nilpotent_lift") or ("nilpotent" in lowered_name and "mkdv" in lowered_name):
        collisions.extend(family.name for family in registry if "nilpotent-lift" in family.fingerprints)
        collisions.extend(family.name for family in registry if "mkdv" in family.fingerprints)
        checklist = nilpotent_collision_checklist()
        return PriorArtCollisionReport(
            candidate_name=candidate_name,
            classification=CandidateClassification.KNOWN_MECHANISM_NEW_PRESENTATION,
            collisions=tuple(dict.fromkeys(collisions)),
            checklist=checklist,
            novelty_status="collision_detected",
        )

    if metadata.get("sphere_tangent_flow"):
        collisions.extend(family.name for family in registry if "sphere" in family.fingerprints)
        if metadata.get("heisenberg_template"):
            collisions.extend(family.name for family in registry if "heisenberg" in family.fingerprints)
            collisions.extend(family.name for family in registry if "akns" in family.fingerprints)
        zcr_note = (
            "Formal infinite nonlocal tower evidence requires human review against known coverings."
            if metadata.get("sx_formal_infinite_tower_zcr")
            else "No nontrivial zero-curvature representation has been validated here."
        )
        return PriorArtCollisionReport(
            candidate_name=candidate_name,
            classification=CandidateClassification.NEEDS_HUMAN_REVIEW,
            collisions=tuple(dict.fromkeys(collisions)),
            checklist=(
                "Sphere-valued cross-product flow is tangent by construction.",
                "Known Heisenberg ferromagnet and symmetric-space collisions must be checked.",
                zcr_note,
                "Do not promote without gauge, spectral, conservation, and collision evidence.",
            ),
            novelty_status="needs_human_review",
        )

    if metadata.get("density_matrix_flow"):
        collisions.extend(
            family.name
            for family in registry
            if "coadjoint-orbit" in family.fingerprints
            or "symmetric-space" in family.fingerprints
            or "nls" in family.fingerprints
        )
        return PriorArtCollisionReport(
            candidate_name=candidate_name,
            classification=CandidateClassification.NEEDS_HUMAN_REVIEW,
            collisions=tuple(dict.fromkeys(collisions)),
            checklist=(
                "Density-matrix commutator flows may collide with coadjoint-orbit systems.",
                "Isospectral and dissipative tangent terms require separate invariant checks.",
                "No external mathematical claim is available without full gate evidence.",
            ),
            novelty_status="needs_human_review",
        )

    if metadata.get("nonlocal_covering"):
        collisions.extend(family.name for family in registry if "nonlocal" in family.fingerprints)
        return PriorArtCollisionReport(
            candidate_name=candidate_name,
            classification=CandidateClassification.NEEDS_HUMAN_REVIEW,
            collisions=tuple(dict.fromkeys(collisions)),
            checklist=(
                "Nonlocal covering and pseudopotential collision zones must be checked.",
                "Local projection and gauge-removal evidence remain required.",
                "No nonlocal ZCR validation has been completed for this probe.",
            ),
            novelty_status="needs_human_review",
        )

    if metadata.get("cohomological_deformation"):
        collisions.extend(
            family.name
            for family in registry
            if "drinfeld-sokolov" in family.fingerprints
            or "integrable-coupling" in family.fingerprints
            or "akns" in family.fingerprints
        )
        return PriorArtCollisionReport(
            candidate_name=candidate_name,
            classification=CandidateClassification.NEEDS_HUMAN_REVIEW,
            collisions=tuple(dict.fromkeys(collisions)),
            checklist=(
                "Gauge coboundary and cocycle representatives must be separated.",
                "Known deformation and reduction families are active collision zones.",
                "No cohomology quotient computation has validated this probe.",
            ),
            novelty_status="needs_human_review",
        )

    return PriorArtCollisionReport(
        candidate_name=candidate_name,
        classification=CandidateClassification.NEEDS_HUMAN_REVIEW,
        collisions=(),
        checklist=("No automatic novelty claim; human prior-art review required.",),
        novelty_status="needs_human_review",
    )
