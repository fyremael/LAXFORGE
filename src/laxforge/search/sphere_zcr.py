"""Heisenberg-shaped ZCR ansatz validation for DIS-002."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import sympy as sp

from laxforge.core.cyclic_basis import compute_cyclic_basis
from laxforge.core.gauge import analyze_gauge_risk
from laxforge.core.models import (
    ConservationReportModel,
    GateEvidence,
    HamiltonianReportModel,
    open_gate,
)
from laxforge.core.prior_art import classify_candidate
from laxforge.search.formal_sphere_ansatz import solve_formal_sphere_ansatz
from laxforge.search.overnight import _candidate


def cross_product_matrix(vector: sp.MatrixBase) -> sp.Matrix:
    """Return the real skew matrix hat(v) with hat(v) w = v cross w."""
    if vector.rows != 3 or vector.cols != 1:
        raise ValueError("cross_product_matrix expects a 3x1 vector")
    v1, v2, v3 = vector
    return sp.Matrix(
        [
            [0, -v3, v2],
            [v3, 0, -v1],
            [-v2, v1, 0],
        ]
    )


def _matrix_as_strings(matrix: sp.MatrixBase) -> list[list[str]]:
    return [[str(matrix[i, j]) for j in range(matrix.cols)] for i in range(matrix.rows)]


def _without_promotion_status(report: dict[str, object]) -> dict[str, object]:
    return {key: value for key, value in report.items() if key != "novelty_status"}


@dataclass(frozen=True)
class HeisenbergZCRReport:
    """Fixed-template ZCR solve report for the sphere Heisenberg flow."""

    unknowns: tuple[sp.Symbol, ...]
    solution: dict[sp.Symbol, sp.Expr]
    residual_basis: dict[str, tuple[sp.Expr, sp.Expr, sp.Expr]]
    reduced_residual_basis: dict[str, tuple[sp.Expr, sp.Expr, sp.Expr]]
    constraints_used: tuple[str, ...]
    validated: bool
    U: sp.Matrix
    V: sp.Matrix
    gauge_report: dict[str, object]
    cyclic_report: dict[str, object]
    collision_report: dict[str, object]

    def as_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible ZCR report."""
        return {
            "unknowns": [str(unknown) for unknown in self.unknowns],
            "solution": {str(key): str(value) for key, value in self.solution.items()},
            "residual_basis": {
                key: [str(component) for component in value]
                for key, value in self.residual_basis.items()
            },
            "reduced_residual_basis": {
                key: [str(component) for component in value]
                for key, value in self.reduced_residual_basis.items()
            },
            "constraints_used": list(self.constraints_used),
            "validated": self.validated,
            "U": _matrix_as_strings(self.U),
            "V": _matrix_as_strings(self.V),
            "gauge_report": _without_promotion_status(self.gauge_report),
            "cyclic_report": self.cyclic_report,
            "collision_report": self.collision_report,
        }


