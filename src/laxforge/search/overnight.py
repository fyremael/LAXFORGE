"""Wide deterministic overnight-style candidate triage."""

from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import sympy as sp

from laxforge.core.dossier import CandidateDossier
from laxforge.core.prior_art import classify_candidate


DERIVATIVE_ATOMS: tuple[tuple[str, str, int], ...] = (
    ("sx", "s_x", 1),
    ("sxx", "s_xx", 2),
    ("sxxx", "s_xxx", 3),
    ("sxxxx", "s_xxxx", 4),
    ("sxxxxx", "s_xxxxx", 5),
    ("sxxxxxx", "s_xxxxxx", 6),
    ("sxxxxxxx", "s_xxxxxxx", 7),
)

ENERGY_SUMS: tuple[tuple[str, str, int, int], ...] = (
    ("energy_12", "<s_x,s_x> + <s_xx,s_xx>", 2, 2),
    ("energy_23", "<s_xx,s_xx> + <s_xxx,s_xxx>", 3, 3),
    ("energy_34", "<s_xxx,s_xxx> + <s_xxxx,s_xxxx>", 4, 4),
    ("mixed_energy_13", "<s_x,s_xxx> + <s_xx,s_xx>", 3, 3),
)


@dataclass(frozen=True)
class OvernightSearchConfig:
    """Configuration for a wide deterministic evidence pass."""

    target_count: int = 1024
    action_queue_limit: int = 80
    include_zero_control: bool = True
    max_derivative_order: int = 7


@dataclass(frozen=True)
class OvernightCandidate:
    """One candidate descriptor from the wide overnight pass."""

    name: str
    family: str
    descriptor: str
    order: int
    scalar_factor: str
    vector_atom: str
    derivative_span: tuple[int, ...]
    tangent_condition: sp.Expr
    tangent_status: str
    connection_status: str
    gate_summary: dict[str, Any]
    dossier: CandidateDossier
    failure_reasons: tuple[str, ...]
    priority_score: int
    audit_surprisal: dict[str, object]

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-compatible candidate record."""
        dossier = self.dossier.as_dict()
        dossier.pop("novelty_status", None)
        collision_report = dict(dossier.get("collision_report") or {})
        collision_report.pop("novelty_status", None)
        dossier["collision_report"] = collision_report
        return {
            "name": self.name,
            "family": self.family,
            "descriptor": self.descriptor,
            "order": self.order,
            "scalar_factor": self.scalar_factor,
            "vector_atom": self.vector_atom,
            "derivative_span": list(self.derivative_span),
            "tangent_condition": str(self.tangent_condition),
            "tangent_status": self.tangent_status,
            "connection_status": self.connection_status,
            "gate_summary": self.gate_summary,
            "dossier": dossier,
            "failure_reasons": list(self.failure_reasons),
            "priority_score": self.priority_score,
            "audit_surprisal": self.audit_surprisal,
        }

    def to_markdown(self) -> str:
        """Render a compact candidate audit note."""
        lines = [
            f"# Candidate: {self.name}",
            "",
            f"- Family: `{self.family}`",
            f"- Descriptor: `{self.descriptor}`",
            f"- Classification: `{self.dossier.classification.value}`",
            f"- Recommendation: `{self.dossier.recommendation}`",
            f"- Order: {self.order}",
            f"- Tangent status: `{self.tangent_status}`",
            f"- Connection status: `{self.connection_status}`",
            f"- Priority score: {self.priority_score}",
            f"- Audit surprisal: {self.audit_surprisal['score']}",
            "",
            "## Gates",
            "",
        ]
        for key in sorted(self.gate_summary):
            lines.append(f"- `{key}`: `{self.gate_summary[key]}`")
        lines.extend(["", "## Failure Reasons", ""])
        lines.extend(f"- {reason}" for reason in self.failure_reasons)
        return "\n".join(lines).rstrip() + "\n"


@dataclass(frozen=True)
class OvernightSearchReport:
    """Structured report for an overnight-style wide search."""

    run_id: str
    title: str
    status: str
    candidates: tuple[OvernightCandidate, ...]
    action_queue: tuple[OvernightCandidate, ...]
    family_counts: dict[str, int]
    order_counts: dict[str, int]
    recommendation_counts: dict[str, int]
    gate_counts: dict[str, dict[str, int]]
    analysis_notes: tuple[str, ...]
    next_actions: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-compatible report."""
        return {
            "run_id": self.run_id,
            "title": self.title,
            "status": self.status,
            "candidate_count": len(self.candidates),
            "action_queue_count": len(self.action_queue),
            "candidates": [candidate.as_dict() for candidate in self.candidates],
            "action_queue": [candidate.as_dict() for candidate in self.action_queue],
            "family_counts": dict(self.family_counts),
            "order_counts": dict(self.order_counts),
            "recommendation_counts": dict(self.recommendation_counts),
            "gate_counts": self.gate_counts,
            "analysis_notes": list(self.analysis_notes),
            "next_actions": list(self.next_actions),
        }

    def to_markdown(self) -> str:
        """Render the report as Markdown."""
        lines = [
            f"# {self.title}",
            "",
            f"- Run ID: `{self.run_id}`",
            f"- Status: `{self.status}`",
            f"- Candidates: {len(self.candidates)}",
            f"- Action queue: {len(self.action_queue)}",
            "",
            "## Analysis",
            "",
        ]
        lines.extend(f"- {note}" for note in self.analysis_notes)
        lines.extend(
            [
                "",
                "## Family Counts",
                "",
                "| Family | Count |",
                "|---|---:|",
            ]
        )
        for family, count in self.family_counts.items():
            lines.append(f"| `{family}` | {count} |")
        lines.extend(
            [
                "",
                "## Top Action Queue",
                "",
                "| Candidate | Family | Order | Score | Status |",
                "|---|---|---:|---:|---|",
            ]
        )
        for candidate in self.action_queue[:25]:
            lines.append(
                "| "
                f"{candidate.name} | "
                f"`{candidate.family}` | "
                f"{candidate.order} | "
                f"{candidate.priority_score} | "
                f"`{candidate.connection_status}` |"
            )
        lines.extend(["", "## Next Actions", ""])
        lines.extend(f"- {action}" for action in self.next_actions)
        return "\n".join(lines).rstrip() + "\n"


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def _derivative_atom_name(order: int) -> str:
    return "s" + ("x" * order)


