# LAXFORGE Content Kit

This kit provides promotional and educational copy for LAXFORGE, plus an
introductory bridge to LAXCERT. It is intentionally conservative: LAXFORGE
produces audit-ready evidence, and LAXCERT validates compatible certificate
artifacts. Neither system should be described as proving novelty by itself.

## Positioning

### One-line description

LAXFORGE is a gauge-aware discovery and audit engine for zero-curvature
representations, Lax pairs, and integrable-systems candidates.

### Short description

LAXFORGE helps researchers generate, reduce, test, and document candidate Lax
pairs without skipping the difficult parts: zero-curvature validation, gauge and
fake-pair checks, cyclic-basis fingerprints, conservation-law evidence,
Hamiltonian attempts, and prior-art collision review.

### Extended description

LAXFORGE is built for mathematical clean-room work in integrable systems. It
turns symbolic searches into structured candidate dossiers, where every result
is tracked through falsification gates before it can be considered interesting.
The system is not a novelty oracle. Its job is to produce reproducible evidence:
the candidate pair, the generated or target PDE, the curvature expansion,
coefficient splitting, gauge-risk assessment, invariant fingerprints, structure
extraction attempts, and known-family collision notes.

LAXCERT complements that workflow by acting as a certificate consumer. LAXFORGE
can export compatible candidate artifacts; LAXCERT is responsible for checking
the formal certificate boundary. Together, the projects separate discovery,
evidence emission, and certificate validation.

## Messaging Pillars

### 1. Evidence before excitement

LAXFORGE is designed around the rule that compatibility is not enough. A
candidate has to pass through explicit gates before it becomes a serious review
target.

Use this language:

- "candidate dossier"
- "audit-ready evidence"
- "gauge-risk report"
- "known-family collision check"
- "human review target"

Avoid this language:

- "discovers new integrable systems automatically"
- "proves novelty"
- "guarantees publishable Lax pairs"
- "solves the classification problem"

### 2. Gauge-aware by default

Symbolic Lax-pair searches often produce familiar, fake, reducible, or
gauge-equivalent structures. LAXFORGE treats that risk as a first-class part of
the workflow rather than an afterthought.

### 3. Reproducible dossiers

The useful output is not only a formula. It is the surrounding record that lets
a human or another tool inspect how the formula survived, failed, or remained
blocked.

### 4. LAXCERT as the certificate boundary

LAXFORGE emits candidate artifacts. LAXCERT certifies compatible artifacts.
That separation keeps the trust boundary explicit and makes promotional claims
cleaner.

## Audience Copy

### For integrable-systems researchers

LAXFORGE is a structured assistant for exploring zero-curvature
representations. It can help generate candidate connections, expand curvature,
split coefficients, track gauge risk, compute fingerprints, and preserve the
prior-art collision trail needed for expert review.

### For symbolic-computation developers

LAXFORGE is a modular Python scaffold for auditable symbolic discovery. It
separates coefficient algebras, curvature expansion, ansatz solving, gauge
analysis, invariant extraction, and dossier generation so each layer can be
tested independently.

### For reviewers and collaborators

LAXFORGE does not ask you to trust a raw search hit. It produces a dossier:
what was tested, what passed, what failed, what remains unknown, and which
known families may already explain the result.

### For LAXCERT users

LAXFORGE can produce a LAXCERT-ingestable calibration artifact containing
`candidate.json`, `laxforge_manifest.json`, and `source_report.json`. LAXCERT
then owns the certificate validation step.

## Educational Explainers

### Lay Backgrounder: What LAXFORGE is trying to do

Most scientific software answers a question such as "what happens if I run this
simulation?" LAXFORGE is aimed at a different kind of question: "does this
mathematical pattern have enough structure to be worth serious attention?"

The setting is a part of mathematics called integrable systems. These are
special differential equations that behave with unusual order. Many equations
used in physics and geometry are difficult because small effects interact in
complicated ways. An integrable system is still often nonlinear and difficult,
but it carries hidden structure that can make it more understandable. That
structure may appear as conserved quantities, spectral data, recursion
patterns, or a Lax pair.

