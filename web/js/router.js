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
        <a href="#/studio/three_state" ${route.startsWith("/studio") ? 'aria-current="page"' : ""}>Examples</a>
        <a href="#/nonclaims" ${route === "/nonclaims" ? 'aria-current="page"' : ""}>Limits</a>
      </nav>
    </header>`;
}

function landing() {
  return `
    ${topbar("/")}
    <figure class="hero">
      <img src="./art/hero.jpg" width="1792" height="1008" alt="A brass inspection stamp and teal wax seal on a dark steel bench." />
    </figure>
    <h1 class="claim">An independent inspector for answers from AI.</h1>
    <p class="lede">
      Your model can propose a solution. realize stamps whether that solution actually holds —
      and when it cannot tell, it says so. This page only shows stamps. It never inspects.
    </p>
    <div class="steps">
      <article>
        <h3>1. The job</h3>
        <p>Write what must be true. “Always pick the larger number.” “Recolor this picture.”</p>
      </article>
      <article>
        <h3>2. A proposal</h3>
        <p>A person or an AI suggests an answer — a formula, a sequence of steps, a guess.</p>
      </article>
      <article>
        <h3>3. The stamp</h3>
        <p>On your machine, <code>realize check</code> inspects the proposal. Four stamps. Never a shrug dressed as yes.</p>
      </article>
    </div>
    <p class="kicker">The four stamps</p>
    <figure class="hero" style="margin-bottom:12px">
      <img src="./art/four-tags.jpg" width="1792" height="1008" alt="Four metal inspection tags: teal, amber, violet, graphite." />
    </figure>
    <div class="tiles" aria-label="The four stamps">
      <div class="tile"><div class="v v-pass">Holds</div><p>This answer works for the job as written. Technical name: PASS.</p></div>
      <div class="tile"><div class="v v-counter">This one fails</div><p>We found a case where it breaks. Technical name: COUNTEREXAMPLE.</p></div>
      <div class="tile"><div class="v v-unsat">Empty catalog</div><p>Nothing in this small list of possible answers works. Technical name: UNSAT.</p></div>
      <div class="tile"><div class="v v-unknown">Not enough</div><p>We ran out of time, or the question is outside what we can inspect. Technical name: UNKNOWN.</p></div>
    </div>
    <section class="nonclaims">
      <h2>What this is not</h2>
      <ol>
        <li>It does not understand arbitrary English. Unrecognized jobs get “Not enough.”</li>
        <li>It does not let the AI grade itself. The inspector is a separate program.</li>
        <li>Wishing for a nicer answer does not change the evidence.</li>
        <li>This webpage cannot certify anything. Paste a stamp from your computer.</li>
      </ol>
      <p><a href="#/nonclaims">The full list of limits</a></p>
    </section>
    <p class="kicker">Three worked examples</p>
    <div class="stories">
      <a class="story" href="#/studio/three_state">
        <img src="./art/three-keys.jpg" alt="" />
        <div class="pad">
          <h3>Three keys, one lock</h3>
          <p>Any two people can agree. All three cannot. Stamp: empty catalog.</p>
        </div>
      </a>
      <a class="story" href="#/studio/max_formula">
        <img src="./art/larger-number.jpg" alt="" />
        <div class="pad">
          <h3>Always pick the larger number</h3>
          <p>A short formula holds. A too-simple catalog is empty.</p>
        </div>
      </a>
      <a class="story" href="#/studio/grid_recolor">
        <img src="./art/recolor.jpg" alt="" />
        <div class="pad">
          <h3>Recolor a picture</h3>
          <p>Recolor holds. Keep the same colors while recoloring does not.</p>
        </div>
      </a>
    </div>
    <a class="enter" href="#/studio/three_state">Open the examples</a>
    <div class="install">
      <p>The inspector lives on your machine, not in this browser:</p>
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
    <a href="https://github.com/ZuluYokohama/realize/blob/main/skills/realize/SKILL.md">for agents</a>
    <a href="https://github.com/ZuluYokohama/realize/blob/main/papers/README.md">papers</a>
  </footer>`;
}

function studioChrome(stage) {
  const items = [
    ["three_state", "Three keys"],
    ["max_formula", "Larger number"],
    ["grid_recolor", "Recolor"],
    ["paste", "Paste a stamp"],
  ];
  const links = items
    .map(
      ([id, label]) =>
        `<a href="#/studio/${id}" ${stage === id ? 'aria-current="page"' : ""}>${label}</a>`
    )
    .join("");
  return `${topbar("/studio")}
    <div class="studio-head">
      <p class="mark">examples — this page only displays stamps</p>
      <nav class="stages">${links}</nav>
    </div>
    <div id="stage"></div>
    ${footer()}`;
}

function nonclaims() {
  return `${topbar("/nonclaims")}
    <h1 class="claim">Limits, in plain language</h1>
    <p class="lede">realize is a small, honest inspector. It is useful because of what it refuses to pretend.</p>
    <section class="nonclaims">
      <ol>
        <li><strong>Not a universal English compiler.</strong> If the job is not in its catalog, it stamps “Not enough.” It will not invent a formal job from a paragraph.</li>
        <li><strong>“Not enough” is required.</strong> Some questions cannot be settled with the time and catalog you gave. That is not a hidden “no.”</li>
        <li><strong>Wishes do not rewrite evidence.</strong> Preferences never flip a fail into a hold.</li>
        <li><strong>No geometry theatre, no consciousness claims.</strong> This package is a checker.</li>
        <li><strong>Counts are coverage, not a leaderboard.</strong></li>
        <li><strong>A proof about a model is not a measurement of the world.</strong></li>
        <li><strong>Independence blocks one cheating path.</strong> It does not bless the Python runtime.</li>
        <li><strong>Empty catalog is scoped.</strong> It means “nothing in this list,” not “no answer exists anywhere.”</li>
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