def _derivative_atom_expr(order: int) -> str:
    return "s_" + ("x" * order)


def _derivative_atoms(max_order: int) -> tuple[tuple[str, str, int], ...]:
    if max_order <= len(DERIVATIVE_ATOMS):
        return DERIVATIVE_ATOMS[:max_order]
    atoms = list(DERIVATIVE_ATOMS)
    for order in range(len(DERIVATIVE_ATOMS) + 1, max_order + 1):
        atoms.append((_derivative_atom_name(order), _derivative_atom_expr(order), order))
    return tuple(atoms)


def _scalar_factors(max_order: int) -> tuple[tuple[str, str, int, int], ...]:
    factors: list[tuple[str, str, int, int]] = [("unit", "1", 0, 0)]
    scalar_atoms = _derivative_atoms(max_order)[:6]
    for left_key, left_expr, left_order in scalar_atoms:
        for right_key, right_expr, right_order in scalar_atoms:
            if right_order < left_order:
                continue
            order = max(left_order, right_order)
            if order <= max_order:
                factors.append(
                    (
                        f"ip_{left_key}_{right_key}",
                        f"<{left_expr},{right_expr}>",
                        order,
                        left_order + right_order,
                    )
                )
    factors.extend(factor for factor in ENERGY_SUMS if factor[2] <= max_order)
    return tuple(factors)


def _vector_atoms(max_order: int) -> tuple[tuple[str, str, int, tuple[int, ...], int], ...]:
    atoms: list[tuple[str, str, int, tuple[int, ...], int]] = []
    derivative_atoms = _derivative_atoms(max_order)
    for key, expr, order in derivative_atoms:
        if order <= max_order:
            atoms.append((key, expr, order, (order,), 1))
    for left_key, left_expr, left_order in derivative_atoms:
        for right_key, right_expr, right_order in derivative_atoms:
            if right_order <= left_order:
                continue
            order = max(left_order, right_order)
            if order <= max_order:
                atoms.append(
                    (
                        f"{left_key}_cross_{right_key}",
                        f"{left_expr} x {right_expr}",
                        order,
                        (left_order, right_order),
                        2,
                    )
                )
    return tuple(atoms)


