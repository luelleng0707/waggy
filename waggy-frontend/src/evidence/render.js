/**
 * Formats a Phase N evidence-report JSON body for display.
 * Values, deltas, canonical rows, and as-of membership come from that body.
 */

const PROVENANCE_FIELDS = [
  ["observation_id", "observation_id"],
  ["dog_id", "dog_id"],
  ["observation_type", "observation_type"],
  ["value", "value"],
  ["unit", "unit"],
  ["observer_role", "observer_role"],
  ["source", "source"],
  ["observed_at", "Observation time (observed_at)"],
  ["recorded_at", "Recording time (recorded_at)"],
  ["source_session_id", "source_session_id"],
  ["event_id", "event_id"],
];

const DELTA_FIELDS = [
  ["previous_observation_id", "previous_observation_id"],
  ["current_observation_id", "current_observation_id"],
  ["previous_value", "previous_value"],
  ["current_value", "current_value"],
  ["delta", "delta"],
  ["unit", "unit"],
  ["observed_at_previous", "observed_at_previous"],
  ["observed_at_current", "observed_at_current"],
];

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function literal(value) {
  if (value === null || value === undefined) {
    return "null";
  }
  return escapeHtml(value);
}

function provenanceList(record) {
  const row = record && typeof record === "object" ? record : {};
  const items = PROVENANCE_FIELDS.map(([key, label]) => {
    const timeClass =
      key === "observed_at" ? " time-observed" : key === "recorded_at" ? " time-recorded" : "";
    return `<div class="prov-field${timeClass}" data-field="${key}"><dt>${escapeHtml(label)}</dt><dd>${literal(row[key])}</dd></div>`;
  });
  return `<dl class="provenance">${items.join("")}</dl>`;
}

function renderDelta(delta) {
  if (delta == null || delta.delta == null) {
    const fields =
      delta == null
        ? ""
        : `<dl class="delta-fields">${DELTA_FIELDS.map(([key]) => {
            const shown = key === "delta" ? "null" : literal(delta[key]);
            return `<div data-delta-field="${key}"><dt>${escapeHtml(key)}</dt><dd>${shown}</dd></div>`;
          }).join("")}</dl>`;
    return `<div class="delta" data-delta="absent"><p class="delta-absent">No numeric delta is available.</p>${fields}</div>`;
  }
  const items = DELTA_FIELDS.map(([key]) => {
    const shown = key === "delta" ? escapeHtml(JSON.stringify(delta.delta)) : literal(delta[key]);
    return `<div data-delta-field="${key}"><dt>${escapeHtml(key)}</dt><dd>${shown}</dd></div>`;
  });
  return `<div class="delta" data-delta="present" data-delta-value="${escapeHtml(JSON.stringify(delta.delta))}"><dl class="delta-fields">${items.join("")}</dl></div>`;
}

function renderSeries(series) {
  const observationType = literal(series.observation_type);
  const history = Array.isArray(series.history) ? series.history : [];
  const timeline = Array.isArray(series.timeline) ? series.timeline : [];
  const historyHtml = history.length
    ? history
        .map(
          (row, index) =>
            `<li class="history-row" data-history-index="${index}">${provenanceList(row)}</li>`,
        )
        .join("")
    : `<li class="history-empty">No history rows were returned for this series.</li>`;
  const canonical = series.canonical_observation;
  const canonicalHtml =
    canonical == null
      ? `<p class="canonical-empty">No canonical observation was returned.</p>`
      : `<div class="canonical" data-canonical="present">${provenanceList(canonical)}</div>`;
  const timelineHtml = timeline.length
    ? timeline
        .map((point, index) => {
          const observation = point && point.observation ? point.observation : {};
          return `<li class="timeline-point" data-timeline-index="${index}">${provenanceList(observation)}<h4>Consecutive delta</h4>${renderDelta(point ? point.delta_from_previous : null)}</li>`;
        })
        .join("")
    : `<li class="timeline-empty">No timeline points were returned for this series.</li>`;
  return `<article class="series" data-observation-type="${escapeHtml(series.observation_type ?? "")}">
    <h2>Observation type</h2>
    <p class="observation-type">${observationType}</p>
    <h3>History</h3>
    <ol class="history">${historyHtml}</ol>
    <h3>Canonical observation</h3>
    <p class="canonical-policy">Canonical observation selected by the evidence policy. This selection is not a medical diagnosis and is not clinical validation.</p>
    ${canonicalHtml}
    <h3>Timeline</h3>
    <ol class="timeline">${timelineHtml}</ol>
  </article>`;
}

export function renderEvidenceReport(report) {
  const body = report && typeof report === "object" ? report : {};
  if (!Array.isArray(body.series)) {
    return `<section class="evidence-report" data-report="malformed"><p class="report-malformed">The evidence report response did not include a series array.</p></section>`;
  }
  const stamps = `<dl class="report-stamps">
    <div class="time-generated"><dt>Report generation time (generated_at)</dt><dd data-generated-at>${literal(body.generated_at)}</dd></div>
    <div class="time-cutoff"><dt>Replay cutoff (as_of)</dt><dd data-as-of>${body.as_of == null ? "No replay cutoff was supplied." : literal(body.as_of)}</dd></div>
  </dl>`;
  if (body.series.length === 0) {
    return `<section class="evidence-report" data-empty="true">
      <h1>Evidence report</h1>
      <p data-dog-id>${literal(body.dog_id)}</p>
      ${stamps}
      <p class="empty-series">No evidence series were returned.</p>
    </section>`;
  }
  return `<section class="evidence-report" data-empty="false">
    <h1>Evidence report</h1>
    <p data-dog-id>${literal(body.dog_id)}</p>
    ${stamps}
    ${body.series.map((series) => renderSeries(series)).join("")}
  </section>`;
}

export function renderEvidenceError(error) {
  const body = error && typeof error === "object" ? error : {};
  const code = typeof body.code === "string" ? body.code : "";
  const message = typeof body.message === "string" ? body.message : "";
  return `<section class="evidence-error" data-error-code="${escapeHtml(code)}">
    <h1>Evidence report unavailable</h1>
    <p>Error code <span data-error-code-text>${literal(code)}</span></p>
    <p data-error-message>${literal(message)}</p>
  </section>`;
}
