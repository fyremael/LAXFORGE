#!/usr/bin/env python
"""Run the formal LAXFORGE discovery procedure audit without writing artifacts."""

from __future__ import annotations

from laxforge.core.procedures import build_procedure_audit_report


def main() -> None:
    """Print the current procedure audit summary."""
    report = build_procedure_audit_report()
    print("LAXFORGE procedure audit")
    print(f"Procedure: {report.procedure_id} v{report.version}")
    print(f"Status: {report.status}")
    print(f"Summary: {report.summary}")
    for check in report.checks:
        print(f"  - {check.check_id} {check.status}: {check.detail}")
    if not report.passed:
        raise SystemExit("Procedure audit failed")


if __name__ == "__main__":
    main()