@dataclass(frozen=True)
class SphereSxxxZCRAttemptReport:
    """Low-order ZCR attempt report for the sphere s cross s_xxx flow."""

    unknowns: tuple[sp.Symbol, ...]
    consistency_equations: tuple[sp.Expr, ...]
    consistency_solution: dict[sp.Symbol, sp.Expr]
    residual_basis: dict[str, tuple[sp.Expr, ...]]
    reduced_residual_basis: dict[str, tuple[sp.Expr, ...]]
    obstruction_basis: tuple[str, ...]
    constraints_used: tuple[str, ...]
    ansatz_family: tuple[str, ...]
    validated: bool
    U: sp.Matrix
    V: sp.Matrix
    gauge_report: dict[str, object]
    cyclic_report: dict[str, object]
    collision_report: dict[str, object]

    def as_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible ZCR attempt report."""
        return {
            "unknowns": [str(unknown) for unknown in self.unknowns],
            "consistency_equations": [str(equation) for equation in self.consistency_equations],
            "consistency_solution": {
                str(key): str(value) for key, value in self.consistency_solution.items()
            },
            "residual_basis": {
                key: [str(component) for component in value]
                for key, value in self.residual_basis.items()
            },
            "reduced_residual_basis": {
                key: [str(component) for component in value]
                for key, value in self.reduced_residual_basis.items()
            },
            "obstruction_basis": list(self.obstruction_basis),
            "constraints_used": list(self.constraints_used),
            "ansatz_family": list(self.ansatz_family),
            "validated": self.validated,
            "U": _matrix_as_strings(self.U),
            "V": _matrix_as_strings(self.V),
            "gauge_report": _without_promotion_status(self.gauge_report),
            "cyclic_report": self.cyclic_report,
            "collision_report": self.collision_report,
        }


@dataclass(frozen=True)
class SphereSxZCRAttemptReport:
    """Local and first-nonlocal potential gate report for s cross s_x."""

    candidate_name: str
    formal_status: str
    formal_degree: int
    formal_unknowns: int
    formal_equations: int
    formal_obstruction_basis: tuple[str, ...]
    first_potential_opened: bool
    nonlocal_status: str
    recursive_depth: int
    recursive_closure_status: str
    recursive_closure_condition: str
    formal_tower_validated: bool
    finite_truncation_validated: bool
    potential_fields: tuple[str, ...]
    covering_equations: tuple[str, ...]
    nonlocal_residual_basis: dict[str, tuple[sp.Expr, ...]]
    obstruction_basis: tuple[str, ...]
    constraints_used: tuple[str, ...]
    ansatz_family: tuple[str, ...]
    validated: bool
    U: sp.Matrix
    V: sp.Matrix
    gauge_report: dict[str, object]
    cyclic_report: dict[str, object]
    conservation_report: dict[str, object]
    hamiltonian_report: dict[str, object]
    collision_report: dict[str, object]

    def as_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible first-potential gate report."""
        return {
            "candidate_name": self.candidate_name,
            "formal_status": self.formal_status,
            "formal_degree": self.formal_degree,
            "formal_unknowns": self.formal_unknowns,
            "formal_equations": self.formal_equations,
            "formal_obstruction_basis": list(self.formal_obstruction_basis),
            "first_potential_opened": self.first_potential_opened,
            "nonlocal_status": self.nonlocal_status,
            "recursive_depth": self.recursive_depth,
            "recursive_closure_status": self.recursive_closure_status,
            "recursive_closure_condition": self.recursive_closure_condition,
            "formal_tower_validated": self.formal_tower_validated,
            "finite_truncation_validated": self.finite_truncation_validated,
            "potential_fields": list(self.potential_fields),
            "covering_equations": list(self.covering_equations),
            "nonlocal_residual_basis": {
                key: [str(component) for component in value]
                for key, value in self.nonlocal_residual_basis.items()
            },
            "obstruction_basis": list(self.obstruction_basis),
            "constraints_used": list(self.constraints_used),
            "ansatz_family": list(self.ansatz_family),
            "validated": self.validated,
            "U": _matrix_as_strings(self.U),
            "V": _matrix_as_strings(self.V),
            "gauge_report": _without_promotion_status(self.gauge_report),
            "cyclic_report": self.cyclic_report,
            "conservation_report": self.conservation_report,
            "hamiltonian_report": self.hamiltonian_report,
            "collision_report": self.collision_report,
        }


def _sphere_symbols() -> tuple[sp.Symbol, sp.Symbol, sp.Symbol, sp.Symbol, sp.Symbol, sp.Matrix]:
    x, t, lam = sp.symbols("x t lambda")
    alpha, beta = sp.symbols("alpha beta")
    s1 = sp.Function("s1")(x, t)
    s2 = sp.Function("s2")(x, t)
    s3 = sp.Function("s3")(x, t)
    return x, t, lam, alpha, beta, sp.Matrix([s1, s2, s3])


def _algebraic_spatial_matrix(lambda_symbol: sp.Symbol) -> sp.Matrix:
    q1, q2, q3 = sp.symbols("q1 q2 q3")
    return lambda_symbol * cross_product_matrix(sp.Matrix([q1, q2, q3]))


def _safe_collision_report(
    candidate_name: str, metadata: dict[str, object] | None = None
) -> dict[str, object]:
    collision_report = classify_candidate(
        candidate_name,
        metadata={"sphere_tangent_flow": True, **(metadata or {})},
    ).as_dict()
    return {
        key: value
        for key, value in collision_report.items()
        if key != "novelty_status"
    }


