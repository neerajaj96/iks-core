"use strict";

const DATA_BASE = "data/";
const PAGE_SIZE = 50;

const CONFIG = {
  dhatus: {
    file: "dhatus.json",
    claimsFile: "dhatu-claims.json",
    label: "Dhātus",
    placeholder: "Search roots, codes, or meanings",
    empty: "No matching Dhātus. Adjust the search or filters.",
  },
  rules: {
    file: "rules.json",
    claimsFile: "rule-claims.json",
    label: "Sūtras",
    placeholder: "Search sūtra numbers, text, or topics",
    empty: "No matching sūtras. Adjust the search or topic.",
  },
  terms: {
    file: "terms.json",
    claimsFile: "term-claims.json",
    label: "Terms",
    placeholder: "Search terms, definitions, or English glosses",
    empty: "No matching terms. Adjust the search.",
  },
};

const GANA_NAMES = {
  1: "Bhvādi",
  2: "Adādi",
  3: "Juhotyādi",
  4: "Divādi",
  5: "Svādi",
  6: "Tudādi",
  7: "Rudhādi",
  8: "Tanvādi",
  9: "Kryādi",
  10: "Curādi",
};

const PADA_NAMES = {
  P: "Parasmaipada",
  A: "Ātmanepada",
  U: "Ubhayapada",
};

const TIER_NAMES = {
  core: "Core",
  additional: "Additional",
  extended: "Extended",
  outside_common: "Outside common",
};

const state = {
  meta: null,
  tab: "dhatus",
  rows: [],
  cache: new Map(),
  query: "",
  page: 1,
  selected: null,
  detailToken: 0,
  filters: {
    gana: "",
    pada: "",
    tier: "",
    flagged: false,
    topic: "",
  },
};

const $ = (id) => document.getElementById(id);

