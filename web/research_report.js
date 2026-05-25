const reportData = window.LAXFORGE_DASHBOARD_DATA;
const reportColors = ["#087f8c", "#c27b29", "#b24f4b", "#3d7d4f", "#6f5a91", "#356b9b"];

function make(tag, className, value) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (value !== undefined) node.textContent = value;
  return node;
}

function setChildren(parent, children) {
  parent.replaceChildren(...children);
}

function text(value) {
  return value === null || value === undefined || value === "" ? "unknown" : String(value);
}

function titleCase(value) {
  return text(value)
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function items() {
  return reportData.items || reportData.candidates || [];
}

function metricValue(key, fallback = 0) {
  return reportData.metrics?.[key] ?? fallback;
}

function toneForStatus(status) {
  if (status === "pass") return "pass";
  if (status === "fail") return "fail";
  return "warn";
}

function toneForDisposition(value) {
  if (value === "discard") return "fail";
  if (value === "blocked" || value === "needs_human_review") return "warn";
  if (value === "audit" || value === "calibration") return "pass";
  return "neutral";
}

function itemById(itemId) {
  return items().find((item) => item.id === itemId);
}

function listBlock(values) {
  const list = make("ul");
  values.forEach((value) => list.append(make("li", null, value)));
  return list;
}

function tag(value, tone = "neutral") {
  const node = make("span", "tag", titleCase(value));
  node.dataset.tone = tone;
  return node;
}

function paragraphs(values) {
  return values.map((value) => make("p", null, value));
}

function candidateCountByLane(lane) {
  return items().filter((item) => item.lane === lane).length;
}

function recommendationCount(name) {
  return reportData.metrics?.recommendation_counts?.[name] ?? 0;
}

function renderReadout() {
  const slot = document.getElementById("report-readout-copy");
  const frontier = reportData.iterative_process?.frontier || [];
  const firstFrontier = frontier[0];
  const sphereSx = frontier.find((record) => record.item_id === "sphere-s-cross-s-x-tangent-candidate");
  const sxxx = itemById("sphere-s-cross-s-xxx-exploratory-candidate");
  const heisenberg = itemById("sphere-s-cross-s-xx-heisenberg-shaped-candidate");
  const dis003Count = candidateCountByLane("DIS-003");
  const dis006Count = candidateCountByLane("DIS-006");
  const fullScale = reportData.full_scale_search || {};
  const readout = [
    `LAXFORGE is now operating as a controlled evidence machine rather than a collection of isolated symbolic demonstrations. The current payload tracks ${metricValue("tracked_items_total")} normalized records, including ${dis003Count} DIS-003 density probes and a DIS-006 scaled triage batch of ${dis006Count} sphere-tangent candidates.`,
    `FULL-001 has now carried out the full current search loop across ${fullScale.generated_candidate_count || metricValue("discovery_candidate_count")} discovery candidates. The result is an active frontier, not a conclusion: the action queue records which candidates should receive solver effort first.`,
    `The strongest mathematical infrastructure result is M0: the zero-curvature reporting layer can certify an exact pure-gauge flatness case with the convention U_t - V_x + [U,V], matrix shape, coefficient basis, residual-zero status, and per-entry residual grid exposed for audit.`,
    `The strongest calibration result is the second-jet nilpotent mKdV lane. It recovers a known mechanism, verifies Hamiltonian structure, and records ${itemById("second-jet-nilpotent-mkdv")?.conservation_count ?? 0} conservation-law signals. That gives the search process a working reference target before frontier candidates are judged.`,
    `The first serious cycle did not produce a validated third-order sphere ZCR. It changed the state of s_cross_s_xxx from open frontier to blocked by the current low-order so(3) ansatz family. That is useful: it narrows the next search without pretending to rule out broader families.`,
    `The next phase is deliberately broader: DIS-006 records 100+ deterministic tangent-flow descriptors, verifies their tangent construction, and leaves ZCR, spectral, gauge, cyclic, conservation, and collision evidence open until candidate-specific solver passes run.`,
    `The most actionable next item is ${firstFrontier?.name || "the first queued frontier candidate"}. The sphere s_cross_s_x candidate has moved out of the recursive tower blocker and into ${titleCase(sphereSx?.potential_status || "formal_nonlocal_tower_validated")} because the formal recurrence D_x(p{k+1}) = s cross p{k} closes the zero-curvature residual as a power series, while bounded truncations still retain top residuals.`,
    `Known-family discipline is active. The ${heisenberg?.short_name || "Heisenberg-shaped"} candidate has validated ZCR evidence, but it is classified as a known-family collision and recommended discard. This is the intended behavior: validation alone is not enough to keep a candidate alive.`,
  ];

  const statusRail = make("aside", "readout-rail");
  [
    ["Discarded", recommendationCount("discard"), "controls, collisions, or known mechanisms"],
    ["Review", recommendationCount("needs_human_review"), "frontier records with open gates"],
    ["Blocked", recommendationCount("blocked"), sxxx?.connection_status || "current-family obstruction"],
  ].forEach(([label, value, detail]) => {
    const row = make("div", "rail-stat");
    row.append(make("span", null, label));
    row.append(make("strong", null, value));
    row.append(make("small", null, detail));
    statusRail.append(row);
  });

  const prose = make("div", "readout-prose");
  paragraphs(readout).forEach((paragraph) => prose.append(paragraph));
  setChildren(slot, [prose, statusRail]);
}

function renderQuestion() {
  const slot = document.getElementById("report-question");
  const copy = [
    "The working problem is to separate real zero-curvature structure from artifacts produced by controls, gauge-trivial connections, known families, and underpowered ansatz choices. The system deliberately assumes every candidate is weak until it survives documented tests.",
    "A candidate is therefore not treated as promising because it looks elegant. It must show tangent consistency where relevant, a zero-curvature representation with honest residual handling, spectral-parameter evidence, gauge-risk analysis, cyclic or structural fingerprints, conservation evidence, and a prior-art collision check.",
    "This report is not trying to sell a result. It is trying to make the current evidence legible enough that the next research step is obvious and the discarded branches remain auditable.",
  ];
  setChildren(slot, paragraphs(copy));
}

function renderMethods() {
  const slot = document.getElementById("report-methods");
  const copy = [
    "The pipeline now follows a repeatable loop: generate a deterministic candidate, solve or attempt a ZCR ansatz, reduce the curvature residual, run gauge and cyclic-basis checks where the current code supports them, check collisions against known families, and classify the result conservatively.",
    "Controls are not decoration. The zero-flow control verifies that the search can discard fake evidence, while the pure-gauge M0 artifact verifies that the reporting layer can preserve an exact flatness proof without writing proof files automatically.",
    "Blocked is a valid outcome. In SERIOUS-001, the implemented low-order so(3) ansatz family leaves structural obstruction terms for s_cross_s_xxx. The report records that obstruction as a limit of the current family, not a final mathematical exclusion.",
  ];
  setChildren(slot, paragraphs(copy));
}

function dossierCard({ eyebrow, title, paragraphs: copy, stats, tone }) {
  const card = make("article", "dossier-card");
  card.dataset.tone = tone || "neutral";
  const header = document.createElement("header");
  header.append(make("p", "eyebrow", eyebrow));
  header.append(make("h3", null, title));
  const body = make("div", "dossier-copy");
  paragraphs(copy).forEach((paragraph) => body.append(paragraph));
  const statRow = make("div", "dossier-stats");
  stats.forEach(([label, value]) => {
    const statNode = make("div", "mini-stat");
    statNode.append(make("span", null, label));
    statNode.append(make("strong", null, value));
    statRow.append(statNode);
  });
  card.append(header, body, statRow);
  return card;
}

function renderDossiers() {
  const slot = document.getElementById("report-dossiers");
  const artifact = itemById("m0-pure-gauge-flatness-audit");
  const calibration = itemById("second-jet-nilpotent-mkdv");
  const sxx = itemById("sphere-s-cross-s-xx-heisenberg-shaped-candidate");
  const sxxx = itemById("sphere-s-cross-s-xxx-exploratory-candidate");
  const semidirectProbe = itemById("semidirect-non-split-product-deformation-probe");
  const frontier = reportData.iterative_process?.frontier || [];
  const dis006Count = candidateCountByLane("DIS-006");
  const fullScale = reportData.full_scale_search || {};

  const cards = [
    dossierCard({
      eyebrow: "M0",
      title: "Flatness reporting is proof-ready",
      tone: "pass",
      paragraphs: [
        "The pure-gauge fixture gives the report layer a clean target: a diagonal connection whose mixed partials cancel exactly. The artifact records the curvature convention, coefficient basis, matrix shape, and residual grid.",
        "This matters because every later search needs a trustworthy way to show both zero residuals and unresolved residuals without hiding terms in prose.",
      ],
      stats: [
        ["Residual", artifact?.curvature_residual_zero ? "zero" : "open"],
        ["Terms", `${artifact?.curvature_terms_nonzero ?? 0}/${artifact?.curvature_terms_total ?? 0}`],
      ],
    }),
    dossierCard({
      eyebrow: "Calibration",
      title: "mKdV remains the reference mechanism",
      tone: "pass",
      paragraphs: [
        "The prompt-pack calibration recovers the second-jet nilpotent mKdV mechanism and carries Hamiltonian and conservation evidence. It functions as a reference lane for algebra, zero-curvature, and dossier formatting.",
        "The classification stays conservative: this is a known mechanism presentation, not a frontier candidate.",
      ],
      stats: [
        ["Conservation", calibration?.conservation_count ?? 0],
        ["Hamiltonian", calibration?.hamiltonian_verified ? "verified" : "open"],
      ],
    }),
    dossierCard({
      eyebrow: "FULL-001",
      title: "Full-scale pass has been carried out",
      tone: "warn",
      paragraphs: [
        "The full-scale pass runs every current discovery lane through the supported gates, audits the partition into discard and frontier records, and exposes a prioritized action queue for solver work.",
        "The result is deliberately conservative. DIS-006 provides breadth, while FULL-001 records that no scaled batch candidate has a constructed ZCR matrix pair yet.",
      ],
      stats: [
        ["Candidates", fullScale.generated_candidate_count || 0],
        ["Queue", fullScale.action_queue?.length || 0],
      ],
    }),
    dossierCard({
      eyebrow: "DIS-002",
      title: "Sphere-valued search has explicit gate evidence",
      tone: "warn",
      paragraphs: [
        "The sphere lane now contains a meaningful spread: a zero control discarded as fake, a first-order tangent candidate with formal infinite nonlocal tower evidence and downstream gates still open, a second-order Heisenberg-shaped case validated but discarded as known, and a third-order case blocked by the current ansatz family.",
        "That distribution is healthy for a serious search process. It shows the system can preserve obstruction evidence while still discarding attractive cases when collision evidence is stronger.",
      ],
      stats: [
        ["DIS-002 items", candidateCountByLane("DIS-002")],
        ["Known ZCR", sxx?.zcr_validated ? "yes" : "no"],
      ],
    }),
    dossierCard({
      eyebrow: "DIS-006",
      title: "Scaled triage now carries 100+ candidates",
      tone: "warn",
      paragraphs: [
        "The next phase adds a deterministic batch of sphere-tangent flow descriptors built from cross products, derivative atoms, scalar invariants, and two-term blends. Every non-control candidate is tangent by construction.",
        "The batch does not claim a ZCR. Its value is coverage: each record is now visible to the dashboard, procedure audit, collision guard, and frontier queue so solver work can be selected systematically.",
      ],
      stats: [
        ["Batch size", dis006Count],
        ["Default", "review"],
      ],
    }),
    dossierCard({
      eyebrow: "SERIOUS-001",
      title: "Third-order ansatz attempt produced an obstruction",
      tone: "warn",
      paragraphs: [
        "SERIOUS-001 targeted s_cross_s_xxx with a real so(3) low-order ansatz. The attempt records unknowns, constraints, gauge and cyclic evidence, collision context, and obstruction basis.",
        "The result is blocked, not discarded globally. The implemented ansatz family is too narrow to validate the target, and that obstruction now informs the next family expansion.",
      ],
      stats: [
        ["Status", titleCase(sxxx?.recommendation || "blocked")],
        ["Obstructions", sxxx?.zcr_obstruction_basis?.length ?? 0],
      ],
    }),
    dossierCard({
      eyebrow: "DIS-001",
      title: "Semidirect search has crossed the algebra gate",
      tone: "warn",
      paragraphs: [
        "The semidirect lane has useful controls, a known split nilpotent lift, and now an associative non-split product table for the deformation probe.",
        "The blocker moved forward: the matrix pair and curvature split are constructed, while the residual solve, gauge-preserving reductions, and structure evidence remain open gates.",
      ],
      stats: [
        ["DIS-001 items", candidateCountByLane("DIS-001")],
        ["Probe", titleCase(semidirectProbe?.frontier_status || "blocked")],
      ],
    }),
    dossierCard({
      eyebrow: "ITER / PROC",
      title: "The process is coherent enough for another cycle",
      tone: "pass",
      paragraphs: [
        "ITER-001 keeps the next blockers visible: the non-split semidirect residual pass, the first-order sphere formal-tower downstream gates, and the third-order sphere obstruction retained for broader ansatz work.",
        "PROC-001 passes its formal audit checks. That does not make any candidate stronger, but it means the search procedure is partitioning frontier and discard states consistently.",
      ],
      stats: [
        ["Frontier", frontier.length],
        ["Audit", titleCase(reportData.procedure_audit?.status || "unknown")],
      ],
    }),
  ];

  setChildren(slot, cards);
}

function renderInstrumentRing() {
  const slot = document.getElementById("instrument-ring");
  const counts = reportData.metrics?.recommendation_counts || {};
  const entries = Object.entries(counts);
  const total = entries.reduce((sum, [, count]) => sum + count, 0) || 1;
  const radius = 43;
  const circumference = 2 * Math.PI * radius;
  let offset = 0;
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("viewBox", "0 0 120 120");
  svg.setAttribute("role", "img");
  svg.setAttribute("aria-label", "Disposition ring");

  const back = document.createElementNS("http://www.w3.org/2000/svg", "circle");
  back.setAttribute("cx", "60");
  back.setAttribute("cy", "60");
  back.setAttribute("r", String(radius));
  back.setAttribute("fill", "none");
  back.setAttribute("stroke", "#e1e7df");
  back.setAttribute("stroke-width", "13");
  svg.append(back);

  entries.forEach(([label, count], index) => {
    const segment = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    const length = (count / total) * circumference;
    segment.setAttribute("cx", "60");
    segment.setAttribute("cy", "60");
    segment.setAttribute("r", String(radius));
    segment.setAttribute("fill", "none");
    segment.setAttribute("stroke", reportColors[index % reportColors.length]);
    segment.setAttribute("stroke-width", "13");
    segment.setAttribute("stroke-linecap", "round");
    segment.setAttribute("stroke-dasharray", `${length} ${circumference - length}`);
    segment.setAttribute("stroke-dashoffset", String(-offset));
    segment.setAttribute("transform", "rotate(-90 60 60)");
    const titleNode = document.createElementNS("http://www.w3.org/2000/svg", "title");
    titleNode.textContent = `${titleCase(label)}: ${count}`;
    segment.append(titleNode);
    offset += length;
    svg.append(segment);
  });

  const countText = document.createElementNS("http://www.w3.org/2000/svg", "text");
  countText.setAttribute("x", "60");
  countText.setAttribute("y", "56");
  countText.setAttribute("text-anchor", "middle");
  countText.setAttribute("font-size", "17");
  countText.setAttribute("font-weight", "900");
  countText.setAttribute("fill", "#16211d");
  countText.textContent = metricValue("tracked_items_total");
  svg.append(countText);

  const labelText = document.createElementNS("http://www.w3.org/2000/svg", "text");
  labelText.setAttribute("x", "60");
  labelText.setAttribute("y", "73");
  labelText.setAttribute("text-anchor", "middle");
  labelText.setAttribute("font-size", "7");
  labelText.setAttribute("font-weight", "800");
  labelText.setAttribute("fill", "#61706a");
  labelText.textContent = "TRACKED ITEMS";
  svg.append(labelText);

  setChildren(slot, [svg]);
}

function renderReportMetrics() {
  const slot = document.getElementById("report-metrics");
  const metrics = [
    {
      label: "Tracked",
      value: metricValue("tracked_items_total"),
      detail: "normalized records",
      tone: "pass",
    },
    {
      label: "Candidates",
      value: metricValue("discovery_candidate_count"),
      detail: "DIS-001 to DIS-006",
      tone: "pass",
    },
    {
      label: "Validated ZCR",
      value: metricValue("validated_zcr_count"),
      detail: "known-family evidence",
      tone: "warn",
    },
    {
      label: "Discard",
      value: reportData.metrics?.recommendation_counts?.discard ?? 0,
      detail: "controls or collisions",
      tone: "fail",
    },
    {
      label: "Review",
      value: reportData.metrics?.recommendation_counts?.needs_human_review ?? 0,
      detail: "incomplete gates",
      tone: "warn",
    },
    {
      label: "Blocked",
      value: metricValue("blocked_frontier_count"),
      detail: "frontier limits",
      tone: "warn",
    },
    {
      label: "Procedure",
      value: titleCase(metricValue("procedure_audit_status", "unknown")),
      detail: `${metricValue("procedure_check_count")} checks`,
      tone: metricValue("procedure_audit_status") === "pass" ? "pass" : "warn",
    },
    {
      label: "Surprisal",
      value: metricValue("highest_surprisal"),
      detail: "highest audit score",
      tone: "warn",
    },
  ];

  setChildren(
    slot,
    metrics.map((metric) => {
      const card = make("article", "metric-tile");
      card.dataset.tone = metric.tone;
      card.append(make("span", null, metric.label));
      card.append(make("strong", null, metric.value));
      card.append(make("small", null, metric.detail));
      return card;
    }),
  );
}

function renderSummary() {
  const slot = document.getElementById("report-summary");
  const summary = reportData.plain_summary || {};
  const copy = make("div", "summary-copy");
  copy.append(make("p", "eyebrow", "Short Version"));
  copy.append(make("h2", null, summary.headline || "Evidence search in progress"));
  copy.append(make("p", null, summary.lede || "The current report has no summary payload."));
  const insights = make("div", "summary-insights");
  (summary.bullets || []).slice(0, 4).forEach((bullet, index) => {
    const insight = make("article", "summary-insight");
    insight.append(make("span", null, `0${index + 1}`));
    insight.append(make("p", null, bullet));
    insights.append(insight);
  });
  copy.append(insights);

  const bottom = make("aside", "summary-bottom");
  bottom.append(make("span", null, "Bottom line"));
  bottom.append(make("strong", null, summary.bottom_line || "Evidence is tracked without promotion claims."));
  setChildren(slot, [copy, bottom]);
}

function renderTimeline() {
  const slot = document.getElementById("report-timeline");
  const laneCounts = new Map((reportData.lanes || []).map((lane) => [lane.name, lane.items]));
  const descriptions = {
    M0: "Pure-gauge flatness report validates residual zero and proof-artifact readiness.",
    "PROMPT-PACK": "mKdV calibration recovers a known mechanism and verifies conservation evidence.",
    "DIS-001": "Semidirect lane contains controls, a known mechanism lift, and one blocked algebra frontier.",
    "DIS-002": "Sphere lane keeps tangent candidates conservative and marks the Heisenberg case as known.",
    "DIS-003": "Density-matrix lane records commutator and dissipative tangent probes.",
    "DIS-004": "Nonlocal covering lane records pseudopotential probes with open gates.",
    "DIS-005": "Cohomology lane records cocycle and coboundary separation work.",
    "DIS-006": "Scaled sphere-tangent triage adds 100+ descriptors with open solver gates.",
    "ITER-001": "Frontier process queues the next actionable candidates with explicit gate gaps.",
    "PROC-001": "Procedure audit verifies the run discipline and claim guard.",
    "SERIOUS-001": "Third-order sphere ansatz attempt is blocked by the current low-order family.",
    "FULL-001": "Full-scale pass ranks the current action queue after supported gates.",
  };

  const nodes = (reportData.run_ids || []).map((runId) => {
    const node = make("article", "timeline-node");
    node.append(make("span", "node-line"));
    node.append(make("strong", null, runId));
    node.append(make("p", null, descriptions[runId] || "Evidence lane recorded."));
    const count = [...laneCounts.entries()].find(([name]) => name.includes(runId))?.[1];
    node.append(tag(count === undefined ? "tracked" : `${count} item${count === 1 ? "" : "s"}`, "pass"));
    return node;
  });

  setChildren(slot, nodes);
}

function renderDispositionMix() {
  const slot = document.getElementById("report-disposition");
  const counts = reportData.metrics?.recommendation_counts || {};
  const total = Object.values(counts).reduce((sum, count) => sum + count, 0) || 1;
  const rows = Object.entries(counts).map(([label, count]) => {
    const row = make("div", "bar-row");
    const track = make("div", "bar-track");
    const fill = make("div", "bar-fill");
    fill.dataset.tone = toneForDisposition(label);
    fill.style.width = `${Math.max(4, (count / total) * 100)}%`;
    track.append(fill);
    row.append(make("span", "bar-label", titleCase(label)), track, make("strong", null, count));
    return row;
  });
  setChildren(slot, rows);
}

function renderGateHeatmap() {
  const slot = document.getElementById("report-gates");
  const rows = items();
  if (!rows.length) {
    setChildren(slot, [make("div", "empty-state", "No gate rows recorded.")]);
    return;
  }
  const table = make("table", "gate-table");
  const thead = document.createElement("thead");
  const head = document.createElement("tr");
  head.append(make("th", null, "Item"));
  rows[0].gates.forEach((gate) => head.append(make("th", null, gate.label)));
  thead.append(head);

  const tbody = document.createElement("tbody");
  rows.forEach((item) => {
    const row = document.createElement("tr");
    row.append(make("td", null, item.short_name || item.name));
    item.gates.forEach((gate) => {
      const cell = document.createElement("td");
      const chip = make("span", "gate-cell", titleCase(gate.status));
      chip.dataset.status = gate.status;
      chip.title = `${gate.label}: ${text(gate.value)}`;
      cell.append(chip);
      row.append(cell);
    });
    tbody.append(row);
  });

  table.append(thead, tbody);
  setChildren(slot, [table]);
}

function renderAuditSurprisal() {
  const slot = document.getElementById("report-surprisal");
  const rows = [...items()].sort((a, b) => b.surprisal.score - a.surprisal.score).slice(0, 6);
  setChildren(
    slot,
    rows.map((item) => {
      const row = make("article", "surprisal-row");
      const track = make("div", "bar-track");
      const fill = make("div", "bar-fill");
      fill.dataset.tone = item.surprisal.score > 45 ? "warn" : "pass";
      fill.style.width = `${item.surprisal.score}%`;
      track.append(fill);
      const copy = make("div");
      copy.append(make("strong", null, item.short_name || item.name));
      copy.append(make("p", null, (item.surprisal.drivers || []).slice(0, 2).join("; ")));
      row.append(copy, track, make("strong", null, item.surprisal.score));
      return row;
    }),
  );
}

function renderFrontier() {
  const slot = document.getElementById("report-frontier");
  const records = reportData.iterative_process?.frontier || [];
  setChildren(
    slot,
    records.map((record) => {
      const card = make("article", "frontier-card");
      const header = document.createElement("header");
      header.append(make("p", "eyebrow", `${record.lane} / priority ${record.priority}`));
      header.append(make("h3", null, record.name));
      header.append(tag(record.potential_status, toneForDisposition(record.recommendation)));
      card.append(header);
      card.append(make("p", null, record.next_action));
      card.append(listBlock(record.gate_gaps || []));
      const row = make("div", "tag-row");
      row.append(tag(record.recommendation, toneForDisposition(record.recommendation)));
      row.append(tag(record.connection_status, "warn"));
      card.append(row);
      return card;
    }),
  );
}

function renderSeriousCycle() {
  const slot = document.getElementById("report-cycle");
  const cycle = reportData.serious_cycle || {};
  const target = itemById(cycle.target_item_id) || {};
  const baseline = cycle.baseline_process?.frontier?.[0]?.potential_status || "unknown";
  const refreshed = cycle.refreshed_process?.frontier?.find((record) => record.item_id === cycle.target_item_id)
    ?.potential_status || target.frontier_status || "unknown";
  const compare = make("div", "cycle-compare");
  const before = make("div", "cycle-step");
  before.append(make("span", null, "Before attempt"));
  before.append(make("strong", null, titleCase(baseline)));
  const after = make("div", "cycle-step");
  after.append(make("span", null, "After attempt"));
  after.append(make("strong", null, titleCase(refreshed)));
  compare.append(before, after);

  const status = make("div", "tag-row");
  status.append(tag(cycle.result_status || "unknown", toneForDisposition(cycle.result_status)));
  status.append(tag(target.connection_status || "unknown", "warn"));

  const obstruction = target.zcr_obstruction_basis || target.failure_reasons || [];
  setChildren(slot, [
    status,
    make("p", null, cycle.next_action || target.next_action || "No next action recorded."),
    compare,
    make("h3", null, "Obstruction evidence"),
    listBlock(obstruction),
  ]);
}

function renderProcedureAudit() {
  const slot = document.getElementById("report-procedure");
  const audit = reportData.procedure_audit || {};
  const summary = make("div", "process-row");
  summary.append(make("strong", null, audit.procedure_id || "PROC-001"));
  summary.append(make("span", null, `${text(audit.status)} / ${audit.failure_count ?? 0} failures`));
  summary.append(tag(`${audit.checks?.length ?? 0} checks`, audit.status === "pass" ? "pass" : "warn"));
  const checks = (audit.checks || []).map((check) => {
    const row = make("article", "procedure-check");
    const dot = make("span", "check-dot", check.status[0]?.toUpperCase() || "?");
    const copy = make("div");
    copy.append(make("span", null, check.check_id));
    copy.append(make("strong", null, check.label));
    copy.append(make("p", null, check.detail));
    row.append(dot, copy);
    return row;
  });
  setChildren(slot, [summary, ...checks]);
}

function renderArtifacts() {
  const artifact = items().find((item) => item.proof_summary || item.residual_grid);
  const slot = document.getElementById("report-artifacts");
  const gridSlot = document.getElementById("report-residual");
  if (!artifact) {
    setChildren(slot, [make("div", "empty-state", "No proof artifact recorded.")]);
    setChildren(gridSlot, []);
    return;
  }
  const proof = artifact.proof_summary || {};
  const facts = [
    `Convention: ${text(proof.curvature_convention || artifact.detail?.equation)}`,
    `Matrix shape: ${text((proof.matrix_shape || []).join(" x "))}`,
    `Coefficient basis: ${text((proof.coefficient_basis || []).join(", "))}`,
    `Residual zero: ${artifact.curvature_residual_zero ? "yes" : "no"}`,
    `Terms: ${artifact.curvature_terms_nonzero} unresolved of ${artifact.curvature_terms_total}`,
  ];
  setChildren(slot, [make("h3", null, artifact.name), listBlock(facts)]);

  const grid = proof.entry_status_grid || artifact.residual_grid;
  const cells = [];
  (grid || []).forEach((row) => {
    row.forEach((value) => {
      const cell = make("span", "residual-cell", value);
      cell.dataset.status = value === "OK" ? "pass" : "fail";
      cells.push(cell);
    });
  });
  setChildren(gridSlot, cells);
}

function renderCollisionMap() {
  const slot = document.getElementById("report-collisions");
  const families = reportData.collision_family_map || [];
  const max = Math.max(1, ...families.map((family) => family.item_ids.length));
  setChildren(
    slot,
    families.map((family, index) => {
      const row = make("article", "collision-row");
      const left = make("div");
      const dot = make("span", "collision-dot");
      dot.style.background = reportColors[index % reportColors.length];
      left.append(dot, make("strong", null, family.family));
      const track = make("div", "bar-track");
      const fill = make("div", "bar-fill");
      fill.style.background = reportColors[index % reportColors.length];
      fill.style.width = `${Math.max(8, (family.item_ids.length / max) * 100)}%`;
      track.append(fill);
      row.append(left, track, make("strong", null, family.item_ids.length));
      return row;
    }),
  );
}

function renderTechnicalLedger() {
  const slot = document.getElementById("report-ledger");
  const table = make("table");
  const head = document.createElement("thead");
  const headRow = document.createElement("tr");
  ["Item", "Lane", "Disposition", "Connection", "Gate Summary", "Failure Reasons"].forEach((label) =>
    headRow.append(make("th", null, label)),
  );
  head.append(headRow);
  const body = document.createElement("tbody");
  items().forEach((item) => {
    const row = document.createElement("tr");
    const gateSummary = Object.entries(item.gate_summary || {})
      .map(([key, value]) => `${key}: ${value}`)
      .join("; ");
    [
      item.short_name || item.name,
      item.lane,
      titleCase(item.recommendation),
      item.connection_status,
      gateSummary,
      (item.failure_reasons || []).join("; "),
    ].forEach((value) => row.append(make("td", null, value)));
    body.append(row);
  });
  table.append(head, body);
  setChildren(slot, [table]);
}

function bootReport() {
  if (!reportData) {
    document.body.textContent = "Report data missing.";
    return;
  }
  document.getElementById("schema-pill").textContent = `Schema v${reportData.schema_version}`;
  renderInstrumentRing();
  renderReportMetrics();
  renderSummary();
  renderReadout();
  renderQuestion();
  renderMethods();
  renderDossiers();
  renderTimeline();
  renderDispositionMix();
  renderGateHeatmap();
  renderAuditSurprisal();
  renderFrontier();
  renderSeriousCycle();
  renderProcedureAudit();
  renderArtifacts();
  renderCollisionMap();
  renderTechnicalLedger();
}

bootReport();