def _priority(
    family: str,
    order: int,
    scalar_complexity: int,
    vector_complexity: int,
    derivative_span: tuple[int, ...],
) -> int:
    span_width = max(derivative_span) - min(derivative_span) if derivative_span else 0
    family_bonus = {
        "scalar_weighted_cross": 6,
        "two_atom_blend": 9,
        "cross_atom_blend": 12,
        "energy_gradient_blend": 10,
    }.get(family, 4)
    return (
        22
        + min(order * 4, 32)
        + min(scalar_complexity, 10)
        + vector_complexity * 3
        + span_width
        + family_bonus
    )


def _audit_surprisal(
    family: str,
    order: int,
    priority_score: int,
    scalar_factor: str,
    vector_atom: str,
    fake_pair: bool,
) -> dict[str, object]:
    if fake_pair:
        return {
            "score": 4,
            "band": "control",
            "drivers": ["zero-control baseline", "discard recommendation"],
        }
    score = 20 + min(priority_score, 55)
    drivers = ["tangent construction", "open ZCR gate"]
    if order >= 6:
        score += 8
        drivers.append("high derivative order")
    if "cross" in vector_atom:
        score += 7
        drivers.append("nested cross-product vector atom")
    if scalar_factor != "unit":
        score += 4
        drivers.append("nonconstant scalar weighting")
    if family != "scalar_weighted_cross":
        score += 5
        drivers.append("blend family")
    score = max(4, min(94, score))
    band = "escalate" if score >= 78 else "inspect" if score >= 55 else "watch"
    return {"score": score, "band": band, "drivers": drivers}


def _curvature_summary(status: str) -> dict[str, object]:
    if status == "validated_zero_control":
        return {
            "curvature_residual_zero": True,
            "curvature_terms_total": 0,
            "curvature_terms_nonzero": 0,
            "basis_split_complete": True,
            "status": status,
        }
    return {
        "curvature_residual_zero": False,
        "curvature_terms_total": 0,
        "curvature_terms_nonzero": None,
        "basis_split_complete": False,
        "status": status,
        "reason": "overnight triage records descriptors before constructing matrix pairs",
    }


def _gauge_report() -> dict[str, object]:
    return {
        "gauge_risk_score": None,
        "status": "not_attempted",
        "spectral_report": {"status": "unresolved"},
        "reason": "no matrix pair constructed in overnight triage pass",
    }


