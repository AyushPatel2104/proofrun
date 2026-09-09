import { createArrayRenderer } from "./renderers/array.js";
import { createPlayer } from "./player.js";

const canvas = document.getElementById("arrayCanvas");
const renderer = createArrayRenderer(canvas);
const timeline = document.getElementById("timeline");
const inspector = document.getElementById("inspector");

let catalog = [];
let lastRun = null;
let hasTrace = false;

function setTheme(theme) {
  const next = theme === "light" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", next);
  try {
    localStorage.setItem("proofrun-theme", next);
  } catch {
    /* ignore */
  }
  document.getElementById("themeToggle").setAttribute(
    "aria-label",
    next === "dark" ? "Switch to light theme" : "Switch to dark theme"
  );
  document.documentElement.dispatchEvent(new CustomEvent("proofrun:theme"));
  if (hasTrace) {
    canvas._theme = "";
    canvas._cssW = 0;
  }
}

function setExecStatus(text) {
  const el = document.getElementById("execStatus");
  if (el) el.textContent = text;
}

function setVizActive(active) {
  hasTrace = active;
  document.getElementById("vizEmpty").hidden = active;
  canvas.hidden = !active;
  document.getElementById("timelineEmpty").hidden = active;
  timeline.hidden = !active;
  document.getElementById("inspectorEmpty").hidden = active;
  inspector.hidden = !active;
  setExecStatus(active ? "Trace loaded" : "Idle");
}

function humanEventDescription(event) {
  if (!event) return "";
  const type = (event.type || "").toLowerCase();
  const msg = (event.message || "").trim();
  const p = event.payload || {};

  if (type.includes("compare") || type === "compare") {
    if (typeof p.i === "number" && typeof p.j === "number") {
      return `Comparing indices ${p.i} and ${p.j}`;
    }
  }
  if (type.includes("swap") || type === "swap") {
    if (typeof p.i === "number" && typeof p.j === "number") {
      return `Swapping indices ${p.i} and ${p.j}`;
    }
  }
  if (
    typeof p.index === "number" &&
    (type.includes("probe") || type.includes("visit") || type.includes("check"))
  ) {
    return `Probing index ${p.index}`;
  }
  if (msg) return msg.charAt(0).toUpperCase() + msg.slice(1);
  return type ? type.replace(/_/g, " ") : "Event";
}

function setComplexity(c) {
  c = c || {};
  document.getElementById("cxBest").textContent = c.best || "—";
  document.getElementById("cxAvg").textContent = c.avg || "—";
  document.getElementById("cxWorst").textContent = c.worst || "—";
  document.getElementById("cxMem").textContent = c.memory || "—";
  document.getElementById("complexity").textContent =
    `best ${c.best || "?"}, avg ${c.avg || "?"}, worst ${c.worst || "?"}, memory ${c.memory || "?"}`;
}

function setProveUI(status, detail, method) {
  const badge = document.getElementById("proveStatus");
  const methodEl = document.getElementById("proveMethod");
  const detailEl = document.getElementById("proveDetail");

  if (status === "PASS") {
    badge.textContent = "✓ Verified";
    badge.className = "status-badge ok";
    methodEl.textContent = "Output matches independent reference";
    if (method) methodEl.textContent = `${methodEl.textContent} · ${method}`;
  } else if (status === "FAIL") {
    badge.textContent = "✗ Failed verification";
    badge.className = "status-badge bad";
    methodEl.textContent = method || "Independent oracle comparison";
  } else if (status === "NOT_AVAILABLE") {
    badge.textContent = "Not available";
    badge.className = "status-badge warn";
    methodEl.textContent = "Demo replay — live Prove requires Run";
  } else {
    badge.textContent = "Awaiting run";
    badge.className = "status-badge idle";
    methodEl.textContent = "Independent oracle comparison";
  }
  detailEl.textContent = detail || "";
}

