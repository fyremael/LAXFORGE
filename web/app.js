const data = window.LAXFORGE_DASHBOARD_DATA;
const storageKey = "laxforge.dashboard.state.v2";
const colors = ["#087f8c", "#c27b29", "#b24f4b", "#3d7d4f", "#6f5a91"];

const defaultState = {
  tab: "overview",
  search: "",
  lane: "all",
  recommendation: "all",
  gate: "all",
  sort: "surprisal",
  selectedId: null,
  selectedFamily: null,
};

const state = loadState();

function loadState() {
  try {
    return { ...defaultState, ...JSON.parse(localStorage.getItem(storageKey) || "{}") };
  } catch {
    return { ...defaultState };
  }
}

function saveState() {
  localStorage.setItem(storageKey, JSON.stringify(state));
}

function items() {
  return data.items || data.candidates || [];
}

function frontierRecords() {
  return data.iterative_process?.frontier || [];
}

function procedureAudit() {
  return data.procedure_audit || { procedure_steps: [], checks: [] };
}

function text(value) {
  return value === null || value === undefined ? "unknown" : String(value);
}

function titleCase(value) {
  return text(value)
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function make(tag, className, value) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (value !== undefined) node.textContent = value;
  return node;
}

function setChildren(parent, children) {
  parent.replaceChildren(...children);
}

function toneForStatus(status) {
  if (status === "pass") return "pass";
  if (status === "fail") return "fail";
  return "warn";
}

function toneForRecommendation(value) {
  if (value === "discard") return "fail";
  if (value === "needs_human_review" || value === "blocked") return "warn";
  if (value === "calibration" || value === "audit") return "pass";
  return "neutral";
}

function matchesSearch(item) {
  const needle = state.search.trim().toLowerCase();
  if (!needle) return true;
  const haystack = [
    item.name,
    item.short_name,
    item.lane,
    item.classification_label,
    item.recommendation,
    item.connection_status,
    ...(item.collisions || []),
    ...(item.failure_reasons || []),
  ]
    .join(" ")
    .toLowerCase();
  return haystack.includes(needle);
}

function filteredItems() {
  let filtered = items().filter(matchesSearch);
  if (state.lane !== "all") {
    filtered = filtered.filter((item) => item.lane === state.lane);
  }
  if (state.recommendation !== "all") {
    filtered = filtered.filter((item) => item.recommendation === state.recommendation);
  }
  if (state.gate !== "all") {
    filtered = filtered.filter((item) => item.gates.some((gate) => gate.status === state.gate));
  }

  if (state.sort === "surprisal") {
    filtered.sort((a, b) => b.surprisal.score - a.surprisal.score);
  } else if (state.sort === "lane") {
    filtered.sort((a, b) => a.lane.localeCompare(b.lane) || a.name.localeCompare(b.name));
  } else if (state.sort === "order") {
    filtered.sort((a, b) => (a.order ?? 99) - (b.order ?? 99));
  }
  return filtered;
}

function currentSelection() {
  return items().find((item) => item.id === state.selectedId) || items()[0] || null;
}

function ensureSelected() {
  const visible = filteredItems();
  if (
    state.tab === "frontier" &&
    frontierRecords().length &&
    !frontierRecords().some((record) => record.item_id === state.selectedId)
  ) {
    state.selectedId = frontierRecords()[0].item_id;
    return;
  }
  if (!items().some((item) => item.id === state.selectedId)) {
    state.selectedId = visible[0]?.id || items()[0]?.id || null;
  }
}

function selectItem(itemId) {
  state.selectedId = itemId;
  saveState();
  render();
}

function renderRuns() {
  const runStrip = document.getElementById("run-strip");
  setChildren(
    runStrip,
    data.lanes.map((lane) => make("span", "run-pill", `${lane.name}: ${lane.items}`)),
  );
}

function option(value, label) {
  const node = document.createElement("option");
  node.value = value;
  node.textContent = label;
  return node;
}

function renderFilterOptions() {
  const laneFilter = document.getElementById("lane-filter");
  const recommendationFilter = document.getElementById("recommendation-filter");
  const lanes = [...new Set(items().map((item) => item.lane))].sort();
  const recommendations = [...new Set(items().map((item) => item.recommendation))].sort();
  setChildren(laneFilter, [option("all", "All lanes"), ...lanes.map((lane) => option(lane, lane))]);
  setChildren(recommendationFilter, [
    option("all", "All dispositions"),
    ...recommendations.map((value) => option(value, titleCase(value))),
  ]);
}

