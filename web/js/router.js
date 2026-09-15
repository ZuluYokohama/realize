import { renderThreeState } from "./stages/three_state.js";
import { renderMaxFormula } from "./stages/max_formula.js";
import { renderGrid } from "./stages/grid_recolor.js";
import { renderPaste } from "./paste.js";

function topbar(route) {
  return `
    <header class="topbar">
      <a class="mark" href="#/">realize</a>
      <nav class="nav">
        <a href="#/" ${route === "/" ? 'aria-current="page"' : ""}>What it is</a>
        <a href="#/studio/three_state" ${route.startsWith("/studio") ? 'aria-current="page"' : ""}>See it work</a>
        <a href="#/nonclaims" ${route === "/nonclaims" ? 'aria-current="page"' : ""}>Limits</a>
      </nav>
    </header>`;
}

function footer() {
  return `<footer class="foot">
    <span>MIT</span>
    <a href="https://github.com/ZuluYokohama/realize">source</a>
    <a href="https://github.com/ZuluYokohama/realize/blob/main/skills/realize/SKILL.md">for agents</a>
    <a href="https://github.com/ZuluYokohama/realize/blob/main/papers/README.md">papers</a>
  </footer>`;
}

function studioChrome(stage) {
  const items = [
    ["three_state", "Three people"],
    ["max_formula", "Larger number"],
    ["grid_recolor", "Recolor"],
    ["paste", "Paste a result"],
  ];
  const links = items
    .map(
      ([id, label]) =>
        `<a href="#/studio/${id}" ${stage === id ? 'aria-current="page"' : ""}>${label}</a>`
    )
    .join("");
  return `${topbar("/studio")}
    <div class="studio-head">
      <p class="mark">examples — display only</p>
      <nav class="stages">${links}</nav>
    </div>
    <div id="stage"></div>
    ${footer()}`;
}

function limits() {
  return `${topbar("/nonclaims")}
    <h1 class="claim">What it will not pretend</h1>
    <p class="lede">It is useful because it refuses to bluff.</p>
    <section class="nonclaims">
      <ol>
        <li><strong>Not every English sentence is a job it can check.</strong> If it does not recognize the job, it says it cannot tell. It will not invent the rules from a paragraph.</li>
        <li><strong>“Can’t tell yet” is a real answer.</strong> Running out of time is not a hidden no.</li>
        <li><strong>Wanting a nicer result does not change the check.</strong></li>
        <li><strong>This is a checker, not a theory of mind.</strong></li>
        <li><strong>A proof about a model is not a measurement of the world.</strong></li>
        <li><strong>The AI may propose. It may not certify.</strong> This page cannot certify either.</li>
      </ol>
    </section>
    ${footer()}`;
}

function parseRoute() {
  const h = (location.hash || "").replace(/^#/, "");
  if (!h || h === "/") return { name: "landing" };
  if (h === "/nonclaims") return { name: "limits" };
  if (h === "/studio") return { name: "studio", stage: "three_state" };
  const m = h.match(/^\/studio\/(three_state|max_formula|grid_recolor|paste)$/);
  if (m) return { name: "studio", stage: m[1] };
  return { name: "landing" };
}

async function render() {
  const landing = document.getElementById("landing");
  const app = document.getElementById("app");
  const route = parseRoute();
  if (route.name === "landing") {
    landing.hidden = false;
    app.hidden = true;
    app.replaceChildren();
    return;
  }
  landing.hidden = true;
  app.hidden = false;
  if (route.name === "limits") {
    app.innerHTML = limits();
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
render();
