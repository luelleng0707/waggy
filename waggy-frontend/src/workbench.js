/* Phase U reconstruction from the current HTTP and interface contracts.
   Care-history rows follow the array order from GET /api/v1/dogs/{dog_id}/events.
   That order is not a recovered historical sort. */
import { getApiBaseUrl } from "./api/config.js";
import {
  createDog,
  explainAnalysis,
  getDog,
  getRecalculationExplanation,
  listDogEvents,
  patchDog,
  recomputeDog,
  runWorkbenchAnalysis,
} from "./api/client.js";
import { DEMO_DOG, WORKBENCH_EXAMPLE_REQUEST } from "./demo/dogs.js";

var currentAnalysis = null;
var lastRecalculation = null;
var selectedBundleForNutrition = null;
var currentRole = "customer";

function $(id) {
  return document.getElementById(id);
}

function readForm() {
  var form = document.querySelector("#dog-profile-fields");
  var data = new FormData();
  form.querySelectorAll("input").forEach(function (input) {
    data.append(input.name, input.value);
  });
  var weight = data.get("weight");
  var budget = data.get("monthly_budget");
  var conditions = String(data.get("observed_conditions") || "")
    .split(",")
    .map(function (item) { return item.trim(); })
    .filter(Boolean);
  var body = {
    name: String(data.get("name") || ""),
    primary_breed: String(data.get("primary_breed") || ""),
    secondary_breed: String(data.get("secondary_breed") || ""),
    birthday: String(data.get("birthday") || ""),
    as_of_date: String(data.get("as_of_date") || ""),
    sex: String(data.get("sex") || ""),
    activity_level: String(data.get("activity_level") || ""),
    current_environment: String(data.get("current_environment") || ""),
    observed_conditions: conditions,
  };
  if (weight !== "") body.weight = Number(weight);
  if (budget !== "") body.monthly_budget = Number(budget);
  return body;
}

function roleContext() {
  return {
    groomer: {
      observations: ($("groomer-observations") && $("groomer-observations").value) || "",
      observed_conditions: [],
    },
    business: { segment: ($("business-segment") && $("business-segment").value) || "" },
  };
}

function dogIdFromForm() {
  return String(($("dog-id") && $("dog-id").value) || "").trim();
}

function setDogId(value) {
  if ($("dog-id")) $("dog-id").value = value;
}

function formatApiError(status, text) {
  var parsed = null;
  try {
    parsed = text ? JSON.parse(text) : null;
  } catch (err) {
    parsed = null;
  }
  if (parsed && parsed.error && parsed.error.message) {
    return (parsed.error.code ? parsed.error.code + ": " : "") + parsed.error.message;
  }
  return "API failure " + status + " response.status " + status;
}

function showError(message) {
  $("workbench-error").textContent = message;
}

function fillForm(profile) {
  var fields = ["name", "primary_breed", "secondary_breed", "birthday", "as_of_date", "sex", "activity_level", "current_environment"];
  fields.forEach(function (name) {
    var input = document.querySelector('#dog-profile-fields [name="' + name + '"]');
    if (input) input.value = profile[name] == null ? "" : String(profile[name]);
  });
  var weight = document.querySelector('#dog-profile-fields [name="weight"]');
  if (weight) weight.value = profile.weight == null ? "" : String(profile.weight);
  var conditions = document.querySelector('#dog-profile-fields [name="observed_conditions"]');
  if (conditions) conditions.value = (profile.observed_conditions || []).join(", ");
}

function updateIntakeForRole(role) {
  var dog = $("dog-profile-fields");
  dog.hidden = role === "developer";
  document.querySelectorAll("[data-view]").forEach(function (node) {
    if (node.id === "dog-profile-fields") return;
    node.hidden = node.getAttribute("data-view") !== role && node.getAttribute("data-view") !== "customer";
  });
  $("groomer-fields").hidden = role !== "groomer";
  $("business-fields").hidden = role !== "business";
  document.querySelector("[data-view='developer']").hidden = role !== "developer";
}

function persistRole(role) {
  var url = new URL(window.location.href);
  url.searchParams.set("role", role);
  window.history.replaceState(null, "", url.pathname + "?" + url.searchParams.toString());
}

function switchRole(role) {
  currentRole = role;
  persistRole(role);
  document.querySelectorAll("#role-selector [data-role]").forEach(function (button) {
    button.setAttribute("aria-pressed", button.getAttribute("data-role") === role ? "true" : "false");
  });
  updateIntakeForRole(role);
  if (currentAnalysis) renderRole(currentRole, currentAnalysis);
}