function renderControls() {
  document.getElementById("search-input").value = state.search;
  document.getElementById("lane-filter").value = state.lane;
  document.getElementById("recommendation-filter").value = state.recommendation;
  document.getElementById("gate-filter").value = state.gate;
  document.getElementById("sort-select").value = state.sort;
}

function bindControls() {
  document.getElementById("search-input").addEventListener("input", (event) => {
    state.search = event.target.value;
    saveState();
    render();
  });
  document.getElementById("lane-filter").addEventListener("change", (event) => {
    state.lane = event.target.value;
    saveState();
    render();
  });
  document.getElementById("recommendation-filter").addEventListener("change", (event) => {
    state.recommendation = event.target.value;
    saveState();
    render();
  });
  document.getElementById("gate-filter").addEventListener("change", (event) => {
    state.gate = event.target.value;
    saveState();
    render();
  });
  document.getElementById("sort-select").addEventListener("change", (event) => {
    state.sort = event.target.value;
    saveState();
    render();
  });
}

function renderTabs() {
  document.querySelectorAll("#tabbar button").forEach((button) => {
    button.classList.toggle("active", button.dataset.tab === state.tab);
    button.onclick = () => {
      state.tab = button.dataset.tab;
      if (
        state.tab === "frontier" &&
        !frontierRecords().some((record) => record.item_id === state.selectedId)
      ) {
        state.selectedId = frontierRecords()[0]?.item_id || state.selectedId;
      }
      saveState();
      render();
    };
  });
  document.querySelectorAll("[data-tab-panel]").forEach((panel) => {
    panel.classList.toggle("active", panel.dataset.tabPanel === state.tab);
  });
}

function renderMetrics() {
  const metrics = document.getElementById("metric-cards");
  setChildren(
    metrics,
    data.metric_cards.map((metric) => {
      const card = make("article", "metric-card");
      card.dataset.tone = metric.tone;
      card.append(make("p", null, metric.label));
      card.append(make("strong", null, metric.value));
      card.append(make("span", null, metric.detail));
      return card;
    }),
  );
}

function renderPlainSummary() {
  const slot = document.getElementById("plain-summary");
  const summary = data.plain_summary;
  if (!summary) {
    setChildren(slot, []);
    return;
  }

  const textBlock = make("div", "summary-copy");
  textBlock.append(make("p", "section-label", "Plain Summary"));
  textBlock.append(make("h2", null, summary.headline));
  textBlock.append(make("p", null, summary.lede));

  const list = make("ul", "summary-bullets");
  summary.bullets.forEach((bullet) => {
    list.append(make("li", null, bullet));
  });
  textBlock.append(list);

  const bottomLine = make("aside", "summary-bottom");
  bottomLine.append(make("span", null, "Bottom line"));
  bottomLine.append(make("strong", null, summary.bottom_line));
  setChildren(slot, [textBlock, bottomLine]);
}

function renderSurprisalChart() {
  const slot = document.getElementById("surprisal-chart");
  const rows = [...filteredItems()].sort((a, b) => b.surprisal.score - a.surprisal.score);
  const list = make("div", "surprisal-list");
  rows.forEach((item) => {
    const row = make("button", "surprisal-row");
    row.type = "button";
    row.onclick = () => selectItem(item.id);
    const left = make("div");
    const label = make("span", null, item.short_name);
    const track = make("div", "bar-track");
    const fill = make("div", "bar-fill");
    fill.style.width = `${item.surprisal.score}%`;
    track.append(fill);
    left.append(label, track);
    row.append(left, make("strong", null, item.surprisal.score));
    list.append(row);
  });
  setChildren(slot, rows.length ? [list] : [make("div", "empty-state", "No items match filters.")]);
}