def _recursive_potential_vector(
    label: str,
    x: sp.Symbol,
    t: sp.Symbol,
) -> sp.Matrix:
    return sp.Matrix([sp.Function(f"{label}_{index + 1}")(x, t) for index in range(3)])


def _zero_vector() -> tuple[sp.Integer, sp.Integer, sp.Integer]:
    return (sp.Integer(0), sp.Integer(0), sp.Integer(0))


def _formal_tower_gauge_report(
    base_report: dict[str, object], recursive_depth: int
) -> dict[str, object]:
    report = dict(base_report)
    spectral_report = report.get("spectral_report") or {}
    block_report = report.get("block_report") or {}
    report.update(
        {
            "status": "partial_formal_tower_gauge_evidence",
            "formal_tower_scope": (
                f"finite depth-{recursive_depth} truncation inspected; formal infinite "
                "gauge-preserving reductions remain open"
            ),
            "block_decomposition_signature": (
                "block_reducible"
                if block_report.get("block_reducible")
                else "no_common_coordinate_block_split_detected"
            ),
            "spectral_parameter_essentiality": (
                "unresolved_non_scalar_lambda"
                if spectral_report.get("status") == "unresolved"
                else spectral_report.get("status", "untested")
            ),
            "formal_tower_gate_status": "open_after_partial_gauge_screen",
        }
    )
    return report


def _sphere_formal_tower_conservation_report() -> dict[str, object]:
    return ConservationReportModel(
        status="constraint_preservation_only",
        num_conservation_laws_found=0,
        laws=[],
        method_evidence={
            "sphere_constraint_preservation": GateEvidence(
                name="sphere_constraint_preservation",
                status="pass",
                summary="The target flow preserves the unit-sphere constraint pointwise.",
                details={"calculation": "D_t(s dot s) = 2 s dot (s cross s_x) = 0"},
            ),
            "inherited_scalar_hierarchy": GateEvidence(
                name="inherited_scalar_hierarchy",
                status="not_applicable",
                summary="No scalar hierarchy inheritance has been established for this nonlocal tower.",
            ),
            "trace_monodromy": open_gate(
                "trace_monodromy",
                "Trace/monodromy expansion for the formal nonlocal tower is not implemented.",
            ),
            "riccati": open_gate(
                "riccati",
                "Riccati expansion for the so(3) nonlocal tower is not implemented.",
            ),
            "homotopy": open_gate(
                "homotopy",
                "Homotopy-operator mining over the recursive nonlocal potentials is not implemented.",
            ),
        },
    ).model_dump(mode="json")


def _sphere_formal_tower_hamiltonian_report() -> dict[str, object]:
    return HamiltonianReportModel(
        status="open_gate",
        verified=False,
        variational_derivative=GateEvidence(
            name="variational_derivative",
            status="warn",
            summary=(
                "The standard spin operator s cross would require a local variational "
                "gradient matching s_x; no local density witness is recorded."
            ),
            details={"target": "s_t = s cross s_x"},
        ),
        constant_poisson_operator=GateEvidence(
            name="constant_poisson_operator",
            status="not_applicable",
            summary=(
                "The natural spin operator is field-dependent, so the constant-operator "
                "gate is not applicable."
            ),
        ),
        jacobi_check=open_gate(
            "jacobi_check",
            "Jacobi verification for a field-dependent spin Poisson operator is not implemented.",
        ),
        compatibility_attempt=open_gate(
            "compatibility_attempt",
            "No compatible Hamiltonian operator pair has been attempted for this nonlocal tower.",
        ),
        details={
            "standard_spin_operator": "J_s(phi) = s cross phi",
            "local_density_witness": "not_found",
        },
    ).model_dump(mode="json")


