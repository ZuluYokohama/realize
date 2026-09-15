import { jsonEl, loadJSON, metaEl, panel, stampEl } from "../stamp.js";

const FILES = {
  larger: "./fixtures/max_formula.larger.json",
  smaller: "./fixtures/max_formula.smaller.json",
  midpoint: "./fixtures/max_formula.midpoint.json",
  absdiff: "./fixtures/max_formula.absdiff.json",
  affine: "./fixtures/max_formula.affine_unsat.json",
  unknown: "./fixtures/max_formula.unknown.json",
};

function halfplanes(identities) {
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("class", "ev");
  svg.setAttribute("viewBox", "0 0 420 220");
  svg.setAttribute("role", "img");
  svg.innerHTML = `
    <polygon points="20,20 200,20 200,200 20,200" fill="#12151a" stroke="#2a2e33"/>
    <polygon points="200,20 200,200 20,200" fill="#161c1b" stroke="#2a9d8f"/>
    <text x="110" y="36" text-anchor="middle" fill="#8b9088" font-size="11" font-family="IBM Plex Mono, monospace">a ≥ b</text>
    <polygon points="220,20 400,20 400,200 220,200" fill="#12151a" stroke="#2a2e33"/>
    <polygon points="220,20 400,20 400,200" fill="#161c1b" stroke="#2a9d8f"/>
    <text x="310" y="36" text-anchor="middle" fill="#8b9088" font-size="11" font-family="IBM Plex Mono, monospace">b ≥ a</text>
  `;
  const a = identities?.a_ge_b;
  const b = identities?.b_ge_a;
  const t1 = document.createElementNS("http://www.w3.org/2000/svg", "text");
  t1.setAttribute("x", "110");
  t1.setAttribute("y", "120");
  t1.setAttribute("text-anchor", "middle");
  t1.setAttribute("fill", "#e6e2d8");
  t1.setAttribute("font-size", "12");
  t1.setAttribute("font-family", "IBM Plex Mono, monospace");
  t1.textContent = a ? `want ${a.want.join(",")}  got ${a.got.join(",")}` : "";
  const t2 = t1.cloneNode();
  t2.setAttribute("x", "310");
  t2.textContent = b ? `want ${b.want.join(",")}  got ${b.got.join(",")}` : "";
  svg.append(t1, t2);
  return svg;
}

export async function renderMaxFormula(root, cert) {
  const wrap = document.createElement("div");
  const switcher = document.createElement("div");
  switcher.className = "stages";
  switcher.style.marginBottom = "12px";
  const keys = [
    ["larger", "larger"],
    ["smaller", "smaller"],
    ["midpoint", "midpoint"],
    ["absdiff", "absdiff"],
    ["affine", "affine only"],
    ["unknown", "unrecognized"],
  ];
  let current = "larger";

  async function show(key, fromCert) {
    current = key;
    for (const b of switcher.querySelectorAll("button")) {
      b.classList.toggle("on", b.dataset.key === key);
    }
    const c = fromCert || (await loadJSON(FILES[key]));
    mount(c);
  }

  for (const [key, label] of keys) {
    const b = document.createElement("button");
    b.className = "chip";
    b.dataset.key = key;
    b.textContent = label;
    b.addEventListener("click", () => show(key));
    switcher.appendChild(b);
  }
  wrap.appendChild(switcher);
  const stage = document.createElement("div");
  wrap.appendChild(stage);
  root.appendChild(wrap);

  function mount(c) {
    stage.replaceChildren();
    const cols = document.createElement("div");
    cols.className = "columns";
    const spec = {
      grammar: "bounded_coeff_template",
      phrase: c.witness?.phrase || c.spec_id,
      template: "c0 + c1 a + c2 b + c3 |a-b|",
    };
    const ev = document.createElement("div");
    if (c.witness?.identities) ev.appendChild(halfplanes(c.witness.identities));
    else {
      const p = document.createElement("p");
      p.className = "caption";
      p.textContent =
        c.verdict === "UNSAT"
          ? `Empty template. universe=${c.witness?.universe ?? "125"} valid=0`
          : c.witness?.reason || "no identities on this plate";
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

  if (cert) {
    await show("larger", cert);
  } else {
    await show("larger");
  }
}