For a lay audience, a Lax pair can be thought of as a pair of mathematical
instructions that watch the same motion from two directions. If the two
instructions agree perfectly, their agreement produces the equation being
studied. The agreement condition is called zero curvature. It is a compact way
to say that two ways of moving through the mathematical system are compatible.

That compatibility is powerful, but it can also be misleading. A symbolic
computer search can produce formulas that look impressive while hiding one of
several problems:

- The formula may be a disguised version of something already known.
- A parameter may look important but disappear after a change of variables.
- The pair may be gauge-equivalent to a simpler or fake pair.
- The calculation may depend on an assumption that was never recorded.
- The output may satisfy one algebraic check but lack deeper integrable
  structure.

LAXFORGE exists because the hard part is not only finding formulas. The hard
part is building an evidence trail around them.

#### The everyday analogy

Imagine a metal detector on a beach. It can beep when it finds something under
the sand, but the beep is not the discovery. Someone still has to dig, identify
the object, check whether it is valuable, and record where it came from. In the
same way, a symbolic search can produce a candidate Lax pair, but the candidate
is only the beep. LAXFORGE is the careful follow-up process: dig, clean, test,
compare, label, and decide whether a human expert should inspect it.

#### What LAXFORGE receives

LAXFORGE starts with a mathematical search space. That search space may include:

- fields, such as unknown functions `u`, `v`, `p`, or `q`;
- independent variables, usually space `x` and time `t`;
- a coefficient algebra, which describes what kind of symbolic objects are
  allowed;
- an ansatz, which is a structured guess for the shape of the candidate pair;
- constraints, such as degree limits, symmetry requirements, or known target
  equations.

The ansatz matters because the possible universe of formulas is too large to
search blindly. A good ansatz is like a well-designed experiment: it narrows the
question enough that a result can be checked.

#### What LAXFORGE does with a candidate

When LAXFORGE has a possible pair `U` and `V`, it does not treat the pair as a
result. It treats it as an object under examination.

The first check is the zero-curvature calculation:

```text
U_t - V_x + [U, V] = 0.
```

This expression asks whether the time-change of `U`, the space-change of `V`,
and their matrix interaction cancel exactly. If they cancel, the pair may encode
a differential equation. If they do not cancel, LAXFORGE records the leftover
terms rather than hiding the failure.

The next step is coefficient splitting. A symbolic expression can contain many
independent pieces: powers of a spectral parameter, basis elements of an
algebra, derivatives of fields, or matrix entries. LAXFORGE separates those
pieces so the evidence says which terms vanish and which terms remain.

After that, LAXFORGE asks a more subtle question: is this pair meaningful, or
is it only a change of costume? This is where gauge checks and invariant
fingerprints enter.

#### Why "gauge" matters in plain language

In mathematics and physics, the same object can often be described in many
coordinate systems. A gauge transformation is one kind of change in description.
Two formulas can look different on paper but represent the same underlying
structure after such a transformation.

That matters because a search engine could otherwise count the same idea many
times. LAXFORGE tries to record whether a candidate appears reducible,
gauge-trivial, parameter-removable, or related to a known family. It does not
pretend this is always easy. When a check is incomplete, the dossier should say
so.

#### Why prior art matters

Integrable systems have a long mathematical history. A candidate that looks
fresh in one notation may be a known hierarchy member, a standard reduction, or
an integrable coupling already understood in another language. LAXFORGE keeps a
known-family collision trail so that "we found a formula" does not become "we
found new mathematics."

The right standard is conservative:

```text
generate -> solve -> reduce -> falsify -> extract structure -> review
```

The final step is review, not automatic promotion.

#### What a candidate dossier contains

A LAXFORGE dossier is the record surrounding a candidate. A useful dossier can
include:

- the candidate pair `U` and `V`;
- the generated or target differential equation;
- the zero-curvature expansion;
- the coefficient-splitting proof;
- unresolved residual terms, if any;
- gauge and fake-pair risk notes;
- cyclic-basis or other invariant fingerprints;
- spectral-parameter evidence;
- conservation-law attempts;
- Hamiltonian-structure attempts;
- known-family collision notes;
- a conservative classification.

