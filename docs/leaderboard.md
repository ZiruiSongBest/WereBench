---
layout: default
title: Leaderboard
nav_order: 4
---

# Leaderboard

Interactive results table for **WereAlign on WereBench**.  
Click the metric buttons (RI, SJ, DR, PS, CT, **Avg.**, VA, OI) to sort:
- **1st click:** sort **descending** by that metric  
- **2nd click:** sort **ascending**  
- **3rd click:** sort **descending** (and repeats)

> Numbers are transcribed from **Table 3** of the WereBench paper. Update the `DATA` array below if your results change later.  
> Source: Table 3 in the paper PDF. 

<div id="lb-root"></div>

<style>
/* ---- Table basics ---- */
#lb-root { margin-top: 1rem; }
.lb-wrap { overflow-x: auto; }
.lb-table {
  border-collapse: collapse;
  min-width: 860px;
  width: 100%;
  font-size: 0.95rem;
}
.lb-table th, .lb-table td {
  border-bottom: 1px solid #e5e7eb;
  padding: 10px 12px;
  text-align: right;
  white-space: nowrap;
}
.lb-table th:first-child, .lb-table td:first-child {
  text-align: left;
  position: sticky;
  left: 0;
  background: #fff;
}
.lb-table thead th {
  position: sticky;
  top: 0;
  background: #fff;
  z-index: 2;
}