def _candidate(
    *,
    name: str,
    family: str,
    descriptor: str,
    order: int,
    scalar_factor: str,
    vector_atom: str,
    derivative_span: tuple[int, ...],
    priority_score: int,
    fake_pair: bool = False,
) -> OvernightCandidate:
    metadata = {"fake_pair": fake_pair} if fake_pair else {"sphere_tangent_flow": True}
    collision_report = classify_candidate(name, metadata=metadata)
    recommendation = "discard" if fake_pair else "needs_human_review"
    connection_status = "validated_zero_control" if fake_pair else "not_constructed_overnight_triage"
    tangent_status = "zero_control" if fake_pair else "tangent"
    tangent_condition = sp.Integer(0)
    failure_reasons = (
        (
            "zero flow and zero connection are retained only as a run control",
            "control is classified fake and recommended discard",
            "no spectral, gauge, cyclic, conservation, or Hamiltonian evidence is present",
        )
        if fake_pair
        else (
            "flow is tangent by cross-product construction",
            "zero-curvature matrix pair has not been constructed in the overnight pass",
            "spectral, gauge, cyclic, conservation, and Hamiltonian gates remain open",
            "sphere, Heisenberg, and symmetric-space collision checks remain active",
        )
    )
    audit_surprisal = _audit_surprisal(
        family,
        order,
        priority_score,
        scalar_factor,
        vector_atom,
        fake_pair,
    )
    gate_summary = {
        "tangent_condition": str(tangent_condition),
        "tangent_status": tangent_status,
        "curvature_validation": connection_status,
        "gauge_risk_score": None,
        "spectral_parameter_status": "unresolved",
        "cyclic_fingerprint_status": "not_attempted",
        "conservation_evidence": "not_mined",
        "collision_classification": collision_report.classification.value,
        "recommendation": recommendation,
        "descriptor": descriptor,
        "priority_score": priority_score,
        "audit_surprisal": audit_surprisal["score"],
    }
    dossier = CandidateDossier(
        name=name,
        classification=collision_report.classification,
        curvature_summary=_curvature_summary(connection_status),
        gauge_report=_gauge_report(),
        collision_report=collision_report.as_dict(),
        conservation_report={"status": "not_mined", "num_conservation_laws_found": 0},
        hamiltonian_report={"status": "not_attempted", "verified": False},
        recommendation=recommendation,
        novelty_status=collision_report.novelty_status,
    )
    return OvernightCandidate(
        name=name,
        family=family,
        descriptor=descriptor,
        order=order,
        scalar_factor=scalar_factor,
        vector_atom=vector_atom,
        derivative_span=derivative_span,
        tangent_condition=tangent_condition,
        tangent_status=tangent_status,
        connection_status=connection_status,
        gate_summary=gate_summary,
        dossier=dossier,
        failure_reasons=failure_reasons,
        priority_score=priority_score,
        audit_surprisal=audit_surprisal,
    )


def _candidate_specs(
    config: OvernightSearchConfig,
) -> list[tuple[str, str, str, int, str, str, tuple[int, ...], int, int, int]]:
    scalar_factors = _scalar_factors(config.max_derivative_order)
    vector_atoms = _vector_atoms(config.max_derivative_order)
    specs: list[tuple[str, str, str, int, str, str, tuple[int, ...], int, int, int]] = []

    for scalar_key, scalar_expr, scalar_order, scalar_complexity in scalar_factors:
        for vector_key, vector_expr, vector_order, span, vector_complexity in vector_atoms:
            order = max(scalar_order, vector_order)
            name = f"overnight sphere {scalar_key} times {vector_key}"
            descriptor = f"s x (({scalar_expr}) {vector_expr})"
            priority = _priority(
                "scalar_weighted_cross",
                order,
                scalar_complexity,
                vector_complexity,
                span,
            )
            specs.append(
                (
                    name,
                    "scalar_weighted_cross",
                    descriptor,
                    order,
                    scalar_key,
                    vector_key,
                    span,
                    priority,
                    scalar_complexity,
                    vector_complexity,
                )
            )

    blend_scalars = scalar_factors[:12]
    for scalar_key, scalar_expr, scalar_order, scalar_complexity in blend_scalars:
        for left_index, (left_key, left_expr, left_order, left_span, left_complexity) in enumerate(
            vector_atoms
        ):
            for right_key, right_expr, right_order, right_span, right_complexity in vector_atoms[
                left_index + 1 :
            ]:
                order = max(scalar_order, left_order, right_order)
                span = tuple(sorted(set(left_span + right_span)))
                family = (
                    "cross_atom_blend"
                    if "cross" in left_key or "cross" in right_key
                    else "two_atom_blend"
                )
                name = f"overnight sphere {scalar_key} blend {left_key} {right_key}"
                descriptor = f"s x (({scalar_expr}) {left_expr} + {right_expr})"
                priority = _priority(
                    family,
                    order,
                    scalar_complexity,
                    left_complexity + right_complexity,
                    span,
                )
                specs.append(
                    (
                        name,
                        family,
                        descriptor,
                        order,
                        scalar_key,
                        f"{left_key}+{right_key}",
                        span,
                        priority,
                        scalar_complexity,
                        left_complexity + right_complexity,
                    )
                )

    return sorted(specs, key=lambda item: (-item[7], item[1], item[0]))