function renderRecommendationChart() {
  const slot = document.getElementById("recommendation-chart");
  const counts = {};
  filteredItems().forEach((item) => {
    counts[item.recommendation] = (counts[item.recommendation] || 0) + 1;
  });
  const entries = Object.entries(counts);
  const total = entries.reduce((sum, [, count]) => sum + count, 0);
  if (!total) {
    setChildren(slot, [make("div", "empty-state", "No dispositions in view.")]);
    return;
  }

  const radius = 45;
  const circumference = 2 * Math.PI * radius;
  let offset = 0;
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("viewBox", "0 0 120 120");
  svg.setAttribute("width", "150");
  svg.setAttribute("height", "150");

  entries.forEach(([, count], index) => {
    const segment = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    const length = (count / total) * circumference;
    segment.setAttribute("cx", "60");
    segment.setAttribute("cy", "60");
    segment.setAttribute("r", radius);
    segment.setAttribute("fill", "none");
    segment.setAttribute("stroke", colors[index % colors.length]);
    segment.setAttribute("stroke-width", "18");
    segment.setAttribute("stroke-dasharray", `${length} ${circumference - length}`);
    segment.setAttribute("stroke-dashoffset", `${-offset}`);
    segment.setAttribute("transform", "rotate(-90 60 60)");
    svg.append(segment);
    offset += length;
  });

  const legend = make("div", "legend");
  entries.forEach(([label, count], index) => {
    const row = make("div", "legend-item");
    const swatch = make("span", "legend-swatch");
    swatch.style.background = colors[index % colors.length];
    row.append(swatch, make("span", null, titleCase(label)), make("strong", null, count));
    legend.append(row);
  });

  const wrap = make("div", "donut-wrap");
  wrap.append(svg, legend);
  setChildren(slot, [wrap]);
}

function renderGateHeatmap(targetId, rows = filteredItems()) {
  const slot = document.getElementById(targetId);
  if (!rows.length) {
    setChildren(slot, [make("div", "empty-state", "No gate rows match filters.")]);
    return;
  }
  const table = make("table", "gate-table");
  const thead = document.createElement("thead");
  const header = document.createElement("tr");
  header.append(make("th", null, "Item"));
  rows[0].gates.forEach((gate) => header.append(make("th", null, gate.label)));
  thead.append(header);

  const tbody = document.createElement("tbody");
  rows.forEach((item) => {
    const row = document.createElement("tr");
    const name = make("button", "table-link", item.short_name);
    name.type = "button";
    name.onclick = () => selectItem(item.id);
    const nameCell = document.createElement("td");
    nameCell.append(name);
    row.append(nameCell);
    item.gates.forEach((gate) => {
      const cell = document.createElement("td");
      const dot = make("button", "gate-cell", gate.status[0].toUpperCase());
      dot.type = "button";
      dot.dataset.status = gate.status;
      dot.title = `${gate.label}: ${text(gate.value)}`;
      dot.onclick = () => selectItem(item.id);
      cell.append(dot);
      row.append(cell);
    });
    tbody.append(row);
  });

  table.append(thead, tbody);
  setChildren(slot, [table]);
}

function itemCard(item) {
  const card = make("article", "candidate-card");
  card.classList.toggle("active", item.id === state.selectedId);
  card.onclick = () => selectItem(item.id);

  const title = make("div", "candidate-title");
  title.append(make("small", null, `${item.lane} / ${titleCase(item.item_type)}`));
  title.append(make("strong", null, item.short_name));
  const chips = make("div", "chip-row");
  const classification = make("span", "chip", item.classification_label);
  classification.dataset.tone = toneForRecommendation(item.recommendation);
  const disposition = make("span", "chip", titleCase(item.recommendation));
  disposition.dataset.tone = toneForRecommendation(item.recommendation);
  chips.append(classification, disposition);
  title.append(chips);

  const status = make("div", "status-line");
  const gateRow = make("div", "gate-row");
  item.gates.forEach((gate) => {
    const chip = make("span", "gate-chip", `${gate.label}: ${titleCase(gate.status)}`);
    chip.dataset.status = toneForStatus(gate.status);
    gateRow.append(chip);
  });
  status.append(gateRow);
  status.append(make("p", null, item.failure_reasons[0] || "evidence tracked"));

  const meter = make("div", "surprisal-meter");
  const score = make("div", "score");
  score.append(make("strong", null, item.surprisal.score));
  score.append(make("span", null, item.surprisal.band));
  const track = make("div", "bar-track");
  const fill = make("div", "bar-fill");
  fill.style.width = `${item.surprisal.score}%`;
  track.append(fill);
  meter.append(score, track);

  card.append(title, status, meter);
  return card;
}