function emptyState() {
  $("package-view").textContent = "";
  $("health-analysis").textContent = "";
}

function roleFromLocation() {
  var path = window.location.pathname;
  if (path === "/business") return "business";
  if (path === "/developer") return "developer";
  if (path === "/classic" || path === "/demo" || path === "/") return "customer";
  var requested = new URLSearchParams(window.location.search).get("role");
  if (requested === "customer" || requested === "groomer" || requested === "business" || requested === "developer") {
    return requested;
  }
  return "customer";
}

function productNamesLine(option, nameOpts) {
  var products = (option && option.products) || [];
  var names = products.map(function (item) { return item.product_name; }).filter(Boolean);
  if (nameOpts && nameOpts.names === false) return "";
  return names.join(", ");
}

function renderCustomer(role) {
  var view = $("package-view");
  view.innerHTML = "";
  var heading = document.createElement("h2");
  heading.textContent = "Care packages";
  view.appendChild(heading);
  var options = (((role || {}).wellness || {}).package_options) || {};
  Object.keys(options).forEach(function (tier) {
    (options[tier] || []).forEach(function (option) {
      var card = document.createElement("article");
      card.textContent = productNamesLine(option);
      view.appendChild(card);
    });
  });
  var briefing = (role || {}).preventative_briefing;
  if (briefing) {
    var note = document.createElement("p");
    note.textContent = typeof briefing === "string" ? briefing : JSON.stringify(briefing);
    view.appendChild(note);
  }
}

function renderGroomer(role) {
  var view = $("package-view");
  var note = document.createElement("p");
  note.textContent = "Observations stay on the request. They are not a diagnosis.";
  view.appendChild(note);
  renderOptions((((role || {}).package_options) && { groomer: role.package_options }) || {});
}

function renderBusiness() {
  var view = $("package-view");
  var note = document.createElement("p");
  note.textContent = "Demo commercial dataset not loaded";
  view.appendChild(note);
}

function renderDeveloper(envelope) {
  var paths = [
    "canonical.scientific_analysis.findings",
    "canonical.scientific_analysis.nutrient_targets",
    "canonical.product_matching.recommendations",
    "canonical.package_optimization.package_options",
    "canonical.scientific_analysis.evidence",
    "canonical.package_optimization.search",
    "canonical.analyze.version",
    "analysis_signature",
  ];
  var view = $("developer-live");
  view.textContent = "Live response\n" + paths.join("\n") + "\n" + JSON.stringify(envelope, null, 2);
  var funnel = document.createElement("pre");
  funnel.className = "wb-funnel";
  var search = (((envelope || {}).canonical || {}).package_optimization || {}).search || {};
  funnel.textContent = [
    "structurally eligible " + (search.structurally_eligible == null ? "" : search.structurally_eligible),
    "minimum failures " + JSON.stringify(search.minimum_failures || []),
    "maximum failures " + JSON.stringify(search.maximum_failures || []),
    "non-dominated " + (search.non_dominated == null ? "" : search.non_dominated),
    "package_options",
    String(search.method || ""),
    "EXHAUSTIVE_ENUMERATION",
    "PACKAGE_OPTIMIZER_V2_1",
    "PRODUCT_MATCH_V2_1",
    "warehouse_version " + ((envelope && envelope.warehouse_version) || ""),
  ].join("\n");
  $("package-view").appendChild(funnel);
}

function renderHealthAnalysis(role) {
  var host = $("health-analysis");
  host.innerHTML = "";
  var analysis = (role && (role.health_analysis || role.preventative_briefing)) || null;
  host.textContent = analysis ? JSON.stringify(analysis) : "";
  host.id = "health-analysis";
}

function renderOptions(grouped) {
  var view = $("package-view");
  Object.keys(grouped || {}).forEach(function (tier) {
    var rows = Array.isArray(grouped[tier]) ? grouped[tier] : [];
    rows.forEach(function (option, index) {
      var key = tier + ":" + index;
      var card = document.createElement("article");
      var names = document.createElement("p");
      names.textContent = productNamesLine(option);
      card.appendChild(names);
      var why = document.createElement("p");
      why.textContent = "Why this bundle";
      card.appendChild(why);
      var nutrition = document.createElement("button");
      nutrition.type = "button";
      nutrition.textContent = "View nutrition";
      nutrition.setAttribute("data-open-nutrition", key);
      nutrition.addEventListener("click", function () {
        openNutritionModal({ opt: option }, key);
      });
      card.appendChild(nutrition);
      view.appendChild(card);
    });
  });
}

