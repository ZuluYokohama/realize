const TOKEN = {
  PASS: "v-pass",
  COUNTEREXAMPLE: "v-counter",
  UNSAT: "v-unsat",
  UNKNOWN: "v-unknown",
};

export function stampEl(verdict) {
  const el = document.createElement("div");
  el.className = `stamp ${TOKEN[verdict] || "v-unknown"}`;
  el.textContent = verdict || "UNKNOWN";
  el.setAttribute("role", "status");
  return el;
}

export function adapterEl(message) {
  const el = document.createElement("div");
  el.className = "adapter";
  el.setAttribute("role", "alert");
  el.textContent = message;
  return el;
}

export function metaEl(cert) {
  const wrap = document.createElement("div");
  wrap.className = "meta mono";
  const rows = [
    ["spec_id", cert.spec_id],
    ["spec_digest", cert.spec_digest],
    ["checker", cert.checker ? `${cert.checker.name} ${cert.checker.version}` : ""],
    ["optimality", cert.optimality],
  ];
  for (const [k, v] of rows) {
    const d = document.createElement("div");
    d.textContent = `${k}: ${v ?? ""}`;
    wrap.appendChild(d);
  }
  return wrap;
}

export function jsonEl(obj) {
  const pre = document.createElement("pre");
  pre.className = "json";
  pre.textContent = JSON.stringify(obj, null, 2);
  return pre;
}

export function panel(title, child) {
  const p = document.createElement("section");
  p.className = "panel";
  const h = document.createElement("h3");
  h.textContent = title;
  const body = document.createElement("div");
  body.className = "body";
  body.appendChild(child);
  p.append(h, body);
  return p;
}

export async function loadJSON(path) {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`fixture ${path}: ${res.status}`);
  return res.json();
}

export function storyHead({ kicker, title, art, alt, body }) {
  const wrap = document.createElement("div");
  wrap.className = "story-copy";
  const fig = document.createElement("figure");
  fig.className = "plate";
  const img = document.createElement("img");
  img.src = art;
  img.alt = alt || "";
  fig.appendChild(img);
  const k = document.createElement("p");
  k.className = "kicker";
  k.textContent = kicker;
  const h = document.createElement("h2");
  h.textContent = title;
  const p = document.createElement("p");
  p.textContent = body;
  wrap.append(fig, k, h, p);
  return wrap;
}

export function engineerDrawer(label, node) {
  const d = document.createElement("details");
  d.className = "eng";
  const s = document.createElement("summary");
  s.textContent = label;
  d.append(s, node);
  return d;
}

export function humanStamp(verdict) {
  const map = {
    PASS: "It holds",
    COUNTEREXAMPLE: "This one is wrong",
    UNSAT: "Nothing here works",
    UNKNOWN: "Can't tell yet",
  };
  const wrap = document.createElement("div");
  const el = stampEl(verdict);
  el.textContent = map[verdict] || verdict;
  wrap.appendChild(el);
  const note = document.createElement("p");
  note.className = "caption mono";
  note.textContent = verdict || "";
  wrap.appendChild(note);
  return wrap;
}
