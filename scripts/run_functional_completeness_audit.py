#!/usr/bin/env python
"""Run the LAXFORGE functional-completeness audit."""

from __future__ import annotations

from laxforge.core.completeness import build_functional_completeness_audit_report


def main() -> None:
    """Print the audit and fail if any spec-parity check fails."""
    report = build_functional_completeness_audit_report()
    print(report.to_markdown())
    if not report.passed:
        raise SystemExit("Functional-completeness audit failed")


if __name__ == "__main__":
    main()
