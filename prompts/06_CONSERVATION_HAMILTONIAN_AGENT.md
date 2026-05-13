# Codex Prompt 06 — Conservation and Hamiltonian Agent

Implement initial conservation-law and Hamiltonian tests.

## Scope

Work in:

```text
src/laxforge/core/conservation.py
src/laxforge/core/hamiltonian.py
tests/
```

## Required features

1. Implement variational derivatives for scalar and vector fields.
2. Implement skew-adjointness checks for simple differential operators.
3. Validate constant Poisson operators.
4. For the second-jet mKdV example, verify the Hamiltonian density:

```text
h = u_x w_x + 1/2 v_x^2 - 2 u^3 w - 3 u^2 v^2
```

with Poisson operator:

```text
J = [[0,0,Dx],[0,Dx,0],[Dx,0,0]]
```

5. Add inherited conservation-law expansion for truncated polynomial lifts.

## Definition of done

The nilpotent mKdV calibration dossier includes at least three conserved quantities and one verified Hamiltonian representation.