def _gate_counts(candidates: tuple[OvernightCandidate, ...]) -> dict[str, dict[str, int]]:
    counts = {
        "tangent": {"pass": 0, "warn": 0, "fail": 0},
        "curvature": {"pass": 0, "warn": 0, "fail": 0},
        "gauge": {"pass": 0, "warn": 0, "fail": 0},
        "spectral": {"pass": 0, "warn": 0, "fail": 0},
        "cyclic": {"pass": 0, "warn": 0, "fail": 0},
        "conservation": {"pass": 0, "warn": 0, "fail": 0},
        "collision": {"pass": 0, "warn": 0, "fail": 0},
    }
    for candidate in candidates:
        if candidate.tangent_status in {"tangent", "zero_control"}:
            counts["tangent"]["pass"] += 1
        else:
            counts["tangent"]["fail"] += 1

        if candidate.connection_status == "validated_zero_control":
            counts["curvature"]["pass"] += 1
            counts["collision"]["fail"] += 1
        else:
            counts["curvature"]["warn"] += 1
            counts["collision"]["warn"] += 1
        counts["gauge"]["warn"] += 1
        counts["spectral"]["warn"] += 1
        counts["cyclic"]["warn"] += 1
        counts["conservation"]["warn"] += 1
    return counts


def _analysis_notes(candidates: tuple[OvernightCandidate, ...]) -> tuple[str, ...]:
    review_count = sum(1 for candidate in candidates if candidate.dossier.recommendation == "needs_human_review")
    discard_count = sum(1 for candidate in candidates if candidate.dossier.recommendation == "discard")
    family_counts = Counter(candidate.family for candidate in candidates)
    top_family, top_family_count = family_counts.most_common(1)[0]
    high_order_count = sum(1 for candidate in candidates if candidate.order >= 6)
    cross_atom_count = sum(1 for candidate in candidates if "cross" in candidate.vector_atom)
    queue_orders = Counter(candidate.order for candidate in _action_queue(candidates, 25))
    queue_order_summary = ", ".join(f"order {order}: {count}" for order, count in sorted(queue_orders.items()))
    discard_phrase = "1 is a control or discard record" if discard_count == 1 else f"{discard_count} are controls or discard records"
    return (
        f"The run generated {len(candidates)} deterministic descriptors: {review_count} remain review-only and {discard_phrase}.",
        "Every non-control descriptor is tangent by construction because the target flow has the form s x A.",
        "The search is broad but shallow: no overnight descriptor has a constructed matrix pair, so curvature, spectral, gauge, cyclic, and conservation gates stay open.",
        f"The largest family is {top_family} with {top_family_count} records; this means the queue is dominated by blended tangent descriptors rather than solved ZCR evidence.",
        f"{high_order_count} records reach derivative order six or higher, and {cross_atom_count} records contain nested cross-product vector atoms.",
        f"The top 25 action-queue preview concentrates as {queue_order_summary}; solver sampling should cover family diversity instead of taking only the highest score.",
        "Known sphere and symmetric-space collision zones apply across the batch, so the correct interpretation is triage pressure, not promotion.",
    )


def _next_actions() -> tuple[str, ...]:
    return (
        "Run a small representative ZCR ansatz on the top queue, stratified by family and derivative order.",
        "Start with one scalar-weighted cross candidate and one cross-atom blend before expanding the solver family.",
        "For any candidate with a matrix pair, immediately run gauge-risk, cyclic-fingerprint, spectral, and collision checks.",
        "Discard candidates that reduce to controls, known-family templates, removable parameters, or unsupported ansatz obstructions.",
    )


def _action_queue(
    candidates: tuple[OvernightCandidate, ...],
    limit: int,
) -> tuple[OvernightCandidate, ...]:
    review_candidates = [
        candidate for candidate in candidates if candidate.dossier.recommendation == "needs_human_review"
    ]
    return tuple(
        sorted(
            review_candidates,
            key=lambda candidate: (
                -candidate.audit_surprisal["score"],
                -candidate.priority_score,
                -candidate.order,
                candidate.family,
                candidate.name,
            ),
        )[:limit]
    )


