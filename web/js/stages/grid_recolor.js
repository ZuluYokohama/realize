import { jsonEl, loadJSON, metaEl, panel, stampEl } from "../stamp.js";

const FILES = {
  recolor: "./fixtures/grid_recolor.pass.json",
  histogram: "./fixtures/grid_recolor.histogram_unsat.json",
  empty: "./fixtures/grid_recolor.empty_counterexample.json",
};

function grid(m, { hit } = {}) {
  const el = document.createElement("div");
  el.className = "grid3";
  for (let i = 0; i < 3; i++) {
    for (let j = 0; j < 3; j++) {
      const v = m[i][j];
      const c = document.createElement("div");
      c.className = "cell";
      if (v !== 0) c.classList.add("fg");
      if (v === 2) c.classList.add("red");
      if (hit && v === 3) c.classList.add("hit");
      c.textContent = String(v);
      el.appendChild(c);
    }
  }
  return el;
}

function arrow(text) {
  const d = document.createElement("div");
  d.className = "arrow";
  d.textContent = text;
  return d;
}

export async function renderGrid(root, cert) {
  const ctx = await loadJSON("./fixtures/grid_recolor.context.json");
  const wrap = document.createElement("div");
  const switcher = document.createElement("div");
  switcher.className = "stages";
  switcher.style.marginBottom = "12px";
  const keys = [
    ["recolor", "recolor"],
    ["histogram", "histogram"],
    ["empty", "empty series"],
  ];
  const stage = document.createElement("div");
  wrap.append(switcher, stage);
  root.appendChild(wrap);

  async function show(key, fromCert) {
    for (const b of switcher.querySelectorAll("button")) {
      b.classList.toggle("on", b.dataset.key === key);
    }
    const c = fromCert || (await loadJSON(FILES[key]));
    mount(key, c);
  }

  for (const [key, label] of keys) {
    const b = document.createElement("button");
    b.className = "chip";
    b.dataset.key = key;
    b.textContent = label;
    b.addEventListener("click", () => show(key));
    switcher.appendChild(b);
  }

  function maskOf(X) {
    return X.map((row) => row.map((v) => (v === 0 ? 0 : 1)));
  }

  function mount(key, c) {
    stage.replaceChildren();
    const cols = document.createElement("div");
    cols.className = "columns";
    const spec = {
      ops: key === "empty" ? [] : ["Extract", "Render2"],
      K: key === "histogram" ? { preserve_histogram: true } : null,
      X: ctx.X,
    };
    const ev = document.createElement("div");
    ev.className = "flow";
    ev.appendChild(grid(ctx.X, { hit: key === "histogram" }));
    ev.appendChild(arrow("Extract Grid→Mask"));
    ev.appendChild(grid(maskOf(ctx.X)));
    ev.appendChild(arrow("Render2 Mask→Grid"));
    const y = c.witness?.Y || (key === "empty" ? ctx.X : c.witness?.expected);
    if (y) ev.appendChild(grid(y));
    if (key === "histogram") {
      const p = document.createElement("p");
      p.className = "caption";
      p.textContent = "Color-3 in X: 1. Color-3 required in Y: 0. Conjunction empty.";
      ev.appendChild(p);
    }
    const right = document.createElement("div");
    right.appendChild(stampEl(c.verdict));
    right.appendChild(metaEl(c));
    cols.append(
      panel("spec", jsonEl(spec)),
      panel("evidence", ev),
      panel("certificate", right)
    );
    stage.appendChild(cols);
  }

  if (cert) await show("recolor", cert);
  else await show("recolor");
}