/* ---- Buttons in the header ---- */
.lb-metric {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  border: 1px solid #d1d5db;
  border-radius: 9999px;
  background: #fafafa;
  cursor: pointer;
  font-size: 0.9rem;
  line-height: 1;
}
.lb-metric:hover { background: #f3f4f6; }
.lb-metric .arrow { opacity: 0.7; font-size: 0.95rem; }
.lb-metric.active { border-color: #111827; }

/* ---- Cell heat colors (computed inline) ---- */
.lb-cell { border-radius: 6px; padding: 6px 8px; display:inline-block; min-width:56px; }

/* ---- Legend & small UI bits ---- */
.lb-legend { font-size: 0.85rem; color: #6b7280; margin-bottom: 8px; }
.lb-footer { font-size: 0.85rem; color: #6b7280; margin-top: 8px; }
</style>

<script>
(function() {
  // ======== 1) Data ========
  // Values copied from Table 3 of the WereBench paper (RI, SJ, DR, PS, CT, Avg., VA, OI).
  // Edit here to update the leaderboard later.
  const DATA = [
    { Model: "GPT-5-nano",       RI:0.282, SJ:0.384, DR:0.233, PS:0.346, CT:0.339, "Avg.":0.317, VA:0.364, OI:0.496 },
    { Model: "GPT-oss-20B",      RI:0.319, SJ:0.432, DR:0.331, PS:0.346, CT:0.364, "Avg.":0.358, VA:0.255, OI:0.264 },
    { Model: "Gemma-3-27B-IT",   RI:0.347, SJ:0.437, DR:0.289, PS:0.443, CT:0.293, "Avg.":0.362, VA:0.509, OI:0.435 },
    { Model: "Qwen3-30B-A3B",    RI:0.397, SJ:0.574, DR:0.375, PS:0.454, CT:0.416, "Avg.":0.443, VA:0.388, OI:0.349 },
    { Model: "Qwen3-32B",        RI:0.367, SJ:0.562, DR:0.425, PS:0.536, CT:0.445, "Avg.":0.467, VA:0.576, OI:0.432 },
    { Model: "Llama-4-Scout",    RI:0.413, SJ:0.586, DR:0.419, PS:0.618, CT:0.336, "Avg.":0.474, VA:0.503, OI:0.512 },
    { Model: "QwQ-32B",          RI:0.430, SJ:0.575, DR:0.463, PS:0.502, CT:0.470, "Avg.":0.488, VA:0.600, OI:0.472 },
    { Model: "GPT-5-mini",       RI:0.415, SJ:0.529, DR:0.431, PS:0.601, CT:0.464, "Avg.":0.488, VA:0.552, OI:0.575 },
    { Model: "DeepSeek-V3.1",    RI:0.442, SJ:0.674, DR:0.456, PS:0.740, CT:0.462, "Avg.":0.555, VA:0.685, OI:0.586 },
    { Model: "Gemini-2.5-Flash", RI:0.517, SJ:0.614, DR:0.562, PS:0.753, CT:0.436, "Avg.":0.576, VA:0.485, OI:0.507 },
    { Model: "DeepSeek-V3.2-Exp",RI:0.481, SJ:0.692, DR:0.502, PS:0.785, CT:0.521, "Avg.":0.602, VA:0.782, OI:0.580 },
    { Model: "GLM-4.5",          RI:0.512, SJ:0.690, DR:0.584, PS:0.699, CT:0.533, "Avg.":0.603, VA:0.539, OI:0.537 },
    { Model: "GPT-5",            RI:0.516, SJ:0.657, DR:0.525, PS:0.795, CT:0.521, "Avg.":0.603, VA:0.618, OI:0.616 },
    { Model: "Deepseek-R1",      RI:0.516, SJ:0.676, DR:0.539, PS:0.778, CT:0.561, "Avg.":0.614, VA:0.642, OI:0.434 },
    { Model: "Gemini-2.5-pro",   RI:0.620, SJ:0.769, DR:0.695, PS:0.877, CT:0.637, "Avg.":0.720, VA:0.733, OI:0.561 },
  ];

  const COLS = [
    { key: "Model", label: "Model", numeric: false },
    { key: "RI",    label: "RI",    numeric: true },
    { key: "SJ",    label: "SJ",    numeric: true },
    { key: "DR",    label: "DR",    numeric: true },
    { key: "PS",    label: "PS",    numeric: true },
    { key: "CT",    label: "CT",    numeric: true },
    { key: "Avg.",  label: "Avg.",  numeric: true },
    { key: "VA",    label: "VA",    numeric: true },
    { key: "OI",    label: "OI",    numeric: true },
  ];

  // ======== 2) Compute min/max for heat colors per numeric column ========
  const stats = {};
  for (const c of COLS) {
    if (!c.numeric) continue;
    const vals = DATA.map(d => d[c.key]);
    const min = Math.min(...vals), max = Math.max(...vals);
    stats[c.key] = { min, max };
  }

  // Color function: darker color = larger value (column-wise)
  function heatColor(colKey, v) {
    const s = stats[colKey];
    if (!s) return "transparent";
    const span = (s.max - s.min) || 1e-9;
    const t = (v - s.min) / span;           // 0..1
    const light = 92 - (t * 52);            // 92% (light) -> 40% (dark)
    return `hsl(217, 90%, ${light}%)`;      // blue scale
  }

  // ======== 3) Sorting state & behavior ========
  // Requirement: click cycles as Desc -> Asc -> Desc -> ...
  const cycle = { }; // per-column cycle index: 0 (desc), 1 (asc), 2 (desc), then back to 0
  const cycleToDir = idx => (idx === 1 ? "asc" : "desc");

  let sortKey = "Avg.";     // default sort by Avg. desc
  cycle["Avg."] = 0;        // start at desc

  function byKey(key, dir) {
    return (a, b) => {
      if (dir === "desc") {
        return (b[key] - a[key]) || (b["Avg."] - a["Avg."]) || a["Model"].localeCompare(b["Model"]);
      } else {
        return (a[key] - b[key]) || (a["Avg."] - b["Avg."]) || a["Model"].localeCompare(b["Model"]);
      }
    };
  }

  // ======== 4) Render ========
  const root = document.getElementById("lb-root");
  const wrap = document.createElement("div");
  wrap.className = "lb-wrap";
  root.appendChild(wrap);

  const legend = document.createElement("div");
  legend.className = "lb-legend";
  legend.textContent = "Darker cell background = higher value within that column.";
  root.insertBefore(legend, wrap);

  const table = document.createElement("table");
  table.className = "lb-table";
  wrap.appendChild(table);

  function renderHeader() {
    const thead = document.createElement("thead");
    const tr = document.createElement("tr");

    for (const c of COLS) {
      const th = document.createElement("th");
      if (c.numeric) {
        const btn = document.createElement("button");
        btn.className = "lb-metric";
        btn.dataset.key = c.key;
        btn.title = "Click to sort by " + c.label;
        btn.innerHTML = `<span>${c.label}</span><span class="arrow">↕</span>`;
        if (sortKey === c.key) btn.classList.add("active");
        btn.addEventListener("click", () => {
          const idx = (cycle[c.key] ?? -1) + 1; // -1->0(desc) on first click
          cycle[c.key] = idx % 3;
          sortKey = c.key;
          // reset others' cycle so future clicks begin their own cycle
          for (const k of Object.keys(cycle)) if (k !== c.key) delete cycle[k];
          renderBody();
          renderHeader(); // refresh arrow/border state
        });
        th.appendChild(btn);
      } else {
        th.textContent = c.label;
      }
      tr.appendChild(th);
    }
    thead.appendChild(tr);
    // replace thead
    const old = table.querySelector("thead");
    if (old) table.removeChild(old);
    table.appendChild(thead);

    // update active button visuals + arrow direction
    const activeBtn = table.querySelector(`.lb-metric[data-key="${sortKey}"]`);
    if (activeBtn) {
      activeBtn.classList.add("active");
      const idx = cycle[sortKey] ?? 0; // default to desc
      const dir = cycleToDir(idx);
      const arrow = activeBtn.querySelector(".arrow");
      arrow.textContent = dir === "desc" ? "↓" : "↑";
    }
  }

  function renderBody() {
    const idx = cycle[sortKey] ?? 0;
    const dir = cycleToDir(idx);
    const sorted = [...DATA].sort(byKey(sortKey, dir));

    const tbody = document.createElement("tbody");
    for (const row of sorted) {
      const tr = document.createElement("tr");
      for (const c of COLS) {
        const td = document.createElement("td");
        if (c.numeric) {
          const val = row[c.key];
          const span = document.createElement("span");
          span.className = "lb-cell";
          span.style.background = heatColor(c.key, val);
          span.textContent = Number(val).toFixed(3);
          td.appendChild(span);
        } else {
          td.textContent = row[c.key];
        }
        tr.appendChild(td);
      }
      tbody.appendChild(tr);
    }
    // replace tbody
    const old = table.querySelector("tbody");
    if (old) table.removeChild(old);
    table.appendChild(tbody);
  }

  renderHeader();
  renderBody();

  const foot = document.createElement("div");
  foot.className = "lb-footer";
  foot.textContent = "Tip: Click the same metric multiple times to cycle Desc → Asc → Desc.";
  root.appendChild(foot);
})();
</script>
