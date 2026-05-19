const DATA_URL = "campaign_monitor_data.json";
const POLL_MS = 2500;

const $ = (id) => document.getElementById(id);

function formatNumber(value) {
  return Number(value || 0).toLocaleString();
}

function setText(id, value) {
  const node = $(id);
  if (node) node.textContent = value;
}

function esc(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function connection(state, label) {
  const pill = $("connection-pill");
  if (!pill) return;
  pill.className = `pill ${state}`;
  pill.textContent = label;
}

function entries(map) {
  return Object.entries(map || {}).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
}

function renderBars(id, map) {
  const host = $(id);
  if (!host) return;
  const rows = entries(map);
  const total = rows.reduce((sum, [, count]) => sum + count, 0) || 1;
  host.innerHTML = rows
    .map(([label, count]) => {
      const width = Math.max(2, (count / total) * 100);
      return `
        <div class="bar-row">
          <div class="bar-meta">
            <span>${esc(label)}</span>
            <strong>${formatNumber(count)}</strong>
          </div>
          <div class="bar-track" aria-hidden="true">
            <div class="bar-fill" style="width:${width}%"></div>
          </div>
        </div>
      `;
    })
    .join("");
}

function tagClass(value) {
  if (value === true || value === "validated_known_collision") return "good";
  if (String(value || "").includes("blocked")) return "warn";
  if (String(value || "").includes("discard")) return "stop";
  return "";
}

function renderAttempts(attempts) {
  const host = $("attempt-stream");
  if (!host) return;
  const rows = attempts || [];
  host.innerHTML = rows
    .slice()
    .reverse()
    .map((attempt) => {
      const reasons = (attempt.failure_reasons || []).slice(0, 2).join(" ");
      return `
        <article class="attempt">
          <div>
            <h3>${esc(attempt.candidate_name || "unnamed candidate")}</h3>
            <p>${esc(attempt.descriptor || "")}</p>
            <p>${esc(reasons)}</p>
          </div>
          <div class="tags">
            <span class="tag ${tagClass(attempt.attempt_status)}">${esc(attempt.attempt_status)}</span>
            <span class="tag">${esc(attempt.family)}</span>
            <span class="tag">order ${esc(attempt.order ?? "?")}</span>
            <span class="tag">${esc(attempt.formal_ansatz_status || "formal n/a")}</span>
          </div>
        </article>
      `;
    })
    .join("");
}

function render(payload) {
  const counts = payload.counts || {};
  const statusCounts = counts.attempt_status || {};
  setText("metric-attempts", formatNumber(payload.attempt_count));
  setText("metric-candidates", formatNumber(payload.candidate_count));
  setText("metric-rounds", formatNumber(payload.rounds_completed));
  setText("metric-survivors", formatNumber(counts.automated_survivors));
  setText("metric-collisions", formatNumber(counts.known_collision));
  setText("metric-validated", formatNumber(counts.validated_zcr));
  setText("run-id", payload.run_id || "run pending");
  setText("run-status", `Status: ${payload.status || "unknown"}`);
  setText("updated-at", `updated ${payload.updated_at || "pending"}`);
  setText("guard-note", (payload.language_guard && payload.language_guard.note) || "");
  setText("output-dir", payload.output_dir || "");

  const hasSurvivor = Number(counts.automated_survivors || 0) > 0;
  connection(payload.status === "running" ? "pass" : hasSurvivor ? "warn" : "fail", payload.status || "offline");
  renderBars("status-bars", statusCounts);
  renderBars("formal-bars", counts.formal_ansatz_status || {});
  renderBars("family-bars", counts.family || {});
  renderAttempts(payload.latest_attempts || []);
}

async function refresh() {
  try {
    const response = await fetch(`${DATA_URL}?t=${Date.now()}`, { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const payload = await response.json();
    render(payload);
  } catch (error) {
    connection("fail", "waiting");
    setText("run-status", `Monitor snapshot unavailable: ${error.message}`);
  }
}

refresh();
window.setInterval(refresh, POLL_MS);