function renderCandidateBoard() {
  const board = document.getElementById("candidate-board");
  const rows = filteredItems();
  const groups = [
    ["discard", "Discard"],
    ["blocked", "Blocked"],
    ["needs_human_review", "Needs Human Review"],
    ["calibration", "Calibration"],
    ["audit", "Audit"],
  ];
  const columns = groups.map(([key, label]) => {
    const column = make("section", "board-column");
    const groupItems = rows.filter((item) => item.recommendation === key);
    const heading = make("div", "board-heading");
    heading.append(make("h2", null, label));
    heading.append(make("span", null, groupItems.length));
    column.append(heading);
    if (groupItems.length) {
      groupItems.forEach((item) => column.append(itemCard(item)));
    } else {
      column.append(make("div", "empty-state", "No items."));
    }
    return column;
  });
  setChildren(board, columns);
}

function frontierCard(record) {
  const item = items().find((entry) => entry.id === record.item_id);
  const card = make("button", "frontier-card");
  card.type = "button";
  card.onclick = () => selectItem(record.item_id);
  card.classList.toggle("active", record.item_id === state.selectedId);

  const heading = make("div", "frontier-heading");
  heading.append(make("small", null, `${record.lane} / ${titleCase(record.potential_status)}`));
  heading.append(make("strong", null, item?.short_name || record.name));

  const priority = make("div", "frontier-priority");
  priority.append(make("span", null, "Priority"));
  priority.append(make("strong", null, record.priority));

  const gaps = make("ul", "frontier-gaps");
  record.gate_gaps.slice(0, 3).forEach((gap) => gaps.append(make("li", null, gap)));

  card.append(heading, priority, make("p", null, record.next_action), gaps);
  return card;
}

function renderFrontierList() {
  const slot = document.getElementById("frontier-list");
  const visibleIds = new Set(filteredItems().map((item) => item.id));
  const rows = frontierRecords().filter((record) => visibleIds.has(record.item_id));
  const process = data.iterative_process;

  const strip = make("div", "process-strip");
  strip.append(
    stat("Process", process?.process_status || "unknown"),
    stat("Frontier", frontierRecords().length),
    stat("Visible", rows.length),
    stat("Stop", process?.stop_reason || "unknown"),
  );

  setChildren(
    slot,
    rows.length
      ? [strip, ...rows.map(frontierCard)]
      : [strip, make("div", "empty-state", "No frontier records match filters.")],
  );
}

function auditCheckRow(check) {
  const row = make("article", "audit-check");
  row.dataset.status = check.status;
  const dot = make("span", "check-dot", check.status[0].toUpperCase());
  dot.dataset.status = check.status;
  const copy = make("div");
  copy.append(make("strong", null, `${check.check_id} ${check.label}`));
  copy.append(make("p", null, check.detail));
  row.append(dot, copy);
  return row;
}

function procedureStepCard(step) {
  const card = make("article", "procedure-step");
  card.append(make("small", null, `${step.step_id} / ${step.owner}`));
  card.append(make("strong", null, step.label));
  card.append(make("p", null, step.completion_rule));
  return card;
}

function renderProcedureAudit() {
  const slot = document.getElementById("procedure-list");
  const audit = procedureAudit();
  const summary = make("div", "process-strip");
  summary.append(
    stat("Procedure", audit.procedure_id || "unknown"),
    stat("Status", audit.status || "unknown"),
    stat("Failures", audit.failure_count ?? 0),
    stat("Warnings", audit.warning_count ?? 0),
  );

  const checks = make("section", "audit-checks");
  (audit.checks || []).forEach((check) => checks.append(auditCheckRow(check)));

  const steps = make("section", "procedure-steps");
  (audit.procedure_steps || []).forEach((step) => steps.append(procedureStepCard(step)));

  setChildren(slot, [summary, checks, steps]);
}

function residualGrid(grid) {
  if (!grid) return make("div", "empty-state", "No residual grid recorded.");
  const wrapper = make("div", "residual-grid");
  grid.forEach((row) => {
    row.forEach((value) => {
      const cell = make("span", "residual-cell", value);
      cell.dataset.status = value === "OK" ? "pass" : "fail";
      wrapper.append(cell);
    });
  });
  return wrapper;
}

function artifactCard(item) {
  const card = make("button", "artifact-card");
  card.type = "button";
  card.onclick = () => selectItem(item.id);
  card.classList.toggle("active", item.id === state.selectedId);
  card.append(make("strong", null, item.short_name));
  card.append(make("span", null, `${item.curvature_terms_nonzero} unresolved terms`));
  card.append(residualGrid(item.residual_grid));
  return card;
}

