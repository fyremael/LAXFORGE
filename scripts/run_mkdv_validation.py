#!/usr/bin/env python
"""Run the nilpotent second-jet mKdV validation example."""

from __future__ import annotations

from pprint import pprint

from laxforge.examples.mkdv_second_jet import validate


def main() -> None:
    result = validate()
    print("LAXFORGE calibration: second-jet nilpotent mKdV")
    print("Checks:")
    pprint(result["checks"])
    if not all(result["checks"].values()):
        raise SystemExit("Validation failed")
    print("\nAll symbolic checks passed.")


if __name__ == "__main__":
    main()