function renderCompare() {
  return null;
}

function renderRole(role, envelope) {
  emptyState();
  var roles = (envelope && envelope.roles) || {};
  if (role === "customer") renderCustomer(roles.customer || {});
  if (role === "groomer") renderGroomer(roles.groomer || {});
  if (role === "business") renderBusiness(roles.business || {});
  if (role === "developer") renderDeveloper(envelope || {});
  renderHealthAnalysis(roles[role] || {});
  if (role === "customer") {
    var wellness = ((roles.customer || {}).wellness || {}).package_options || {};
    renderOptions(wellness);
  }
}


function evidenceReportHref(dogId) {
  var params = new URLSearchParams();
  params.set("dog_id", dogId);
  return "/evidence-report?" + params.toString();
}

function renderCareHistory(dogId, events) {
  var panel = $("care-history-panel");
  panel.setAttribute("data-dog-id", dogId || "");
  var list = $("care-history-list");
  list.innerHTML = "";
  var previous = $("care-history-evidence-link");
  if (previous) previous.remove();
  if (dogId) {
    var link = document.createElement("a");
    link.id = "care-history-evidence-link";
    link.textContent = "Evidence report";
    link.href = evidenceReportHref(dogId);
    panel.insertBefore(link, list);
  }
  (events || []).forEach(function (event) {
    var item = document.createElement("li");
    item.textContent = [
      event.event_id,
      event.event_type,
      event.kind,
      event.value,
      event.source,
      event.observed_at,
      event.recorded_at,
      event.timestamp,
    ].map(function (part) { return part == null ? "" : String(part); }).filter(Boolean).join(" · ");
    list.appendChild(item);
  });
}

async function loadPersistedDog(dogId) {
  var dog = await getDog(dogId);
  if (!dog.ok) {
    showError(formatApiError(dog.status, dog.bodyText));
    return;
  }
  fillForm(dog.payload || {});
  if (dog.payload && dog.payload.weight_kg != null && !dog.payload.weight) {
    var weight = document.querySelector('#dog-profile-fields [name="weight"]');
    if (weight) weight.value = String(dog.payload.weight_kg);
  }
  setDogId(dog.payload.dog_id || dogId);
  var history = await listDogEvents(dog.payload.dog_id || dogId);
  if (!history.ok) {
    showError(formatApiError(history.status, history.bodyText));
    return;
  }
  renderCareHistory(dog.payload.dog_id || dogId, (history.payload && history.payload.events) || []);
}

function dogWriteBody(includeIdentity) {
  var body = readForm();
  delete body.as_of_date;
  if (!includeIdentity) return body;
  return body;
}

async function saveDog() {
  var id = dogIdFromForm();
  var body = dogWriteBody(false);
  var result = id ? await patchDog(id, body) : await createDog(body);
  if (!result.ok) {
    showError(formatApiError(result.status, result.bodyText));
    return;
  }
  setDogId(result.payload.dog_id || id);
  await loadPersistedDog(dogIdFromForm());
}

function loadDemo() {
  fillForm(DEMO_DOG);
  setDogId("");
  renderCareHistory("", []);
  showError("");
}

async function runAnalysis() {
  var WORKBENCH_PATH = "/api/v1/presentation/workbench";
  showError("");
  var body = readForm();
  var id = dogIdFromForm();
  if (id) body.dog_id = id;
  body.role_context = roleContext();
  body.correlation_id = "workbench-ui";
  try {
    var response = await runWorkbenchAnalysis(body);
    if (!response.ok) {
      showError(formatApiError(response.status, response.bodyText) + " " + WORKBENCH_PATH);
      return;
    }
    currentAnalysis = response.payload;
    renderRole(currentRole, currentAnalysis);
  } catch (err) {
    showError("Network failure. Retry the analysis when the service is available.");
  }
}

$("module-load-demo");

function documentedEndpoints() {
  return [
    "/api/v1/dogs",
    "/api/v1/dogs/",
    "/recompute",
    "/api/v1/presentation/workbench",
    "/api/v1/ai/explain",
  ];
}