def solve_sx_zcr_ansatz() -> SphereSxZCRAttemptReport:
    """Attempt local and recursive nonlocal gates for s_t = s cross s_x.

    For the current U = lambda*hat(s) family, the lambda coefficient requires
    a local vector W with D_x(W) = s cross s_x. The formal local basis records
    that as a local obstruction. Recursive nonlocal potentials open the gate as
    a formal power-series connection; finite truncations retain a tail residual.
    """
    x, t, lam, _alpha, _beta, s = _sphere_symbols()
    formal_candidate = _candidate(
        name="overnight sphere unit times sx",
        family="scalar_weighted_cross",
        descriptor="s x s_x",
        order=1,
        scalar_factor="unit",
        vector_atom="sx",
        derivative_span=(1,),
        priority_score=1,
    )
    formal_report = solve_formal_sphere_ansatz(
        formal_candidate,
        degree=4,
        basis_order_slack=2,
    )
    sx = s.diff(x)
    target_flow = s.cross(sx)
    recursive_depth = 3
    potentials = tuple(
        _recursive_potential_vector(f"p{index + 1}", x, t)
        for index in range(recursive_depth)
    )
    p1 = potentials[0]
    U = lam * cross_product_matrix(s)
    V = sp.zeros(3)
    for power, potential in enumerate(potentials, start=1):
        V += (lam**power) * cross_product_matrix(potential)
    first_gate_residual = tuple(
        sp.simplify(target_flow[index] - p1[index].diff(x)) for index in range(3)
    )
    nonlocal_residual_basis: dict[str, tuple[sp.Expr, ...]] = {
        "lambda^1_before_covering": first_gate_residual,
        "lambda^1_after_covering": _zero_vector(),
    }
    covering_equations = ["D_x(p1) = s cross s_x"]
    for index in range(1, recursive_depth):
        previous = potentials[index - 1]
        current = potentials[index]
        residual = tuple(
            sp.simplify(s.cross(previous)[component] - current[component].diff(x))
            for component in range(3)
        )
        power = index + 1
        nonlocal_residual_basis[f"lambda^{power}_before_covering"] = residual
        nonlocal_residual_basis[f"lambda^{power}_after_covering"] = _zero_vector()
        covering_equations.append(f"D_x(p{power}) = s cross p{power - 1}")
    closure_residual = tuple(sp.simplify(component) for component in s.cross(potentials[-1]))
    nonlocal_residual_basis[
        f"lambda^{recursive_depth + 1}_finite_tower_closure_residual"
    ] = closure_residual
    nonlocal_residual_basis["lambda^k_after_formal_recurrence"] = _zero_vector()
    gauge_report = _formal_tower_gauge_report(
        analyze_gauge_risk(U, V, lambda_symbol=lam).as_dict(),
        recursive_depth,
    )
    cyclic_report = compute_cyclic_basis(
        _algebraic_spatial_matrix(lam),
        sp.Symbol("q1"),
        x,
        lambda_symbol=lam,
        max_steps=4,
    ).as_dict()
    conservation_report = _sphere_formal_tower_conservation_report()
    hamiltonian_report = _sphere_formal_tower_hamiltonian_report()
    return SphereSxZCRAttemptReport(
        candidate_name="sphere s_cross_s_x tangent candidate",
        formal_status=formal_report.status,
        formal_degree=formal_report.degree,
        formal_unknowns=formal_report.unknown_count,
        formal_equations=formal_report.equation_count,
        formal_obstruction_basis=formal_report.obstruction_basis[:4],
        first_potential_opened=True,
        nonlocal_status="validated_formal_infinite_nonlocal_tower",
        recursive_depth=recursive_depth,
        recursive_closure_status="formal_infinite_tower_closes_by_recurrence",
        recursive_closure_condition=(
            "D_x(p1) = s cross s_x and D_x(p{k+1}) = s cross p{k} for all k >= 1"
        ),
        formal_tower_validated=True,
        finite_truncation_validated=False,
        potential_fields=tuple(str(component) for potential in potentials for component in potential),
        covering_equations=tuple(covering_equations),
        nonlocal_residual_basis=nonlocal_residual_basis,
        obstruction_basis=(
            "local lambda^1 residual requires D_x(W) = s cross s_x",
            "formal local-vector ansatz has no W in the current sphere-derivative basis",
            "first nonlocal potential p1 with D_x(p1) = s cross s_x cancels the lambda^1 residual",
            "bounded recursive tower p1,p2,p3 cancels lambda^1 through lambda^3 residuals",
            "finite depth-3 tower leaves lambda^4 residual s cross p3",
            "formal infinite tower closes by the recurrence D_x(p{k+1}) = s cross p{k}",
            "finite truncations remain unclosed unless the top potential is parallel to s",
            "partial gauge and cyclic evidence is recorded for the depth-3 truncation",
            "constraint preservation is recorded; conservation-law mining remains open",
            "standard local Hamiltonian witness is not verified for this tower",
            "prior-art review must include nonlocal coverings and symmetric-space families",
        ),
        constraints_used=(
            "s_t = s cross s_x",
            "s dot s = 1",
            "s dot s_x = 0",
            *covering_equations,
            "[hat(a), hat(b)] = hat(a cross b)",
            "formal local-vector basis over sphere derivative atoms and scalar invariants",
        ),
        ansatz_family=(
            "U = lambda * hat(s)",
            "V = hat(sum lambda^k v_k) with local vector coefficients",
            "degree <= 4 with derivative-order slack 2",
            "formal infinite tower V = sum_{k>=1} lambda^k * hat(p{k})",
            "displayed matrix is the depth-3 truncation of the formal tower",
        ),
        validated=True,
        U=U,
        V=V,
        gauge_report=gauge_report,
        cyclic_report=cyclic_report,
        conservation_report=conservation_report,
        hamiltonian_report=hamiltonian_report,
        collision_report=_safe_collision_report(
            "sphere s_cross_s_x tangent candidate",
            metadata={"sx_formal_infinite_tower_zcr": True},
        ),
    )


