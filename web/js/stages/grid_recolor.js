import {
  engineerDrawer,
  humanStamp,
  jsonEl,
  loadJSON,
  metaEl,
  panel,
  storyHead,
} from "../stamp.js";

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

export async function renderGrid(root, cert) {
  const ctx = await loadJSON("./fixtures/grid_recolor.context.json");
  root.appendChild(
    storyHead({
      art: "./art/recolor.jpg",
      alt: "Ceramic tiles on a bench, some dark, some teal, one cracked amber.",
      kicker: "Example · holds, empty, fails",
      title: "Recolor a picture",
      body:
        "Take a small picture. Recolor the shape. That holds. Ask to keep every color count the same while recoloring: the catalog is empty. Do nothing at all: that answer fails.",
    })
  );
  const wrap = document.createElement("div");
  const switcher = document.createElement("div");
  switcher.className = "stages";
  switcher.style.marginBottom = "12px";
  const keys = [
    ["recolor", "recolor"],
    ["histogram", "keep colors"],
    ["empty", "do nothing"],
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

  function mount(key, c) {
    stage.replaceChildren();
    const cols = document.createElement("div");
    cols.className = "columns";
    const ev = document.createElement("div");
    ev.className = "flow";
    ev.appendChild(grid(ctx.X, { hit: key === "histogram" }));
    const y = c.witness?.Y || (key === "empty" ? ctx.X : null);
    if (y) ev.appendChild(grid(y));
    const note = document.createElement("p");
    note.className = "caption";
    note.textContent =
      key === "histogram"
        ? "The picture has one cell of color 3. Recoloring removes it. You cannot keep the histogram and recolor."
        : key === "empty"
          ? "Doing nothing leaves the picture unchanged. That is not a recolor."
          : "Extract the shape, then paint it. The job holds.";
    ev.appendChild(note);
    const right = document.createElement("div");
    right.appendChild(humanStamp(c.verdict));
    right.appendChild(metaEl(c));
    cols.append(
      panel("the picture", ev),
      panel("the stamp", right)
    );
    stage.appendChild(cols);
    stage.appendChild(engineerDrawer("Technical record", jsonEl(c)));
  }

  if (cert) await show("recolor", cert);
  else await show("recolor");
}
