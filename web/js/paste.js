import { adapterEl } from "./stamp.js";
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
  const box = document.createElement("div");
  const ta = document.createElement("textarea");
  ta.className = "paste";
  ta.setAttribute("aria-label", "Certificate JSON");
  ta.placeholder = "Paste a realize.v0 certificate JSON from `realize check` stdout.";
  const btn = document.createElement("button");
  btn.className = "enter";
  btn.style.marginTop = "12px";
  btn.textContent = "Render";
  const out = document.createElement("div");
  out.style.marginTop = "20px";
  btn.addEventListener("click", () => {
    out.replaceChildren();
    let obj;
    try {
      obj = JSON.parse(ta.value);
    } catch (err) {
      out.appendChild(adapterEl(`JSON parse: ${err.message}`));
      return;
    }
    if (looksLikeSpec(obj)) {
      out.appendChild(
        adapterEl("This looks like a spec. Run `realize check` locally and paste the certificate.")
      );
      return;
    }
    if (looksLikeCandidate(obj)) {
      out.appendChild(
        adapterEl("This looks like a candidate. Run `realize check spec.json candidate.json` and paste stdout.")
      );
      return;
    }
    if (!looksLikeCertificate(obj)) {
      out.appendChild(
        adapterEl("Certificate missing verdict, spec_digest, or checker.name.")
      );
      return;
    }
    if (obj.checker.name !== "realize.checker") {
      const w = document.createElement("div");
      w.className = "warn";
      w.textContent = `checker.name is ${obj.checker.name}, not realize.checker. Rendered anyway; not relabeled.`;
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
