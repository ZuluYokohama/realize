import {
  engineerDrawer,
  jsonEl,
  loadJSON,
  overclaimPlate,
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

function daysTable() {
  const days = ["Mon", "Tue", "Wed"];
  const rows = [
    ["Ava", [1, 1, 0]],
    ["Ben", [0, 1, 1]],
    ["Cy", [1, 0, 1]],
    ["all three", [0, 0, 0]],
  ];
  const table = document.createElement("table");
  table.className = "days";
  const thead = document.createElement("thead");
  const head = document.createElement("tr");
  head.appendChild(document.createElement("th"));
  for (const d of days) {
    const th = document.createElement("th");
    th.textContent = d;
    head.appendChild(th);
  }
  thead.appendChild(head);
  table.appendChild(thead);
  const tbody = document.createElement("tbody");
  for (const [name, marks] of rows) {
    const tr = document.createElement("tr");
    const n = document.createElement("th");
    n.scope = "row";
    n.textContent = name;
    tr.appendChild(n);
    for (const m of marks) {
      const td = document.createElement("td");
      td.textContent = m ? "yes" : "—";
      td.className = m ? "yes" : "no";
      tr.appendChild(td);
    }
    tbody.appendChild(tr);
  }
  table.appendChild(tbody);
  return table;
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
        "Every pair has a day. There is no day for all three. Models report the pairs and call it done.",
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
  job.append(people, daysTable(), meaning);
  const cols = document.createElement("div");
  cols.className = "columns";
  cols.append(panel("the calendars", job));
  root.appendChild(cols);
  root.appendChild(
    overclaimPlate(
      "Every pair overlaps, so there is a day that works for the group. You’re covered.",
      cert
    )
  );
  root.appendChild(
    engineerDrawer("Technical record", jsonEl({ id: "vcms.three_state", certificate: cert }))
  );
}
