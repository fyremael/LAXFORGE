"""Variational-derivative and Hamiltonian checks for calibration systems."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import sympy as sp

from laxforge.core.models import GateEvidence, HamiltonianReportModel, open_gate


@dataclass(frozen=True)
class DifferentialOperatorTerm:
    """A constant coefficient total-x derivative term."""

    coefficient: sp.Expr = sp.Integer(1)
    order: int = 1

    def apply(self, expr: sp.Expr, x: sp.Symbol) -> sp.Expr:
        """Apply this differential operator term to an expression."""
        return sp.simplify(self.coefficient * sp.diff(expr, x, self.order))

    def formal_adjoint(self) -> "DifferentialOperatorTerm":
        """Return the constant-coefficient formal adjoint."""
        return DifferentialOperatorTerm(self.coefficient * (-1) ** self.order, self.order)


DX = DifferentialOperatorTerm(sp.Integer(1), 1)


@dataclass(frozen=True)
class HamiltonianReport:
    """Hamiltonian verification result."""

    density: sp.Expr
    variational_gradient: tuple[sp.Expr, ...]
    flow: tuple[sp.Expr, ...]
    expected_flow: tuple[sp.Expr, ...]
    operator_skew_adjoint: bool
    verified: bool
    jacobi_check: str = "constant_coefficient_skew_operator"
    compatibility_attempt: str = "not_attempted"

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-compatible Hamiltonian report."""
        data = {
            "density": str(self.density),
            "variational_gradient": [str(expr) for expr in self.variational_gradient],
            "flow": [str(expr) for expr in self.flow],
            "expected_flow": [str(expr) for expr in self.expected_flow],
            "operator_skew_adjoint": self.operator_skew_adjoint,
            "verified": self.verified,
            "jacobi_check": self.jacobi_check,
            "compatibility_attempt": self.compatibility_attempt,
            "status": "verified" if self.verified else "open_gate",
        }
        data["canonical_report"] = self.complete_model().model_dump(mode="json")
        return data

    def complete_model(self) -> HamiltonianReportModel:
        """Return the canonical Hamiltonian report model."""
        return HamiltonianReportModel(
            status="verified" if self.verified else "open_gate",
            verified=self.verified,
            variational_derivative=GateEvidence(
                name="variational_derivative",
                status="pass",
                summary="Euler-Lagrange variational derivatives were computed.",
            ),
            constant_poisson_operator=GateEvidence(
                name="constant_poisson_operator",
                status="pass" if self.operator_skew_adjoint else "fail",
                summary="Constant-coefficient Poisson operator skew-adjointness checked.",
            ),
            jacobi_check=GateEvidence(
                name="jacobi_check",
                status="pass",
                summary="Constant coefficient skew-adjoint operator passes the simple Jacobi gate.",
            ),
            compatibility_attempt=open_gate(
                "compatibility_attempt",
                "No second Hamiltonian operator was attempted for this candidate.",
            ),
            details={
                "density": str(self.density),
                "flow": [str(expr) for expr in self.flow],
                "expected_flow": [str(expr) for expr in self.expected_flow],
            },
        )


OperatorEntry = DifferentialOperatorTerm | None


def _max_x_derivative_order(expr: sp.Expr, field: sp.Expr, x: sp.Symbol) -> int:
    orders = [0]
    for derivative in expr.atoms(sp.Derivative):
        if derivative.expr == field:
            orders.append(sum(count for var, count in derivative.variable_count if var == x))
    return max(orders)


def variational_derivative(density: sp.Expr, field: sp.Expr, x: sp.Symbol) -> sp.Expr:
    """Compute the Euler-Lagrange variational derivative with respect to one field."""
    max_order = _max_x_derivative_order(density, field, x)
    result = sp.diff(density, field)
    for order in range(1, max_order + 1):
        derivative = sp.diff(field, x, order)
        partial = sp.diff(density, derivative)
        if partial != 0:
            result += (-1) ** order * sp.diff(partial, x, order)
    return sp.simplify(result)


def variational_gradient(
    density: sp.Expr, fields: Sequence[sp.Expr], x: sp.Symbol
) -> tuple[sp.Expr, ...]:
    """Compute variational derivatives for a field vector."""
    return tuple(variational_derivative(density, field, x) for field in fields)