function renderTimeline(events, activeIndex) {
  timeline.innerHTML = "";
  (events || []).forEach((e, i) => {
    const li = document.createElement("li");
    li.className = "timeline-item" + (i === activeIndex ? " active" : "");
    li.setAttribute("aria-current", i === activeIndex ? "step" : "false");

    const step = document.createElement("span");
    step.className = "tl-step";
    step.textContent = String(e.step != null ? e.step : i);

    const type = document.createElement("span");
    type.className = "tl-type";
    type.textContent = (e.type || "event").replace(/_/g, " ");

    const msg = document.createElement("span");
    msg.className = "tl-msg";
    msg.textContent = humanEventDescription(e);

    li.appendChild(step);
    li.appendChild(type);
    li.appendChild(msg);
    timeline.appendChild(li);
  });

  const active = timeline.querySelector(".timeline-item.active");
  if (active) active.scrollIntoView({ block: "nearest", behavior: "smooth" });
}

const player = createPlayer({
  onFrame: ({ state, highlights, event, index, total, trace }) => {
    if (!hasTrace) setVizActive(true);
    renderer.render(state, highlights, { eventType: event && event.type });

    const name =
      (trace.manifestSnapshot && trace.manifestSnapshot.name) || trace.algorithmId || "—";
    if (!lastRun) document.getElementById("algoName").textContent = name;
    const c = (trace.manifestSnapshot && trace.manifestSnapshot.complexity) || {};
    if (!lastRun) setComplexity(c);

    document.getElementById("stepInfo").textContent =
      index < 0 ? `Ready · ${total} events` : `Step ${index + 1} / ${total}`;
    document.getElementById("eventInfo").textContent = humanEventDescription(event);
    setExecStatus(index < 0 ? "Ready" : `Step ${index + 1}/${total}`);

    if (!lastRun) document.getElementById("eventCount").textContent = String(total);

    inspector.textContent = JSON.stringify(
      {
        step: event && event.step,
        type: event && event.type,
        message: event && event.message,
        state,
        payload: event && event.payload,
      },
      null,
      2
    );

    renderTimeline(trace.events || [], index);
  },
});

function showError(msg) {
  const el = document.getElementById("formError");
  if (!msg) {
    el.hidden = true;
    el.textContent = "";
    return;
  }
  el.hidden = false;
  el.textContent = msg;
}

function setBusy(which, busy, okText) {
  const el = document.getElementById("runStatus");
  const runBtn = document.getElementById("btnRun");
  const benchBtn = document.getElementById("btnBench");
  if (which === "run") {
    runBtn.disabled = busy;
    runBtn.classList.toggle("is-loading", busy);
    el.textContent = busy ? "Running…" : okText || "";
    el.className = "inline-status" + (busy ? " busy" : okText ? " ok" : "");
    setExecStatus(busy ? "Running" : okText ? "Complete" : "Idle");
  }
  if (which === "bench") {
    benchBtn.disabled = busy;
    const status = document.getElementById("benchStatus");
    if (busy) {
      status.textContent = "Running controlled repeats…";
      status.className = "measure-value";
    }
  }
}

function selectedAlgo() {
  return catalog.find((a) => a.id === document.getElementById("algoSelect").value);
}

function updateAlgoContext() {
  const algo = selectedAlgo();
  document.getElementById("algoContextName").textContent = (algo && algo.name) || "—";
  document.getElementById("algoContextFamily").textContent = (algo && algo.family) || "—";
  document.getElementById("explanation").textContent = (algo && algo.explanation) || "";
  const mini = document.getElementById("algoComplexityMini");
  mini.innerHTML = "";
  const c = (algo && algo.complexity) || {};
  for (const [label, key] of [
    ["Best", "best"],
    ["Avg", "avg"],
    ["Worst", "worst"],
    ["Space", "memory"],
  ]) {
    const wrap = document.createElement("div");
    const dt = document.createElement("dt");
    dt.textContent = label;
    const dd = document.createElement("dd");
    dd.textContent = c[key] || "—";
    wrap.appendChild(dt);
    wrap.appendChild(dd);
    mini.appendChild(wrap);
  }
}