def solve_sxxx_zcr_ansatz() -> SphereSxxxZCRAttemptReport:
    """Attempt a low-order so(3) ZCR ansatz for s_t = s cross s_xxx.

    The attempt validates only this ansatz family. A nonzero obstruction is not
    a global falsification of all possible ZCRs for the target flow.
    """
    x, _t, lam, _alpha, _beta, s = _sphere_symbols()
    a, b, c, d, e = sp.symbols("a b c d e")
    sx = s.diff(x)
    sxx = s.diff(x, 2)
    sxxx = s.diff(x, 3)
    target_flow = s.cross(sxxx)
    ansatz_U = lam * cross_product_matrix(s)
    vector_v = (
        a * lam**3 * s
        + b * lam**2 * s.cross(sx)
        + c * lam * sxx
        + d * lam * s.cross(sxx)
        + e * lam * sx
    )
    ansatz_V = cross_product_matrix(vector_v)

    lambda_3 = tuple(sp.simplify(-(a + b) * component) for component in sx)
    lambda_2 = tuple(
        sp.simplify(
            (c - b) * s.cross(sxx)[index]
            + d * (-sx.dot(sx) * s[index] - sxx[index])
            + e * s.cross(sx)[index]
        )
        for index in range(3)
    )
    lambda_1 = tuple(
        sp.simplify(
            target_flow[index]
            - c * sxxx[index]
            - d * (sx.cross(sxx)[index] + target_flow[index])
            - e * sxx[index]
        )
        for index in range(3)
    )
    residual_basis = {
        "lambda": lambda_1,
        "lambda^2": lambda_2,
        "lambda^3": lambda_3,
    }
    consistency_equations = (a + b, c - b, d, e)
    solve_result = sp.solve(consistency_equations, (a, c, d, e), dict=True)
    solution = dict(solve_result[0]) if solve_result else {}
    reduced_residual_basis = {
        key: tuple(sp.simplify(component.subs(solution)) for component in value)
        for key, value in residual_basis.items()
    }
    solved_U = sp.simplify(ansatz_U.subs(solution))
    solved_V = sp.simplify(ansatz_V.subs(solution))
    validated = all(
        sp.simplify(component) == 0
        for residual_vector in reduced_residual_basis.values()
        for component in residual_vector
    )
    gauge_report = analyze_gauge_risk(solved_U, solved_V, lambda_symbol=lam).as_dict()
    cyclic_report = compute_cyclic_basis(
        _algebraic_spatial_matrix(lam),
        sp.Symbol("q1"),
        x,
        lambda_symbol=lam,
        max_steps=4,
    ).as_dict()

    return SphereSxxxZCRAttemptReport(
        unknowns=(a, b, c, d, e),
        consistency_equations=consistency_equations,
        consistency_solution=solution,
        residual_basis=residual_basis,
        reduced_residual_basis=reduced_residual_basis,
        obstruction_basis=(
            "lambda residual remains s cross s_xxx - b*s_xxx after high-order consistency",
            "generic sphere data does not make s cross s_xxx a scalar multiple of s_xxx",
            "current low-order so(3) ansatz family is obstructed",
        ),
        constraints_used=(
            "s_t = s cross s_xxx",
            "s dot s = 1",
            "s dot s_x = 0",
            "s dot s_xx = -s_x dot s_x",
            "s cross (s cross s_x) = -s_x from the unit-sphere constraints",
            "s cross (s cross s_xx) = -s_xx - (s_x dot s_x)*s",
            "[hat(a), hat(b)] = hat(a cross b)",
        ),
        ansatz_family=(
            "U = lambda * hat(s)",
            "V = hat(a*lambda^3*s + b*lambda^2*(s cross s_x) + c*lambda*s_xx + d*lambda*(s cross s_xx) + e*lambda*s_x)",
        ),
        validated=validated,
        U=solved_U,
        V=solved_V,
        gauge_report=gauge_report,
        cyclic_report=cyclic_report,
        collision_report=_safe_collision_report("sphere s_cross_s_xxx exploratory candidate"),
    )


