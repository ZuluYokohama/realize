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
  el.setAttribute("role", "img");
  el.setAttribute("aria-label", "tiny picture");
  for (let i = 0; i < 3; i++) {
    for (let j = 0; j < 3; j++) {
      const v = m[i][j];
      const c = document.createElement("div");
      c.className = `cell c${v}`;
      if (hit && v === 3) c.classList.add("hit");
      const cap = document.createElement("span");
      cap.style.opacity = "0.55";
      cap.style.fontSize = "10px";
      cap.textContent = String(v);
      c.appendChild(cap);
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
      kicker: "Example · holds, impossible, wrong",
      title: "Recolor a picture",
      body:
        "You asked an AI to recolor a tiny picture. Recolor holds. Recolor and keep every color the same is impossible. Doing nothing is not a recolor.",
    })
  );
  const wrap = document.createElement("div");
  const switcher = document.createElement("div");
  switcher.className = "stages";
  switcher.style.marginBottom = "12px";
  const keys = [
    ["recolor", "recolor"],
    ["histogram", "keep every color"],
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
    const ev = document.createElement("div");
    ev.className = "flow";
    const before = document.createElement("div");
    const bh = document.createElement("p");
    bh.className = "kicker";
    bh.textContent = "before";
    before.append(bh, grid(ctx.X, { hit: key === "histogram" }));
    ev.appendChild(before);
    const y = c.witness?.Y || (key === "empty" ? ctx.X : null);
    if (y) {
      const after = document.createElement("div");
      const ah = document.createElement("p");
      ah.className = "kicker";
      ah.textContent = "after";
      after.append(ah, grid(y));
      ev.appendChild(after);
    }
    const note = document.createElement("p");
    note.className = "caption";
    note.textContent =
      key === "histogram"
        ? "Recolor removes color 3. You cannot keep every color and recolor."
        : key === "empty"
          ? "The picture is unchanged. That is not a recolor."
          : "Extract the shape, then paint it.";
    ev.appendChild(note);
    const right = document.createElement("div");
    right.appendChild(humanStamp(c.verdict));
    right.appendChild(metaEl(c));
    const cols = document.createElement("div");
    cols.className = "columns";
    cols.append(panel("the picture", ev), panel("the result", right));
    stage.appendChild(cols);
    stage.appendChild(engineerDrawer("Technical record", jsonEl(c)));
  }

  if (cert) await show("recolor", cert);
  else await show("recolor");
}