function renderLegend(algo) {
  const box = document.getElementById("legend");
  box.innerHTML = "";
  const items = (algo && algo.params && algo.params.legend) || [];
  if (!items.length) {
    box.innerHTML = "<span class=\"field-hint\">Legend updates with the selected algorithm.</span>";
    return;
  }
  const title = document.createElement("div");
  title.className = "legend-title";
  title.textContent = "Highlight legend";
  box.appendChild(title);
  for (const item of items) {
    const row = document.createElement("div");
    row.className = "legend-item";
    const sw = document.createElement("span");
    sw.className = `swatch ${item.swatch || "accent"}`;
    const lab = document.createElement("span");
    lab.textContent = item.label;
    row.appendChild(sw);
    row.appendChild(lab);
    box.appendChild(row);
  }
}

function renderParams() {
  const algo = selectedAlgo();
  const box = document.getElementById("paramFields");
  box.innerHTML = "";
  const pre = document.getElementById("precondition");
  pre.textContent = (algo && algo.params && algo.params.precondition) || "";
  pre.hidden = !pre.textContent;
  updateAlgoContext();
  renderLegend(algo);
  if (!algo) return;
  for (const field of algo.params.fields || []) {
    const label = document.createElement("label");
    label.className = "field";
    label.htmlFor = `param_${field.name}`;
    label.appendChild(document.createTextNode(field.label));
    const input = document.createElement("input");
    input.type = "number";
    input.id = `param_${field.name}`;
    input.dataset.param = field.name;
    input.required = true;
    input.setAttribute("aria-label", field.label);
    label.appendChild(input);
    box.appendChild(label);
  }
}

function collectParams() {
  const params = {};
  document.querySelectorAll("#paramFields input[data-param]").forEach((el) => {
    if (el.value !== "") params[el.dataset.param] = Number(el.value);
  });
  return params;
}

function setParams(params) {
  if (!params) return;
  for (const [k, v] of Object.entries(params)) {
    const el = document.getElementById(`param_${k}`);
    if (el) el.value = v;
  }
}

function formatResult(result) {
  if (!result) return "—";
  if (result.kind === "array") return result.value.join(", ") || "(empty)";
  if (result.kind === "index") return result.found ? `index ${result.value}` : "not found (−1)";
  if (result.kind === "pair") {
    return result.found ? `pair (${result.left}, ${result.right})` : "no pair";
  }
  if (result.kind === "window") {
    return `maxSum=${result.maxSum} window=[${result.start}, ${result.end}]`;
  }
  if (result.kind === "rangeSum") {
    return `sum(a[${result.left}..${result.right}]) = ${result.value}`;
  }
  return JSON.stringify(result);
}

function inputSummaryText(values, params) {
  const n = values ? values.length : 0;
  const head = values && values.length
    ? values.slice(0, 12).join(",") + (values.length > 12 ? ",…" : "")
    : "(empty)";
  const extras = [];
  if (params && params.target != null) extras.push(`target=${params.target}`);
  if (params && params.window != null) extras.push(`K=${params.window}`);
  if (params && params.left != null) extras.push(`L=${params.left}`);
  if (params && params.right != null) extras.push(`R=${params.right}`);
  return `n=${n} [${head}]${extras.length ? " · " + extras.join(" · ") : ""}`;
}

function applyRunResponse(data) {
  lastRun = data;
  if (data.trace) {
    setVizActive(true);
    player.load(data.trace);
  }
  document.getElementById("algoName").textContent =
    (data.algorithm && data.algorithm.name) || "—";
  document.getElementById("inputSummary").textContent = inputSummaryText(
    data.input,
    data.params
  );
  document.getElementById("resultText").textContent = formatResult(data.result);
  const st = data.correctness && data.correctness.status;
  setProveUI(
    st,
    (data.correctness && data.correctness.detail) || "",
    (data.correctness && data.correctness.method) || ""
  );
  setComplexity((data.algorithm && data.algorithm.complexity) || {});
  const events = data.trace && data.trace.events ? data.trace.events.length : 0;
  document.getElementById("eventCount").textContent = String(events);
  const ms = data.measure && data.measure.interactive && data.measure.interactive.runtime_s;
  const timing = document.getElementById("interactiveTiming");
  timing.className = "measure-value";
  timing.textContent = ms != null
    ? `${(ms * 1000).toFixed(2)} ms (n=${data.measure.interactive.n})`
    : "—";
  const benchStatus = document.getElementById("benchStatus");
  benchStatus.className = "measure-value";
  benchStatus.textContent = "Ready — separate from interactive timing";
  document.getElementById("benchOut").hidden = true;
  document.getElementById("benchOut").textContent = "";
}