The classification is an evidence state. It may say calibration, discard,
blocked, known, fake, or needs human review. It should not say "new" unless a
human mathematical review has earned that conclusion outside the automated
pipeline.

#### Where LAXCERT enters the story

LAXFORGE is the discovery and evidence-emission side. LAXCERT is introduced as
the certificate-validation side for compatible artifacts.

That separation is important. LAXFORGE can export a structured artifact such as
`candidate.json`, `laxforge_manifest.json`, and `source_report.json`. The source
report states the trust boundary: LAXFORGE proposed the candidate artifact;
LAXCERT checks the certificate according to its own schema and proof strategy.

For a lay audience, the relationship is similar to preparing a lab sample and
sending it to a certification process. LAXFORGE prepares and documents the
sample. LAXCERT checks the certificate. Neither should be described as a
shortcut around expert judgment.

#### Why this project is useful even without novelty claims

The cautious posture is a strength. In research software, failed or blocked
results can still be valuable when they are recorded clearly. They prevent
repeated work, reveal where the search space is saturated, show which checks
need better tools, and make collaboration easier.

LAXFORGE is useful because it turns symbolic exploration into a reproducible
workflow. It helps answer practical questions:

- Did the curvature actually vanish?
- Which coefficients were checked?
- Is the spectral parameter essential or removable?
- Is there evidence of conservation laws?
- Did this collide with a known hierarchy?
- What remains unknown?
- What should be tested next?

That is the heart of the project: not a machine that announces discoveries, but
a system that makes mathematical evidence harder to lose and easier to review.

#### Plain-language glossary

- **Ansatz**: A structured guess for the shape of a formula.
- **Candidate**: A possible result under test, not a conclusion.
- **Coefficient splitting**: Separating a symbolic expression into independent
  pieces so each piece can be checked.
- **Conservation law**: A quantity that stays unchanged as the system evolves.
- **Dossier**: The evidence record attached to a candidate.
- **Gauge transformation**: A change of mathematical description that may leave
  the underlying structure the same.
- **Hamiltonian structure**: A way to express evolution using energy-like
  mathematical geometry.
- **Integrable system**: A differential equation with unusually rich hidden
  structure.
- **Lax pair**: Two linked mathematical objects whose compatibility can encode
  a differential equation.
- **LAXCERT**: A certificate-validation counterpart for compatible LAXFORGE
  exports.
- **Novelty**: A human-reviewed mathematical conclusion, not an automatic
  software output.
- **Prior-art collision**: Evidence that a candidate may match a known family
  or previously understood construction.
- **Spectral parameter**: A parameter in a Lax representation that may carry
  important structural information, unless it can be removed.
- **Zero curvature**: The compatibility condition saying two mathematical
  directions fit together without residual obstruction.

### What is a zero-curvature representation?

A zero-curvature representation encodes an evolution equation as the flatness
condition

```text
U_t - V_x + [U, V] = 0.
```

Here `U` and `V` are matrix-valued or operator-valued connections. When the
flatness condition is equivalent to a PDE, the representation can reveal
integrable structure: spectral data, conservation laws, recursion mechanisms,
or links to known hierarchies.

### Why gauge checks matter

Two Lax pairs can look different but describe the same underlying structure
after a gauge transformation. A search engine that ignores gauge equivalence
can overcount old mathematics, mistake removable parameters for spectral
parameters, or preserve fake pairs that carry no meaningful integrability
evidence. LAXFORGE records gauge risk so candidates stay honest.

### What LAXFORGE means by "candidate"

A candidate is not a claim. It is an object under test. LAXFORGE uses
classifications such as fake, known, calibration, blocked, discard, or needs
human review to prevent symbolic output from being promoted too early.

### How LAXCERT fits

LAXCERT is introduced as the certificate checker for compatible LAXFORGE
exports. LAXFORGE builds an artifact and declares the trust boundary. LAXCERT
validates the artifact against its schema and proof strategy.

## Reusable Snippets

### README or project page blurb

