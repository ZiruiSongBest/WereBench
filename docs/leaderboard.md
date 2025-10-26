---
layout: default
title: Leaderboard
nav_order: 4
---

# Leaderboard

**Main results on _WereAlign_ over _WereBench_**.

Avg. is the macro‑average over these five dimensions in speech evaluation. All scores are averaged over five independent decodes per item.

Source: Table 3 in the paper.

<style>
  .lb-wrap { margin-top: 0.75rem; }
  .lb-table { width: 100%; border-collapse: separate; border-spacing: 0; font-size: 0.95rem; }
  .lb-table thead th, .lb-table tbody td { border-bottom: 1px solid #e5e7eb; padding: 8px 10px; text-align: center; }
  .lb-table thead th.model, .lb-table tbody td.model { text-align: left; white-space: nowrap; }
  .lb-table thead tr.group-row th { 
    font-weight: 600; color: #334155; background: #f6f8fa; 
    border-top: 1px solid #e5e7eb; border-bottom: 1px solid #e5e7eb;
  }
  .lb-table thead tr.header-row th { background: #ffffff; }
  .lb-table .sort-btn {
    border: 1px solid #d1d5db; background: #fff; border-radius: 6px; padding: 4px 8px; 
    line-height: 1; cursor: pointer; font-size: 0.9rem;
  }
  .lb-table .sort-btn:hover { background: #f8fafc; }
  .lb-table .sort-btn.active { border-color: #6366f1; box-shadow: 0 0 0 2px rgba(99,102,241,0.15) inset; }
  .lb-legend { font-size: 0.9rem; color: #64748b; margin: 6px 0 14px; }
  .lb-scroll { overflow-x: auto; }
  .lb-note { font-size: 0.85rem; color: #64748b; margin-top: 8px; }
</style>

<div class="lb-wrap">
  <div class="lb-scroll">
    <table id="leaderboard-table" class="lb-table">
      <thead>
        <!-- Group header row (labels only; no buttons) -->
        <tr class="group-row">
          <th class="model" rowspan="2">Model</th>
          <th colspan="6">Speech Evaluation</th>
          <th colspan="2">Decision Evaluation</th>
        </tr>
        <!-- Actual metric header row (with sort buttons) -->
        <tr class="header-row" id="metric-header-row">
          <th><button class="sort-btn" data-key="RI">RI</button></th>
          <th><button class="sort-btn" data-key="SJ">SJ</button></th>
          <th><button class="sort-btn" data-key="DR">DR</button></th>
          <th><button class="sort-btn" data-key="PS">PS</button></th>
          <th><button class="sort-btn" data-key="CT">CT</button></th>
          <th><button class="sort-btn" data-key="Avg">Avg.</button></th>
          <th><button class="sort-btn" data-key="VA">VA</button></th>
          <th><button class="sort-btn" data-key="OI">OI</button></th>
        </tr>
      </thead>
      <tbody id="leaderboard-body">
        <!-- rows injected by JS -->
      </tbody>
    </table>
  </div>
  <div class="lb-note">Tip — darker cells mean larger values within that column.</div>
</div>

<script>
/**
 * You can replace DATA with your own numbers.
 * If you already expose window.LEADERBOARD_DATA elsewhere, it will be used instead.
 * Property keys must match the data-key of the header buttons: RI,SJ,DR,PS,CT,Avg,VA,OI
 */
const FALLBACK_DATA = [
  { Model: "GPT-5-nano",        RI:0.282, SJ:0.384, DR:0.233, PS:0.346, CT:0.339, Avg:0.317, VA:0.364, OI:0.496 },
  { Model: "GPT-oss-20B",       RI:0.319, SJ:0.432, DR:0.331, PS:0.346, CT:0.364, Avg:0.358, VA:0.255, OI:0.264 },
  { Model: "Gemma-3-27B-IT",    RI:0.347, SJ:0.437, DR:0.289, PS:0.443, CT:0.293, Avg:0.362, VA:0.509, OI:0.435 },
  { Model: "Qwen3-30B-A3B",     RI:0.397, SJ:0.574, DR:0.375, PS:0.454, CT:0.416, Avg:0.443, VA:0.388, OI:0.349 },
  { Model: "Qwen3-32B",         RI:0.367, SJ:0.562, DR:0.425, PS:0.536, CT:0.445, Avg:0.467, VA:0.576, OI:0.432 },
  { Model: "Llama-4-Scout",     RI:0.413, SJ:0.586, DR:0.419, PS:0.618, CT:0.336, Avg:0.474, VA:0.503, OI:0.512 },
  { Model: "QwQ-32B",           RI:0.430, SJ:0.575, DR:0.463, PS:0.502, CT:0.470, Avg:0.488, VA:0.600, OI:0.472 },
  { Model: "GPT-5-mini",        RI:0.415, SJ:0.529, DR:0.431, PS:0.601, CT:0.464, Avg:0.488, VA:0.552, OI:0.575 },
  { Model: "DeepSeek-V3.1",     RI:0.442, SJ:0.674, DR:0.456, PS:0.740, CT:0.462, Avg:0.555, VA:0.685, OI:0.586 },
  { Model: "Gemini-2.5-Flash",  RI:0.517, SJ:0.614, DR:0.562, PS:0.753, CT:0.436, Avg:0.576, VA:0.485, OI:0.507 },
  { Model: "DeepSeek-V3.2-Exp", RI:0.481, SJ:0.692, DR:0.502, PS:0.785, CT:0.521, Avg:0.602, VA:0.782, OI:0.580 },
  { Model: "GLM-4.5",           RI:0.512, SJ:0.690, DR:0.584, PS:0.699, CT:0.533, Avg:0.603, VA:0.539, OI:0.537 },
  { Model: "GPT-5",             RI:0.516, SJ:0.657, DR:0.525, PS:0.795, CT:0.521, Avg:0.603, VA:0.618, OI:0.616 },
  { Model: "Deepseek-R1",       RI:0.516, SJ:0.676, DR:0.539, PS:0.778, CT:0.561, Avg:0.614, VA:0.642, OI:0.434 },
  { Model: "Gemini-2.5-pro",    RI:0.620, SJ:0.769, DR:0.695, PS:0.877, CT:0.637, Avg:0.720, VA:0.733, OI:0.561 }
];
const DATA = (typeof window !== "undefined" && window.LEADERBOARD_DATA) || FALLBACK_DATA;

const COLS = ["RI","SJ","DR","PS","CT","Avg","VA","OI"];
const TBODY = document.getElementById("leaderboard-body");
const headerRow = document.getElementById("metric-header-row");
const buttons = Array.from(headerRow.querySelectorAll(".sort-btn"));
let activeSort = { key: null, dir: "desc" }; // dir ∈ {"desc","asc"}

/* ---------- render ---------- */
function renderRows(rows) {
  TBODY.innerHTML = "";
  rows.forEach(r => {
    const tr = document.createElement("tr");

    const tdModel = document.createElement("td");
    tdModel.className = "model";
    tdModel.textContent = r.Model;
    tr.appendChild(tdModel);

    COLS.forEach(k => {
      const td = document.createElement("td");
      const val = typeof r[k] === "number" ? r[k] : parseFloat(r[k]);
      td.textContent = (val || val === 0) ? val.toFixed(3) : "";
      td.dataset.value = isFinite(val) ? val : "";
      tr.appendChild(td);
    });

    TBODY.appendChild(tr);
  });

  // apply per-column shading after rows are in DOM
  shadeByColumn();
}

function shadeByColumn() {
  // For each metric column independently:
  COLS.forEach((k, idx) => {
    // idx starts from 0 but table has "Model" first column → offset by +1
    const colIndex = idx + 1;
    const cells = Array.from(TBODY.querySelectorAll(`tr td:nth-child(${colIndex+1})`));
    const values = cells.map(td => parseFloat(td.dataset.value)).filter(v => isFinite(v));
    if (!values.length) return;

    const min = Math.min(...values);
    const max = Math.max(...values);
    const span = Math.max(max - min, 1e-9);

    cells.forEach(td => {
      const v = parseFloat(td.dataset.value);
      if (!isFinite(v)) { td.style.background = ""; return; }
      // normalize [0,1], larger=better → darker
      const t = (v - min) / span;
      const alpha = 0.1 + 0.35 * t; // 0.10~0.45
      // blue-ish
      td.style.backgroundColor = `rgba(59,130,246,${alpha})`;  // Tailwind blue-500 tone
      td.style.color = "#111827";          // white text on darker tone
    });
  });
}

/* ---------- sort ---------- */
function sortRows(key, dir) {
  const sorted = [...DATA].sort((a, b) => {
    const va = +a[key], vb = +b[key];
    if (dir === "desc") return vb - va;
    return va - vb;
  });
  renderRows(sorted);
}

function setActiveButton(key, dir) {
  buttons.forEach(btn => btn.classList.remove("active"));
  const btn = buttons.find(b => b.dataset.key === key);
  if (btn) {
    btn.classList.add("active");
    // Add arrow indicator
    const base = btn.textContent.replace(/[↑↓]\s*$/,"");
    btn.textContent = base + (dir === "desc" ? " ↓" : " ↑");
  }
  // Reset others' arrows
  buttons.forEach(b => {
    if (b.dataset.key !== key) b.textContent = b.textContent.replace(/[↑↓]\s*$/,"");
  });
}

// attach click handlers: 1st=desc, 2nd=asc, 3rd=desc...
buttons.forEach(btn => {
  btn.addEventListener("click", () => {
    const key = btn.dataset.key;
    // cycle: null/other → desc → asc → desc ...
    if (activeSort.key !== key) {
      activeSort = { key, dir: "desc" };
    } else {
      activeSort.dir = activeSort.dir === "desc" ? "asc" : "desc";
    }
    setActiveButton(activeSort.key, activeSort.dir);
    sortRows(activeSort.key, activeSort.dir);
  });
});

// initial render (no sort applied until user clicks)
renderRows(DATA);
</script>