async function api(path, options) {
  const res = await fetch(path, options);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data.error || `Request failed (${res.status})`);
  }
  return data;
}

async function initCatalog() {
  const data = await api("/api/catalog");
  catalog = data.algorithms || [];
  const sel = document.getElementById("algoSelect");
  sel.innerHTML = "";
  for (const a of catalog) {
    const opt = document.createElement("option");
    opt.value = a.id;
    opt.textContent = `${a.name} (${a.family})`;
    sel.appendChild(opt);
  }
  sel.onchange = renderParams;
  renderParams();
}

async function checkHealth() {
  const el = document.getElementById("serverStatus");
  try {
    const h = await api("/api/health");
    el.textContent = h.ok ? "Local Engine · ready" : (h.message || "Engine missing");
    el.title = h.message || "";
    el.className = h.ok ? "engine-pill ok-text" : "engine-pill error";
  } catch {
    el.textContent = "Engine offline";
    el.title = "Start with: powershell -File scripts/run_product.ps1";
    el.className = "engine-pill error";
  }
}

async function loadDemoTrace(url, algoId) {
  showError("");
  lastRun = null;
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(
      "Could not load demo trace.\nWhy: the canned file is missing or unreachable.\nFix: use Run for live traces."
    );
  }
  const trace = await res.json();
  setVizActive(true);
  player.load(trace);
  document.getElementById("algoName").textContent =
    (trace.manifestSnapshot && trace.manifestSnapshot.name) || trace.algorithmId;
  document.getElementById("inputSummary").textContent = "canned demo (replay)";
  document.getElementById("resultText").textContent = "Canned demo loaded (replay only).";
  setProveUI(
    "NOT_AVAILABLE",
    "Demo replay does not re-run correctness verification. Use Run for live verification."
  );
  setComplexity((trace.manifestSnapshot && trace.manifestSnapshot.complexity) || {});
  document.getElementById("eventCount").textContent = String((trace.events || []).length);
  document.getElementById("interactiveTiming").textContent = "— (demo)";
  document.getElementById("interactiveTiming").className = "measure-value muted-value";
  document.getElementById("benchStatus").textContent =
    "Use Run first for the current input, then benchmark.";
  document.getElementById("benchStatus").className = "measure-value muted-value";
  const match = catalog.find((a) => a.id === (algoId || trace.algorithmId));
  if (match) {
    document.getElementById("algoSelect").value = match.id;
    renderParams();
  }
  document.getElementById("workspace").scrollIntoView({ behavior: "smooth", block: "start" });
}

document.getElementById("themeToggle").onclick = () => {
  const cur = document.documentElement.getAttribute("data-theme") || "dark";
  setTheme(cur === "dark" ? "light" : "dark");
};

document.querySelectorAll(".example-card").forEach((btn) => {
  btn.addEventListener("click", async () => {
    document.querySelectorAll(".example-card").forEach((b) => b.classList.remove("is-selected"));
    btn.classList.add("is-selected");
    try {
      await loadDemoTrace(btn.dataset.example, btn.dataset.algo);
      document.getElementById("runStatus").textContent = "Example loaded (replay)";
      document.getElementById("runStatus").className = "inline-status ok";
    } catch (err) {
      showError(String(err.message || err));
    }
  });
});

