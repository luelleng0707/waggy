/**
 * Loads GET /api/v1/dogs/{dog_id}/evidence-report.
 * Query keys are the Phase N parameters only.
 */

const QUERY_KEYS = ["observation_type", "as_of", "generated_at"];

export function evidenceReportPath(dogId, params) {
  const search = new URLSearchParams();
  const source = params && typeof params === "object" ? params : {};
  for (const key of QUERY_KEYS) {
    const value = source[key];
    if (value != null && String(value).trim() !== "") {
      search.set(key, String(value));
    }
  }
  const path = `/api/v1/dogs/${encodeURIComponent(dogId)}/evidence-report`;
  const query = search.toString();
  return query ? `${path}?${query}` : path;
}

export function evidenceErrorView(status, body) {
  const error = body && body.error && typeof body.error === "object" ? body.error : {};
  return {
    status,
    code: typeof error.code === "string" ? error.code : "",
    message: typeof error.message === "string" ? error.message : "",
    field: Object.prototype.hasOwnProperty.call(error, "field") ? error.field : null,
  };
}

export async function fetchEvidenceReport(fetchImpl, dogId, params) {
  const response = await fetchImpl(evidenceReportPath(dogId, params), {
    method: "GET",
    headers: { Accept: "application/json" },
  });
  const body = await response.json();
  if (!response.ok) {
    return { ok: false, error: evidenceErrorView(response.status, body) };
  }
  return { ok: true, report: body };
}
