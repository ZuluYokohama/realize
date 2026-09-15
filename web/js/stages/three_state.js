import { jsonEl, loadJSON, metaEl, stampEl } from "../stamp.js";

const SVG = `
<svg class="ev" viewBox="0 0 420 280" role="img" aria-label="Three inputs on one fibre z, empty triple intersection">
  <rect x="150" y="20" width="120" height="36" fill="none" stroke="#7b6bbe"/>
  <text x="210" y="43" text-anchor="middle" fill="#e6e2d8" font-size="13" font-family="IBM Plex Mono, monospace">fibre z</text>
  <line x1="210" y1="56" x2="70" y2="130" stroke="#2a2e33"/>
  <line x1="210" y1="56" x2="210" y2="130" stroke="#2a2e33"/>
  <line x1="210" y1="56" x2="350" y2="130" stroke="#2a2e33"/>
  <circle cx="70" cy="150" r="28" fill="#12151a" stroke="#e6e2d8"/>
  <circle cx="210" cy="150" r="28" fill="#12151a" stroke="#e6e2d8"/>
  <circle cx="350" cy="150" r="28" fill="#12151a" stroke="#e6e2d8"/>
  <text x="70" y="155" text-anchor="middle" fill="#e6e2d8" font-size="16" font-family="IBM Plex Mono, monospace">0</text>
  <text x="210" y="155" text-anchor="middle" fill="#e6e2d8" font-size="16" font-family="IBM Plex Mono, monospace">1</text>
  <text x="350" y="155" text-anchor="middle" fill="#e6e2d8" font-size="16" font-family="IBM Plex Mono, monospace">2</text>
  <text x="70" y="198" text-anchor="middle" fill="#8b9088" font-size="11" font-family="IBM Plex Mono, monospace">{0,1}</text>
  <text x="210" y="198" text-anchor="middle" fill="#8b9088" font-size="11" font-family="IBM Plex Mono, monospace">{1,2}</text>
  <text x="350" y="198" text-anchor="middle" fill="#8b9088" font-size="11" font-family="IBM Plex Mono, monospace">{0,2}</text>
  <text x="140" y="128" fill="#2a9d8f" font-size="10" font-family="IBM Plex Mono, monospace">∩ {1}</text>
  <text x="255" y="128" fill="#2a9d8f" font-size="10" font-family="IBM Plex Mono, monospace">∩ {2}</text>
  <text x="185" y="230" fill="#2a9d8f" font-size="10" font-family="IBM Plex Mono, monospace">∩ {0}</text>
  <rect x="125" y="240" width="170" height="28" fill="none" stroke="#7b6bbe"/>
  <text x="210" y="259" text-anchor="middle" fill="#7b6bbe" font-size="12" font-family="IBM Plex Mono, monospace">∩ triple = ∅  {0,1,2}</text>
</svg>
`;

export async function renderThreeState(root, cert) {
  if (!cert) cert = await loadJSON("./fixtures/three_state.certificate.json");
  const cols = document.createElement("div");
  cols.className = "columns";
  const spec = {
    id: "vcms.three_state",
    R: { 0: [0, 1], 1: [1, 2], 2: [0, 2] },
    encoder: "collapse_all → z",
  };
  const ev = document.createElement("div");
  ev.innerHTML = SVG;
  const cap = document.createElement("p");
  cap.className = "caption";
  cap.textContent = "Pairwise intersections are nonempty. The fibre is not.";
  ev.appendChild(cap);
  const right = document.createElement("div");
  right.appendChild(stampEl(cert.verdict));
  right.appendChild(metaEl(cert));
  cols.append(panel("spec", jsonEl(spec)), panel("evidence", ev), panel("certificate", right));
  root.appendChild(cols);
}

function panel(title, child) {
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