def run_overnight_search(
    config: OvernightSearchConfig | None = None,
) -> OvernightSearchReport:
    """Run the wide deterministic overnight-style candidate pass."""
    config = config or OvernightSearchConfig()
    if config.target_count < 500:
        raise ValueError("OVERNIGHT-001 requires at least 500 candidates")

    candidates: list[OvernightCandidate] = []
    if config.include_zero_control:
        candidates.append(
            _candidate(
                name="overnight sphere zero-flow zero-connection control",
                family="control",
                descriptor="s_t = 0 with U = V = 0",
                order=0,
                scalar_factor="unit",
                vector_atom="zero",
                derivative_span=(),
                priority_score=0,
                fake_pair=True,
            )
        )

    specs = _candidate_specs(config)
    family_order = ("cross_atom_blend", "scalar_weighted_cross", "two_atom_blend")
    buckets = {
        family: [spec for spec in specs if spec[1] == family]
        for family in family_order
    }
    bucket_index = {family: 0 for family in family_order}
    selected_specs = []
    while len(selected_specs) + len(candidates) < config.target_count:
        made_progress = False
        for family in family_order:
            index = bucket_index[family]
            if index < len(buckets[family]):
                selected_specs.append(buckets[family][index])
                bucket_index[family] = index + 1
                made_progress = True
                if len(selected_specs) + len(candidates) >= config.target_count:
                    break
        if not made_progress:
            break

    for spec in selected_specs:
        if len(candidates) >= config.target_count:
            break
        (
            name,
            family,
            descriptor,
            order,
            scalar_factor,
            vector_atom,
            derivative_span,
            priority_score,
            _scalar_complexity,
            _vector_complexity,
        ) = spec
        candidates.append(
            _candidate(
                name=name,
                family=family,
                descriptor=descriptor,
                order=order,
                scalar_factor=scalar_factor,
                vector_atom=vector_atom,
                derivative_span=derivative_span,
                priority_score=priority_score,
            )
        )

    if len(candidates) < config.target_count:
        raise RuntimeError(
            f"OVERNIGHT-001 generated only {len(candidates)} candidates; requested {config.target_count}"
        )

    candidate_tuple = tuple(candidates)
    action_queue = _action_queue(candidate_tuple, config.action_queue_limit)
    family_counts = dict(sorted(Counter(candidate.family for candidate in candidate_tuple).items()))
    order_counts = dict(
        sorted((str(order), count) for order, count in Counter(candidate.order for candidate in candidate_tuple).items())
    )
    recommendation_counts = dict(
        sorted(Counter(candidate.dossier.recommendation for candidate in candidate_tuple).items())
    )
    return OvernightSearchReport(
        run_id="OVERNIGHT-001",
        title="OVERNIGHT-001 Wide Candidate Evidence Run",
        status="frontier_active",
        candidates=candidate_tuple,
        action_queue=action_queue,
        family_counts=family_counts,
        order_counts=order_counts,
        recommendation_counts=recommendation_counts,
        gate_counts=_gate_counts(candidate_tuple),
        analysis_notes=_analysis_notes(candidate_tuple),
        next_actions=_next_actions(),
    )


def write_overnight_search_report(
    report: OvernightSearchReport,
    output_dir: str | Path,
    overwrite: bool = True,
) -> Path:
    """Write JSON and Markdown only when explicitly requested."""
    output_path = Path(output_dir)
    if output_path.exists() and any(output_path.iterdir()) and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing overnight output: {output_path}")
    output_path.mkdir(parents=True, exist_ok=True)
    (output_path / "overnight_search.json").write_text(
        json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_path / "overnight_search.md").write_text(report.to_markdown(), encoding="utf-8")
    return output_path


def write_overnight_data_js(
    path: str | Path,
    report: OvernightSearchReport | None = None,
    overwrite: bool = True,
) -> Path:
    """Write static web data for the overnight presentation."""
    output_path = Path(path)
    if output_path.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite overnight data: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps((report or run_overnight_search()).as_dict(), indent=2, sort_keys=True)
    output_path.write_text("window.LAXFORGE_OVERNIGHT_DATA = " + data + ";\n", encoding="utf-8")
    return output_path
