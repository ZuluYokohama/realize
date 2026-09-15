import {
  engineerDrawer,
  humanStamp,
  jsonEl,
  loadJSON,
  metaEl,
  panel,
  storyHead,
} from "../stamp.js";

function person(name, accepts) {
  const el = document.createElement("div");
  el.className = "person";
  const h = document.createElement("h4");
  h.textContent = name;
  const chips = document.createElement("div");
  chips.className = "chips";
  for (const n of accepts) {
    const c = document.createElement("span");
    c.className = "chip-n";
    c.textContent = String(n);
    chips.appendChild(c);
  }
  const p = document.createElement("p");
  p.className = "caption";
  p.textContent = `will accept ${accepts.join(" or ")}`;
  el.append(h, chips, p);
  return el;
}

export async function renderThreeState(root, cert) {
  if (!cert) cert = await loadJSON("./fixtures/three_state.certificate.json");
  root.appendChild(
    storyHead({
      art: "./art/three-keys.jpg",
      alt: "Three iron keys on one ring that never meet in the middle.",
      kicker: "Example · nothing here works",
      title: "Three people, one door code",
      body:
        "Three coworkers must pick one code. Any two of them can agree. All three cannot. If an AI claimed it found a shared code, the check would stop it.",
    })
  );
  const people = document.createElement("div");
  people.className = "people";
  people.append(
    person("Ava", [0, 1]),
    person("Ben", [1, 2]),
    person("Cy", [0, 2])
  );
  const meaning = document.createElement("p");
  meaning.className = "caption";
  meaning.textContent =
    "A shared code would have to sit in all three lists. It doesn’t.";
  const job = document.createElement("div");
  job.append(people, meaning);
  const right = document.createElement("div");
  right.appendChild(humanStamp(cert.verdict));
  right.appendChild(metaEl(cert));
  const cols = document.createElement("div");
  cols.className = "columns";
  cols.append(panel("the job", job), panel("the result", right));
  root.appendChild(cols);
  root.appendChild(
    engineerDrawer("Technical record", jsonEl({ id: "vcms.three_state", certificate: cert }))
  );
}