function renderArtifactList() {
  const slot = document.getElementById("artifact-list");
  const artifactItems = filteredItems().filter((item) => item.proof_summary || item.residual_grid);
  setChildren(
    slot,
    artifactItems.length
      ? artifactItems.map(artifactCard)
      : [make("div", "empty-state", "No artifacts match filters.")],
  );
}

function renderCollisionMap() {
  const slot = document.getElementById("collision-map");
  const visibleIds = new Set(filteredItems().map((item) => item.id));
  const families = data.collision_family_map
    .map((family) => ({
      ...family,
      item_ids: family.item_ids.filter((id) => visibleIds.has(id)),
    }))
    .filter((family) => family.item_ids.length);

  if (!families.length) {
    setChildren(slot, [make("div", "empty-state", "No collision families in view.")]);
    return;
  }

  const max = Math.max(...families.map((family) => family.item_ids.length));
  const nodes = families.map((family, index) => {
    const row = make("button", "collision-family");
    row.type = "button";
    row.onclick = () => {
      state.selectedFamily = family.family;
      state.selectedId = family.item_ids[0] || state.selectedId;
      saveState();
      render();
    };
    row.classList.toggle("active", family.family === state.selectedFamily);
    const swatch = make("span", "legend-swatch");
    swatch.style.background = colors[index % colors.length];
    const label = make("strong", null, family.family);
    const count = make("span", null, `${family.item_ids.length}`);
    const track = make("div", "bar-track");
    const fill = make("div", "bar-fill");
    fill.style.width = `${(family.item_ids.length / max) * 100}%`;
    track.append(fill);
    row.append(swatch, label, count, track);
    return row;
  });
  setChildren(slot, nodes);
}

function stat(label, value) {
  const item = make("div", "detail-stat");
  item.append(make("span", "detail-kicker", label));
  item.append(make("strong", null, text(value)));
  return item;
}

function listBlock(label, values) {
  const fragment = document.createDocumentFragment();
  fragment.append(make("p", "section-label", label));
  const list = make("ul", "detail-list");
  (values && values.length ? values : ["none recorded"]).forEach((value) => {
    list.append(make("li", null, value));
  });
  fragment.append(list);
  return fragment;
}

function renderProofSummary(item) {
  if (!item.proof_summary) return null;
  const summary = item.proof_summary;
  const block = make("div", "proof-block");
  block.append(make("p", "section-label", "Proof Summary"));
  const grid = make("div", "detail-grid");
  grid.append(
    stat("Convention", summary.curvature_convention),
    stat("Shape", summary.matrix_shape.join(" x ")),
    stat("Basis", summary.coefficient_basis.join(", ")),
    stat("Residual Zero", summary.residual_zero),
  );
  block.append(grid);
  block.append(residualGrid(summary.entry_status_grid));
  return block;
}

function zcrLines(item) {
  const lines = [];
  if (item.zcr_validated) {
    lines.push(`solution ${JSON.stringify(item.zcr_solution)}`);
  }
  if (item.cyclic_fingerprint) {
    lines.push(item.cyclic_fingerprint);
  }
  (item.zcr_obstruction_basis || []).forEach((term) => lines.push(term));
  (item.zcr_constraints || []).forEach((constraint) => lines.push(constraint));
  return lines;
}

function selectedFrontierRecord(item) {
  if (!item) return null;
  return frontierRecords().find((record) => record.item_id === item.id) || null;
}

function frontierDetailNodes(item) {
  const baseNodes = detailNodes(item);
  const record = selectedFrontierRecord(item);
  if (!record) {
    return [
      make("p", "detail-kicker", "Discovery Frontier"),
      make("h2", null, "No active frontier action"),
      ...baseNodes,
    ];
  }

  const processGrid = make("div", "detail-grid");
  processGrid.append(
    stat("Frontier Status", titleCase(record.potential_status)),
    stat("Priority", record.priority),
    stat("Iteration", record.iteration),
    stat("Lane", record.lane),
  );

  return [
    make("p", "detail-kicker", "Discovery Frontier"),
    make("h2", null, record.name),
    processGrid,
    listBlock("Next Action", [record.next_action]),
    listBlock("Gate Gaps", record.gate_gaps),
    listBlock("Evidence Summary", record.evidence_summary),
    ...baseNodes,
  ];
}

