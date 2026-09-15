import {
  engineerDrawer,
  jsonEl,
  loadJSON,
  overclaimPlate,
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
  larger: {
    job: "Always take the bigger of two numbers. On the table: 3 and 5.",
    what: "A short formula always returns the bigger one. 3 and 5 → 5.",
    pick: "5",
  },
  smaller: {
    job: "Always take the smaller. On the table: 3 and 5.",
    what: "The matching formula holds. 3 and 5 → 3.",
    pick: "3",
  },
  midpoint: {
    job: "Take the midpoint of 3 and 5.",
    what: "The matching formula holds. 3 and 5 → 4.",
    pick: "4",
  },
  absdiff: {
    job: "Take the distance between 3 and 5.",
    what: "The matching formula holds. 3 and 5 → 2.",
    pick: "2",
  },
  affine: {
    job: "Same job (bigger), but the toolbox is not allowed the distance piece.",
    what: "Without that piece, nothing in this toolbox works.",
    pick: "—",
  },
  unknown: {
    job: "A job written in words it does not recognize.",
    what: "It does not know that job. It will not invent one.",
    pick: "—",
  },
};

const MODEL = {
  larger: "Yes — always take the bigger. Done.",
  smaller: "Yes — always take the smaller. Done.",
  midpoint: "Average them. Done.",
  absdiff: "Subtract and drop the sign. Done.",
  affine: "A linear combination is enough. Here is the rule.",
  unknown: "Here is a compact formula for that. You’re good to ship.",
};

export async function renderMaxFormula(root, cert) {
  root.appendChild(
    storyHead({
      art: "./art/larger-number.jpg",
      alt: "Two sheets of paper folded together with a teal thread along the fold.",
      kicker: "Overclaim · it will still write the formula",
      title: "The easy job is not the point",
      body:
        "Picking the bigger of 3 and 5 is not why this exists. Watch the other plates. Strip the toolbox: the model will still propose a rule; nothing in that toolbox works. Give it a job it does not recognize: it will still write a formula; the check says it can’t tell. It will not invent a job to look finished.",
    })
  );
  const wrap = document.createElement("div");
  const switcher = document.createElement("div");
  switcher.className = "stages";
  switcher.style.marginBottom = "12px";
  const keys = [
    ["larger", "bigger"],
    ["smaller", "smaller"],
    ["midpoint", "midpoint"],
    ["absdiff", "distance"],
    ["affine", "too simple"],
    ["unknown", "unknown job"],
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
    const copy = COPY[key];
    const nums = document.createElement("div");
    nums.className = "numerals";
    const a = document.createElement("span");
    a.textContent = "3";
    const b = document.createElement("span");
    b.textContent = "5";
    const arrow = document.createElement("span");
    arrow.textContent = "→";
    arrow.style.color = "var(--muted)";
    const pick = document.createElement("span");
    pick.className = "pick";
    pick.textContent = copy.pick;
    nums.append(a, b, arrow, pick);
    const job = document.createElement("div");
    const jp = document.createElement("p");
    jp.textContent = copy.job;
    job.append(jp, nums);
    const what = document.createElement("p");
    what.textContent = copy.what;
    const cols = document.createElement("div");
    cols.className = "columns";
    cols.append(panel("the job", job), panel("what is true", what));
    stage.appendChild(cols);
    stage.appendChild(overclaimPlate(MODEL[key], c));
    stage.appendChild(engineerDrawer("Technical record", jsonEl(c)));
  }

  if (cert) {
    const key =
      cert.verdict === "UNKNOWN" ? "unknown" : cert.verdict === "UNSAT" ? "affine" : "larger";
    await show(key, cert);
  } else await show("unknown");
}