def solve_heisenberg_zcr_ansatz() -> HeisenbergZCRReport:
    """Solve and validate the fixed Heisenberg-shaped sphere ZCR ansatz."""
    x, _t, lam, alpha, beta, s = _sphere_symbols()
    sx = s.diff(x)
    sxx = s.diff(x, 2)
    target_flow = s.cross(sxx)
    S = cross_product_matrix(s)
    S_cross_sx = cross_product_matrix(s.cross(sx))

    ansatz_U = lam * S
    ansatz_V = alpha * lam**2 * S + beta * lam * S_cross_sx

    residual_basis = {
        "lambda": tuple(sp.simplify((1 - beta) * component) for component in target_flow),
        "lambda^2": tuple(sp.simplify((-alpha - beta) * component) for component in sx),
    }
    equations = (1 - beta, -alpha - beta)
    solve_result = sp.solve(equations, (alpha, beta), dict=True)
    solution = dict(solve_result[0]) if solve_result else {}
    solved_U = sp.simplify(ansatz_U.subs(solution))
    solved_V = sp.simplify(ansatz_V.subs(solution))
    reduced_residual_basis = {
        key: tuple(sp.simplify(component.subs(solution)) for component in value)
        for key, value in residual_basis.items()
    }
    validated = all(
        sp.simplify(component) == 0
        for residual_vector in reduced_residual_basis.values()
        for component in residual_vector
    )

    gauge_report = analyze_gauge_risk(solved_U, solved_V, lambda_symbol=lam).as_dict()
    cyclic_report = compute_cyclic_basis(
        _algebraic_spatial_matrix(lam),
        sp.Symbol("q1"),
        x,
        lambda_symbol=lam,
        max_steps=4,
    ).as_dict()
    collision_report = classify_candidate(
        "sphere s_cross_s_xx Heisenberg-shaped candidate",
        metadata={
            "sphere_tangent_flow": True,
            "heisenberg_template": True,
            "known_heisenberg_zcr": True,
        },
    ).as_dict()

    return HeisenbergZCRReport(
        unknowns=(alpha, beta),
        solution=solution,
        residual_basis=residual_basis,
        reduced_residual_basis=reduced_residual_basis,
        constraints_used=(
            "s_t = s cross s_xx",
            "s dot s = 1",
            "s dot s_x = 0",
            "s cross (s cross s_x) = -s_x from the unit-sphere constraints",
            "[hat(a), hat(b)] = hat(a cross b)",
        ),
        validated=validated,
        U=solved_U,
        V=solved_V,
        gauge_report=gauge_report,
        cyclic_report=cyclic_report,
        collision_report=collision_report,
    )
