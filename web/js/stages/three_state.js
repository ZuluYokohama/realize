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
  p.textContent = `free ${accepts.join(" or ")}`;
  el.append(h, chips, p);
  return el;
}

export async function renderThreeState(root, cert) {
  if (!cert) cert = await loadJSON("./fixtures/three_state.certificate.json");
  root.appendChild(
    storyHead({
      art: "./art/three-keys.jpg",
      alt: "Three iron keys on one ring that never meet in the middle.",
      kicker: "Overclaim · every pair works",
      title: "Every pair can meet. The group cannot.",
      body:
        "Ask a model to find one time three people can meet. Ava can do Monday or Tuesday, Ben Tuesday or Wednesday, Cy Monday or Wednesday. Every pair has a day. There is no day for all three. Models report the pairs and call it done. The check stamps: nothing here works.",
    })
  );
  const people = document.createElement("div");
  people.className = "people";
  people.append(
    person("Ava", ["Mon", "Tue"]),
    person("Ben", ["Tue", "Wed"]),
    person("Cy", ["Mon", "Wed"])
  );
  const meaning = document.createElement("p");
  meaning.className = "caption";
  meaning.textContent =
    "A shared day would have to sit in all three calendars. It doesn’t.";
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
