import { fetchEvidenceReport } from "./load.js";
import { renderEvidenceError, renderEvidenceReport } from "./render.js";

const form = document.querySelector("#evidence-query");
const output = document.querySelector("#evidence-output");

function fieldValue(name) {
  const data = new FormData(form);
  return String(data.get(name) || "").trim();
}

function queryFields() {
  return {
    dog_id: fieldValue("dog_id"),
    observation_type: fieldValue("observation_type"),
    as_of: fieldValue("as_of"),
    generated_at: fieldValue("generated_at"),
  };
}

function writePageQuery(fields) {
  const search = new URLSearchParams();
  search.set("dog_id", fields.dog_id);
  if (fields.observation_type) search.set("observation_type", fields.observation_type);
  if (fields.as_of) search.set("as_of", fields.as_of);
  if (fields.generated_at) search.set("generated_at", fields.generated_at);
  const next = `${window.location.pathname}?${search.toString()}`;
  window.history.replaceState(null, "", next);
}

async function loadReport(event) {
  if (event) event.preventDefault();
  const fields = queryFields();
  if (!fields.dog_id) {
    output.innerHTML = renderEvidenceError({
      code: "",
      message: "A dog id is required to request the evidence report.",
    });
    return;
  }
  writePageQuery(fields);
  output.innerHTML = `<p class="evidence-loading">Loading evidence report…</p>`;
  try {
    const result = await fetchEvidenceReport(window.fetch.bind(window), fields.dog_id, fields);
    output.innerHTML = result.ok ? renderEvidenceReport(result.report) : renderEvidenceError(result.error);
  } catch (err) {
    output.innerHTML = renderEvidenceError({
      code: "",
      message: err instanceof Error ? err.message : "The evidence report request failed.",
    });
  }
}

function fillFromLocation() {
  const search = new URLSearchParams(window.location.search);
  for (const name of ["dog_id", "observation_type", "as_of", "generated_at"]) {
    const input = form.elements.namedItem(name);
    if (input && search.has(name)) input.value = search.get(name) || "";
  }
}

form.addEventListener("submit", loadReport);
fillFromLocation();
if (fieldValue("dog_id")) {
  loadReport();
}
