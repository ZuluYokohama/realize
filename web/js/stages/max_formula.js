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
  larger: "./fixtures/max_formula.larger.json",
  smaller: "./fixtures/max_formula.smaller.json",
  midpoint: "./fixtures/max_formula.midpoint.json",
  absdiff: "./fixtures/max_formula.absdiff.json",
  affine: "./fixtures/max_formula.affine_unsat.json",
  unknown: "./fixtures/max_formula.unknown.json",
};

const COPY = {
  larger: "Always pick the larger of two numbers.",
  smaller: "Always pick the smaller.",
  midpoint: "Pick the midpoint.",
  absdiff: "Pick the distance between them.",
  affine: "Same job, but only with a too-simple catalog (no absolute value). Empty.",
  unknown: "A phrase the inspector does not recognize. Not enough.",
};

export async function renderMaxFormula(root, cert) {
  root.appendChild(
    storyHead({
      art: "./art/larger-number.jpg",
      alt: "Two sheets of paper folded into half-planes with a teal thread along the fold.",
      kicker: "Example · holds, empty, and not enough",
      title: "Always pick the larger number",
      body:
        "The job is ordinary. The inspector searches a small catalog of formulas. For “larger,” a short formula holds. If you forbid the absolute-value piece, the catalog is empty. If you type a phrase it does not know, it stamps not enough — it does not guess.",
    })
  );
  const wrap = document.createElement("div");
  const switcher = document.createElement("div");
  switcher.className = "stages";
  switcher.style.marginBottom = "12px";
  const keys = [
    ["larger", "larger"],
    ["smaller", "smaller"],
    ["midpoint", "midpoint"],
    ["absdiff", "distance"],
    ["affine", "too simple"],
    ["unknown", "unrecognized"],
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
    const job = document.createElement("p");
    job.textContent = COPY[key];
    const ev = document.createElement("p");
    ev.className = "caption";
    if (c.witness?.identities) {
      ev.textContent = "A formula in the catalog matches both sides of the comparison.";
    } else if (c.verdict === "UNSAT") {
      ev.textContent = `Catalog size ${c.witness?.universe ?? 125}. Valid answers: 0.`;
    } else {
      ev.textContent = "The inspector will not invent a job from an unknown phrase.";
    }
    const right = document.createElement("div");
    right.appendChild(humanStamp(c.verdict));
    right.appendChild(metaEl(c));
    cols.append(panel("the job", job), panel("what happened", ev), panel("the stamp", right));
    stage.appendChild(cols);
    stage.appendChild(engineerDrawer("Technical record", jsonEl(c)));
  }

  if (cert) await show("larger", cert);
  else await show("larger");
}
