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
