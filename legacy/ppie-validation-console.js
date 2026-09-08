/**
 * Clinical Execution Explorer — scientific assessment audit UI.
 * Consumes POST /api/v1/ppie/validation-console (engine-emitted ledgers only).
 */
(function () {
  'use strict';

  const API_KEY = (window.WagtopiaAPI && window.WagtopiaAPI.API_KEY) || '';
  const NT = 'NOT CURRENTLY TRACEABLE';

  const PRESET_BODIES = {
    golden_retriever: {
      name: 'Sunny', pet_name: 'Sunny', breeds: ['Golden Retriever'], birthday: '2020-06-01',
      weight: 28, sex: 'Female', activity_level: 'Moderate', current_environment: 'Temperate Suburban', observed_conditions: []
    },
    german_shepherd: {
      name: 'Rex', pet_name: 'Rex', breeds: ['German Shepherd Dog'], birthday: '2019-04-12',
      weight: 34, sex: 'Male', activity_level: 'High', current_environment: 'Temperate Suburban', observed_conditions: []
    },
    border_collie: {
      name: 'Pip', pet_name: 'Pip', breeds: ['Border Collie'], birthday: '2021-01-20',
      weight: 18, sex: 'Female', activity_level: 'High', current_environment: 'Rural Cool', observed_conditions: []
    },
    french_bulldog: {
      name: 'Biscuit', pet_name: 'Biscuit', breeds: ['French Bulldog'], birthday: '2022-08-08',
      weight: 12, sex: 'Male', activity_level: 'Low', current_environment: 'Urban Indoor', observed_conditions: []
    },
    mixed_breed: {
      name: 'Dolly', pet_name: 'Dolly', breeds: ['Golden Retriever', 'Labrador Retriever'], birthday: '2021-03-15',
      weight: 30, sex: 'Female', activity_level: 'High', current_environment: 'Shanghai Summer', observed_conditions: []
    },
    senior_labrador: {
      name: 'Maple', pet_name: 'Maple', breeds: ['Labrador Retriever'], birthday: '2013-05-01',
      weight: 32, sex: 'Female', activity_level: 'Low', current_environment: 'Temperate Suburban', observed_conditions: []
    },
    large_breed_puppy: {
      name: 'Scout', pet_name: 'Scout', breeds: ['Golden Retriever'], birthday: '2025-09-01',
      weight: 14, sex: 'Male', activity_level: 'Moderate', current_environment: 'Temperate Suburban', observed_conditions: []
    },
    golden_20kg: {
      name: 'CompareA', pet_name: 'CompareA', breeds: ['Golden Retriever'], birthday: '2020-06-01',
      weight: 20, sex: 'Female', activity_level: 'Moderate', current_environment: 'Temperate Suburban', observed_conditions: []
    },
    golden_25kg: {
      name: 'CompareB', pet_name: 'CompareB', breeds: ['Golden Retriever'], birthday: '2020-06-01',
      weight: 25, sex: 'Female', activity_level: 'Moderate', current_environment: 'Temperate Suburban', observed_conditions: []
    }
  };

  const GRAPH_NODES = [
    { id: 'profile', label: 'ProfileNode', stage: 'payload' },
    { id: 'breed', label: 'BreedNode', stage: 'biology' },
    { id: 'biology', label: 'BiologyNode', stage: 'biology' },
    { id: 'risk', label: 'RiskNode', stage: 'health_risk' },
    { id: 'nutrition', label: 'NutritionNode', stage: 'nutrition' },
    { id: 'ingredient', label: 'IngredientNode', stage: 'nutrition' },
    { id: 'product', label: 'ProductNode', stage: 'optimization' },
    { id: 'package', label: 'PackageNode', stage: 'optimization' },
    { id: 'assessment', label: 'AssessmentNode', stage: 'assembly' },
    { id: 'export', label: 'ExportNode', stage: 'assembly' }
  ];

  const esc = (s) =>
    String(s ?? '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');

  let consoleDoc = null;
  let presets = [];
  let activePreset = 'mixed_breed';
  let lastBootId = null;
  let loading = false;
  let openTermKey = null;

  function debugEnabled() {
    return (
      /(?:\?|&)(?:debug|dev)=(?:1|true)\b/i.test(location.search) ||
      location.pathname === '/developer'
    );
  }

  function currentBody() {
    return JSON.parse(JSON.stringify(PRESET_BODIES[activePreset] || PRESET_BODIES.mixed_breed));
  }

  function pre(obj) {
    try {
      return `<pre class="vc-pre">${esc(JSON.stringify(obj, null, 2))}</pre>`;
    } catch (_) {
      return `<pre class="vc-pre">${esc(String(obj))}</pre>`;
    }
  }

  function pill(t, cls) {
    return `<span class="vc-pill${cls ? ' ' + cls : ''}">${esc(t)}</span>`;
  }

  function fmtMs(v) {
    if (v == null || v === NT || v === '') return NT;
    const n = Number(v);
    if (Number.isFinite(n)) return `${n.toFixed(n >= 100 ? 0 : 1)} ms`;
    return String(v);
  }

  function fmtNum(v, digits) {
    if (v == null || v === '') return '—';
    const n = Number(v);
    if (!Number.isFinite(n)) return String(v);
    return n.toFixed(digits != null ? digits : (Math.abs(n) >= 10 ? 1 : 3));
  }

  async function api(path, opts) {
    return fetch(path, {
      ...opts,
      headers: {
        Accept: 'application/json',
        ...(API_KEY ? { 'x-api-key': API_KEY } : {}),
        ...(opts && opts.body ? { 'Content-Type': 'application/json' } : {}),
        ...(opts && opts.headers)
      }
    });
  }

  function section(id, title, body, aside) {
    return `<section class="vc-section" id="${esc(id)}">
      <div class="vc-section-head">
        <h2>${esc(title)}</h2>
        ${aside ? `<span class="vc-muted">${aside}</span>` : ''}
      </div>
      <div class="vc-section-body">${body}</div>
    </section>`;
  }

  function kv(items) {
    return `<div class="vc-kv">${items
      .map(
        ([k, v]) => `<div class="vc-kv-item"><span>${esc(k)}</span><strong>${v}</strong></div>`
      )
      .join('')}</div>`;
  }

  function profileFields(profile, raw) {
    const p = profile || {};
    const r = raw || {};
    const breeds = p.breeds || r.breeds || (p.primary_breed ? [p.primary_breed] : []);
    const breedLabel = Array.isArray(breeds) ? breeds.join(' × ') : String(breeds || '—');
    return [
      ['Breed', esc(breedLabel || p.breed || '—')],
      ['Age', esc(p.age_years != null ? p.age_years : p.age || '—')],
      ['Weight', esc(p.weight_kg != null ? `${p.weight_kg} kg` : r.weight != null ? `${r.weight} kg` : '—')],
      ['Sex', esc(p.sex || r.sex || '—')],
      ['Neutered', esc(p.neutered != null ? (p.neutered ? 'Yes' : 'No') : r.neutered != null ? r.neutered : '—')],
      ['Activity', esc(p.activity_level || r.activity_level || '—')],
      ['Body condition', esc(p.body_condition || p.bcs || r.body_condition || '—')],
      ['Environment', esc(p.current_environment || r.current_environment || '—')],
      ['Medical history', esc((p.medical_history || r.observed_conditions || []).length ? JSON.stringify(p.medical_history || r.observed_conditions) : 'None')],
      ['Supplements', esc(p.supplements || r.supplements || '—')]
    ];
  }

  function showTrace(title, payload) {
    const app = document.getElementById('vc-app');
    const panel = document.getElementById('vc-prov-panel');
    const body = document.getElementById('vc-prov-body');
    if (!panel || !body) return;
    app && app.classList.add('has-trace');
    panel.hidden = false;
    body.innerHTML = `<div class="vc-h3">${esc(title)}</div>${pre(payload)}`;
  }

  function hideTrace() {
    const app = document.getElementById('vc-app');
    const panel = document.getElementById('vc-prov-panel');
    if (panel) panel.hidden = true;
    app && app.classList.remove('has-trace');
  }

  function allLookups() {
    const out = [];
    for (const fx of consoleDoc.formula_executions || []) {
      for (const lu of fx.lookups || []) {
        out.push({
          ...lu,
          _formula_id: fx.formula_id,
          _subject: fx.condition || fx.subject,
          _repository: inferRepo(lu.table || lu.csv_file)
        });
      }
    }
    return out;
  }

  function inferRepo(table) {
    const t = String(table || '').toLowerCase();
    if (t.includes('breed')) return 'BreedRepository';
    if (t.includes('ingredient') || t.includes('condition_ingredient')) return 'IngredientRepository';
    if (t.includes('product') || t.includes('package') || t.includes('ext_')) return 'ProductRepository';
    if (t.includes('nutrient') || t.includes('food')) return 'NutritionRepository';
    if (t.includes('trait') || t.includes('purpose') || t.includes('benefit')) return 'PhysiologyRepository';
    if (t.includes('mixed')) return 'InteractionRepository';
    if (t.includes('protocol') || t.includes('groom') || t.includes('clinical') || t.includes('activity'))
      return 'PreventionRepository';
    return 'DataRepository';
  }

  function clickVal(label, value, payload) {
    const data = encodeURIComponent(JSON.stringify(payload || {}));
    return `<button type="button" class="vc-click-val" data-trace-title="${esc(label)}" data-trace="${data}">${esc(value)}</button>`;
  }

  function formulaExpression(fx) {
    if (!fx) return '';
    const steps = fx.steps || [];
    const exprs = steps.filter((s) => s.expression).map((s) => s.expression);
    if (exprs.length) return exprs.join('\n');
    if (fx.formula_expression) return String(fx.formula_expression);
    return 'FORMULA DOCUMENTATION MISSING';
  }

  function termButtons(fx) {
    const outs = fx.outputs || {};
    const terms = [];
    const push = (name, val, unit, detail) => {
      if (val == null || val === '') return;
      terms.push({ name, val, unit: unit || '', detail });
    };
    push('base_prevalence', outs.base_risk_percent, '%', { source: 'outputs.base_risk_percent' });
    push('interaction_modifier', outs.interaction_factor, '', { source: 'outputs.interaction_factor' });
    push('benefit_factor', outs.benefit_factor, '', { source: 'outputs.benefit_factor' });
    push('risk_after_interaction', outs.risk_after_interaction_percent, '%', {});
    push('final_trait_risk', outs.final_trait_risk_percent, '%', {});
    push('final_risk', outs.final_risk_percent, '%', { final: true });
    push('confidence', outs.confidence_percent, '%', {});

    for (const m of fx.modifiers || []) {
      push(m.modifier || 'modifier', m.value != null ? m.value : m.after, m.unit || '', {
        modifier: m,
        lookups: (fx.lookups || []).filter(
          (lu) => String(lu.table || '').includes(String(m.source_table || '').replace('.csv', ''))
        )
      });
    }

    if (!terms.length) {
      for (const s of fx.steps || []) {
        const v = s.after != null ? s.after : s.result;
        if (v == null) continue;
        push(s.name, v, s.unit || '', { step: s });
      }
    }

    return terms
      .map((t, i) => {
        const key = `${fx.formula_id}:${fx.condition || fx.subject}:${t.name}:${i}`;
        const open = openTermKey === key;
        return `<div>
          <button type="button" class="vc-term${open ? ' is-open' : ''}" data-term-key="${esc(key)}">
            <span class="name">${esc(t.name)}</span>
            <span class="val">${esc(fmtNum(t.val))}${esc(t.unit)}</span>
          </button>
          ${
            open
              ? `<div class="vc-term-expand">${pre({
                  term: t.name,
                  value: t.val,
                  unit: t.unit,
                  detail: t.detail,
                  formula_id: fx.formula_id,
                  subject: fx.condition || fx.subject,
                  code: fx.code
                })}</div>`
              : ''
          }
        </div>`;
      })
      .join('');
  }

  function renderFxCard(fx, open) {
    if (!fx) return '';
    const subject = fx.condition || fx.subject || fx.formula_name || fx.formula_id;
    const outs = fx.outputs || {};
    const final =
      outs.final_risk_percent != null
        ? `${fmtNum(outs.final_risk_percent, 1)}%`
        : outs.final_value != null
          ? String(outs.final_value)
          : outs.target != null
            ? String(outs.target)
            : '—';
    const conf =
      outs.confidence_percent != null
        ? `${fmtNum(outs.confidence_percent, 1)}%`
        : (fx.confidence && fx.confidence[0] && fx.confidence[0].value) || '—';
    const timing = fx.timing || {};
    const code = fx.code || {};
    const sourceLoc = fx.source_location || {};
    const execStatus = fx.execution_status || {};
    const expr = formulaExpression(fx);
    const steps = (fx.steps || [])
      .map((s) => {
        const before = s.before != null ? `${esc(s.before)} → ` : '';
        const after = s.after != null || s.result != null ? esc(s.after != null ? s.after : s.result) : '';
        return `<li>
          <strong>${esc(s.name)}</strong>
          ${s.expression ? `<div class="vc-muted"><code>${esc(s.expression)}</code></div>` : ''}
          <div>${before}<span class="vc-click-val" data-trace-title="${esc(s.name)}" data-trace="${esc(
            encodeURIComponent(JSON.stringify(s))
          )}">${after}${esc(s.unit || '')}</span></div>
        </li>`;
      })
      .join('');
    const lookups = (fx.lookups || [])
      .slice(0, 24)
      .map(
        (lu) => `<tr>
          <td>${esc(inferRepo(lu.table))}</td>
          <td>${esc(lu.table || lu.csv_file || '—')}</td>
          <td>${esc(lu.row_id || (lu.csv_row != null ? 'row ' + lu.csv_row : '—'))}</td>
          <td>${esc(lu.decision || (lu.matched ? 'matched' : '—'))}</td>
          <td>${esc(lu.evidence_id || '—')}</td>
        </tr>`
      )
      .join('');

    return `<details class="vc-fx"${open ? ' open' : ''}>
      <summary>
        <div>
          <div class="vc-fx-title">${esc(subject)}</div>
          <div class="vc-fx-sub">${esc(fx.formula_id)} · ${esc(fx.stage || '')} · ${pill(final)} confidence ${esc(conf)}</div>
        </div>
        <div class="vc-muted">${esc(fmtMs(timing.elapsed_ms || timing.ms))}</div>
      </summary>
      <div class="vc-fx-body">
        <div>
          <div class="vc-h3">Purpose</div>
          <p>${esc(fx.purpose || fx.formula_name || 'Formula execution emitted by engine')}</p>
        </div>
        <div>
          <div class="vc-h3">Execution Status</div>
          ${pre(execStatus)}
        </div>
        <div>
          <div class="vc-h3">Inputs</div>
          ${pre(fx.inputs || {})}
        </div>
        <div>
          <div class="vc-h3">Parameters</div>
          ${pre(fx.parameters || [])}
        </div>
        <div>
          <div class="vc-h3">Formula</div>
          <div class="vc-formula-box">${esc(expr)}</div>
        </div>
        <div>
          <div class="vc-h3">Intermediate values · click a term</div>
          <div class="vc-term-grid">${termButtons(fx)}</div>
        </div>
        <div>
          <div class="vc-h3">Step ledger</div>
          <ol>${steps || '<li class="vc-muted">No steps emitted</li>'}</ol>
        </div>
        <div>
          <div class="vc-h3">Repository lookups</div>
          <table class="vc-lookup-table">
            <thead><tr><th>Repository</th><th>Table</th><th>Row</th><th>Decision</th><th>Evidence</th></tr></thead>
            <tbody>${lookups || '<tr><td colspan="5">None</td></tr>'}</tbody>
          </table>
        </div>
        <div>
          <div class="vc-h3">Outputs</div>
          ${pre(outs)}
        </div>
        <div>
          <div class="vc-h3">Warehouse</div>
          ${pre({
            status: fx.warehouse_status || 'WAREHOUSE_NOT_AVAILABLE',
            references: fx.lookups || [],
            note:
              fx.warehouse_status === 'WAREHOUSE_ROW_TRACED'
                ? null
                : 'WAREHOUSE ROW: NOT AVAILABLE'
          })}
        </div>
        <div>
          <div class="vc-h3">Scientific Evidence</div>
          ${pre({
            status: fx.evidence_status || 'EVIDENCE_NOT_AVAILABLE',
            references: fx.evidence_references || [],
            note:
              fx.evidence_status === 'EVIDENCE_TRACED'
                ? null
                : 'EVIDENCE: NOT AVAILABLE FOR THIS EXECUTION'
          })}
        </div>
        <div>
          <div class="vc-h3">Dependencies</div>
          ${pre(fx.dependencies || [])}
        </div>
        <div>
          <div class="vc-h3">Replay</div>
          ${pre(fx.replay || { status: 'NOT_AVAILABLE', detail: 'REPLAY: NOT AVAILABLE' })}
        </div>
        <div>
          <div class="vc-h3">Sensitivity</div>
          ${pre(fx.sensitivity || { status: 'NOT_AVAILABLE', rows: [] })}
        </div>
        <div>
          <div class="vc-h3">Publication risk classification</div>
          ${pre(fx.publication_risk || [{ classification: 'Unknown', reason: 'No mapped rows' }])}
        </div>
        <div>
          <div class="vc-h3">Formula source</div>
          <div class="vc-code-ref">${esc(sourceLoc.file || code.file || 'SOURCE: NOT_AVAILABLE')} · ${esc(
      sourceLoc.function || code.function || '—'
    )}${
      sourceLoc.line_start
        ? ' · lines ' + esc(String(sourceLoc.line_start)) + '–' + esc(String(sourceLoc.line_end || sourceLoc.line_start))
        : ''
    }</div>
          ${sourceLoc.excerpt && sourceLoc.excerpt.length ? pre(sourceLoc.excerpt) : '<p class="vc-muted">SOURCE: NOT_AVAILABLE</p>'}
        </div>
      </div>
    </details>`;
  }

  function riskWaterfall(fx, ledger) {
    const outs = (fx && fx.outputs) || {};
    const chain = (ledger && (ledger.expanded_chain || ledger.steps)) || [];
    const rows = [];
    if (outs.base_risk_percent != null) rows.push({ label: 'Breed / trait base', value: Number(outs.base_risk_percent) });
    if (outs.risk_after_interaction_percent != null)
      rows.push({ label: 'After interaction', value: Number(outs.risk_after_interaction_percent) });
    if (outs.final_trait_risk_percent != null)
      rows.push({ label: 'After benefits', value: Number(outs.final_trait_risk_percent) });
    if (outs.final_risk_percent != null) rows.push({ label: 'Final risk', value: Number(outs.final_risk_percent) });
    if (!rows.length && chain.length) {
      for (const s of chain) {
        if (s.value == null || !s.traceable) continue;
        rows.push({ label: s.label || s.name, value: Number(s.value) });
      }
    }
    if (!rows.length) return `<p class="vc-muted">No waterfall values emitted.</p>`;
    const max = Math.max(...rows.map((r) => Math.abs(r.value) || 0), 1);
    return `<div class="vc-waterfall">${rows
      .map((r, i) => {
        const prev = i ? rows[i - 1].value : r.value;
        const delta = i ? r.value - prev : r.value;
        const w = Math.min(100, (Math.abs(r.value) / max) * 100);
        return `<div class="vc-wf-row">
          <div>${esc(r.label)}</div>
          <div class="vc-wf-bar"><div class="vc-wf-fill" style="width:${w}%"></div></div>
          <div class="vc-wf-delta">${esc(fmtNum(r.value, 1))}%${
            i ? ` (${delta >= 0 ? '+' : ''}${esc(fmtNum(delta, 1))})` : ''
          }</div>
        </div>`;
      })
      .join('')}</div>`;
  }

  function renderExplorer() {
    const main = document.getElementById('vc-main');
    if (!main || !consoleDoc) return;

    const profile = (consoleDoc.profile_inspector && consoleDoc.profile_inspector.normalized) || {};
    const rawReq = (consoleDoc.profile_inspector && consoleDoc.profile_inspector.raw_request) || currentBody();
    const checklist = consoleDoc.validation_checklist || [];
    const lookups = allLookups();
    const timeline = consoleDoc.pipeline_timeline || [];
    const riskFx = (consoleDoc.formula_executions || []).filter((fx) => fx.formula_id === 'RISK_V2_1');
    const nutFx = (consoleDoc.formula_executions || []).filter((fx) =>
      String(fx.formula_id || '').includes('NUTRIENT')
    );
    const allFx = consoleDoc.formula_executions || [];
    const evidence = consoleDoc.evidence || consoleDoc.evidence_objects || [];
    const nutrition = consoleDoc.nutrition || [];
    const ingredients = consoleDoc.ingredients || [];
    const products = consoleDoc.products || {};
    const packages = consoleDoc.packages || consoleDoc.package_optimizer || {};
    const perf = consoleDoc.performance || {};
    const timings = perf.stage_timings_ms || consoleDoc.overview?.stage_timings_ms || {};
    const ledgers = consoleDoc.risk_ledgers || [];
    const finalObjs = consoleDoc.raw_production_objects || {};
    const petName = profile.name || profile.pet_name || rawReq.name || activePreset;
    const runtimeFlow = consoleDoc.runtime_stage_flow || [];
    const replayRows = consoleDoc.replay || [];
    const sensitivityRows = consoleDoc.sensitivity || [];
    const pubRisk = consoleDoc.publication_risk || [];
    const numericalProv = consoleDoc.numerical_provenance || [];
    const statusSummary = consoleDoc.execution_status_summary || {};
    const riskCount = (consoleDoc.risk_ledgers || []).length || (consoleDoc.explain_why || []).length || 0;
    const citationCount = (consoleDoc.evidence || []).filter((e) => e && (e.url || e.source_url)).length;
    const replayAvailable = replayRows.filter((r) => r && r.status !== 'NOT_AVAILABLE').length;
    const replayCoverage = allFx.length ? `${fmtNum((replayAvailable / allFx.length) * 100, 1)}%` : '0%';

    const timelineById = {};
    for (const t of timeline) timelineById[t.id] = t;

    const PIPELINE_STAGES = [
      'INPUT',
      'PROFILE_NORMALIZE_V2_1',
      'BREED_RESOLVE_V2_1',
      'TRAIT_BLEND_V2_1',
      'RISK_V2_1',
      'NUTRIENT_TARGET_V2_1',
      'ACTIVITY_V2_1',
      'PRODUCT_MATCH_V2_1',
      'PACKAGE_OPTIMIZER_V2_1',
      'EVIDENCE_RANK_V2_1',
      'VALIDATION_V2_1',
      'OUTPUT'
    ];
    const catalogSource = (consoleDoc.overview && consoleDoc.overview.catalog_source) || 'warehouse';
    const demoCatalog = Boolean(consoleDoc.overview && consoleDoc.overview.demo_catalog);
    const selectedProducts = products.selected || (products.outputs && products.outputs.selected) || [];
    const pipelineHtml = section(
      'pipeline',
      'Runtime pipeline',
      `<p class="vc-muted">${esc(demoCatalog ? 'DEMO CATALOG · demonstration data, not scientific evidence' : 'Warehouse catalog input')}</p>
       <ol class="vc-pipeline">${PIPELINE_STAGES.map((s) => `<li>${esc(s)}</li>`).join('')}</ol>
       ${kv([
         ['Catalog source', esc(catalogSource)],
         ['Product match selected', esc(String(selectedProducts.length))],
         ['Package tiers', esc(String((packages.tiers || []).length))]
       ])}`
    );

    const inputHtml = section(
      'input',
      'Input',
      `${kv(profileFields(profile, rawReq))}
       <details class="vc-collapse" style="margin-top:14px"><summary>Raw request JSON</summary>${pre(rawReq)}</details>`,
      esc(petName)
    );

    const checks = Array.isArray(checklist)
      ? checklist
          .map((c) => {
            const ok = typeof c === 'object' ? c.ok !== false && c.pass !== false && c.status !== 'fail' : !!c;
            const label =
              typeof c === 'object' ? c.label || c.check || c.name || c.message || JSON.stringify(c) : String(c);
            return `<li><span class="${ok ? 'vc-check-ok' : 'vc-check-fail'}">${ok ? '✓' : '✗'}</span><div>${esc(
              label
            )}</div></li>`;
          })
          .join('')
      : '';
    const missing = (consoleDoc.profile_inspector && consoleDoc.profile_inspector.missing_values) || [];
    const validationHtml = section(
      'validation',
      'Validation',
      `<ul class="vc-check-list">${
        checks ||
        `<li><span class="vc-check-ok">✓</span><div>Profile accepted by engine</div></li>
         <li><span class="vc-check-ok">✓</span><div>Breed resolved</div></li>
         <li><span class="vc-check-ok">✓</span><div>Activity / environment normalized</div></li>`
      }</ul>
       <div class="vc-h3" style="margin-top:16px">Normalized profile</div>
       ${pre(profile)}
       ${missing.length ? `<div class="vc-h3">Missing values</div>${pre(missing)}` : ''}`
    );

    const clinicalOutputHtml = section(
      'clinical_output',
      'Clinical Output',
      (ledgers.length
        ? `<table class="vc-lookup-table">
            <thead><tr><th>Condition</th><th>Observed</th><th>Estimated</th><th>Priority</th></tr></thead>
            <tbody>${ledgers
              .map((row) => {
                const observed =
                  row.observed_breed_prevalence_percent != null
                    ? `${fmtNum(row.observed_breed_prevalence_percent, 1)}%`
                    : 'EVIDENCE INCOMPLETE';
                const estimated =
                  row.final_probability_pct != null ? `${fmtNum(row.final_probability_pct, 1)}%` : '—';
                const priority = row.priority_score != null ? fmtNum(row.priority_score, 2) : '—';
                return `<tr><td>${esc(row.condition || '—')}</td><td>${esc(observed)}</td><td>${esc(
                  estimated
                )}</td><td>${esc(priority)}</td></tr>`;
              })
              .join('')}</tbody>
          </table>`
        : '<p class="vc-muted">No clinical condition rows emitted.</p>')
    );

    const runtimeFlowHtml = section(
      'runtime_flow',
      'Data Flow',
      runtimeFlow.length
        ? runtimeFlow
            .map(
              (s) => `<details class="vc-collapse">
              <summary>${esc(s.stage || 'stage')} · ${esc(s.formula_id || '—')}</summary>
              <div class="vc-h3">Input</div>
              ${pre(s.input || {})}
              <div class="vc-h3">Process</div>
              ${pre(s.process || {})}
              <div class="vc-h3">Output</div>
              ${pre(s.output || {})}
            </details>`
            )
            .join('')
        : '<p class="vc-muted">No runtime stage flow emitted.</p>'
    );

    const byRepo = {};
    for (const lu of lookups) {
      const r = lu._repository;
      (byRepo[r] = byRepo[r] || []).push(lu);
    }
    const repoHtml = section(
      'repository',
      'Repository Retrieval',
      Object.keys(byRepo).length
        ? `<div class="vc-card-stack">${Object.keys(byRepo)
            .sort()
            .map((repo) => {
              const rows = byRepo[repo];
              return `<div class="vc-call">
                <h3>${esc(repo)}</h3>
                <div class="vc-meta-row">${pill(rows.length + ' lookups')} ${pill(fmtMs(NT), 'vc-pill-warn')}</div>
                <table class="vc-lookup-table">
                  <thead><tr><th>Method / table</th><th>Returned</th><th>Evidence</th><th>Subject</th></tr></thead>
                  <tbody>${rows
                    .slice(0, 40)
                    .map((lu) => {
                      const cols = lu.selected_columns || lu.columns || lu.primary_key || {};
                      return `<tr>
                        <td><code>${esc(lu.table || 'lookup')}</code></td>
                        <td>${clickVal('Lookup row', lu.row_id || 'row ' + (lu.csv_row ?? '—'), lu)}</td>
                        <td>${esc(lu.evidence_id || '—')}</td>
                        <td>${esc(lu._subject || '')}<div class="vc-muted">${esc(
                          typeof cols === 'object' ? JSON.stringify(cols).slice(0, 120) : cols
                        )}</div></td>
                      </tr>`;
                    })
                    .join('')}</tbody>
                </table>
              </div>`;
            })
            .join('')}</div>`
        : `<p class="vc-muted">No repository lookups were emitted on formula executions.</p>`,
      `${lookups.length} lookups`
    );

    const timelineHtml = section(
      'timeline',
      'FormulaGraph Timeline',
      `<ol class="vc-timeline">${GRAPH_NODES.map((node) => {
        const st = timelineById[node.stage] || {};
        const present = st.present !== false && (st.elapsed_ms != null || node.stage === 'payload');
        const fxFor = allFx.filter((fx) => {
          const stage = String(fx.stage || '').toLowerCase();
          if (node.id === 'risk') return fx.formula_id === 'RISK_V2_1';
          if (node.id === 'nutrition' || node.id === 'ingredient') return String(fx.formula_id).includes('NUTRIENT');
          if (node.id === 'package') return String(fx.formula_id).includes('PACKAGE');
          return stage.includes(node.id);
        });
        return `<li class="vc-timeline-node${present ? '' : ' is-missing'}">
          <span class="vc-timeline-dot"></span>
          <details class="vc-timeline-card">
            <summary>
              <span>${esc(node.label)}</span>
              <span class="vc-muted">${esc(st.label || node.stage)} · ${esc(fmtMs(st.elapsed_ms))}</span>
            </summary>
            <div class="vc-section-body">
              <p>${esc(st.message || 'Pipeline stage')}</p>
              <div class="vc-meta-row">
                ${st.record_count != null ? pill(st.record_count + ' records') : ''}
                ${(st.source_files || []).slice(0, 6).map((f) => pill(f)).join('')}
              </div>
              ${fxFor.slice(0, 3).map((fx) => renderFxCard(fx, false)).join('') || '<p class="vc-muted">Expand Formula Details for executions tied to this node.</p>'}
            </div>
          </details>
        </li>`;
      }).join('')}</ol>`
    );

    const formulasHtml = section(
      'formulas',
      'Formula Details',
      allFx.length
        ? allFx.map((fx, i) => renderFxCard(fx, i < 2)).join('')
        : `<p class="vc-muted">No formula_executions in payload.</p>`,
      `${allFx.length} executions`
    );

    const evidenceHtml = section(
      'evidence',
      'Scientific Evidence',
      (Array.isArray(evidence) && evidence.length
        ? evidence
            .slice(0, 30)
            .map((e) => {
              const cond = e.condition || e.subject || e.title || 'Evidence';
              return `<div class="vc-evidence-chain">
                <strong>${esc(cond)}</strong>
                <div class="arrow">↓ Scientific relationship</div>
                <div>${esc(e.relationship || e.mechanism || e.summary || e.claim || '—')}</div>
                <div class="arrow">↓ Quote</div>
                <div>${esc(e.quote || 'EVIDENCE INCOMPLETE')}</div>
                <div class="arrow">↓ Supporting papers / sources</div>
                <div>${esc(e.source_name || e.paper || e.citation || e.evidence_id || '—')}${
                  e.year ? ' · ' + esc(e.year) : ''
                }${e.doi ? ' · DOI ' + esc(e.doi) : ''}</div>
                <div class="arrow">↓ Link</div>
                <div>${
                  e.url ? `<a href="${esc(e.url)}" target="_blank" rel="noopener noreferrer">${esc(e.url)}</a>` : '<span class="vc-nt">EVIDENCE INCOMPLETE</span>'
                }</div>
                <div class="arrow">↓ Confidence / level</div>
                <div>${pill(e.evidence_level || e.confidence || e.strength || '—')} ${
                  e.repository || e.table ? pill(e.repository || e.table) : ''
                }</div>
                ${e.evidence_status === 'EVIDENCE INCOMPLETE' ? '<div class="vc-nt">EVIDENCE INCOMPLETE</div>' : ''}
              </div>`;
            })
            .join('')
        : riskFx
            .slice(0, 8)
            .map((fx) => {
              const srcs = [
                ...new Set((fx.lookups || []).map((lu) => lu.evidence_id).filter(Boolean))
              ];
              return `<div class="vc-evidence-chain">
                <strong>${esc(fx.condition)}</strong>
                <div class="arrow">↓ Repository lookups with evidence ids</div>
                <div>${srcs.map((s) => pill(s)).join(' ') || '<span class="vc-nt">' + NT + '</span>'}</div>
                <div class="arrow">↓ Confidence</div>
                <div>${pill(((fx.outputs || {}).confidence_percent != null ? fmtNum(fx.outputs.confidence_percent, 1) + '%' : '—'))}</div>
              </div>`;
            })
            .join('')) || `<p class="vc-muted">No evidence objects emitted.</p>`
    );

    const numericalHtml = section(
      'numerical_provenance',
      'Numerical Provenance',
      numericalProv.length
        ? numericalProv
            .map((entry) => {
              const rows = entry.rows || [];
              return `<details class="vc-collapse">
                <summary>${esc(entry.formula_id || '—')} · ${esc(entry.subject || '—')} · ${esc(rows.length)} rows</summary>
                ${rows.length ? pre(rows) : '<p class="vc-muted">No mapped rows.</p>'}
              </details>`;
            })
            .join('')
        : '<p class="vc-muted">No numerical provenance rows mapped to runtime formulas.</p>'
    );

    const replayHtml = section(
      'replay',
      'Replay',
      replayRows.length ? pre(replayRows) : '<p class="vc-muted">REPLAY: NOT AVAILABLE</p>'
    );

    const sensitivityHtml = section(
      'sensitivity',
      'Sensitivity',
      sensitivityRows.length ? pre(sensitivityRows) : '<p class="vc-muted">No supported replay traces for sensitivity.</p>'
    );

    const publicationRiskHtml = section(
      'publication_risk',
      'Publication Risk',
      pubRisk.length ? pre(pubRisk) : '<p class="vc-muted">No publication-risk rows emitted.</p>'
    );

    const risksHtml = section(
      'risks',
      'Risk Aggregation',
      (riskFx.length ? riskFx : ledgers)
        .slice(0, 12)
        .map((item, idx) => {
          const fx = item.formula_id ? item : item.formula_execution || riskFx[idx];
          const ledger = item.condition && item.expanded_chain ? item : ledgers.find((l) => l.condition === (fx && fx.condition));
          const cond = (fx && fx.condition) || (ledger && ledger.condition) || 'Condition';
          const final =
            (fx && fx.outputs && fx.outputs.final_risk_percent) ||
            (ledger && ledger.final_probability_pct);
          return `<div class="vc-call">
            <h3>${esc(cond)} · ${clickVal(
              cond + ' risk',
              final != null ? fmtNum(final, 1) + '%' : '—',
              { fx, ledger }
            )}</h3>
            <div class="vc-h3">Aggregation waterfall</div>
            ${riskWaterfall(fx, ledger)}
            ${fx ? renderFxCard(fx, false) : ''}
          </div>`;
        })
        .join('') || `<p class="vc-muted">No risk executions.</p>`
    );

    const nutritionHtml = section(
      'nutrition',
      'Nutrition',
      (nutrition.length
        ? nutrition
            .map((n) => {
              const name = n.nutrient || n.nutrient_name || n.name || 'Nutrient';
              const target = n.target ?? n.target_dose ?? n.amount;
              const unit = n.unit || n.target_unit || '';
              const reason = n.reason || n.condition || n.purpose || '—';
              return `<div class="vc-call">
                <h3>${esc(name)}</h3>
                ${kv([
                  ['Target', esc(target != null ? `${target}${unit}` : '—')],
                  ['Current', esc(n.current != null ? n.current : '—')],
                  ['Formula', esc(n.formula || n.expression || NT)],
                  ['Reason', esc(reason)],
                  ['Repository', esc(n.source_table || n.repository || 'NutritionRepository')],
                  ['Evidence', esc(n.source_name || n.evidence_id || n.paper || '—')]
                ])}
                ${n.calculation ? `<div class="vc-formula-box">${esc(n.calculation)}</div>` : ''}
              </div>`;
            })
            .join('')
        : nutFx.map((fx) => renderFxCard(fx, false)).join('')) ||
        `<p class="vc-muted">No nutrition targets emitted.</p>`
    );

    const ingList = Array.isArray(ingredients)
      ? ingredients
      : ingredients.selected || ingredients.items || [];
    const ingredientsHtml = section(
      'ingredients',
      'Ingredient Selection',
      (ingList.length
        ? ingList
            .map((ing) => {
              const name = ing.ingredient || ing.ingredient_name || ing.name || 'Ingredient';
              return `<div class="vc-call">
                <h3>${esc(name)}</h3>
                ${kv([
                  ['Reason selected', esc(ing.reason || ing.why || ing.condition || '—')],
                  ['Conditions supported', esc((ing.conditions || ing.supports || []).join?.(', ') || ing.condition || '—')],
                  ['Mechanism', esc(ing.mechanism || ing.mechanism_summary || '—')],
                  ['Papers', esc(ing.source_name || ing.paper || ing.evidence_id || '—')],
                  ['Warnings', esc(ing.interaction_warning || ing.warnings || 'None')],
                  ['Confidence', esc(ing.confidence || ing.evidence_level || '—')],
                  ['Formula score', esc(ing.score != null ? ing.score : NT)]
                ])}
              </div>`;
            })
            .join('')
        : `<p class="vc-muted">Ingredient resolution detail ${esc(NT)} as a dedicated list — see nutrition formula lookups.</p>
           ${nutFx[0] ? renderFxCard(nutFx[0], false) : ''}`)
    );

    const selected = products.selected || (products.outputs && products.outputs.selected) || [];
    const rejected = products.rejected || (products.outputs && products.outputs.rejected) || [];
    const productsHtml = section(
      'products',
      'Product Optimization',
      `<div class="vc-meta-row" style="margin-bottom:12px">
         ${pill((selected.length || 0) + ' selected', 'vc-pill-ok')}
         ${pill((Array.isArray(rejected) ? rejected.length : 0) + ' rejected')}
         ${products.formula_id ? pill(products.formula_id) : ''}
       </div>
       <div class="vc-h3">Final ranking</div>
       <div class="vc-card-stack">${(selected || [])
         .map((p, i) => {
           const name = p.product_name || p.name || p.product_id || 'Product';
           return `<div class="vc-call">
             <h3>#${i + 1} · ${esc(name)}</h3>
             ${kv([
               ['Score', esc(p.score != null ? p.score : p.final_score != null ? p.final_score : NT)],
               ['Price', esc(p.price != null ? p.price : p.list_price_rmb != null ? p.list_price_rmb : '—')],
               ['Coverage', esc(p.coverage != null ? p.coverage : NT)],
               ['Nutrition match', esc(p.nutrition_match != null ? p.nutrition_match : NT)],
               ['Compatibility', esc(p.compatibility != null ? p.compatibility : NT)],
               ['Why', esc(p.reason || p.why || '—')]
             ])}
             ${clickVal('Product object', 'Inspect', p)}
           </div>`;
         })
         .join('') || '<p class="vc-muted">No products selected.</p>'}</div>
       ${
         Array.isArray(rejected) && rejected.length
           ? `<details class="vc-collapse" style="margin-top:12px"><summary>Rejected candidates (${rejected.length})</summary>${pre(
               rejected.slice(0, 40)
             )}</details>`
           : ''
       }`
    );

    const tiers = packages.tiers || (packages.outputs && packages.outputs.tiers) || [];
    const packagesHtml = section(
      'packages',
      'Package Optimization',
      tiers.length
        ? tiers
            .map((t) => {
              const title = t.title || t.tier || t.name || 'Package';
              const pkgProducts = t.products_selected || t.products || [];
              const productIds = t.outputs && t.outputs.product_ids ? t.outputs.product_ids : [];
              return `<div class="vc-call">
                <h3>${esc(title)}</h3>
                ${kv([
                  ['Bundle score', esc(t.score != null ? t.score : t.bundle_score != null ? t.bundle_score : t.outputs?.overall_score != null ? t.outputs.overall_score : NT)],
                  ['Coverage', esc(t.coverage != null ? t.coverage : t.outputs?.coverage_score != null ? t.outputs.coverage_score : t.coverage_score != null ? t.coverage_score : NT)],
                  ['Monthly', esc(t.monthly_cost != null ? t.monthly_cost : t.outputs?.monthly_cost != null ? t.outputs.monthly_cost : t.price != null ? t.price : '—')],
                  ['Yearly', esc(t.yearly_cost != null ? t.yearly_cost : t.outputs?.yearly_cost != null ? t.outputs.yearly_cost : '—')],
                  ['Why won', esc(t.why || t.reason || t.selection_reason || t.outputs?.summary || '—')]
                ])}
                ${(pkgProducts.length || productIds.length)
                  ? `<ul class="vc-bullets">${(pkgProducts.length
                    ? pkgProducts.map((p) => `<li>${esc(p.name || p.product_name || p.product_id || NT)}</li>`)
                    : productIds.map((id) => `<li>${esc(id)}</li>`)).join('')}</ul>`
                  : `<p class="vc-muted">Package products ${esc(NT)}</p>`}
                ${t.optimization_formula || t.formula ? `<div class="vc-formula-box">${esc(t.optimization_formula || t.formula)}</div>` : ''}
                ${clickVal(title, 'Inspect package', t)}
                ${(t.removed_products || []).length ? `<details class="vc-collapse"><summary>Removed products</summary>${pre(t.removed_products)}</details>` : ''}
              </div>`;
            })
            .join('')
        : `<p class="vc-muted">No package tiers emitted.</p>${allFx
            .filter((fx) => String(fx.formula_id).includes('PACKAGE'))
            .map((fx) => renderFxCard(fx, true))
            .join('')}`
    );

    const assessmentHtml = section(
      'assessment',
      'Final Assessment',
      `<details class="vc-collapse" open><summary>AssessmentResult / production objects</summary>${pre(
        finalObjs.assessment || finalObjs.clinical_assessment || consoleDoc.assessment_provenance || finalObjs
      )}</details>
       <details class="vc-collapse"><summary>Analyze keys</summary>${pre(consoleDoc.raw_analyze_keys || [])}</details>`
    );

    const jsonHtml = section(
      'json',
      'JSON Output',
      `<details class="vc-collapse"><summary>Full Clinical Execution Explorer document</summary>${pre({
        schema: consoleDoc.schema,
        overview: consoleDoc.overview,
        profile_inspector: consoleDoc.profile_inspector,
        formula_executions: consoleDoc.formula_executions,
        risk_ledgers: consoleDoc.risk_ledgers,
        nutrition: consoleDoc.nutrition,
        products: consoleDoc.products,
        packages: consoleDoc.packages,
        evidence: consoleDoc.evidence,
        performance: consoleDoc.performance
      })}</details>
       <details class="vc-collapse"><summary>Raw analyze.debug</summary>${pre(consoleDoc.analyze_debug || {})}</details>`
    );

    const stageEntries = Object.entries(timings).filter(([k]) => k !== 'total_pipeline');
    const total = Number(timings.total_pipeline) || stageEntries.reduce((s, [, v]) => s + (Number(v) || 0), 0) || 1;
    const performanceHtml = section(
      'performance',
      'Performance',
      `${kv([
        ['Repository time', `<span class="vc-nt">${esc(NT)}</span>`],
        ['FormulaGraph time', esc(fmtMs(timings.total_pipeline))],
        ['Serialization time', `<span class="vc-nt">${esc(NT)}</span>`],
        ['Total time', esc(fmtMs(timings.total_pipeline))]
      ])}
       <div class="vc-h3" style="margin-top:16px">Each stage</div>
       <div class="vc-perf-bars">${stageEntries
         .map(([k, v]) => {
           const n = Number(v) || 0;
           const w = Math.min(100, (n / total) * 100);
           return `<div class="vc-perf-row">
             <div>${esc(k)}</div>
             <div class="vc-wf-bar"><div class="vc-wf-fill" style="width:${w}%"></div></div>
             <div class="vc-wf-delta">${esc(fmtMs(v))}</div>
           </div>`;
         })
         .join('')}</div>
       <div class="vc-h3" style="margin-top:16px">FormulaNode timings</div>
       <div class="vc-card-stack">${allFx
         .map((fx) => {
           const ms = (fx.timing && (fx.timing.elapsed_ms || fx.timing.ms)) || NT;
           return `<div class="vc-call"><strong>${esc(fx.condition || fx.subject || fx.formula_id)}</strong> · ${esc(
             fmtMs(ms)
           )}</div>`;
         })
         .join('') || `<p class="vc-muted">Per-formula timings ${esc(NT)}</p>`}</div>`
    );

    main.innerHTML = `
      <header class="vc-hero">
        <h1>Clinical Execution Explorer</h1>
        <p>${esc(
          consoleDoc.philosophy ||
            'Every stage explains inputs, repository data, formulas, intermediates, evidence, outputs, timing, and confidence.'
        )}</p>
        <div class="vc-meta-row" style="margin-top:12px">
          ${pill(consoleDoc.schema || '—')}
          ${pill(activePreset)}
          ${pill(fmtMs(timings.total_pipeline))}
          ${pill(allFx.length + ' formulas')}
        </div>
      </header>
      <section class="vc-section" id="top_summary">
        <div class="vc-section-head"><h2>Top Summary</h2></div>
        <div class="vc-section-body">
          ${kv([
            ['Dog', esc(petName)],
            ['Conditions assessed', esc(String(riskCount))],
            ['Observed evidence rows', esc(String((consoleDoc.evidence || []).length))],
            ['Formulas executed', esc(String(allFx.length))],
            ['Scientific citations', esc(String(citationCount))],
            ['Replay coverage', esc(replayCoverage)],
            ['Source located', esc(`${statusSummary.source_located || 0}/${allFx.length}`)],
            ['Documented formulas', esc(`${statusSummary.documented || 0}/${allFx.length}`)],
            ['Warehouse row traced', esc(`${statusSummary.warehouse_row_traced || 0}/${allFx.length}`)],
            ['Evidence traced', esc(`${statusSummary.evidence_traced || 0}/${allFx.length}`)]
          ])}
        </div>
      </section>
      ${clinicalOutputHtml}
      ${runtimeFlowHtml}
      ${inputHtml}
      ${pipelineHtml}
      ${validationHtml}
      ${repoHtml}
      ${timelineHtml}
      ${formulasHtml}
      ${evidenceHtml}
      ${numericalHtml}
      ${replayHtml}
      ${sensitivityHtml}
      ${publicationRiskHtml}
      ${risksHtml}
      ${nutritionHtml}
      ${ingredientsHtml}
      ${productsHtml}
      ${packagesHtml}
      ${assessmentHtml}
      ${jsonHtml}
      ${performanceHtml}
    `;

    wireInteractions(main);
  }

  function wireInteractions(root) {
    root.querySelectorAll('[data-trace]').forEach((btn) => {
      btn.addEventListener('click', () => {
        let payload = {};
        try {
          payload = JSON.parse(decodeURIComponent(btn.getAttribute('data-trace') || '{}'));
        } catch (_) {
          payload = { error: 'Could not parse trace payload' };
        }
        showTrace(btn.getAttribute('data-trace-title') || 'Trace', payload);
      });
    });

    root.querySelectorAll('[data-term-key]').forEach((btn) => {
      btn.addEventListener('click', () => {
        const key = btn.getAttribute('data-term-key');
        openTermKey = openTermKey === key ? null : key;
        renderExplorer();
        const el = document.getElementById('formulas') || document.getElementById('risks');
        if (el) el.scrollIntoView({ block: 'nearest' });
      });
    });
  }

  function renderNav() {
    const nav = document.getElementById('vc-nav');
    if (!nav || !consoleDoc) return;
    const items = consoleDoc.nav || [];
    nav.innerHTML = items
      .map(
        (n) =>
          `<button type="button" data-nav="${esc(n.id)}">${esc(n.label || n.id)}</button>`
      )
      .join('');
    nav.querySelectorAll('button').forEach((btn) => {
      btn.addEventListener('click', () => {
        nav.querySelectorAll('button').forEach((b) => b.classList.remove('is-active'));
        btn.classList.add('is-active');
        const id = btn.getAttribute('data-nav');
        const el = document.getElementById(id);
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
        history.replaceState(null, '', `#${id}`);
      });
    });
    const hash = (location.hash || '').replace('#', '');
    if (hash) {
      const match = nav.querySelector(`[data-nav="${hash}"]`);
      if (match) match.click();
    } else if (nav.querySelector('button')) {
      nav.querySelector('button').classList.add('is-active');
    }
  }

  async function loadConsole() {
    if (loading) return;
    loading = true;
    const live = document.getElementById('vc-live');
    const meta = document.getElementById('vc-meta');
    const main = document.getElementById('vc-main');
    if (live) live.textContent = 'Running assessment…';
    if (main)
      main.innerHTML = `<div class="vc-section"><div class="vc-section-body"><p class="vc-muted">POST /api/v1/ppie/validation-console · preset ${esc(
        activePreset
      )}</p></div></div>`;
    try {
      const res = await api('/api/v1/ppie/validation-console?debug=1', {
        method: 'POST',
        body: JSON.stringify(currentBody())
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || res.statusText);
      if (!data.schema || !data.nav) throw new Error('Missing Clinical Execution Explorer fields');
      consoleDoc = data;
      window.__VALIDATION_CONSOLE__ = data;
      openTermKey = null;
      if (meta) meta.textContent = `${data.schema} · ${activePreset}`;
      if (live) live.textContent = 'Live · ready';
      renderNav();
      renderExplorer();
    } catch (err) {
      if (live) live.textContent = 'Failed';
      if (main)
        main.innerHTML = `<div class="vc-section"><div class="vc-section-body"><h2>Load failed</h2><p class="vc-nt">${esc(
          err.message || err
        )}</p></div></div>`;
    } finally {
      loading = false;
    }
  }

  async function loadPresets() {
    const sel = document.getElementById('vc-preset');
    try {
      const res = await api('/api/v1/ppie/debug/presets?debug=1');
      if (res.ok) {
        const data = await res.json();
        presets = data.presets || data || [];
      }
    } catch (_) {
      presets = [];
    }
    if (!presets.length) {
      presets = Object.keys(PRESET_BODIES).map((id) => ({
        id,
        label: id.replace(/_/g, ' ')
      }));
    }
    if (sel) {
      sel.innerHTML = presets
        .map((p) => `<option value="${esc(p.id)}"${p.id === activePreset ? ' selected' : ''}>${esc(p.label || p.id)}</option>`)
        .join('');
      sel.addEventListener('change', () => {
        activePreset = sel.value;
        loadConsole();
      });
    }
  }

  async function pollStatus() {
    try {
      const res = await api('/api/v1/ppie/debug/status?debug=1');
      if (!res.ok) return;
      const data = await res.json();
      if (lastBootId == null) lastBootId = data.boot_id;
      else if (data.boot_id && data.boot_id !== lastBootId) {
        lastBootId = data.boot_id;
        loadConsole();
      }
    } catch (_) {}
  }

  function bindExports() {
    const jsonBtn = document.getElementById('vc-export-json');
    const mdBtn = document.getElementById('vc-export-md');
    const close = document.getElementById('vc-prov-close');
    if (jsonBtn) {
      jsonBtn.addEventListener('click', () => {
        const blob = new Blob([JSON.stringify(consoleDoc || {}, null, 2)], { type: 'application/json' });
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = `clinical-execution-explorer-${activePreset}.json`;
        a.click();
      });
    }
    if (mdBtn) {
      mdBtn.addEventListener('click', async () => {
        const res = await api('/api/v1/ppie/validation-console/markdown?debug=1', {
          method: 'POST',
          body: JSON.stringify(currentBody())
        });
        const data = await res.json();
        const text = data.markdown || data || '';
        const blob = new Blob([typeof text === 'string' ? text : JSON.stringify(text, null, 2)], {
          type: 'text/markdown'
        });
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = `clinical-execution-explorer-${activePreset}.md`;
        a.click();
      });
    }
    if (close) close.addEventListener('click', hideTrace);
    const refresh = document.getElementById('vc-refresh');
    if (refresh) refresh.addEventListener('click', loadConsole);
  }

  async function boot() {
    clearTimeout(window.__VC_BOOT_WATCHDOG__);
    const gate = document.getElementById('vc-gate');
    const app = document.getElementById('vc-app');
    if (!debugEnabled()) {
      if (gate) gate.hidden = false;
      if (app) app.hidden = true;
      return;
    }
    if (gate) gate.hidden = true;
    if (app) app.hidden = false;
    bindExports();
    try {
      const health = await api('/health').then((r) => r.json());
      const banner = document.getElementById('vc-demo-banner');
      if (banner) banner.hidden = !health.demo_catalog;
      const meta = document.getElementById('vc-meta');
      if (meta && health.demo_catalog) meta.textContent = 'DEMO CATALOG · demonstration data';
    } catch (_err) {
      /* health is optional for explorer boot */
    }
    await loadPresets();
    await loadConsole();
    setInterval(pollStatus, 4000);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
