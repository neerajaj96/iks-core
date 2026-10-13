/* IKS-Core Pages app: corpus search, SVG vada graph, client-side demos. No deps. */
const D = (n) => fetch("data/" + n).then((r) => r.json());
const $ = (id) => document.getElementById(id);

document.querySelectorAll("nav button").forEach((b) =>
  b.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((t) => t.classList.remove("on"));
    $("t-" + b.dataset.t).classList.add("on");
  })
);

let SUTRAS = [], TERMS = [], INFS = [], ALLNODES = [], ALLEDGES = [];
Promise.all([D("sutras.json"), D("texts.json"), D("vada_nodes.json"), D("vada_edges.json"),
             D("terms.json"), D("inferences.json")]).then(
  ([sutras, texts, nodes, edges, terms, infs]) => {
    SUTRAS = sutras; TERMS = terms; INFS = infs;
    const ft = $("ftext");
    [...new Set(sutras.map((s) => s.textId))].sort().forEach((t) =>
      ft.append(new Option(t, t))
    );
    renderRows();
    ALLNODES = nodes; ALLEDGES = edges;
    renderGraph(nodes, edges);
    renderLexicon();
    const conf = {};
    SUTRAS.forEach((s) => { conf[s.confidence] = (conf[s.confidence] || 0) + 1; });
    $("statstrip").textContent =
      `${SUTRAS.length} sūtras · ` +
      Object.entries(conf).map(([k, v]) => `${k}: ${v}`).join(" · ") +
      ` · ${TERMS.length} terms · ${INFS.length} inferences · ${nodes.length}V/${edges.length}E`;
  }
);

function renderRows() {
  const q = $("q").value.toLowerCase(), t = $("ftext").value, c = $("fconf").value;
  const rows = SUTRAS.filter(
    (s) =>
      (!t || s.textId === t) &&
      (!c || s.confidence === c) &&
      (!q || (s.sanskrit + s.translation).toLowerCase().includes(q))
  ).slice(0, 200);
  $("count").textContent = `${rows.length} shown / ${SUTRAS.length} total`;
  $("rows").innerHTML = rows
    .map(
      (s) =>
        `<tr><td>${s.adhyaNotation}</td><td>${s.sanskrit.slice(0, 90)}</td>` +
        `<td>${s.translation.slice(0, 110)}</td>` +
        `<td><span class="badge ${s.confidence}">${s.confidence}</span></td></tr>`
    )
    .join("");
}
["q", "ftext", "fconf"].forEach((id) =>
  $(id).addEventListener("input", renderRows)
);
$("fkatha").addEventListener("change", () => renderGraph(ALLNODES, ALLEDGES));

function renderGraph(allNodes, allEdges) {
  const k = ($("fkatha") && $("fkatha").value) || "";
  const nodes = k ? allNodes.filter((n) => n.katha === k) : allNodes;
  const ids = new Set(nodes.map((n) => n.id));
  const edges = allEdges.filter((e) => ids.has(e.from) && ids.has(e.to));
  const svg = $("gv"), n = nodes.length, R = 150, cx = 320, cy = 200;
  const pos = {};
  nodes.forEach((nd, i) => {
    const a = (2 * Math.PI * i) / n;
    pos[nd.id] = [cx + R * Math.cos(a), cy + R * 0.72 * Math.sin(a)];
  });
  let h = "";
  edges.forEach((e) => {
    if (!pos[e.from] || !pos[e.to]) return;
    const [x1, y1] = pos[e.from], [x2, y2] = pos[e.to];
    h += `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#888" stroke-width="${1 + e.weight * 3}"/>`;
  });
  nodes.forEach((nd) => {
    const [x, y] = pos[nd.id];
    const col = nd.katha === "Vitanda" ? "#e88" : nd.katha === "Jalpa" ? "#ec5" : "#8c8";
    h += `<g data-id="${nd.id}" style="cursor:pointer"><circle cx="${x}" cy="${y}" r="14" fill="${col}"/>` +
      `<text x="${x}" y="${y + 30}" font-size="10" text-anchor="middle">${nd.textId}</text></g>`;
  });
  svg.innerHTML = h;
  $("gsummary").textContent = `|V|=${nodes.length} |E|=${edges.length}`;
  svg.querySelectorAll("g").forEach((g) =>
    g.addEventListener("click", () => {
      const nd = nodes.find((x) => x.id === g.dataset.id);
      $("gdetail").innerHTML = `<b>${nd.id}</b> [${nd.textId}, ${nd.katha}] — ${nd.siddhanta}`;
    })
  );
}

function renderLexicon() {
  const q = ($("tq").value || "").toLowerCase();
  const terms = TERMS.filter((t) => !q || (t.iast + t.sanskrit + t.formalSymbol).toLowerCase().includes(q)).slice(0, 120);
  const infs = INFS.filter((i) => !q || (i.id + i.paksa + i.sadhya + i.hetu).toLowerCase().includes(q));
  $("nterms").textContent = TERMS.length;
  $("ninfs").textContent = INFS.length;
  $("tcount").textContent = `${terms.length} terms, ${infs.length} inferences shown`;
  $("trows").innerHTML = terms
    .map((t) => `<tr><td>${t.iast}</td><td>${t.ontologicalSort}</td><td>${t.formalSymbol}</td><td>${t.darsanaScope.join(", ")}</td></tr>`)
    .join("");
  $("irows").innerHTML = infs
    .map((i) => `<tr><td>${i.id}</td><td>${i.form}</td><td>${i.paksa} → ${i.sadhya} via ${i.hetu}</td><td>${i.hetvabhasa}</td></tr>`)
    .join("");
}
$("tq").addEventListener("input", renderLexicon);

/* --- demos (JS ports of Python engine) --- */
$("hill").textContent =
  "pratijñā: parvato vahnimān\nhetu: dhūmāt (A_dhumatva)\n" +
  "udāharaṇa: yo dhūmavān sa vahnimān yathā mahānasam / vyatireka yathā hradaḥ\n" +
  "upanaya: tathā cāyaṃ dhūmavān\nnigamana: tasmāt tathā";
$("abs").textContent = "¬_a^[samyoga,ghatatva] ghata @ bhutala  with PR_ghatatva,samyoga, AN_samyoga(bhutala)";

function detect() {
  const pak = $("d-pak").checked, sap = $("d-sap").checked, vip = $("d-vip").checked;
  const con = $("d-con").checked, def = $("d-def").checked, ctr = $("d-ctr").checked;
  let out;
  if (!pak) out = "Asiddha";
  else if (con) out = "Viruddha";
  else if (def) out = "Badhita";
  else if (ctr && sap) out = "Satpratipaksa";
  else if (sap && vip) out = "Savyabhicara";
  else out = "none (valid)";
  $("d-out").textContent = out;
}
["d-pak", "d-sap", "d-vip", "d-con", "d-def", "d-ctr"].forEach((id) =>
  $(id).addEventListener("change", detect)
);
detect();

const RMAP = { rati: "śṛṅgāra", hasa: "hāsya", soka: "karuṇa", krodha: "raudra", utsaha: "vīra", bhaya: "bhayānaka", jugupsa: "bībhatsa", vismaya: "adbhuta", sama: "śānta" };
function rasa() {
  const v = +$("r-v").value, a = +$("r-a").value, y = +$("r-y").value, s = $("r-s").value;
  $("r-out").textContent = `${RMAP[s]}  intensity ${(0.4 * v + 0.3 * a + 0.3 * (y / 33)).toFixed(3)}`;
}
["r-v", "r-a", "r-y", "r-s"].forEach((id) => $(id).addEventListener("input", rasa));
rasa();