LAXFORGE is a gauge-aware discovery engine for Lax pairs and zero-curvature
representations. It converts symbolic searches into auditable candidate
dossiers: curvature proofs, coefficient splitting, gauge-risk checks,
cyclic-basis fingerprints, conservation/Hamiltonian attempts, and prior-art
collision notes. LAXCERT integration adds a certificate boundary for compatible
exported artifacts.

### Release note

LAXFORGE now includes a LAXCERT calibration export path. The exporter writes a
candidate artifact directory with `candidate.json`, `laxforge_manifest.json`,
and `source_report.json`, keeping discovery output and certificate validation
as separate, auditable steps.

### Conference abstract

We present LAXFORGE, a gauge-aware symbolic workflow for producing auditable
candidate dossiers for zero-curvature representations and Lax pairs. The system
emphasizes falsification gates: coefficient-level curvature validation,
gauge/fake-pair risk, cyclic-basis fingerprints, conservation and Hamiltonian
evidence, and prior-art collision checks. We also introduce LAXCERT as a
certificate-validation boundary for compatible artifacts emitted by LAXFORGE.
The goal is not automated novelty claims, but reproducible evidence suitable
for human mathematical review.

### Social post

LAXFORGE turns Lax-pair search results into audit-ready dossiers: curvature
validation, gauge-risk checks, invariant fingerprints, structure evidence, and
prior-art collision notes. LAXCERT adds the certificate boundary for compatible
exports. Evidence first; claims later.

### Website hero copy

LAXFORGE

Gauge-aware evidence for Lax-pair discovery. Generate, test, reduce, classify,
and export candidate dossiers for human mathematical review.

### LAXCERT intro block

Introducing LAXCERT: the certificate boundary for compatible LAXFORGE outputs.
LAXFORGE proposes structured candidate artifacts; LAXCERT validates the
certificate side. The handoff is explicit, reproducible, and designed to keep
trust assumptions visible.

## Demo Script

### 30-second version

LAXFORGE is for researchers who want symbolic discovery without symbolic
overclaiming. A candidate Lax pair is generated, its zero-curvature residual is
expanded and split, and the result is tracked through gauge, invariant,
structure, and prior-art gates. If the candidate is useful, LAXFORGE emits a
dossier. If it is compatible with LAXCERT, it can also export a certificate
artifact for independent validation.

### 2-minute walkthrough

1. Start with an arena: a coefficient algebra, fields, variables, and an ansatz
   family.
2. Generate candidate `U` and `V` connections.
3. Compute `U_t - V_x + [U, V]` and split the result into coefficient equations.
4. Solve or record obstructions.
5. Run gauge-risk and fake-pair checks.
6. Compute fingerprints and structure evidence where supported.
7. Compare against known families and classify conservatively.
8. Emit a candidate dossier, or export a LAXCERT calibration artifact when the
   certificate schema applies.

## FAQ

### Does LAXFORGE prove a candidate is new?

No. LAXFORGE produces evidence and classifications. Novelty remains a human
mathematical conclusion after validation and prior-art review.

### What is LAXCERT?

LAXCERT is the certificate-validation counterpart for compatible LAXFORGE
exports. It checks certificate artifacts rather than running the discovery
process.

### What is the current calibration example?

The repository includes a second-jet nilpotent mKdV lift and a LAXCERT
section-10 transport calibration export. These are calibration targets, not
novelty claims.

### Who is LAXFORGE for?

Researchers, students, and symbolic-computation developers working with
zero-curvature representations, Lax pairs, integrable hierarchies, and
audit-ready mathematical workflows.

## Taglines

- Evidence first. Claims later.
- Gauge-aware Lax-pair discovery.
- From symbolic hit to auditable dossier.
- Lax-pair search with falsification gates.
- Discovery output with a certificate boundary.

## Content Guardrails

- Say "supports", "tests", "emits", "tracks", and "classifies".
- Do not say "proves novelty", "guarantees integrability", or "automates
  publication".
- Keep LAXCERT framed as validation for compatible artifacts, not as a blanket
  endorsement of all LAXFORGE outputs.
- Describe calibration examples as calibration examples.
- Prefer "needs human review" over "new" unless a human-reviewed conclusion is
  being quoted from an external source.