async function askWaggy() {
  if (!currentAnalysis) {
    showError("Run analysis before Ask Waggy why.");
    return;
  }
  var message = ($("ai-explain-input") && $("ai-explain-input").value) || "Why this result?";
  var response = await explainAnalysis({
    analysis_signature: currentAnalysis.analysis_signature,
    canonical: currentAnalysis.canonical,
    user_message: message,
    role: currentRole,
    dog_id: dogIdFromForm() || null,
    recalculation: lastRecalculation,
  });
  if (!response.ok) {
    showError(formatApiError(response.status, response.bodyText));
    return;
  }
  $("ai-explain-log").textContent = JSON.stringify(response.payload);
  $("ai-explain-panel").hidden = false;
}

function bindToggles() {
  document.querySelectorAll("#role-selector [data-role]").forEach(function (button) {
    button.addEventListener("click", function () {
      switchRole(button.getAttribute("data-role"));
    });
  });
  $("module-analyze").addEventListener("click", function () { runAnalysis(); });
  $("module-load-demo").addEventListener("click", loadDemo);
  $("save-dog").addEventListener("click", function () { saveDog(); });
  $("load-dog").addEventListener("click", function () {
    var id = dogIdFromForm();
    if (id) loadPersistedDog(id);
  });
  $("recompute-preferences").addEventListener("click", function () { recomputeWithPreferences(); });
  $("ai-explain-send").addEventListener("click", function () { askWaggy(); });
  $("copy-workbench-example").addEventListener("click", function () {
    var text = $("workbench-example-json").textContent;
    if (navigator.clipboard) navigator.clipboard.writeText(text);
  });
  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && selectedBundleForNutrition) closeNutritionModal();
  });
  document.addEventListener("click", function (event) {
    if (event.target.closest("[data-close-nutrition]")) closeNutritionModal();
  });
}

async function recomputeWithPreferences() {
  var id = dogIdFromForm();
  if (!id) {
    showError("Save a dog before recomputing preferences.");
    return;
  }
  var body = readForm();
  var response = await recomputeDog(id, {
    preference_change: { monthly_budget: body.monthly_budget },
    expected_analysis_signature: currentAnalysis && currentAnalysis.analysis_signature,
    provenance: "USER",
  });
  if (!response.ok) {
    showError(formatApiError(response.status, response.bodyText));
    return;
  }
  lastRecalculation = response.payload;
  var explanation = response.payload.explanation;
  getRecalculationExplanation(response.payload);
  $("recalculation-facts").textContent = JSON.stringify({
    payload: { explanation: explanation },
    summary_facts: (explanation && explanation.summary_facts) || [],
  });
  if (response.payload && response.payload.presentation) {
    currentAnalysis = response.payload.presentation;
    renderRole(currentRole, currentAnalysis);
  }
}

function boot() {
  $("workbench-example-json").textContent = JSON.stringify(WORKBENCH_EXAMPLE_REQUEST, null, 2);
  bindToggles();
  switchRole(roleFromLocation());
  documentedEndpoints();
  getApiBaseUrl();
}

boot();

function renderNutritionFacts(opt, key, nameOpts) {
  var body = $("nutrition-modal-body");
  if (currentRole === "developer") {
    body.textContent = JSON.stringify(opt || {});
  } else {
    body.textContent = productNamesLine(opt, nameOpts);
  }
  return key;
}

function closeNutritionModal() {
  var body = $("nutrition-modal-body");
  var modal = $("nutrition-modal");
  body.innerHTML = "";
  selectedBundleForNutrition = null;
  modal.hidden = true;
  modal.classList.remove("is-open");
  document.body.classList.remove("wb-modal-open");
}

function openNutritionModal(stored, key) {
  selectedBundleForNutrition = key;
  renderNutritionFacts(stored.opt, key, { names: true });
  var modal = $("nutrition-modal");
  modal.hidden = false;
  modal.classList.add("is-open");
  document.body.classList.add("wb-modal-open");
  var closer = modal.querySelector(".wb-modal-close");
  if (closer) closer.addEventListener("click", closeNutritionModal);
}

function renderBundleReasoning(opt) {
  return (opt && opt.bundle_reasoning) || null;
}

var nutritionPanel = document.querySelector(".wb-modal-panel");
if (nutritionPanel) {
  nutritionPanel.addEventListener("click", function (event) {
    event.stopPropagation();
    if (event.target.closest("[data-close-nutrition]")) closeNutritionModal();
  });
}

var WagtopiaWorkbench = {
  currentAnalysis: function () { return currentAnalysis; },
  roleFromLocation: roleFromLocation,
  dogIdFromForm: dogIdFromForm,
};
window.WagtopiaWorkbench = WagtopiaWorkbench;