function procedureDetailNodes() {
  const audit = procedureAudit();
  const grid = make("div", "detail-grid");
  grid.append(
    stat("Status", audit.status || "unknown"),
    stat("Failures", audit.failure_count ?? 0),
    stat("Warnings", audit.warning_count ?? 0),
    stat("Checks", (audit.checks || []).length),
  );
  const stepLabels = (audit.procedure_steps || []).map(
    (step) => `${step.step_id} ${step.label}: ${step.completion_rule}`,
  );
  const checkLabels = (audit.checks || []).map(
    (check) => `${check.check_id} ${titleCase(check.status)}: ${check.detail}`,
  );
  return [
    make("p", "detail-kicker", "Procedure Audit"),
    make("h2", null, audit.title || "Procedure audit"),
    grid,
    listBlock("Summary", [audit.summary || "no summary recorded"]),
    listBlock("Formal Steps", stepLabels),
    listBlock("Audit Checks", checkLabels),
  ];
}

function detailNodes(item) {
  if (!item) return [make("div", "empty-state", "No item selected.")];
  const heading = document.createDocumentFragment();
  heading.append(make("p", "detail-kicker", `${item.lane} / ${titleCase(item.item_type)}`));
  heading.append(make("h2", null, item.name));

  const detailGrid = make("div", "detail-grid");
  detailGrid.append(
    stat("Surprisal", `${item.surprisal.score} / ${item.surprisal.band}`),
    stat("Disposition", titleCase(item.recommendation)),
    stat("Connection", item.connection_status),
    stat("Curvature", item.curvature_status),
    stat("Gauge Risk", item.gauge_risk_score ?? "not attempted"),
    stat("Spectral", item.spectral_status),
  );

  const gateRow = make("div", "gate-row");
  item.gates.forEach((gate) => {
    const chip = make("span", "gate-chip", `${gate.label}: ${titleCase(gate.status)}`);
    chip.dataset.status = gate.status;
    chip.title = text(gate.value);
    gateRow.append(chip);
  });

  const proof = renderProofSummary(item);
  return [
    heading,
    detailGrid,
    gateRow,
    proof,
    listBlock("Surprisal Drivers", item.surprisal.drivers),
    listBlock("Collision Report", item.collisions),
    listBlock("Collision Families", item.collision_families),
    listBlock("ZCR Evidence", zcrLines(item)),
    listBlock("Failure Reasons", item.failure_reasons),
  ].filter(Boolean);
}

function renderDetails() {
  const selected = currentSelection();
  [
    "candidate-detail-panel",
    "gate-detail-panel",
    "artifact-detail-panel",
  ].forEach((id) => setChildren(document.getElementById(id), detailNodes(selected)));
  setChildren(document.getElementById("frontier-detail-panel"), frontierDetailNodes(selected));
  setChildren(document.getElementById("procedure-detail-panel"), procedureDetailNodes());

  const collisionPanel = document.getElementById("collision-detail-panel");
  if (state.selectedFamily) {
    const related = items().filter((item) =>
      (item.collision_families || []).includes(state.selectedFamily),
    );
    const heading = document.createDocumentFragment();
    heading.append(make("p", "detail-kicker", "Collision Family"));
    heading.append(make("h2", null, state.selectedFamily));
    const names = related.map((item) => `${item.short_name}: ${titleCase(item.recommendation)}`);
    setChildren(collisionPanel, [heading, listBlock("Tracked Items", names), ...detailNodes(selected)]);
  } else {
    setChildren(collisionPanel, detailNodes(selected));
  }
}

function render() {
  ensureSelected();
  renderTabs();
  renderControls();
  renderPlainSummary();
  renderMetrics();
  renderSurprisalChart();
  renderRecommendationChart();
  renderGateHeatmap("overview-gate-heatmap");
  renderGateHeatmap("gate-heatmap");
  renderCandidateBoard();
  renderFrontierList();
  renderProcedureAudit();
  renderArtifactList();
  renderCollisionMap();
  renderDetails();
}

function boot() {
  if (!data) {
    document.body.textContent = "Dashboard data missing.";
    return;
  }
  document.title = data.title;
  renderRuns();
  renderFilterOptions();
  bindControls();
  state.selectedId =
    state.selectedId ||
    items().find((item) => item.zcr_validated)?.id ||
    items()[0]?.id ||
    null;
  render();
}

boot();
