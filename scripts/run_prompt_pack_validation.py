#!/usr/bin/env python
"""Run prompt-pack completion smoke checks."""

from __future__ import annotations

from pprint import pprint

from laxforge.core.dossier import build_mkdv_second_jet_dossier
from laxforge.core.procedures import build_procedure_audit_report
from laxforge.core.solver import recover_scalar_mkdv_v_coefficients
from laxforge.search.bulk import run_scaled_candidate_search
from laxforge.search.full_scale import run_full_scale_search
from laxforge.search.iterative import run_iterative_discovery
from laxforge.search.overnight import run_overnight_search
from laxforge.search.run_matrix import (
    run_cohomological_deformation_search,
    run_density_matrix_search,
    run_nonlocal_covering_search,
)
from laxforge.search.serious_cycle import run_serious_cycle_001
from laxforge.search.sphere import run_sphere_low_order_search


def main() -> None:
    """Print a compact evidence summary for the implemented prompt pack."""
    solve_report = recover_scalar_mkdv_v_coefficients()
    dossier = build_mkdv_second_jet_dossier()
    discovery_report = run_sphere_low_order_search()
    density_report = run_density_matrix_search()
    nonlocal_report = run_nonlocal_covering_search()
    cohomology_report = run_cohomological_deformation_search()
    scaled_report = run_scaled_candidate_search()
    iterative_report = run_iterative_discovery()
    procedure_audit = build_procedure_audit_report(iterative_report)
    serious_cycle = run_serious_cycle_001()
    full_scale = run_full_scale_search()
    overnight = run_overnight_search()

    print("LAXFORGE prompt-pack validation")
    print("Scalar mKdV V recovery:")
    pprint(
        {
            "status": solve_report.status,
            "solved": solve_report.solved,
            "unknowns": solve_report.as_dict()["unknowns"],
            "solution": solve_report.as_dict()["solution"],
        }
    )
    print("\nSecond-jet mKdV dossier:")
    pprint(
        {
            "classification": dossier.classification.value,
            "conservation_laws": dossier.conservation_report["num_conservation_laws_found"]
            if dossier.conservation_report
            else 0,
            "hamiltonian_verified": dossier.hamiltonian_report["verified"]
            if dossier.hamiltonian_report
            else False,
        }
    )
    print("\nControlled discovery run:")
    pprint(
        {
            "run_id": discovery_report.run_id,
            "candidate_count": len(discovery_report.candidates),
            "discard_count": sum(
                1
                for candidate in discovery_report.candidates
                if candidate.dossier.recommendation == "discard"
            ),
            "review_count": sum(
                1
                for candidate in discovery_report.candidates
                if candidate.dossier.recommendation == "needs_human_review"
            ),
        }
    )
    print("\nRestored run-matrix discovery lanes:")
    pprint(
        {
            "density": (density_report.run_id, len(density_report.candidates)),
            "nonlocal": (nonlocal_report.run_id, len(nonlocal_report.candidates)),
            "cohomology": (cohomology_report.run_id, len(cohomology_report.candidates)),
        }
    )
    print("\nScaled discovery phase:")
    pprint(
        {
            "run_id": scaled_report.run_id,
            "candidate_count": len(scaled_report.candidates),
            "discard_count": sum(
                1
                for candidate in scaled_report.candidates
                if candidate.dossier.recommendation == "discard"
            ),
            "review_count": sum(
                1
                for candidate in scaled_report.candidates
                if candidate.dossier.recommendation == "needs_human_review"
            ),
        }
    )
    print("\nIterative discovery frontier:")
    frontier_preview = [
        {
            "name": record.name,
            "status": record.potential_status,
            "priority": record.priority,
        }
        for record in iterative_report.frontier[:12]
    ]
    if len(iterative_report.frontier) > 12:
        frontier_preview.append(
            {
                "name": f"{len(iterative_report.frontier) - 12} additional records retained",
                "status": "summary",
                "priority": 0,
            }
        )
    pprint(
        {
            "run_id": iterative_report.run_id,
            "process_status": iterative_report.process_status,
            "frontier_count": len(iterative_report.frontier),
            "frontier": frontier_preview,
        }
    )
    print("\nProcedure audit:")
    pprint(
        {
            "procedure_id": procedure_audit.procedure_id,
            "status": procedure_audit.status,
            "checks": len(procedure_audit.checks),
            "failures": procedure_audit.failure_count,
            "warnings": procedure_audit.warning_count,
        }
    )
    print("\nSerious cycle:")
    pprint(
        {
            "cycle_id": serious_cycle.cycle_id,
            "result_status": serious_cycle.result_status,
            "target": serious_cycle.target_item_id,
        }
    )
    print("\nFull-scale search:")
    pprint(
        {
            "run_id": full_scale.run_id,
            "status": full_scale.status,
            "generated_candidates": full_scale.generated_candidate_count,
            "frontier_count": full_scale.frontier_count,
            "action_queue": len(full_scale.action_queue),
        }
    )
    print("\nOvernight search:")
    pprint(
        {
            "run_id": overnight.run_id,
            "status": overnight.status,
            "candidate_count": len(overnight.candidates),
            "action_queue": len(overnight.action_queue),
            "recommendations": overnight.recommendation_counts,
        }
    )

    if not solve_report.solved:
        raise SystemExit("Scalar mKdV V recovery failed")
    if dossier.classification.value != "known_mechanism_new_presentation":
        raise SystemExit("Unexpected mKdV dossier classification")
    if not (dossier.hamiltonian_report and dossier.hamiltonian_report["verified"]):
        raise SystemExit("Hamiltonian verification failed")
    if discovery_report.run_id != "DIS-002" or len(discovery_report.candidates) != 4:
        raise SystemExit("DIS-002 controlled sphere search did not produce the fixed candidate set")
    if density_report.run_id != "DIS-003" or len(density_report.candidates) < 3:
        raise SystemExit("DIS-003 density-matrix search did not produce the expected probes")
    if nonlocal_report.run_id != "DIS-004" or len(nonlocal_report.candidates) < 2:
        raise SystemExit("DIS-004 nonlocal search did not produce the expected probes")
    if cohomology_report.run_id != "DIS-005" or len(cohomology_report.candidates) < 2:
        raise SystemExit("DIS-005 cohomology search did not produce the expected probes")
    if scaled_report.run_id != "DIS-006" or len(scaled_report.candidates) < 100:
        raise SystemExit("DIS-006 scaled search did not produce the minimum candidate batch")
    if iterative_report.process_status != "frontier_active" or len(iterative_report.frontier) < 100:
        raise SystemExit("Iterative discovery frontier did not expose the expected active queue")
    if not procedure_audit.passed:
        raise SystemExit("Procedure audit failed")
    if serious_cycle.result_status != "blocked":
        raise SystemExit("SERIOUS-001 did not record the expected blocked result")
    if full_scale.status != "frontier_active" or full_scale.generated_candidate_count < 100:
        raise SystemExit("FULL-001 did not carry out the expected full-scale search")
    if overnight.status != "frontier_active" or len(overnight.candidates) < 1000:
        raise SystemExit("OVERNIGHT-001 did not carry out the expected wide search")


if __name__ == "__main__":
    main()