function escapeHTML(value) {
  return String(value ?? "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  })[char]);
}

function fold(value) {
  return String(value ?? "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase();
}

function formatCount(value) {
  return Number(value).toLocaleString("en-US");
}

function statusLabel(status) {
  return String(status || "unknown").replaceAll("_", " ");
}

function statusBadge(status) {
  const safe = ["verified_primary", "verified_secondary", "flagged_uncertain", "editorial"].includes(status)
    ? status
    : "";
  return `<span class="badge ${safe}">${escapeHTML(statusLabel(status))}</span>`;
}

function setHash(tab, key) {
  const hash = `#${tab}/${encodeURIComponent(key)}`;
  if (window.location.hash !== hash) {
    window.history.replaceState(null, "", hash);
  }
}

function clearHash() {
  if (window.location.hash) {
    window.history.replaceState(null, "", window.location.pathname + window.location.search);
  }
}

function parseHash() {
  const match = window.location.hash.match(/^#(dhatus|rules|terms)\/(.+)$/);
  if (!match) return null;
  try {
    return { tab: match[1], key: decodeURIComponent(match[2]) };
  } catch {
    return null;
  }
}

async function loadJSON(name) {
  if (!state.cache.has(name)) {
    const promise = fetch(`${DATA_BASE}${name}`, { cache: "no-cache" }).then((response) => {
      if (!response.ok) {
        throw new Error(`Could not load ${name} (${response.status})`);
      }
      return response.json();
    });
    state.cache.set(name, promise);
  }
  return state.cache.get(name);
}

async function ensureDataset(tab) {
  const config = CONFIG[tab];
  if (!config) throw new Error(`Unknown tab: ${tab}`);
  state.rows = await loadJSON(config.file);
}

function pageCount(total) {
  return Math.max(1, Math.ceil(total / PAGE_SIZE));
}

function currentKey(row) {
  if (state.tab === "dhatus") return row.code;
  if (state.tab === "rules") return row.number;
  return row.id;
}

function keyMatches(row, key) {
  return currentKey(row) === key || row.id === key;
}

function resetFilters() {
  state.filters = { gana: "", pada: "", tier: "", flagged: false, topic: "" };
  $("gana-filter").value = "";
  $("pada-filter").value = "";
  $("tier-filter").value = "";
  $("topic-filter").value = "";
  $("flagged-filter").checked = false;
}

function filteredRows() {
  let rows = state.rows;
  const query = fold(state.query).trim();

  if (state.tab === "dhatus") {
    rows = rows.filter((row) => {
      if (state.filters.gana && String(row.gana) !== state.filters.gana) return false;
      if (state.filters.pada && row.pada !== state.filters.pada) return false;
      if (state.filters.tier && row.tier !== state.filters.tier) return false;
      if (state.filters.flagged && !row.flagged) return false;
      if (!query) return true;
      return fold([
        row.code,
        row.root_iast,
        row.root_sa,
        row.root_slp1,
        row.meaning_en,
        row.meaning_iast,
        row.meaning_sa,
      ].join(" ")).includes(query);
    });
  } else if (state.tab === "rules") {
    rows = rows.filter((row) => {
      if (state.filters.topic && row.note !== state.filters.topic) return false;
      if (!query) return true;
      return fold([row.number, row.slp1, row.iast, row.sa, row.note].join(" ")).includes(query);
    });
  } else {
    rows = rows.filter((row) => {
      if (!query) return true;
      return fold([row.iast, row.sa, row.en, row.definition, row.rule].join(" ")).includes(query);
    });
  }
  return rows;
}

function renderMeta() {
  const counts = state.meta.counts;
  $("stat-dhatus").textContent = formatCount(counts.dhatus);
  $("stat-rules").textContent = formatCount(counts.rules);
  $("stat-terms").textContent = formatCount(counts.terms);
  $("stat-claims").textContent = formatCount(counts.claims);

  const graphStatus = state.meta.graph_status_counts || {};
  $("about-status").textContent = [
    graphStatus.verified_primary,
    graphStatus.verified_secondary,
    graphStatus.flagged_uncertain,
  ].every((value) => value === undefined)
    ? `${formatCount(counts.claims)} claims`
    : `${formatCount(counts.claims)} claims (${formatCount(graphStatus.verified_primary)} primary, ${formatCount(graphStatus.verified_secondary)} secondary, ${formatCount(graphStatus.flagged_uncertain)} flagged)`;
  $("about-indexed").textContent = formatCount(counts.explorer_claims);
  $("about-version").textContent = state.meta.version;
  $("about-published").textContent = state.meta.published_at;
}

function populateFilters() {
  const gana = $("gana-filter");
  const tier = $("tier-filter");
  const topic = $("topic-filter");
  for (const [value, count] of Object.entries(state.meta.ganas || {})) {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = `${value} · ${GANA_NAMES[value] || "Gaṇa"} (${formatCount(count)})`;
    gana.append(option);
  }
  for (const [value, count] of Object.entries(state.meta.tiers || {})) {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = `${TIER_NAMES[value] || value} (${formatCount(count)})`;
    tier.append(option);
  }
  for (const name of state.meta.topics || []) {
    const option = document.createElement("option");
    option.value = name;
    option.textContent = name;
    topic.append(option);
  }
}

function renderTabs() {
  for (const button of document.querySelectorAll(".tab")) {
    const selected = button.dataset.tab === state.tab;
    button.setAttribute("aria-selected", String(selected));
  }
  const browser = $("panel-browser");
  const about = $("panel-about");
  const isAbout = state.tab === "about";
  browser.hidden = isAbout;
  about.hidden = !isAbout;
  if (!isAbout) {
    browser.setAttribute("aria-labelledby", `tab-${state.tab}`);
  }
}

function render() {
  renderTabs();
  if (state.tab === "about") return;

  const config = CONFIG[state.tab];
  $("search").placeholder = config.placeholder;
  $("dhatu-filters").hidden = state.tab !== "dhatus";
  $("rule-filters").hidden = state.tab !== "rules";
  $("term-filters").hidden = state.tab !== "terms";
  renderTable();
}

function renderTable() {
  const rows = filteredRows();
  const pages = pageCount(rows.length);
  if (state.page > pages) state.page = pages;
  const start = (state.page - 1) * PAGE_SIZE;
  const end = Math.min(start + PAGE_SIZE, rows.length);
  const pageRows = rows.slice(start, end);

  const headers = {
    dhatus: ["Code", "Root", "Gaṇa", "Pada", "Meaning", "Tier"],
    rules: ["Sūtra", "Text", "Topic"],
    terms: ["Term", "English", "Defining sūtra"],
  }[state.tab];
  $("table-head").innerHTML = `<tr>${headers.map((header) => `<th>${escapeHTML(header)}</th>`).join("")}</tr>`;

  const body = $("table-body");
  body.innerHTML = pageRows.map((row) => {
    const selected = row.id === state.selected;
    const attrs = `data-id="${escapeHTML(row.id)}" tabindex="0" aria-selected="${selected}"`;
    if (state.tab === "dhatus") {
      const flagged = row.flagged ? ' <span class="badge flagged_uncertain">flagged</span>' : "";
      return `<tr ${attrs}>
        <td><span class="code">${escapeHTML(row.code)}</span></td>
        <td><span class="deva">${escapeHTML(row.root_sa)}</span><span class="sub">${escapeHTML(row.root_iast)}</span></td>
        <td>${escapeHTML(row.gana)}</td>
        <td title="${escapeHTML(PADA_NAMES[row.pada] || "")}">${escapeHTML(row.pada)}</td>
        <td>${escapeHTML(row.meaning_en)}<span class="sub">${escapeHTML(row.meaning_iast)}</span></td>
        <td>${escapeHTML(TIER_NAMES[row.tier] || row.tier)}${flagged}</td>
      </tr>`;
    }
    if (state.tab === "rules") {
      return `<tr ${attrs}>
        <td><span class="code">A ${escapeHTML(row.number)}</span></td>
        <td><span class="deva">${escapeHTML(row.sa)}</span><span class="sub">${escapeHTML(row.iast)}</span></td>
        <td>${escapeHTML(row.note || "—")}</td>
      </tr>`;
    }
    return `<tr ${attrs}>
      <td><span class="deva">${escapeHTML(row.sa)}</span><span class="sub">${escapeHTML(row.iast)}</span></td>
      <td>${escapeHTML(row.en)}</td>
      <td><span class="code">${row.rule ? `A ${escapeHTML(row.rule)}` : "—"}</span></td>
    </tr>`;
  }).join("");

  const empty = $("empty-state");
  empty.hidden = rows.length !== 0;
  empty.textContent = CONFIG[state.tab].empty;
  $("data-table").hidden = rows.length === 0;
  $("result-count").textContent = state.query
    ? `${formatCount(rows.length)} matching ${CONFIG[state.tab].label.toLowerCase()}`
    : `${formatCount(rows.length)} ${CONFIG[state.tab].label.toLowerCase()}`;
  $("page-label").textContent = `Page ${state.page} of ${pages}`;
  $("page-status").textContent = rows.length
    ? `${formatCount(start + 1)}–${formatCount(end)} of ${formatCount(rows.length)}`
    : "0 records";
  $("prev-page").disabled = state.page <= 1;
  $("next-page").disabled = state.page >= pages;
}

function citationHTML(citation) {
  const rows = [];
  if (citation.source) rows.push(`<dt>Source</dt><dd><code class="iri">${escapeHTML(citation.source)}</code></dd>`);
  if (citation.locator) rows.push(`<dt>Locator</dt><dd>${escapeHTML(citation.locator)}</dd>`);
  if (citation.span_start !== null && citation.span_end !== null) {
    rows.push(`<dt>Span</dt><dd><code>${escapeHTML(citation.span_start)}–${escapeHTML(citation.span_end)}</code></dd>`);
  }
  if (citation.record_hash) rows.push(`<dt>Hash</dt><dd><code class="iri">${escapeHTML(citation.record_hash)}</code></dd>`);
  if (citation.quote) rows.push(`<dt>Evidence</dt><dd><code class="quote">${escapeHTML(citation.quote)}</code></dd>`);
  return rows.length ? `<dl>${rows.join("")}</dl>` : "";
}

function claimHTML(claim) {
  const issue = claim.known_issue
    ? `<p class="known-issue"><b>Known issue:</b> ${escapeHTML(claim.known_issue)}</p>`
    : "";
  return `<article class="claim">
    <div class="claim-head">${statusBadge(claim.status)}<span class="relation">${escapeHTML(claim.relation)}</span></div>
    <p>${escapeHTML(claim.text)}</p>
    ${issue}
    ${citationHTML(claim.citation)}
  </article>`;
}

function detailChrome(row) {
  const iri = `urn:iks:${row.id}`;
  return `<div class="actions">
    <button class="copy" type="button" data-copy="${escapeHTML(iri)}">Copy IRI</button>
    <span class="badge soft">${escapeHTML(row.id)}</span>
  </div>`;
}

function renderDhatuDetail(row, claims) {
  const tier = TIER_NAMES[row.tier] || row.tier;
  return `
    <h2>${escapeHTML(row.root_iast)}</h2>
    <span class="deva">${escapeHTML(row.root_sa)}</span>
    <p class="meta-line">Dhātupāṭha ${escapeHTML(row.code)} · gaṇa ${escapeHTML(row.gana)} (${escapeHTML(GANA_NAMES[row.gana] || "")}) · ${escapeHTML(PADA_NAMES[row.pada] || row.pada)}</p>
    <dl class="kv">
      <dt>Root</dt><dd>${escapeHTML(row.root_iast)} · <code>${escapeHTML(row.root_slp1)}</code></dd>
      <dt>Meaning</dt><dd>${escapeHTML(row.meaning_en)}</dd>
      <dt>IAST</dt><dd>${escapeHTML(row.meaning_iast)}</dd>
      <dt>Sanskrit</dt><dd class="deva">${escapeHTML(row.meaning_sa)}</dd>
      <dt>Tier</dt><dd>${escapeHTML(tier)}</dd>
      <dt>Status</dt><dd>${statusBadge(row.status)}${row.flagged ? " " + statusBadge("flagged_uncertain") : ""}</dd>
    </dl>
    ${detailChrome(row)}
    <h3>Claims and evidence</h3>
    ${claims.map(claimHTML).join("") || "<p class='sub'>No claims indexed.</p>"}
  `;
}

function renderRuleDetail(row, claims) {
  const terms = row.terms.length
    ? `<div class="term-rule-list">${row.terms.map((term) => `<button type="button" data-open-term="${escapeHTML(term.id)}">${escapeHTML(term.iast)} · ${escapeHTML(term.en)}</button>`).join("")}</div>`
    : `<p class="sub">No linked Vyākaraṇa terms.</p>`;
  return `
    <h2>A ${escapeHTML(row.number)}</h2>
    <p class="rule-text">${escapeHTML(row.iast)}</p>
    <span class="deva">${escapeHTML(row.sa)}</span>
    <dl class="kv">
      <dt>SLP1</dt><dd><code>${escapeHTML(row.slp1)}</code></dd>
      <dt>Topic</dt><dd>${escapeHTML(row.note || "—")}</dd>
      <dt>Status</dt><dd>${statusBadge(row.status)}</dd>
    </dl>
    ${detailChrome(row)}
    <h3>Defined terms</h3>
    ${terms}
    <h3>Claims and evidence</h3>
    ${claims.map(claimHTML).join("") || "<p class='sub'>No claims indexed.</p>"}
  `;
}

function renderTermDetail(row, claims) {
  const rule = row.rule
    ? `<button class="link-button" type="button" data-open-rule="${escapeHTML(row.rule_id)}">A ${escapeHTML(row.rule)}</button>`
    : "—";
  return `
    <h2>${escapeHTML(row.iast)}</h2>
    <span class="deva">${escapeHTML(row.sa)}</span>
    <p class="meta-line">${escapeHTML(row.en)}</p>
    <p>${escapeHTML(row.definition)}</p>
    <dl class="kv">
      <dt>Gloss</dt><dd>${statusBadge(row.gloss_status)}</dd>
      <dt>Defined by</dt><dd>${rule}</dd>
      <dt>Status</dt><dd>${statusBadge(row.status)}</dd>
    </dl>
    ${detailChrome(row)}
    <h3>Claims and evidence</h3>
    ${claims.map(claimHTML).join("") || "<p class='sub'>No claims indexed.</p>"}
  `;
}

async function renderDetail(row) {
  const token = ++state.detailToken;
  const detail = $("detail");
  detail.innerHTML = `<p class="detail-placeholder">Loading claims…</p>`;
  try {
    const claimsMap = await loadJSON(CONFIG[state.tab].claimsFile);
    if (token !== state.detailToken) return;
    const claims = claimsMap[row.id] || [];
    if (state.tab === "dhatus") detail.innerHTML = renderDhatuDetail(row, claims);
    else if (state.tab === "rules") detail.innerHTML = renderRuleDetail(row, claims);
    else detail.innerHTML = renderTermDetail(row, claims);
  } catch (error) {
    if (token !== state.detailToken) return;
    detail.innerHTML = `<p class="detail-placeholder">${escapeHTML(error.message)}</p>`;
  }
}

async function selectRow(id, scroll) {
  const row = state.rows.find((candidate) => candidate.id === id);
  if (!row) return;
  state.selected = id;
  setHash(state.tab, currentKey(row));
  renderTable();
  await renderDetail(row);
  if (scroll && window.matchMedia("(max-width: 820px)").matches) {
    $("detail").scrollIntoView({ behavior: "smooth", block: "start" });
  }
}

async function switchTab(tab, updateHash = true) {
  state.detailToken += 1;
  state.selected = null;
  $("detail").innerHTML = `<p class="detail-placeholder">Select a row to inspect its forms, claims, citations, and evidence.</p>`;
  state.page = 1;
  state.query = "";
  $("search").value = "";
  resetFilters();
  if (tab === "about") {
    state.tab = "about";
    render();
    if (updateHash) clearHash();
    return;
  }
  await ensureDataset(tab);
  state.tab = tab;
  render();
  if (updateHash) clearHash();
}

async function openEntity(tab, key, updateHash = true) {
  if (!CONFIG[tab]) return;
  if (state.tab !== tab) {
    await switchTab(tab, false);
  } else {
    state.detailToken += 1;
    state.selected = null;
    state.query = "";
    $("search").value = "";
    resetFilters();
  }
  const index = state.rows.findIndex((row) => keyMatches(row, key));
  if (index < 0) {
    state.page = 1;
    render();
    $("detail").innerHTML = `<p class="detail-placeholder">No ${CONFIG[tab].label.toLowerCase()} record matches “${escapeHTML(key)}”.</p>`;
    return;
  }
  state.page = Math.floor(index / PAGE_SIZE) + 1;
  state.selected = state.rows[index].id;
  render();
  if (updateHash) setHash(tab, currentKey(state.rows[index]));
  await renderDetail(state.rows[index]);
}

async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text);
  } catch {
    const input = document.createElement("textarea");
    input.value = text;
    input.style.position = "fixed";
    input.style.opacity = "0";
    document.body.append(input);
    input.select();
    document.execCommand("copy");
    input.remove();
  }
}

