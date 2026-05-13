# PRIOR_ART_REGISTRY.md — Initial Known-Family Collision Registry

This file is not a substitute for literature review. It is a structured checklist for known collision zones.

## Families to fingerprint early

1. AKNS / Zakharov-Shabat systems.
2. KdV and mKdV scalar hierarchies.
3. NLS hierarchy.
4. sine-Gordon and affine Toda systems.
5. KP and Gelfand-Dickey hierarchies.
6. Drinfel'd-Sokolov reductions.
7. Matrix and vector mKdV systems.
8. Integrable couplings via semidirect products.
9. Nilpotent, perturbation, and jet extensions.
10. Supersymmetric and graded extensions.
11. Nonlocal coverings and pseudopotential systems.
12. Principal chiral model and Heisenberg ferromagnet families.
13. Coadjoint-orbit and symmetric-space hierarchies.

## Collision checklist for each candidate

- Does projection recover a known scalar pair?
- Is the construction a direct sum, block lift, or Jordan perturbation of a known pair?
- Can λ be gauged away?
- Is the field content simply a linearized perturbation equation?
- Does a Miura map reduce it to KdV/mKdV/NLS/Toda?
- Is it a Drinfel'd-Sokolov hierarchy in disguise?
- Is it a known symmetric-space reduction?
- Does the spectral curve carry new data or repeated known data?

## Rule

When in doubt, classify conservatively.

## Scaffold implementation note

The code registry mirrors this checklist for early calibration. In particular,
nilpotent and jet lifts of mKdV are classified conservatively as known-mechanism
new presentations, and fake/trivial control pairs are marked for discard rather
than investigation.
