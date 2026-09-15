import { renderThreeState } from "./stages/three_state.js";
import { renderMaxFormula } from "./stages/max_formula.js";
import { renderGrid } from "./stages/grid_recolor.js";
import { renderPaste } from "./paste.js";

const CLAIM =
  "Independent checker for value-conditioned operator synthesis. Finite kernel. Four verdicts. Agents cannot grade themselves.";

function topbar(route) {
  return `
    <header class="topbar">
      <a class="mark" href="#/">realize</a>
      <nav class="nav">
        <a href="#/" ${route === "/" ? 'aria-current="page"' : ""}>index</a>
        <a href="#/studio/three_state" ${route.startsWith("/studio") ? 'aria-current="page"' : ""}>studio</a>
        <a href="#/nonclaims" ${route === "/nonclaims" ? 'aria-current="page"' : ""}>non-claims</a>
      </nav>
    </header>`;
}

function landing() {
  return `
    ${topbar("/")}
    <p class="claim">${CLAIM}</p>
    <section class="nonclaims">
      <h2>Non-claims — read first</h2>
      <ol>
        <li>Not a universal NL compiler.</li>
        <li><code>UNKNOWN</code> is required.</li>
        <li>Value does not rewrite evidence.</li>
        <li>This page cannot certify. Paste a certificate from <code>realize check</code>.</li>
      </ol>
      <p><a href="#/nonclaims">Full non-claims</a></p>
    </section>
    <div class="tiles" aria-label="Verdict legend">
      <div class="tile"><div class="v v-pass">PASS</div><p>This candidate meets R and K at the declared scope.</p></div>
      <div class="tile"><div class="v v-counter">COUNTEREXAMPLE</div><p>This candidate is false. Not a claim about the class.</p></div>
      <div class="tile"><div class="v v-unsat">UNSAT</div><p>The declared finite class is empty. Scoped, never “no operator exists.”</p></div>
      <div class="tile"><div class="v v-unknown">UNKNOWN</div><p>Budget, coverage, or evidence is insufficient.</p></div>
    </div>
    <a class="enter" href="#/studio/three_state">Enter studio</a>
    <div class="install">
      <p>Kernel (not this page):</p>
      <pre>pip install realize
realize demo three_state
realize check spec.json candidate.json</pre>
    </div>
    ${footer()}`;
}

function footer() {
  return `<footer class="foot">
    <span>MIT</span>
    <a href="https://github.com/ZuluYokohama/realize">source</a>
    <a href="https://github.com/ZuluYokohama/realize/blob/main/skills/realize/SKILL.md">SKILL.md</a>
    <a href="https://github.com/ZuluYokohama/realize/blob/main/papers/README.md">papers</a>
  </footer>`;
}

function studioChrome(stage) {
  const items = [
    ["three_state", "three_state"],
    ["max_formula", "max_formula"],
    ["grid_recolor", "grid_recolor"],
    ["paste", "paste"],
  ];
  const links = items
    .map(
      ([id, label]) =>
        `<a href="#/studio/${id}" ${stage === id ? 'aria-current="page"' : ""}>${label}</a>`
    )
    .join("");
  return `${topbar("/studio")}
    <div class="studio-head">
      <p class="mark">certificate studio — render only</p>
      <nav class="stages">${links}</nav>
    </div>
    <div id="stage"></div>
    ${footer()}`;
}

function nonclaims() {
  return `${topbar("/nonclaims")}
    <h1 class="claim">Non-claims</h1>
    <section class="nonclaims">
      <ol>
        <li><strong>Not a universal natural-language compiler.</strong> Unrecognized phrases return UNKNOWN. The package does not invent a formal R from English.</li>
        <li><strong>UNKNOWN is required.</strong> There is no total exact solver for the unrestricted class. Zero budget and incomplete coverage are UNKNOWN, not UNSAT.</li>
        <li><strong>Value does not rewrite evidence.</strong> Preferences never flip a fail to a pass.</li>
        <li><strong>Geometry, topology, Φ, sheaves, and IsoZ are not in this package</strong> and are not on this page.</li>
        <li><strong>Counts are coverage, not benchmark superiority.</strong></li>
        <li><strong>A proof in a model is not an observation of the world.</strong></li>
        <li><strong>Checker independence reduces one self-confirmation path.</strong> It does not certify the Python runtime.</li>
        <li><strong>UNSAT is scoped</strong> to the declared finite class.</li>
        <li><strong>Agents may propose. They may not certify.</strong> This page cannot certify either.</li>
      </ol>
    </section>
    ${footer()}`;
}

function parseRoute() {
  const h = (location.hash || "#/").replace(/^#/, "") || "/";
  if (h === "/" || h === "") return { name: "landing" };
  if (h === "/nonclaims") return { name: "nonclaims" };
  if (h === "/studio") return { name: "studio", stage: "three_state" };
  const m = h.match(/^\/studio\/(three_state|max_formula|grid_recolor|paste)$/);
  if (m) return { name: "studio", stage: m[1] };
  return { name: "landing" };
}

async function render() {
  const app = document.getElementById("app");
  const route = parseRoute();
  if (route.name === "landing") {
    app.innerHTML = landing();
    return;
  }
  if (route.name === "nonclaims") {
    app.innerHTML = nonclaims();
    return;
  }
  app.innerHTML = studioChrome(route.stage);
  const stage = document.getElementById("stage");
  try {
    if (route.stage === "three_state") await renderThreeState(stage);
    else if (route.stage === "max_formula") await renderMaxFormula(stage);
    else if (route.stage === "grid_recolor") await renderGrid(stage);
    else renderPaste(stage);
  } catch (err) {
    stage.textContent = String(err);
  }
}

window.addEventListener("hashchange", render);
if (!location.hash) location.hash = "#/";
render();
