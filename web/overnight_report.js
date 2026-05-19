const overnightData = window.LAXFORGE_OVERNIGHT_DATA || {};
const candidates = overnightData.candidates || [];
const actionQueue = overnightData.action_queue || [];

const state = {
  search: localStorage.getItem("overnight.search") || "",
  family: localStorage.getItem("overnight.family") || "all",
  order: localStorage.getItem("overnight.order") || "all",
  sort: localStorage.getItem("overnight.sort") || "surprisal",
};

function make(tag, className, text) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  if (text !== undefined) element.textContent = text;
  return element;
}

function titleCase(value) {
  return String(value)
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function countWhere(predicate) {
  return candidates.filter(predicate).length;
}

function maxValue(values) {
  return values.length ? Math.max(...values) : 0;
}

function recommendationCount(name) {
  return overnightData.recommendation_counts?.[name] || 0;
}

function queueTopScore() {
  return maxValue(actionQueue.map((candidate) => candidate.audit_surprisal?.score || 0));
}

function renderReadout() {
  const slot = document.getElementById("executive-readout");
  const review = recommendationCount("needs_human_review");
  const discard = recommendationCount("discard");
  const highOrder = countWhere((candidate) => candidate.order >= 6);
  const crossAtom = countWhere((candidate) => String(candidate.vector_atom).includes("cross"));

  const narrative = make("div");
  narrative.append(
    make(
      "p",
      null,
      `OVERNIGHT-001 generated ${candidates.length} deterministic sphere-tangent descriptors. ${review} remain review-only and ${discard} are discard controls. This is a wide search pass, not a solved-pair result.`
    )
  );
  narrative.append(
    make(
      "p",
      null,
      `The mathematical guarantee in this batch is narrow but real: every non-control target has the form s x A, so it is tangent to the unit sphere constraint. The zero-curvature, spectral, gauge, cyclic, conservation, and Hamiltonian gates are still open until a candidate-specific ansatz is run.`
    )
  );
  narrative.append(
    make(
      "p",
      null,
      `${highOrder} descriptors reach derivative order six or higher, and ${crossAtom} descriptors use nested cross-product vector atoms. Those two features drive the audit-surprisal ranking because they create richer solver pressure, while also increasing collision and reducibility risk.`
    )
  );

  const verdict = make("aside", "plain-verdict");
  verdict.append(make("span", "eyebrow", "Plain result"));
  verdict.append(make("strong", null, "Frontier active"));
  verdict.append(
    make(
      "p",
      null,
      "The honest next step is a stratified solver pass on the action queue, followed immediately by reduction, cyclic, spectral, conservation, and collision checks."
    )
  );

  slot.replaceChildren(narrative, verdict);
}

function renderMetrics() {
  const slot = document.getElementById("metric-grid");
  const highOrder = countWhere((candidate) => candidate.order >= 6);
  const nestedCross = countWhere((candidate) => String(candidate.vector_atom).includes("cross"));
  const families = Object.keys(overnightData.family_counts || {}).length;
  const topScore = queueTopScore();
  const metrics = [
    ["Candidates", candidates.length, "deterministic descriptors", "pass"],
    ["Review", recommendationCount("needs_human_review"), "open solver gates", "warn"],
    ["Discard", recommendationCount("discard"), "control records", "fail"],
    ["Action queue", actionQueue.length, "ranked for solver work", "inspect"],
    ["Families", families, "descriptor families", "inspect"],
    ["High order", highOrder, "order six or higher", "warn"],
    ["Nested cross", nestedCross, "cross-product vector atoms", "warn"],
    ["Top surprisal", topScore, "audit triage score", "inspect"],
    ["Tangent pass", overnightData.gate_counts?.tangent?.pass || 0, "sphere constraint", "pass"],
    ["Curvature open", overnightData.gate_counts?.curvature?.warn || 0, "matrix pairs absent", "warn"],
    ["Spectral open", overnightData.gate_counts?.spectral?.warn || 0, "parameter unresolved", "warn"],
    ["Status", titleCase(overnightData.status || "unknown"), "process state", "inspect"],
  ];

  slot.replaceChildren(
    ...metrics.map(([label, value, detail, tone]) => {
      const card = make("article", "metric-card");
      card.dataset.tone = tone;
      card.append(make("span", null, label));
      card.append(make("strong", null, value));
      card.append(make("small", null, detail));
      return card;
    })
  );
}

function renderNotes() {
  const notes = document.getElementById("analysis-notes");
  notes.append(make("p", "eyebrow", "Analysis"));
  notes.append(make("h2", null, "What the wide pass actually says"));
  const list = make("ul");
  (overnightData.analysis_notes || []).forEach((note) => list.append(make("li", null, note)));
  notes.append(list);

  const actions = document.getElementById("next-actions");
  actions.append(make("p", "eyebrow", "Procedure"));
  actions.append(make("h2", null, "Next honest tests"));
  const ordered = make("ol");
  (overnightData.next_actions || []).forEach((action) => ordered.append(make("li", null, action)));
  actions.append(ordered);
}

function renderBars(containerId, counts) {
  const slot = document.getElementById(containerId);
  const entries = Object.entries(counts || {}).sort((left, right) => right[1] - left[1]);
  const maxCount = maxValue(entries.map(([, count]) => count));
  slot.replaceChildren(
    ...entries.map(([label, count]) => {
      const row = make("div", "bar-row");
      const track = make("div", "bar-track");
      const fill = make("div", "bar-fill");
      fill.style.width = `${maxCount ? (count / maxCount) * 100 : 0}%`;
      track.append(fill);
      row.append(make("div", "bar-label", titleCase(label)));
      row.append(track);
      row.append(make("div", "bar-value", count));
      return row;
    })
  );
}

function renderGates() {
  const slot = document.getElementById("gate-grid");
  const entries = Object.entries(overnightData.gate_counts || {});
  slot.replaceChildren(
    ...entries.map(([gate, counts]) => {
      const tile = make("article", "gate-tile");
      const countList = make("div", "gate-counts");
      ["pass", "warn", "fail"].forEach((status) => {
        const row = make("span");
        row.append(make("em", null, titleCase(status)));
        row.append(make("strong", null, counts[status] || 0));
        countList.append(row);
      });
      tile.append(make("h3", null, titleCase(gate)));
      tile.append(countList);
      return tile;
    })
  );
}

function renderQueue() {
  const slot = document.getElementById("action-queue");
  const cards = actionQueue.slice(0, 24).map((candidate, index) => {
    const card = make("article", "queue-card");
    const pills = make("div", "pill-row");
    pills.append(make("span", "pill", candidate.family));
    pills.append(make("span", "pill", `order ${candidate.order}`));
    pills.append(make("span", "pill", `score ${candidate.audit_surprisal?.score || 0}`));
    const drivers = make("div", "driver-list");
    (candidate.audit_surprisal?.drivers || []).forEach((driver) =>
      drivers.append(make("span", null, driver))
    );
    card.append(make("p", "eyebrow", `Queue ${index + 1}`));
    card.append(make("h3", null, candidate.name.replace("overnight sphere ", "")));
    card.append(pills);
    card.append(make("p", null, candidate.descriptor));
    card.append(drivers);
    return card;
  });
  slot.replaceChildren(...cards);
}

function populateFilters() {
  const familySelect = document.getElementById("family-filter");
  const orderSelect = document.getElementById("order-filter");
  const searchInput = document.getElementById("search-input");
  const sortSelect = document.getElementById("sort-select");

  const familyOptions = ["all", ...Object.keys(overnightData.family_counts || {}).sort()];
  familySelect.replaceChildren(
    ...familyOptions.map((family) => {
      const option = make("option", null, family === "all" ? "All families" : titleCase(family));
      option.value = family;
      return option;
    })
  );

  const orderOptions = ["all", ...Object.keys(overnightData.order_counts || {}).sort((a, b) => Number(a) - Number(b))];
  orderSelect.replaceChildren(
    ...orderOptions.map((order) => {
      const option = make("option", null, order === "all" ? "All orders" : `Order ${order}`);
      option.value = order;
      return option;
    })
  );

  searchInput.value = state.search;
  familySelect.value = state.family;
  orderSelect.value = state.order;
  sortSelect.value = state.sort;

  searchInput.addEventListener("input", () => {
    state.search = searchInput.value;
    localStorage.setItem("overnight.search", state.search);
    renderTable();
  });
  familySelect.addEventListener("change", () => {
    state.family = familySelect.value;
    localStorage.setItem("overnight.family", state.family);
    renderTable();
  });
  orderSelect.addEventListener("change", () => {
    state.order = orderSelect.value;
    localStorage.setItem("overnight.order", state.order);
    renderTable();
  });
  sortSelect.addEventListener("change", () => {
    state.sort = sortSelect.value;
    localStorage.setItem("overnight.sort", state.sort);
    renderTable();
  });
}

function filteredCandidates() {
  const query = state.search.trim().toLowerCase();
  return candidates
    .filter((candidate) => state.family === "all" || candidate.family === state.family)
    .filter((candidate) => state.order === "all" || String(candidate.order) === state.order)
    .filter((candidate) => {
      if (!query) return true;
      return `${candidate.name} ${candidate.descriptor} ${candidate.family}`.toLowerCase().includes(query);
    })
    .sort((left, right) => {
      if (state.sort === "priority") return right.priority_score - left.priority_score;
      if (state.sort === "order") return right.order - left.order || left.name.localeCompare(right.name);
      if (state.sort === "name") return left.name.localeCompare(right.name);
      return (
        (right.audit_surprisal?.score || 0) - (left.audit_surprisal?.score || 0) ||
        right.priority_score - left.priority_score ||
        left.name.localeCompare(right.name)
      );
    });
}

function renderTable() {
  const slot = document.getElementById("candidate-table");
  const table = make("table");
  const head = document.createElement("thead");
  const headRow = document.createElement("tr");
  ["Candidate", "Family", "Order", "Score", "Descriptor", "Gate status"].forEach((label) =>
    headRow.append(make("th", null, label))
  );
  head.append(headRow);

  const body = document.createElement("tbody");
  filteredCandidates()
    .slice(0, 180)
    .forEach((candidate) => {
      const row = document.createElement("tr");
      row.append(make("td", null, candidate.name.replace("overnight sphere ", "")));
      row.append(make("td", null, titleCase(candidate.family)));
      row.append(make("td", null, candidate.order));
      row.append(make("td", null, candidate.audit_surprisal?.score || 0));
      row.append(make("td", null, candidate.descriptor));
      row.append(make("td", null, candidate.connection_status));
      body.append(row);
    });
  table.append(head, body);
  slot.replaceChildren(table);
}

function init() {
  renderReadout();
  renderMetrics();
  renderNotes();
  renderBars("family-bars", overnightData.family_counts);
  renderBars("order-bars", overnightData.order_counts);
  renderGates();
  renderQueue();
  populateFilters();
  renderTable();
}

init();