function bindEvents() {
  for (const button of document.querySelectorAll(".tab")) {
    button.addEventListener("click", () => switchTab(button.dataset.tab).catch(showError));
  }

  $("search").addEventListener("input", (event) => {
    state.query = event.target.value;
    state.page = 1;
    renderTable();
  });

  $("gana-filter").addEventListener("change", (event) => {
    state.filters.gana = event.target.value;
    state.page = 1;
    renderTable();
  });
  $("pada-filter").addEventListener("change", (event) => {
    state.filters.pada = event.target.value;
    state.page = 1;
    renderTable();
  });
  $("tier-filter").addEventListener("change", (event) => {
    state.filters.tier = event.target.value;
    state.page = 1;
    renderTable();
  });
  $("flagged-filter").addEventListener("change", (event) => {
    state.filters.flagged = event.target.checked;
    state.page = 1;
    renderTable();
  });
  $("topic-filter").addEventListener("change", (event) => {
    state.filters.topic = event.target.value;
    state.page = 1;
    renderTable();
  });

  $("table-body").addEventListener("click", (event) => {
    const row = event.target.closest("tr[data-id]");
    if (row) selectRow(row.dataset.id, true).catch(showError);
  });
  $("table-body").addEventListener("keydown", (event) => {
    if (event.key !== "Enter" && event.key !== " ") return;
    const row = event.target.closest("tr[data-id]");
    if (!row) return;
    event.preventDefault();
    selectRow(row.dataset.id, true).catch(showError);
  });

  $("prev-page").addEventListener("click", () => {
    if (state.page > 1) {
      state.page -= 1;
      renderTable();
      $("data-table").scrollIntoView({ behavior: "smooth", block: "start" });
    }
  });
  $("next-page").addEventListener("click", () => {
    if (state.page < pageCount(filteredRows().length)) {
      state.page += 1;
      renderTable();
      $("data-table").scrollIntoView({ behavior: "smooth", block: "start" });
    }
  });

  $("detail").addEventListener("click", (event) => {
    const rule = event.target.closest("[data-open-rule]");
    if (rule) {
      openEntity("rules", rule.dataset.openRule).catch(showError);
      return;
    }
    const term = event.target.closest("[data-open-term]");
    if (term) {
      openEntity("terms", term.dataset.openTerm).catch(showError);
      return;
    }
    const copy = event.target.closest("[data-copy]");
    if (copy) {
      copyText(copy.dataset.copy).then(() => {
        const previous = copy.textContent;
        copy.textContent = "Copied";
        window.setTimeout(() => { copy.textContent = previous; }, 1200);
      }).catch(showError);
    }
  });
}

function showError(error) {
  console.error(error);
  $("result-count").textContent = "The explorer data could not be loaded.";
  $("empty-state").hidden = false;
  $("empty-state").textContent = error.message || String(error);
  $("detail").innerHTML = `<p class="detail-placeholder">${escapeHTML(error.message || String(error))}</p>`;
}

async function init() {
  const meta = await loadJSON("meta.json");
  state.meta = meta;
  renderMeta();
  populateFilters();
  bindEvents();
  await ensureDataset("dhatus");

  const deep = parseHash();
  if (deep) {
    await openEntity(deep.tab, deep.key, false);
    return;
  }
  render();
}

init().catch(showError);