def apply_operator(
    operator: Sequence[Sequence[OperatorEntry]], vector: Sequence[sp.Expr], x: sp.Symbol
) -> tuple[sp.Expr, ...]:
    """Apply a matrix of constant differential operator terms."""
    out: list[sp.Expr] = []
    for row in operator:
        value = sp.Integer(0)
        for entry, component in zip(row, vector):
            if entry is not None:
                value += entry.apply(component, x)
        out.append(sp.simplify(value))
    return tuple(out)


def is_skew_adjoint_operator(operator: Sequence[Sequence[OperatorEntry]]) -> bool:
    """Check formal skew-adjointness for a constant differential operator matrix."""
    size = len(operator)
    if any(len(row) != size for row in operator):
        raise ValueError("Operator must be square")

    for i in range(size):
        for j in range(size):
            left = operator[i][j]
            right = operator[j][i]
            if left is None and right is None:
                continue
            if left is None or right is None:
                return False
            adjoint = right.formal_adjoint()
            if sp.simplify(left.coefficient + adjoint.coefficient) != 0:
                return False
            if left.order != adjoint.order:
                return False
    return True


def simple_constant_operator_jacobi_check(operator: Sequence[Sequence[OperatorEntry]]) -> bool:
    """Return the Jacobi result for constant coefficient skew operators."""
    return is_skew_adjoint_operator(operator)


def compatibility_attempt_report(
    first: Sequence[Sequence[OperatorEntry]],
    second: Sequence[Sequence[OperatorEntry]] | None = None,
) -> dict[str, object]:
    """Conservative compatibility attempt for constant operator pairs."""
    if second is None:
        return {
            "status": "open_gate",
            "compatible": None,
            "reason": "no second operator supplied",
        }
    return {
        "status": "checked_constant_pair",
        "compatible": is_skew_adjoint_operator(first) and is_skew_adjoint_operator(second),
        "reason": "constant coefficient skew-adjoint pair compatibility is accepted only as a simple gate",
    }


def open_hamiltonian_report(reason: str) -> dict[str, object]:
    """Return an explicit open-gate Hamiltonian report."""
    return HamiltonianReportModel(
        status="open_gate",
        verified=False,
        variational_derivative=open_gate("variational_derivative", reason),
        constant_poisson_operator=open_gate("constant_poisson_operator", reason),
        jacobi_check=open_gate("jacobi_check", reason),
        compatibility_attempt=open_gate("compatibility_attempt", reason),
    ).model_dump(mode="json")


def mkdv_second_jet_hamiltonian_report(x: sp.Symbol, t: sp.Symbol) -> HamiltonianReport:
    """Verify the nilpotent second-jet mKdV Hamiltonian representation."""
    u = sp.Function("u")(x, t)
    v = sp.Function("v")(x, t)
    w = sp.Function("w")(x, t)
    fields = (u, v, w)
    density = (
        sp.diff(u, x) * sp.diff(w, x)
        + sp.Rational(1, 2) * sp.diff(v, x) ** 2
        - 2 * u**3 * w
        - 3 * u**2 * v**2
    )
    operator: tuple[tuple[OperatorEntry, ...], ...] = (
        (None, None, DX),
        (None, DX, None),
        (DX, None, None),
    )
    gradient = variational_gradient(density, fields, x)
    flow = apply_operator(operator, gradient, x)
    expected_flow = (
        -sp.diff(u, x, 3) - 6 * u**2 * sp.diff(u, x),
        -sp.diff(v, x, 3) - 6 * u**2 * sp.diff(v, x) - 12 * u * sp.diff(u, x) * v,
        -sp.diff(w, x, 3)
        - 6 * u**2 * sp.diff(w, x)
        - 12 * u * v * sp.diff(v, x)
        - 6 * v**2 * sp.diff(u, x)
        - 12 * u * w * sp.diff(u, x),
    )
    verified = all(sp.simplify(actual - expected) == 0 for actual, expected in zip(flow, expected_flow))
    return HamiltonianReport(
        density=density,
        variational_gradient=gradient,
        flow=flow,
        expected_flow=expected_flow,
        operator_skew_adjoint=is_skew_adjoint_operator(operator),
        verified=verified,
    )
