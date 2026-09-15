import {
  engineerDrawer,
  humanStamp,
  jsonEl,
  loadJSON,
  metaEl,
  panel,
  storyHead,
} from "../stamp.js";

export async function renderThreeState(root, cert) {
  if (!cert) cert = await loadJSON("./fixtures/three_state.certificate.json");
  root.appendChild(
    storyHead({
      art: "./art/three-keys.jpg",
      alt: "Three iron keys on one ring that never meet in the middle.",
      kicker: "Example · empty catalog",
      title: "Three keys, one lock",
      body:
        "Three people must share one combination. Any two of them can agree. All three cannot. The inspector does not pick a winner. It stamps: this catalog is empty.",
    })
  );
  const cols = document.createElement("div");
  cols.className = "columns";
  const job = document.createElement("div");
  job.innerHTML =
    "<p>Person 0 will accept 0 or 1.<br>Person 1 will accept 1 or 2.<br>Person 2 will accept 0 or 2.</p><p class='caption'>Pairwise agreements exist. The triple does not.</p>";
  const right = document.createElement("div");
  right.appendChild(humanStamp(cert.verdict));
  right.appendChild(metaEl(cert));
  cols.append(
    panel("the job", job),
    panel("what that means", document.createTextNode("A shared answer would have to live in all three lists at once. Those lists have no common number.")),
    panel("the stamp", right)
  );
  root.appendChild(cols);
  root.appendChild(
    engineerDrawer(
      "Technical record (spec, certificate)",
      jsonEl({ spec: { id: "vcms.three_state", encoder: "collapse_all" }, certificate: cert })
    )
  );
}
