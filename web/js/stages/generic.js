import { jsonEl, metaEl, panel, stampEl } from "../stamp.js";

export function renderGeneric(root, cert) {
  const cols = document.createElement("div");
  cols.className = "columns";
  const spec = panel("scope", jsonEl(cert.scope || {}));
  const ev = document.createElement("div");
  ev.appendChild(jsonEl(cert.witness || {}));
  const evidence = panel("witness", ev);
  const right = document.createElement("div");
  right.appendChild(stampEl(cert.verdict));
  right.appendChild(metaEl(cert));
  cols.append(spec, evidence, panel("certificate", right));
  root.appendChild(cols);
}
