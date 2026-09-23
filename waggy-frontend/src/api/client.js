import { apiUrl } from "./config.js";

async function request(path, options) {
  var json = options && options.json;
  var response = await fetch(apiUrl(path), {
    method: (options && options.method) || "GET",
    headers: { Accept: "application/json", "Content-Type": "application/json" },
    body: json === undefined ? undefined : JSON.stringify(json),
  });
  var bodyText = await response.text();
  var payload = null;
  try {
    payload = bodyText ? JSON.parse(bodyText) : null;
  } catch (err) {
    payload = null;
  }
  return { ok: response.ok, status: response.status, payload: payload, bodyText: bodyText };
}

export function runWorkbenchAnalysis(body) {
  return request("/api/v1/presentation/workbench", { method: "POST", json: body });
}

export function createDog(body) {
  return request("/api/v1/dogs", { method: "POST", json: body });
}

export function getDog(dogId) {
  return request("/api/v1/dogs/" + encodeURIComponent(dogId), { method: "GET" });
}

export function patchDog(dogId, body) {
  return request("/api/v1/dogs/" + encodeURIComponent(dogId), { method: "PATCH", json: body });
}

export function listDogEvents(dogId) {
  return request("/api/v1/dogs/" + encodeURIComponent(dogId) + "/events", { method: "GET" });
}

export function recomputeDog(dogId, body) {
  return request("/api/v1/dogs/" + encodeURIComponent(dogId) + "/recompute", { method: "POST", json: body });
}

export function explainAnalysis(body) {
  return request("/api/v1/ai/explain", { method: "POST", json: body });
}

export function getRecalculationExplanation(payload) {
  return payload && payload.explanation;
}
