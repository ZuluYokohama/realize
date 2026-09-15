import { adapterEl, storyHead } from "./stamp.js";
import { renderGeneric } from "./stages/generic.js";
import { renderThreeState } from "./stages/three_state.js";
import { renderMaxFormula } from "./stages/max_formula.js";
import { renderGrid } from "./stages/grid_recolor.js";

function looksLikeCertificate(obj) {
  return (
    obj &&
    typeof obj === "object" &&
    typeof obj.verdict === "string" &&
    typeof obj.spec_digest === "string" &&
    obj.checker &&
    obj.checker.name
  );
}

function looksLikeSpec(obj) {
  return obj && obj.specification && obj.problem_family && !obj.verdict;
}

function looksLikeCandidate(obj) {
  return obj && obj.term && obj.spec_id && !obj.verdict;
}

export function renderPaste(root) {
  root.appendChild(
    storyHead({
      art: "./art/hero.jpg",
      alt: "Brass inspection stamp and teal wax seal.",
      kicker: "Display only",
      title: "Paste a result from your computer",
      body:
        "This page cannot check a job. Run realize check on your computer, then paste the JSON it prints. If you paste the job or the guess instead of the result, it will refuse.",
    })
  );
  const box = document.createElement("div");
  const ta = document.createElement("textarea");
  ta.className = "paste";
  ta.setAttribute("aria-label", "Stamp JSON from realize check");
  ta.placeholder = "Paste the JSON printed by: realize check spec.json candidate.json";
  const btn = document.createElement("button");
  btn.className = "enter";
  btn.style.marginTop = "12px";
  btn.textContent = "Show the stamp";
  const out = document.createElement("div");
  out.style.marginTop = "20px";
  btn.addEventListener("click", () => {
    out.replaceChildren();
    let obj;
    try {
      obj = JSON.parse(ta.value);
    } catch (err) {
      out.appendChild(adapterEl(`That is not JSON: ${err.message}`));
      return;
    }
    if (looksLikeSpec(obj)) {
      out.appendChild(
        adapterEl("That looks like the job, not the stamp. Run realize check on your machine and paste what it prints.")
      );
      return;
    }
    if (looksLikeCandidate(obj)) {
      out.appendChild(
        adapterEl("That looks like a proposed answer, not the stamp. Run realize check and paste stdout.")
      );
      return;
    }
    if (!looksLikeCertificate(obj)) {
      out.appendChild(
        adapterEl("A stamp needs verdict, spec_digest, and checker.name.")
      );
      return;
    }
    if (obj.checker.name !== "realize.checker") {
      const w = document.createElement("div");
      w.className = "warn";
      w.textContent = `This stamp was issued by ${obj.checker.name}, not realize.checker. Shown as-is.`;
      out.appendChild(w);
    }
    dispatch(out, obj);
  });
  box.append(ta, btn, out);
  root.appendChild(box);
}

function dispatch(root, cert) {
  const fam = cert.scope?.problem_family;
  const grammar = cert.scope?.grammar;
  if (fam === "encoder" && grammar === "finite_case_table") {
    renderThreeState(root, cert);
    return;
  }
  if (fam === "formula") {
    renderMaxFormula(root, cert);
    return;
  }
  if (fam === "term_series" && grammar === "typed_grid") {
    renderGrid(root, cert);
    return;
  }
  renderGeneric(root, cert);
}