function updateNavActive() {
  const map = [
    ["docs", "docs"],
    ["benchmarks", "benchmarks"],
    ["workspace", "workspace"],
    ["explore", "explore"],
    ["home", "home"],
  ];
  const y = window.scrollY + 100;
  let current = "home";
  for (const [id, key] of map.slice().reverse()) {
    const el = document.getElementById(id);
    if (el && el.offsetTop <= y) {
      current = key;
      break;
    }
  }
  // Brand home maps to no workspace highlight until scrolled past landing
  document.querySelectorAll(".shell-nav a").forEach((a) => {
    const href = (a.getAttribute("href") || "").replace("#", "");
    a.classList.toggle("is-active", href === current);
  });
}
window.addEventListener("scroll", updateNavActive, { passive: true });
window.addEventListener("hashchange", updateNavActive);
updateNavActive();

document.getElementById("btnGenerate").onclick = async () => {
  showError("");
  try {
    const data = await api("/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        algorithmId: document.getElementById("algoSelect").value,
        kind: document.getElementById("genKind").value,
        n: Number(document.getElementById("genN").value),
        seed: Number(document.getElementById("genSeed").value),
      }),
    });
    document.getElementById("inputEditor").value = (data.input || []).join(",");
    setParams(data.params);
    document.getElementById("runStatus").textContent = "Input generated";
    document.getElementById("runStatus").className = "inline-status ok";
  } catch (err) {
    showError(String(err.message || err));
  }
};

document.getElementById("btnRun").onclick = async () => {
  showError("");
  setBusy("run", true);
  try {
    const data = await api("/api/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        algorithmId: document.getElementById("algoSelect").value,
        input: document.getElementById("inputEditor").value,
        params: collectParams(),
        seed: Number(document.getElementById("genSeed").value) || 0,
      }),
    });
    applyRunResponse(data);
    setBusy("run", false, "Run complete");
  } catch (err) {
    setBusy("run", false, "");
    showError(String(err.message || err));
  }
};

document.getElementById("btnBench").onclick = async () => {
  showError("");
  setBusy("bench", true);
  const out = document.getElementById("benchOut");
  try {
    const body = {
      algorithmId: document.getElementById("algoSelect").value,
      input: document.getElementById("inputEditor").value,
      params: collectParams(),
      seed: Number(document.getElementById("genSeed").value) || 0,
    };
    const data = await api("/api/benchmark", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const b = data.benchmark;
    const status = document.getElementById("benchStatus");
    status.className = "measure-value";
    status.textContent = "Completed (process-level repeats)";
    out.hidden = false;
    out.textContent = [
      `${data.algorithm.name} · n=${data.inputSize}`,
      `kind: ${b.kind}`,
      `median: ${(b.runtime_s_median * 1000).toFixed(2)} ms`,
      `min/max: ${(b.runtime_s_min * 1000).toFixed(2)} / ${(b.runtime_s_max * 1000).toFixed(2)} ms`,
      `warmup=${b.warmup} repeats=${b.repeats}`,
      `memory: null (not measured)`,
      b.disclaimer,
    ].join("\n");
    setBusy("bench", false);
  } catch (err) {
    document.getElementById("benchStatus").textContent = "Unavailable — see error";
    document.getElementById("benchStatus").className = "measure-value muted-value";
    setBusy("bench", false);
    showError(String(err.message || err));
  }
};

document.getElementById("btnPlay").onclick = () => {
  player.play();
  setExecStatus("Playing");
};
document.getElementById("btnPause").onclick = () => {
  player.pause();
  setExecStatus("Paused");
};
document.getElementById("btnStep").onclick = () => {
  player.step();
  setExecStatus("Stepping");
};
document.getElementById("btnReset").onclick = () => {
  player.reset();
  setExecStatus("Reset");
};
document.getElementById("speed").oninput = (e) => player.setDelay(Number(e.target.value));

document.getElementById("traceSelect").onchange = async (e) => {
  const url = e.target.value;
  if (!url) return;
  try {
    await loadDemoTrace(url);
  } catch (err) {
    showError(String(err.message || err));
  }
};

window.addEventListener("resize", () => {
  if (hasTrace) canvas._cssW = 0;
});

setVizActive(false);
setTheme(document.documentElement.getAttribute("data-theme") || "dark");

checkHealth()
  .then(initCatalog)
  .then(() => {
    document.getElementById("inputEditor").value = "7,3,9,1,5,2,8,4";
  })
  .catch((err) => showError(String(err.message || err)));
