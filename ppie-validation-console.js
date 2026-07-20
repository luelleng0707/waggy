/**
 * PPIE Live Validation Console — developer/CTO only.
 * Presets, repository browser, compare, live reload. No clinical math.
 */
(function () {
  'use strict';

  const API_KEY = 'wagtopia-demo-key';
  const NT = 'NOT CURRENTLY TRACEABLE';
  const FALLBACK_PRESETS = [
    {
      id: 'mixed_breed',
      label: 'Mixed Breed',
      body: {
        name: 'Dolly',
        pet_name: 'Dolly',
        breeds: ['Golden Retriever', 'Labrador Retriever'],
        birthday: '2021-03-15',
        weight: 30,
        sex: 'Female',
        activity_level: 'High',
        current_environment: 'Shanghai Summer',
        observed_conditions: []
      }
    }
  ];

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

  const esc = s =>
    String(s ?? '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');

  let consoleDoc = null;
  let compareDoc = null;
  let repoCatalog = null;
  let presets = [];
  let activePreset = 'mixed_breed';
  let activeNav = 'report';
  let lastBootId = null;
  let loading = false;
  let selectedProvenance = null;


  function debugEnabled() {
    return /(?:\?|&)(?:debug|dev)=(?:1|true)\b/i.test(location.search);
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

  function pill(t) {
    return `<span class="vc-pill">${esc(t)}</span>`;
  }

  async function api(path, opts) {
    const res = await fetch(path, {
      ...opts,
      headers: {
        Accept: 'application/json',
        'x-api-key': API_KEY,
        ...(opts && opts.body ? { 'Content-Type': 'application/json' } : {}),
        ...(opts && opts.headers)
      }
    });
    return res;
  }

  function renderFormulaExecution(fx) {
    if (!fx) return '';
    const steps = (fx.steps || [])
      .map(s => {
        const before = s.before != null ? `<span class="vc-muted">${esc(s.before)}</span> → ` : '';
        const after =
          s.after != null || s.result != null
            ? `<span class="vc-num">${esc(s.after != null ? s.after : s.result)}${esc(s.unit || '')}</span>`
            : '';
        const inputs =
          Array.isArray(s.inputs)
            ? `<div class="vc-muted">inputs · ${esc(s.inputs.join(', '))}</div>`
            : s.inputs && Object.keys(s.inputs).length
              ? `<details><summary>inputs</summary>${pre(s.inputs)}</details>`
              : '';
        return `<li>
          <strong>Step ${esc(s.step)} · ${esc(s.name)}</strong>
          ${s.expression ? `<div class="vc-muted"><code>${esc(s.expression)}</code></div>` : ''}
          <div>${before}${after}</div>
          ${s.note ? `<div class="vc-muted">${esc(s.note)}</div>` : ''}
          ${inputs}
        </li>`;
      })
      .join('');
    const mods = (fx.modifiers || [])
      .map(
        m => `<li>
          <strong>${esc(m.modifier)}</strong>
          <span class="vc-num">${esc(m.before != null ? m.before : m.running_total_before)}</span>
          <span class="vc-muted">${esc(m.effect)}</span>
          <span class="vc-num">= ${esc(m.after != null ? m.after : m.running_total_after)}${esc(m.unit || '')}</span>
          ${m.source_table ? `<div class="vc-muted">${esc(m.source_table)}${m.row_id ? ' · ' + esc(m.row_id) : m.csv_row != null ? ' · row ' + esc(m.csv_row) : ''}</div>` : ''}
          ${m.primary_key && Object.keys(m.primary_key).length ? `<div class="vc-muted">pk · ${esc(JSON.stringify(m.primary_key))}</div>` : ''}
        </li>`
      )
      .join('');
    const conf = (fx.confidence || fx.confidence_steps || [])
      .map(
        c => `<li>
          <strong>${esc(c.factor)}</strong>
          <span class="vc-num">${c.delta != null ? '+' + esc(c.delta) : esc(c.contribution_percent != null ? c.contribution_percent : c.value)}</span>
          ${c.running != null || c.running_confidence != null ? `<span class="vc-muted">→ ${esc(c.running != null ? c.running : c.running_confidence)}</span>` : ''}
          ${c.expression ? `<div class="vc-muted"><code>${esc(c.expression)}</code></div>` : ''}
          ${c.note ? `<div class="vc-muted">${esc(c.note)}</div>` : ''}
        </li>`
      )
      .join('');
    const lookups = (fx.lookups || [])
      .map(
        lu => `<li>
          <strong>${esc(lu.csv_file || lu.table)}</strong>
          ${lu.row_id ? pill(lu.row_id) : lu.csv_row != null ? pill('row ' + lu.csv_row) : `<span class="vc-nt">${esc(NT)}</span>`}
          ${lu.decision ? pill(lu.decision) : ''}
          ${lu.matched === false ? pill('unmatched') : ''}
          <div class="vc-muted">matched because · ${(lu.matched_on || Object.keys(lu.primary_key || {})).map(k => `${esc(k)} == ${esc((lu.primary_key || {})[k])}`).join(' · ') || '—'}</div>
          <div class="vc-muted">cols · ${esc(JSON.stringify(lu.selected_columns || lu.columns || {}))}</div>
          ${lu.evidence_id ? `<div class="vc-muted">evidence · ${esc(lu.evidence_id)}</div>` : ''}
        </li>`
      )
      .join('');
    const decisions = (fx.decisions || [])
      .map(
        d => `<li>
          <strong>${esc(d.decision)}</strong> ${d.subject ? pill(d.subject) : ''}
          <ul>${(d.reasons || []).map(r => `<li>${esc(r)}</li>`).join('')}</ul>
          ${d.score != null ? `<div class="vc-muted">score · ${esc(d.score)}${d.threshold != null ? ' / threshold ' + esc(d.threshold) : ''}</div>` : ''}
        </li>`
      )
      .join('');
    const comps = (fx.competitions || [])
      .map(
        c => `<li>
          <strong>${esc(c.purpose)}</strong> ${pill(c.candidate_count + ' candidates')}
          <div class="vc-muted">${esc(c.reason || '')}</div>
          <details><summary>candidates</summary>${pre(c.candidates)}</details>
          ${c.selected ? `<details open><summary>selected</summary>${pre(c.selected)}</details>` : ''}
        </li>`
      )
      .join('');
    const out = fx.outputs || {};
    const finalNum =
      out.final_risk_percent != null
        ? out.final_risk_percent + '%'
        : out.daily_dose != null
          ? out.daily_dose
          : out.overall_score != null
            ? out.overall_score
            : null;
    return `<article class="vc-card">
      <h3>${esc(fx.subject || fx.condition || '—')} ${pill(fx.formula_id || 'RISK_V2_1')} ${fx.formula_name ? pill(fx.formula_name) : ''} ${fx.stage ? pill(fx.stage) : ''}</h3>
      ${finalNum != null ? `<p class="vc-big-num">${esc(finalNum)}</p>` : ''}
      ${out.confidence_percent != null ? pill('confidence ' + out.confidence_percent + '%') : ''}
      ${out.logic ? pill(out.logic) : ''}
      ${(fx.consumers || []).length ? `<p class="vc-muted">consumers · ${esc((fx.consumers || []).join(' → '))}</p>` : ''}
      ${fx.timing && fx.timing.elapsed_ms != null ? `<p class="vc-muted">timing · ${esc(fx.timing.elapsed_ms)} ms · lookups ${esc(fx.timing.lookup_count)}</p>` : ''}
      ${fx.code ? `<p class="vc-muted">code · ${esc(JSON.stringify(fx.code))}</p>` : ''}
      <details open><summary>Formula Steps (${(fx.steps || []).length})</summary><ol class="vc-steps">${steps}</ol></details>
      <details open><summary>Modifier Chain (${(fx.modifiers || []).length})</summary><ul class="vc-steps">${mods || '<li class="vc-muted">none</li>'}</ul></details>
      <details open><summary>Confidence Ledger</summary><ul class="vc-steps">${conf || '<li class="vc-muted">none</li>'}</ul></details>
      <details open><summary>Decision Ledger (${(fx.decisions || []).length})</summary><ul class="vc-steps">${decisions || '<li class="vc-muted">none</li>'}</ul></details>
      <details open><summary>Lookup Competition (${(fx.competitions || []).length})</summary><ul class="vc-steps">${comps || '<li class="vc-muted">none</li>'}</ul></details>
      <details open><summary>CSV Lookups (${(fx.lookups || []).length})</summary><ul class="vc-steps">${lookups || '<li class="vc-muted">none</li>'}</ul></details>
      <details><summary>Data Provenance</summary>${pre(fx.provenance)}</details>
      <details><summary>Inputs / Outputs / Timing</summary>${pre({ inputs: fx.inputs, outputs: fx.outputs, timing: fx.timing, lookup_row_coverage: fx.lookup_row_coverage })}</details>
    </article>`;
  }

  function renderExplain(ex) {
    const steps = (ex.steps || [])
      .map(s => {
        const label = s.label || s.name || 'step';
        if (s.status === 'NOT_APPLIED_IN_RISK_V2_1') {
          return `<li><strong>${esc(label)}</strong>
            <span class="vc-muted">not applied in RISK_V2_1</span>
            <div class="vc-muted">${esc(s.reason || '')}</div></li>`;
        }
        if (s.traceable) {
          const op = s.op && s.op !== 'set' && s.op !== 'baseline' ? ` ${esc(s.op)} ` : ' ';
          return `<li><strong>${esc(label)}</strong>
            <span class="vc-num">${op}${esc(s.value)}${esc(s.unit || '')}</span>
            ${s.after_percent != null ? `<span class="vc-muted">→ ${esc(s.after_percent)}%</span>` : ''}
            ${s.source ? `<div class="vc-muted">source · ${esc(typeof s.source === 'string' ? s.source : JSON.stringify(s.source))}</div>` : ''}
            ${s.csv ? `<div class="vc-muted">csv · ${esc(s.csv)}</div>` : ''}
            ${s.formula_id ? pill(s.formula_id) : ''}
          </li>`;
        }
        return `<li><strong>${esc(label)}</strong>
          <div class="vc-nt">${esc(NT)}</div>
          <div class="vc-muted">${esc(s.reason || s.note || s.status || '')}</div>
        </li>`;
      })
      .join('');
    const final = ex.final_probability_pct;
    return `<article class="vc-card" id="explain-${esc(ex.condition)}">
      <h3>
        <button type="button" class="vc-click-title" data-explain="${esc(ex.condition)}">
          ${esc(ex.condition)}
          <span class="vc-big-num">${final != null ? esc(final) + '%' : '—'}</span>
        </button>
      </h3>
      ${pill(ex.formula?.formula_id || 'RISK_V2_1')}
      ${ex.complete_modifier_chain ? pill('applied modifiers traced') : pill('partial')}
      ${ex.confidence_percent != null ? pill('confidence ' + ex.confidence_percent + '%') : ''}
      ${ex.code ? `<p class="vc-muted">code · ${esc(JSON.stringify(ex.code))}</p>` : ''}
      <p class="vc-muted">${esc(ex.audit_note || '')}</p>
      <ul class="vc-steps">${steps}</ul>
      ${ex.csv_refs ? `<details><summary>CSV refs</summary>${pre(ex.csv_refs)}</details>` : ''}
    </article>`;
  }

  function chainHtml(chain) {
    return `<ol class="vc-steps">${(chain || [])
      .map(s => {
        const label = s.step || s.label || s.name || 'step';
        if (s.traceable === false || s.status === NT) {
          return `<li><strong>${esc(label)}</strong><div class="vc-nt">${esc(NT)}</div>
            <div class="vc-muted">${esc(s.reason || '')}</div></li>`;
        }
        if (s.value != null) {
          return `<li><strong>${esc(label)}</strong> <span>${esc(s.value)}${esc(s.unit || '')}</span>
            ${s.formula_id ? pill(s.formula_id) : ''} ${s.csv ? `<div class="vc-muted">csv · ${esc(typeof s.csv === 'string' ? s.csv : JSON.stringify(s.csv))}</div>` : ''}</li>`;
        }
        return `<li><strong>${esc(label)}</strong><div class="vc-nt">${esc(NT)}</div></li>`;
      })
      .join('')}</ol>`;
  }

  function renderNav(nav) {
    const el = document.getElementById('vc-nav');
    if (!el) return;
    el.innerHTML = (nav || [])
      .map(
        n =>
          `<a class="vc-toc-link" href="#${esc(n.id)}">${esc(n.label)}</a>`
      )
      .join('');
  }

  function ntBlock(reason) {
    return `<p class="vc-nt">${esc(NT)}</p><p class="vc-muted">${esc(reason || '')}</p>`;
  }

  function section(id, title, body) {
    return `<section class="vc-report-section" id="${esc(id)}">
      <h2>${esc(title)}</h2>
      ${body}
    </section>`;
  }

  function checklistHtml(list) {
    return (list || [])
      .map(c => {
        const cls = c.ok ? 'vc-ok' : 'vc-bad';
        return `<div class="vc-card"><span class="${cls}">${c.ok ? '✓' : '✗'}</span> <strong>${esc(c.label)}</strong>
          <div class="vc-muted">${esc(c.detail)}</div></div>`;
      })
      .join('');
  }

  function stageBlock(sec) {
    if (!sec) return `<p class="vc-muted">No stage data.</p>`;
    return `<div class="vc-card">
      ${pill(sec.formula_id)} ${pill('alg ' + (sec.algorithm_version || ''))} ${pill('equations hidden')}
      ${(sec.missing || []).length ? `<p class="vc-nt">Missing / fallback</p>${pre(sec.missing)}` : ''}
      <h3>CSV sources</h3>${pre(sec.csv_sources)}
      <h3>Inputs</h3>${pre(sec.inputs)}
      <h3>Outputs</h3>${pre(sec.outputs)}
    </div>`;
  }

  async function ensureRepo() {
    if (repoCatalog) return repoCatalog;
    const res = await api('/api/v1/ppie/debug/repository?debug=1');
    if (!res.ok) throw new Error('repository ' + res.status);
    repoCatalog = await res.json();
    return repoCatalog;
  }

  async function renderRepository() {
    const main = document.getElementById('vc-main');
    main.innerHTML = `<h1 class="vc-h1">Repository Browser</h1><p class="vc-muted">Read-only · manifest.yaml</p><p>Loading…</p>`;
    try {
      const cat = await ensureRepo();
      const tables = cat.tables || [];
      main.innerHTML = `<h1 class="vc-h1">Repository Browser</h1>
        <p class="vc-muted">Read-only · version ${esc(cat.manifest_version)} · hash ${esc(cat.csv_hash)} · ${tables.length} tables</p>
        <input type="search" id="vc-repo-filter" class="vc-select" placeholder="Filter tables…">
        <div id="vc-repo-list" class="vc-repo-list"></div>
        <div id="vc-repo-preview"></div>`;
      const list = document.getElementById('vc-repo-list');
      const draw = filter => {
        const q = (filter || '').toLowerCase();
        list.innerHTML = tables
          .filter(t => !q || t.table.toLowerCase().includes(q) || (t.path || '').toLowerCase().includes(q))
          .map(
            t => `<button type="button" class="vc-repo-row" data-table="${esc(t.table)}">
              <strong>${esc(t.table)}</strong>
              <span>${esc(t.row_count)} rows · ${esc(t.cache_status)}</span>
              <span class="vc-muted">${esc(t.path)}</span>
            </button>`
          )
          .join('');
        list.querySelectorAll('[data-table]').forEach(btn => {
          btn.addEventListener('click', () => loadTablePreview(btn.getAttribute('data-table')));
        });
      };
      draw('');
      document.getElementById('vc-repo-filter').addEventListener('input', e => draw(e.target.value));
    } catch (err) {
      main.innerHTML = `<h1 class="vc-h1">Repository</h1><p class="vc-nt">${esc(err.message)}</p>`;
    }
  }

  async function loadTablePreview(table) {
    const host = document.getElementById('vc-repo-preview');
    host.innerHTML = `<div class="vc-card"><p>Loading ${esc(table)}…</p></div>`;
    const res = await api(`/api/v1/ppie/debug/repository/${encodeURIComponent(table)}?debug=1&limit=40`);
    if (!res.ok) {
      host.innerHTML = `<div class="vc-card"><p class="vc-nt">Failed ${res.status}</p></div>`;
      return;
    }
    const data = await res.json();
    const cols = data.columns || [];
    const head = cols.map(c => `<th>${esc(c)}</th>`).join('');
    const body = (data.rows || [])
      .map(r => `<tr>${cols.map(c => `<td>${esc(r[c])}</td>`).join('')}</tr>`)
      .join('');
    host.innerHTML = `<div class="vc-card">
      <h3>${esc(data.table)}</h3>
      <p class="vc-muted">${esc(data.path)} · showing ${esc(data.rows?.length)} / ${esc(data.filtered_rows)} (total ${esc(data.total_rows)})</p>
      <p>${pill('read-only')} ${pill(data.cache_status)} ${pill('hash ' + data.platform_csv_hash)}</p>
      <input type="search" id="vc-row-q" class="vc-select" placeholder="Search rows…">
      <div class="vc-table-wrap"><table class="vc-table"><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table></div>
    </div>`;
    document.getElementById('vc-row-q').addEventListener('change', async e => {
      const q = e.target.value.trim();
      const r2 = await api(
        `/api/v1/ppie/debug/repository/${encodeURIComponent(table)}?debug=1&limit=40&q=${encodeURIComponent(q)}`
      );
      if (!r2.ok) return;
      const d2 = await r2.json();
      const b2 = (d2.rows || [])
        .map(r => `<tr>${cols.map(c => `<td>${esc(r[c])}</td>`).join('')}</tr>`)
        .join('');
      host.querySelector('tbody').innerHTML = b2;
    });
  }

  async function renderCompare() {
    const main = document.getElementById('vc-main');
    main.innerHTML = `<h1 class="vc-h1">Compare Assessments</h1>
      <p class="vc-muted">Side-by-side diff · highlights every changed field. Why = input deltas; modifier chain may be ${esc(NT)}.</p>
      <div class="vc-compare-controls">
        <label>Left <select id="vc-cmp-left" class="vc-select"></select></label>
        <label>Right <select id="vc-cmp-right" class="vc-select"></select></label>
        <button type="button" class="vc-btn vc-btn-primary" id="vc-cmp-run">Run compare</button>
      </div>
      <div id="vc-cmp-out"></div>`;
    const left = document.getElementById('vc-cmp-left');
    const right = document.getElementById('vc-cmp-right');
    const opts = Object.keys(PRESET_BODIES)
      .map(id => {
        const label = (presets.find(p => p.id === id) || {}).label || id;
        return `<option value="${esc(id)}">${esc(label)}</option>`;
      })
      .join('');
    left.innerHTML = opts;
    right.innerHTML = opts;
    left.value = 'golden_20kg';
    right.value = 'golden_25kg';
    document.getElementById('vc-cmp-run').addEventListener('click', runCompare);
    if (compareDoc) paintCompare(compareDoc);
  }

  async function runCompare() {
    const leftId = document.getElementById('vc-cmp-left').value;
    const rightId = document.getElementById('vc-cmp-right').value;
    const out = document.getElementById('vc-cmp-out');
    out.innerHTML = `<p class="vc-muted">Running both pipelines…</p>`;
    const res = await api('/api/v1/ppie/validation-console/compare?debug=1', {
      method: 'POST',
      body: JSON.stringify({
        left: PRESET_BODIES[leftId],
        right: PRESET_BODIES[rightId],
        left_label: leftId,
        right_label: rightId
      })
    });
    if (!res.ok) {
      out.innerHTML = `<p class="vc-nt">Compare failed (${res.status})</p>`;
      return;
    }
    compareDoc = await res.json();
    paintCompare(compareDoc);
  }

  function paintCompare(doc) {
    const out = document.getElementById('vc-cmp-out');
    if (!out || !doc) return;
    const d = doc.diff || {};
    const rows = (d.changes || [])
      .map(c => {
        const delta =
          c.delta != null ? `<span class="vc-delta">${c.delta > 0 ? '+' : ''}${esc(c.delta)}</span>` : '';
        const why = c.why || {};
        return `<tr class="vc-diff-row">
          <td><code>${esc(c.path)}</code></td>
          <td>${esc(JSON.stringify(c.left))}</td>
          <td>${esc(JSON.stringify(c.right))} ${delta}</td>
          <td>
            <div>${esc(why.status || '')}</div>
            <div class="vc-muted">${esc(why.reason || '')}</div>
            ${why.modifier_chain ? `<div class="vc-nt">${esc(why.modifier_chain)}</div>` : ''}
            ${why.input_deltas ? pre(why.input_deltas) : ''}
          </td>
        </tr>`;
      })
      .join('');
    out.innerHTML = `<div class="vc-card">
      <h3>${esc(d.left_label)} vs ${esc(d.right_label)}</h3>
      <p>${pill(d.change_count + ' changes')} ${pill(d.unchanged_health_priorities + ' health unchanged')}</p>
      <h4>Input deltas</h4>${pre(d.input_deltas)}
      <p class="vc-muted">${esc(d.note)}</p>
      <div class="vc-table-wrap"><table class="vc-table">
        <thead><tr><th>Field</th><th>Left</th><th>Right</th><th>Why</th></tr></thead>
        <tbody>${rows || '<tr><td colspan="4">No differences</td></tr>'}</tbody>
      </table></div>
    </div>`;
  }

  function clickableNum(value, unit, provenance) {
    const v = value == null || value === '' ? '—' : value;
    const u = unit || '';
    const payload = encodeURIComponent(JSON.stringify(provenance || { value: v, unit: u }));
    return `<button type="button" class="vc-num-btn" data-prov="${payload}"><span class="vc-num">${esc(v)}${esc(u)}</span></button>`;
  }

  function ledgerArrow() {
    return `<div class="vc-ledger-arrow">↓</div>`;
  }

  function fxByFormula(fid) {
    return (consoleDoc.formula_executions || []).filter(fx => fx && fx.formula_id === fid);
  }

  function renderFxLedger(fx) {
    if (!fx) return '';
    const out = fx.outputs || {};
    const title =
      fx.subject ||
      fx.condition ||
      out.ingredient_key ||
      out.tier ||
      fx.formula_id ||
      'Execution';
    const headline =
      out.final_risk_percent != null
        ? `${out.final_risk_percent}%`
        : out.daily_dose != null
          ? `${out.daily_dose}${out.unit || ''}`
          : out.overall_score != null
            ? `score ${out.overall_score}`
            : '';

    const equationLines = (fx.steps || [])
      .filter(s => s && s.expression)
      .map((s, i) => `${i + 1}. ${s.name}: ${s.expression}`)
      .join('\n');

    const stepsHtml = (fx.steps || [])
      .map(s => {
        const before =
          s.before != null
            ? clickableNum(s.before, s.unit, { kind: 'step_before', step: s, formula_id: fx.formula_id })
            : '';
        const after =
          s.after != null || s.result != null
            ? clickableNum(s.after != null ? s.after : s.result, s.unit, {
                kind: 'step_after',
                step: s,
                formula_id: fx.formula_id,
                lookups: s.lookups
              })
            : '';
        return `<div class="vc-ledger-step">
          <div class="vc-ledger-step-name"><strong>Step ${esc(s.step)}</strong> · ${esc(s.name)}</div>
          ${s.expression ? `<div class="vc-ledger-expr"><code>${esc(s.expression)}</code></div>` : ''}
          <div class="vc-ledger-flow">${before}${before && after ? ' → ' : ''}${after}</div>
          ${s.note ? `<div class="vc-muted">${esc(s.note)}</div>` : ''}
          ${
            s.inputs != null
              ? Array.isArray(s.inputs)
                ? `<div class="vc-muted">inputs · ${esc(s.inputs.join(', '))}</div>`
                : `<details><summary>inputs</summary>${pre(s.inputs)}</details>`
              : ''
          }
        </div>`;
      })
      .join(ledgerArrow());

    const modsHtml = (fx.modifiers || [])
      .map(
        m => `<div class="vc-ledger-mod">
          ${clickableNum(m.before != null ? m.before : m.running_total_before, m.unit, {
            kind: 'mod_before',
            modifier: m,
            formula_id: fx.formula_id
          })}
          <span class="vc-ledger-op">${esc(m.effect)}</span>
          <span class="vc-muted">${esc(m.modifier)}</span>
          =
          ${clickableNum(m.after != null ? m.after : m.running_total_after, m.unit, {
            kind: 'mod_after',
            modifier: m,
            formula_id: fx.formula_id
          })}
          ${
            m.row_id || m.source_table
              ? `<div class="vc-muted">${esc(m.source_table || '')} ${esc(m.row_id || '')}</div>`
              : ''
          }
          ${m.primary_key && Object.keys(m.primary_key).length ? pre(m.primary_key) : ''}
        </div>`
      )
      .join(ledgerArrow());

    const confHtml = (fx.confidence || fx.confidence_steps || [])
      .map(
        c => `<div class="vc-ledger-conf">
          <strong>${esc(c.factor)}</strong>
          ${clickableNum(
            c.delta != null ? c.delta : c.contribution_percent != null ? c.contribution_percent : c.value,
            '',
            { kind: 'confidence', factor: c, formula_id: fx.formula_id }
          )}
          <span class="vc-muted">→ running ${esc(c.running != null ? c.running : c.running_confidence)}</span>
          ${c.expression ? `<div class="vc-ledger-expr"><code>${esc(c.expression)}</code></div>` : ''}
          ${c.note ? `<div class="vc-muted">${esc(c.note)}</div>` : ''}
        </div>`
      )
      .join(ledgerArrow());

    const lookupsHtml = (fx.lookups || [])
      .map(
        lu => `<div class="vc-ledger-lookup ${lu.decision === 'skipped_lower_than_category_max' ? 'is-skip' : ''}">
          <strong>${esc(lu.csv_file || lu.table)}</strong>
          ${lu.row_id ? pill(lu.row_id) : lu.csv_row != null ? pill('row ' + lu.csv_row) : `<span class="vc-nt">${esc(NT)}</span>`}
          ${lu.decision ? pill(lu.decision) : ''}
          <div class="vc-muted">matched · ${(lu.matched_on || Object.keys(lu.primary_key || {}))
            .map(k => `${esc(k)} == ${esc((lu.primary_key || {})[k])}`)
            .join(' · ')}</div>
          <div class="vc-muted">cols · ${esc(JSON.stringify(lu.selected_columns || lu.columns || {}))}</div>
          ${lu.evidence_id ? `<div class="vc-muted">evidence · ${esc(lu.evidence_id)}</div>` : ''}
        </div>`
      )
      .join('');

    const compsHtml = (fx.competitions || [])
      .map(
        c => `<div class="vc-ledger-comp">
          <strong>${esc(c.purpose)}</strong> ${pill((c.candidate_count || 0) + ' candidates')}
          <div class="vc-muted">${esc(c.reason || '')}</div>
          <details open><summary>All candidates</summary>${pre(c.candidates)}</details>
          ${c.selected ? `<details open><summary>Winner</summary>${pre(c.selected)}</details>` : ''}
        </div>`
      )
      .join('');

    const decisionsHtml = (fx.decisions || [])
      .map(
        d => `<div class="vc-ledger-decision ${String(d.decision || '').toLowerCase().includes('reject') ? 'is-reject' : 'is-accept'}">
          <strong>${esc(d.decision)}</strong> ${d.subject ? pill(d.subject) : ''}
          <ul>${(d.reasons || []).map(r => `<li>${esc(r)}</li>`).join('')}</ul>
          ${
            d.score != null
              ? `<div class="vc-muted">score ${esc(d.score)}${
                  d.threshold != null ? ' / threshold ' + esc(d.threshold) : ''
                }</div>`
              : ''
          }
        </div>`
      )
      .join('');

    const consumers = (fx.consumers || []).length
      ? `<div class="vc-ledger-consumers"><span class="vc-muted">Consumers</span> ${(fx.consumers || [])
          .map(esc)
          .join(' → ')}</div>`
      : '';

    const timing =
      fx.timing && fx.timing.elapsed_ms != null
        ? `<span class="vc-muted">${esc(fx.timing.elapsed_ms)} ms · ${esc(fx.timing.lookup_count || 0)} lookups</span>`
        : '';

    return `<article class="vc-report-block vc-fx-open">
      <header class="vc-report-summary">
        <span class="vc-report-title">${esc(title)}</span>
        ${headline ? `<span class="vc-big-num">${esc(headline)}</span>` : ''}
        ${pill(fx.formula_id)}
        ${fx.stage ? pill(fx.stage) : ''}
        ${timing}
      </header>
      <div class="vc-report-body">
        <div class="vc-ledger-section">
          <h4>Module / function / version</h4>
          <p><strong>${esc(fx.formula_name || fx.formula_id)}</strong></p>
          <p class="vc-muted">${esc((fx.code && fx.code.file) || '—')} :: ${esc((fx.code && fx.code.function) || '—')}</p>
          <p>${pill(fx.formula_id)} ${pill('schema ' + (fx.schema || 'formula_execution.v2'))}</p>
        </div>
        <div class="vc-ledger-section">
          <h4>Executed algorithm (engine-emitted step expressions)</h4>
          ${
            equationLines
              ? `<pre class="vc-pre vc-equation">${esc(equationLines)}</pre>`
              : ntBlock('No step expressions emitted for this execution.')
          }
        </div>
        ${fx.inputs && Object.keys(fx.inputs).length ? `<div class="vc-ledger-section"><h4>Inputs</h4>${pre(fx.inputs)}</div>` : ''}
        <div class="vc-ledger-section"><h4>Steps · running totals</h4>${stepsHtml || ntBlock('No steps')}</div>
        ${(fx.modifiers || []).length ? `<div class="vc-ledger-section"><h4>Modifiers</h4>${modsHtml}</div>` : ''}
        ${(fx.confidence || fx.confidence_steps || []).length ? `<div class="vc-ledger-section"><h4>Confidence</h4>${confHtml}</div>` : ''}
        ${(fx.competitions || []).length ? `<div class="vc-ledger-section"><h4>Lookup competition (every candidate)</h4>${compsHtml}</div>` : ''}
        <div class="vc-ledger-section"><h4>CSV lookups (every row touched)</h4>${lookupsHtml || ntBlock('No lookups')}</div>
        ${(fx.decisions || []).length ? `<div class="vc-ledger-section"><h4>Decisions</h4>${decisionsHtml}</div>` : ''}
        <div class="vc-ledger-section"><h4>Outputs</h4>${pre(out)}</div>
        ${fx.timing ? `<div class="vc-ledger-section"><h4>Runtime</h4>${pre(fx.timing)}</div>` : ''}
        ${consumers}
        ${(fx.provenance || []).length ? `<div class="vc-ledger-section"><h4>Provenance links</h4>${pre(fx.provenance)}</div>` : ''}
      </div>
    </article>`;
  }

  function groupLookupsByTable() {
    const map = {};
    for (const fx of consoleDoc.formula_executions || []) {
      if (!fx) continue;
      for (const lu of fx.lookups || []) {
        if (!lu) continue;
        const key = lu.csv_file || lu.table || 'UNKNOWN';
        if (!map[key]) map[key] = [];
        map[key].push({ ...lu, _formula_id: fx.formula_id, _subject: fx.subject || fx.condition });
      }
    }
    return map;
  }

  function wireProvenanceClicks(root) {
    root.querySelectorAll('.vc-num-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        let data = null;
        try {
          data = JSON.parse(decodeURIComponent(btn.getAttribute('data-prov') || '{}'));
        } catch (_) {
          data = { error: 'Could not parse provenance payload' };
        }
        selectedProvenance = data;
        const panel = document.getElementById('vc-prov-panel');
        const body = document.getElementById('vc-prov-body');
        if (panel && body) {
          panel.hidden = false;
          body.innerHTML = pre(data);
        }
      });
    });
    const close = document.getElementById('vc-prov-close');
    if (close) {
      close.addEventListener('click', () => {
        const panel = document.getElementById('vc-prov-panel');
        if (panel) panel.hidden = true;
      });
    }
  }

  function renderDeveloperReport() {
    const main = document.getElementById('vc-main');
    const profile = (consoleDoc.profile_inspector && consoleDoc.profile_inspector.normalized) || {};
    const rawReq = (consoleDoc.profile_inspector && consoleDoc.profile_inspector.raw_request) || null;
    const petName = profile.name || profile.pet_name || activePreset;
    const et = consoleDoc.engine_trace || {};
    const timings = consoleDoc.overview?.stage_timings_ms || consoleDoc.performance?.stage_timings_ms || {};
    const perf = consoleDoc.performance || {};
    const allFx = consoleDoc.formula_executions || [];
    const riskFx = fxByFormula('RISK_V2_1');
    const nutFx = fxByFormula('NUTRIENT_TARGET_V2_1');
    const pkgFx = fxByFormula('PACKAGE_OPTIMIZER_V2_1');
    const products = consoleDoc.products || {};
    const packages = consoleDoc.packages || consoleDoc.package_optimizer || {};
    const lookupsByTable = groupLookupsByTable();
    const mods = consoleDoc.modifier_ledger || [];
    const confs = consoleDoc.confidence_ledger || [];
    const decisions = consoleDoc.decision_ledger || [];
    const gaps = consoleDoc.gaps || [];
    const missing = consoleDoc.missing_data || [];
    const timeline = consoleDoc.pipeline_timeline || [];
    const graph = consoleDoc.formula_graph || {};
    const dag = consoleDoc.pipeline_dag || {};
    const codeTrace = consoleDoc.code_trace || {};
    const csvMap = consoleDoc.csv_usage_map || {};
    const assemble = consoleDoc.assessment_provenance || {};
    const finalObjs = consoleDoc.raw_production_objects || {};
    const debug = consoleDoc.analyze_debug || finalObjs.debug || {};

    const totalLookups = allFx.reduce((n, fx) => n + ((fx && fx.lookups) || []).length, 0);
    const matchedLookups = allFx.reduce(
      (n, fx) => n + ((fx && fx.lookups) || []).filter(lu => lu && lu.matched !== false && lu.decision !== 'skipped_lower_than_category_max').length,
      0
    );
    const skippedLookups = totalLookups - matchedLookups;

    const s0 = section(
      's0',
      '0 · Assessment Summary',
      `<div class="vc-report-grid">
        <div><span class="vc-muted">Schema</span><div>${esc(consoleDoc.schema)}</div></div>
        <div><span class="vc-muted">Algorithm</span><div>${esc(et.algorithm_version || '—')}</div></div>
        <div><span class="vc-muted">Engine</span><div>${esc(et.engine || et.engine_name || 'PPIE')}</div></div>
        <div><span class="vc-muted">Preset</span><div>${esc(activePreset)}</div></div>
        <div><span class="vc-muted">Profile</span><div>${esc(petName)}</div></div>
        <div><span class="vc-muted">Timestamp</span><div>${esc(et.generated_at || et.timestamp || NT)}</div></div>
        <div><span class="vc-muted">Analyze ms</span><div>${esc((consoleDoc.overview?.timings || {}).analyze ?? NT)}</div></div>
        <div><span class="vc-muted">Assessment ms</span><div>${esc((consoleDoc.overview?.timings || {}).assessment ?? NT)}</div></div>
        <div><span class="vc-muted">Pipeline ms</span><div>${esc(timings.total_pipeline ?? NT)}</div></div>
        <div><span class="vc-muted">Git commit</span><div><span class="vc-nt">${esc(NT)}</span></div></div>
        <div><span class="vc-muted">Cache status</span><div><span class="vc-nt">${esc(NT)}</span></div></div>
        <div><span class="vc-muted">Memory / CPU</span><div><span class="vc-nt">${esc(NT)}</span></div></div>
        <div><span class="vc-muted">Formula executions</span><div>${esc(allFx.length)}</div></div>
        <div><span class="vc-muted">Equation policy</span><div>${esc(consoleDoc.equation_policy)}</div></div>
      </div>
      <p class="vc-muted">${esc(consoleDoc.philosophy || '')}</p>`
    );

    const s1 = section(
      's1',
      '1 · Raw Request',
      rawReq ? pre(rawReq) : ntBlock('No raw_request attached to console payload.')
    );

    const normBits = consoleDoc.profile_inspector || {};
    const s2 = section(
      's2',
      '2 · Input Normalization',
      `<h3>Normalized profile</h3>${pre(profile)}
       <h3>Missing values</h3>${pre(normBits.missing_values || [])}
       <h3>Defaults applied</h3>${pre(normBits.defaults_applied)}
       <h3>Aliases resolved</h3>${pre(normBits.aliases_resolved)}
       <p class="vc-muted">Per-field before→after resolver ledger is ${esc(NT)} until payload adapter emits it.</p>`
    );

    const lookupSections = Object.keys(lookupsByTable)
      .sort()
      .map(table => {
        const rows = lookupsByTable[table];
        return `<div class="vc-table-group">
          <h3>${esc(table)} · ${rows.length} lookup(s)</h3>
          ${rows
            .map(
              lu => `<div class="vc-ledger-lookup">
                ${lu.row_id ? pill(lu.row_id) : lu.csv_row != null ? pill('row ' + lu.csv_row) : `<span class="vc-nt">${esc(NT)}</span>`}
                ${lu.decision ? pill(lu.decision) : ''}
                ${pill(lu._formula_id || '')}
                <div class="vc-muted">${esc(lu._subject || '')}</div>
                <div class="vc-muted">pk · ${esc(JSON.stringify(lu.primary_key || {}))}</div>
                <div class="vc-muted">matched_on · ${esc(JSON.stringify(lu.matched_on || []))}</div>
                <div class="vc-muted">cols · ${esc(JSON.stringify(lu.selected_columns || lu.columns || {}))}</div>
                <div class="vc-muted">cache · <span class="vc-nt">${esc(NT)}</span> · lookup_ms · <span class="vc-nt">${esc(NT)}</span></div>
              </div>`
            )
            .join('')}
        </div>`;
      })
      .join('');

    const competitions = consoleDoc.lookup_competitions || [];
    const s3 = section(
      's3',
      '3 · Repository Lookups',
      `<p>${pill(totalLookups + ' lookups')} ${pill(matchedLookups + ' selected')} ${pill(skippedLookups + ' skipped/rejected')} ${pill(Object.keys(lookupsByTable).length + ' tables')}</p>
       ${lookupSections || ntBlock('No lookups on formula_executions.')}
       <h3>Competitions (every candidate)</h3>
       ${
         competitions.length
           ? competitions
               .map(
                 c => `<div class="vc-ledger-comp">
                   <strong>${esc(c.purpose)}</strong> ${pill(c.formula_id || '')} ${pill((c.candidate_count || 0) + ' candidates')}
                   <div class="vc-muted">${esc(c.reason || '')}</div>
                   ${pre({ candidates: c.candidates, selected: c.selected })}
                 </div>`
               )
               .join('')
           : ntBlock('No competitions recorded.')
       }`
    );

    const s4 = section(
      's4',
      '4 · Formula Execution (every backend formula run)',
      `<p class="vc-muted">${allFx.length} execution(s). Each block shows module, emitted step expressions, inputs, steps, outputs, runtime.</p>
       ${allFx.length ? allFx.map(renderFxLedger).join('') : ntBlock('No formula_executions.')}`
    );

    const s5 = section(
      's5',
      '5 · Modifier Ledger',
      mods.length
        ? mods
            .map(
              m => `<div class="vc-ledger-mod">
                <strong>${esc(m.modifier)}</strong> ${pill(m.formula_id || '')} ${pill(m.subject || '')}
                <div>
                  ${clickableNum(m.before != null ? m.before : m.running_total_before, m.unit, m)}
                  <span class="vc-ledger-op">${esc(m.effect)}</span>
                  =
                  ${clickableNum(m.after != null ? m.after : m.running_total_after, m.unit, m)}
                </div>
                <div class="vc-muted">${esc(m.source_table || '')} ${esc(m.row_id || '')}</div>
                ${m.primary_key ? pre(m.primary_key) : ''}
              </div>`
            )
            .join(ledgerArrow())
        : ntBlock('No modifiers emitted.')
    );

    const s6 = section(
      's6',
      '6 · Confidence Ledger',
      `<p class="vc-muted">Production RISK confidence is category coverage — factors below are exactly what the engine emitted (not a invented study ladder).</p>
       ${
         confs.length
           ? confs
               .map(
                 c => `<div class="vc-ledger-conf">
                   <strong>${esc(c.factor)}</strong> ${pill(c.formula_id || '')} ${pill(c.subject || '')}
                   <div>delta ${esc(c.delta != null ? c.delta : c.contribution_percent ?? c.value)} → running ${esc(c.running != null ? c.running : c.running_confidence)}</div>
                   ${c.expression ? `<code>${esc(c.expression)}</code>` : ''}
                   ${c.note ? `<div class="vc-muted">${esc(c.note)}</div>` : ''}
                 </div>`
               )
               .join(ledgerArrow())
           : ntBlock('No confidence steps.')
       }`
    );

    const s7 = section(
      's7',
      '7 · Nutrition Engine',
      `${nutFx.length ? nutFx.map(renderFxLedger).join('') : ntBlock('No NUTRIENT_TARGET_V2_1 executions.')}
       <h3>Nutrition inspector projection</h3>${pre(consoleDoc.nutrition || [])}
       <h3>Nutrition math</h3>${pre(consoleDoc.nutrition_math || [])}`
    );

    const s8 = section(
      's8',
      '8 · Product Engine',
      `<h3>Selected</h3>${pre(products.selected || [])}
       <h3>Rejected</h3>${pre(products.rejected || [])}
       <h3>Full products inspector</h3>${pre(products)}`
    );

    const s9 = section(
      's9',
      '9 · Package Optimizer',
      `${pkgFx.length ? pkgFx.map(renderFxLedger).join('') : ntBlock('No PACKAGE_OPTIMIZER_V2_1 executions.')}
       <h3>Decision ledger (accept / reject)</h3>
       ${
         decisions.length
           ? decisions
               .map(
                 d => `<div class="vc-ledger-decision ${String(d.decision || '').toLowerCase().includes('reject') ? 'is-reject' : 'is-accept'}">
                   <strong>${esc(d.decision)}</strong> ${pill(d.subject || '')} ${d.tier ? pill(d.tier) : ''}
                   <ul>${(d.reasons || []).map(r => `<li>${esc(r)}</li>`).join('')}</ul>
                 </div>`
               )
               .join('')
           : ntBlock('No decisions.')
       }
       <h3>Package tiers (production objects)</h3>${pre(packages)}`
    );

    const s10 = section(
      's10',
      '10 · Response Assembly',
      `<p class="vc-muted">How ClinicalAssessment / analyze fields map to sources.</p>
       ${pre(assemble)}
       <h3>Code map</h3>${pre(codeTrace)}
       <h3>Consumers (from formula_executions)</h3>
       <ul>${allFx
         .map(
           fx =>
             `<li><code>${esc(fx.formula_id)}</code> · ${esc(fx.subject || fx.condition || '')} → ${(fx.consumers || [])
               .map(esc)
               .join(', ') || '—'}</li>`
         )
         .join('')}</ul>`
    );

    const s11 = section(
      's11',
      '11 · Final API Response (production objects, untransformed)',
      `<p class="vc-muted">Objects returned on the assess/analyze path (subset attached to console). Full console JSON via Export.</p>
       ${pre(finalObjs)}
       <h3>analyze.debug</h3>${pre(debug)}`
    );

    const s12 = section(
      's12',
      '12 · Pipeline Timeline (waterfall)',
      `<ol class="vc-report-stages">
        ${timeline
          .map(s => {
            const ms = s.elapsed_ms != null && s.elapsed_ms !== NT ? s.elapsed_ms : timings[s.id];
            return `<li>
              <strong>${esc(s.label || s.id)}</strong>
              <span class="vc-num">${ms != null && ms !== NT ? esc(ms) + ' ms' : `<span class="vc-nt">${esc(NT)}</span>`}</span>
              ${s.present ? pill('present') : pill('missing')}
              <div class="vc-muted">${esc(s.message || '')}</div>
              ${s.source_files ? pre(s.source_files) : ''}
            </li>`;
          })
          .join('') || `<li>${ntBlock('No timeline')}</li>`}
      </ol>
      <h3>Stage timings ms</h3>${pre(timings)}
      <h3>Performance inspector</h3>${pre(perf)}`
    );

    const s13 = section(
      's13',
      '13 · Dependency Graph',
      `<h3>Formula graph</h3>${pre(graph)}
       <h3>Pipeline DAG</h3>${pre(dag)}
       <h3>CSV usage map</h3>${pre(csvMap)}
       <h3>Code trace</h3>${pre(codeTrace)}`
    );

    const s14 = section(
      's14',
      '14 · Runtime Statistics',
      `<div class="vc-report-grid">
        <div><span class="vc-muted">CSV lookups</span><div>${esc(totalLookups)}</div></div>
        <div><span class="vc-muted">Rows matched/selected</span><div>${esc(matchedLookups)}</div></div>
        <div><span class="vc-muted">Rows skipped/rejected</span><div>${esc(skippedLookups)}</div></div>
        <div><span class="vc-muted">Tables touched</span><div>${esc(Object.keys(lookupsByTable).length)}</div></div>
        <div><span class="vc-muted">Formula executions</span><div>${esc(allFx.length)}</div></div>
        <div><span class="vc-muted">Modifiers</span><div>${esc(mods.length)}</div></div>
        <div><span class="vc-muted">Decisions</span><div>${esc(decisions.length)}</div></div>
        <div><span class="vc-muted">Competitions</span><div>${esc(competitions.length)}</div></div>
        <div><span class="vc-muted">Total pipeline ms</span><div>${esc(timings.total_pipeline ?? NT)}</div></div>
        <div><span class="vc-muted">Cache hits</span><div><span class="vc-nt">${esc(NT)}</span></div></div>
        <div><span class="vc-muted">Memory</span><div><span class="vc-nt">${esc(NT)}</span></div></div>
        <div><span class="vc-muted">CPU</span><div><span class="vc-nt">${esc(NT)}</span></div></div>
      </div>`
    );

    const s15 = section(
      's15',
      '15 · Validation · Gaps · Warnings',
      `<h3>Traceability gaps</h3>
       ${(gaps || [])
         .map(
           g => `<div class="vc-card"><span class="vc-nt">${esc(g.status)}</span> <strong>${esc(g.id)}</strong>
             <div>${esc(g.detail)}</div>
             <div class="vc-muted">${esc(g.instrumentation || '')}</div></div>`
         )
         .join('') || '<p class="vc-muted">None</p>'}
       <h3>Missing data report</h3>${pre(missing)}
       <h3>Validation checklist</h3>${checklistHtml(consoleDoc.validation_checklist)}
       <h3>Observability coverage %</h3>${pre(consoleDoc.observability_coverage)}`
    );

    const science = consoleDoc.science || {};
    const kg = consoleDoc.knowledge_graph || science.knowledge_graph || {};
    const recExpl = consoleDoc.recommendation_explanations || science.recommendation_explanations || [];
    const formExpl = consoleDoc.formula_explanations || science.formula_explanations || [];
    const evObjs = consoleDoc.evidence_objects || science.evidence_objects || [];
    const sciVer = consoleDoc.science_versions || science.versions || {};

    const s16 = section(
      's16',
      '16 · Knowledge Graph',
      `<p class="vc-muted">Deterministic relationship graph (no AI). Nodes/edges from warehouse science tables.</p>
       <div class="vc-report-grid">
         <div><span class="vc-muted">Nodes</span><div>${esc(kg.nodes ?? NT)}</div></div>
         <div><span class="vc-muted">Edges</span><div>${esc(kg.edges ?? NT)}</div></div>
         <div><span class="vc-muted">Types</span><div>${esc(JSON.stringify(kg.by_type || {}))}</div></div>
         <div><span class="vc-muted">Relations</span><div>${esc(JSON.stringify(kg.by_relation || {}))}</div></div>
       </div>
       <h3>Coverage snapshot</h3>${pre(science.coverage_snapshot || {})}
       <h3>Why sample (reverse lookup)</h3>${pre(science.why_examples || {})}
       <h3>Formula graph (execution)</h3>${pre(graph)}`
    );

    const s17 = section(
      's17',
      '17 · Evidence · Reasoning · Confidence',
      `<h3>Recommendation chains</h3>
       ${
         recExpl.length
           ? recExpl
               .map(
                 r => `<div class="vc-card">
                   <strong>${esc((r.chain && r.chain.render) || r.condition || '')}</strong>
                   ${pill(String(r.risk_percent ?? '') + '% risk')}
                   <div class="vc-muted">${esc(JSON.stringify((r.confidence && r.confidence.recommendation) || {}))}</div>
                   ${pre(r.chain || r)}
                 </div>`
               )
               .join('')
           : ntBlock('No recommendation_explanations on analyze.debug.science yet.')
       }
       <h3>Formula explanations</h3>
       ${
         formExpl.length
           ? formExpl
               .map(
                 f => `<div class="vc-card">
                   <strong>${esc(f.formula_id || '')}</strong>
                   <div>${esc(f.human || '')}</div>
                   <div class="vc-muted">dev · ${esc((f.developer && f.developer.expression) || '')}</div>
                   <div class="vc-muted">science · ${esc((f.scientific && f.scientific.narrative) || '')}</div>
                 </div>`
               )
               .join('')
           : ntBlock('No formula_explanations')
       }
       <h3>Evidence objects (sample)</h3>${pre((evObjs || []).slice(0, 12))}`
    );

    const s18 = section(
      's18',
      '18 · Versioned Science',
      `<div class="vc-report-grid">
         <div><span class="vc-muted">Algorithm</span><div>${esc(sciVer.algorithm || et.algorithm_version || NT)}</div></div>
         <div><span class="vc-muted">Warehouse</span><div>${esc(sciVer.warehouse || NT)}</div></div>
         <div><span class="vc-muted">Evidence</span><div>${esc(sciVer.evidence || NT)}</div></div>
         <div><span class="vc-muted">Papers</span><div>${esc(sciVer.papers || NT)}</div></div>
         <div><span class="vc-muted">Formula graph</span><div>${esc(sciVer.formula_graph || NT)}</div></div>
         <div><span class="vc-muted">Knowledge graph</span><div>${esc(sciVer.knowledge_graph || NT)}</div></div>
       </div>
       <p class="vc-muted">Clinical outputs remain Algorithm ${esc(et.algorithm_version || '2.1.0')}; science versions are provenance only.</p>`
    );

    main.innerHTML = `<div class="vc-report vc-developer-report">
      <header class="vc-report-hero">
        <p class="vc-report-kicker">Full Assessment Developer Report</p>
        <h1>${esc(petName)}</h1>
        <p class="vc-report-sub">One page · execution order · every emitted value · no secondary tabs</p>
        <p class="vc-muted">Scroll the entire backend run. Gaps marked ${esc(NT)} are honest missing instrumentation — not hidden behind another page.</p>
      </header>
      ${s0}${s1}${s2}${s3}${s4}${s5}${s6}${s7}${s8}${s9}${s10}${s11}${s12}${s13}${s14}${s15}${s16}${s17}${s18}
      <aside class="vc-prov-panel" id="vc-prov-panel" hidden>
        <h3>Value provenance</h3>
        <div id="vc-prov-body"></div>
        <button type="button" class="vc-btn" id="vc-prov-close">Close</button>
      </aside>
    </div>`;

    wireProvenanceClicks(main);
  }

  function renderMain() {
    if (!consoleDoc) return;
    renderDeveloperReport();
  }

  function wireSearch() {
    const input = document.getElementById('vc-search');
    const hits = document.getElementById('vc-search-hits');
    if (!input || !hits) return;
    input.addEventListener('input', () => {
      const q = input.value.trim().toLowerCase();
      if (!q) {
        hits.innerHTML = '';
        return;
      }
      const list = (consoleDoc.search_index || []).filter(h => {
        const label = String(h.label || '').toLowerCase();
        const kind = String(h.kind || '').toLowerCase();
        const purpose = String(h.purpose || '').toLowerCase();
        return label.includes(q) || kind.includes(q) || purpose.includes(q);
      });
      hits.innerHTML = list
        .slice(0, 20)
        .map(
          h =>
            `<a class="vc-toc-link" href="#s4">${esc(h.kind)} · ${esc(h.label)}</a>`
        )
        .join('');
    });
  }


  function wireExport() {
    document.getElementById('vc-export-json').addEventListener('click', () => {
      const blob = new Blob([JSON.stringify(consoleDoc, null, 2)], { type: 'application/json' });
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = `ppie-validation-${activePreset}.json`;
      a.click();
    });
    document.getElementById('vc-export-md').addEventListener('click', async () => {
      const res = await api('/api/v1/ppie/validation-console/markdown?debug=1', {
        method: 'POST',
        body: JSON.stringify(currentBody())
      });
      const text = res.ok ? await res.text() : '# Export failed\n';
      const blob = new Blob([text], { type: 'text/markdown' });
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = `ppie-validation-${activePreset}.md`;
      a.click();
    });
  }

  function fillPresets(list) {
    presets = list && list.length ? list : FALLBACK_PRESETS;
    const sel = document.getElementById('vc-preset');
    sel.innerHTML = presets
      .map(p => `<option value="${esc(p.id)}">${esc(p.label)}</option>`)
      .join('');
    if (!PRESET_BODIES[activePreset]) activePreset = 'mixed_breed';
    sel.value = activePreset;
    sel.addEventListener('change', () => {
      activePreset = sel.value;
      loadConsole();
    });
  }

  function showLoadError(title, detail, raw) {
    const live = document.getElementById('vc-live');
    const meta = document.getElementById('vc-meta');
    const main = document.getElementById('vc-main');
    const app = document.getElementById('vc-app');
    const gate = document.getElementById('vc-gate');
    if (gate) gate.hidden = true;
    if (app) app.hidden = false;
    if (live) live.textContent = 'Failed';
    if (meta) meta.textContent = title;
    if (!main) return;
    main.innerHTML = `<div class="vc-card">
      <h1 class="vc-h1">${esc(title)}</h1>
      <p class="vc-nt">${esc(detail)}</p>
      <p class="vc-muted">The console never stays on Loading without an explanation. Fix the error below, then click Refresh Assessment.</p>
      ${raw != null ? `<details open><summary>Raw response / error</summary>${pre(raw)}</details>` : ''}
      <button type="button" class="vc-btn vc-btn-primary" id="vc-retry-load">Retry</button>
    </div>`;
    const btn = document.getElementById('vc-retry-load');
    if (btn) btn.addEventListener('click', () => loadConsole(true));
  }

  async function loadConsole(force) {
    if (loading && !force) return;
    loading = true;
    const live = document.getElementById('vc-live');
    const meta = document.getElementById('vc-meta');
    const main = document.getElementById('vc-main');
    if (live) live.textContent = 'Running pipeline…';
    if (meta) meta.textContent = 'Loading assessment…';
    if (main && !consoleDoc) {
      main.innerHTML = `<div class="vc-card"><p class="vc-muted">POST /api/v1/ppie/validation-console?debug=1 · preset ${esc(activePreset)}</p><p>Waiting for response…</p></div>`;
    }
    try {
      const res = await api('/api/v1/ppie/validation-console?debug=1', {
        method: 'POST',
        body: JSON.stringify(currentBody())
      });
      const text = await res.text();
      let payload = null;
      try {
        payload = text ? JSON.parse(text) : null;
      } catch (parseErr) {
        showLoadError(
          `HTTP ${res.status} · invalid JSON`,
          parseErr.message || String(parseErr),
          text.slice(0, 4000)
        );
        return;
      }
      if (!res.ok) {
        const detail =
          (payload && (payload.detail || payload.message || payload.error)) ||
          `Validation console request failed with HTTP ${res.status}`;
        showLoadError(`HTTP ${res.status}`, String(detail), payload || text.slice(0, 4000));
        return;
      }
      if (!payload || typeof payload !== 'object') {
        showLoadError('Empty assessment', 'Response parsed but was null/empty. Nothing to render.', payload);
        return;
      }
      if (!payload.schema && !payload.nav && !payload.formula_executions && !payload.engine_trace) {
        showLoadError(
          'Unexpected payload shape',
          'Response OK but missing Validation Console fields (schema/nav/engine_trace). Showing raw body.',
          payload
        );
        return;
      }
      consoleDoc = payload;
      window.__VALIDATION_CONSOLE__ = consoleDoc;
      if (window.__VC_BOOT_WATCHDOG__) {
        clearTimeout(window.__VC_BOOT_WATCHDOG__);
        window.__VC_BOOT_WATCHDOG__ = null;
      }
      if (meta) {
        meta.textContent = `${consoleDoc.schema || 'console'} · ${activePreset} · alg ${consoleDoc.engine_trace?.algorithm_version || '—'}`;
      }
      const hash = (location.hash || '').replace(/^#/, '');
      if (hash && (consoleDoc.nav || []).some(n => n.id === hash)) activeNav = hash;
      else activeNav = 'report';
      try {
        renderNav(consoleDoc.nav);
        renderMain();
      } catch (renderErr) {
        console.error(renderErr);
        showLoadError(
          'Render failed',
          renderErr && renderErr.message ? renderErr.message : String(renderErr),
          {
            schema: consoleDoc.schema,
            nav_count: (consoleDoc.nav || []).length,
            formula_executions: (consoleDoc.formula_executions || []).length,
            stack: renderErr && renderErr.stack
          }
        );
        return;
      }
      const perf = consoleDoc.performance?.timings || {};
      if (live) {
        live.textContent = `Ready · analyze ${perf.analyze ?? '—'} ms · assess ${perf.assessment ?? '—'} ms`;
      }
    } catch (err) {
      console.error(err);
      showLoadError(
        'Network / request error',
        err && err.message ? err.message : String(err),
        { stack: err && err.stack, preset: activePreset }
      );
    } finally {
      loading = false;
    }
  }


  async function pollStatus() {
    try {
      const res = await api('/api/v1/ppie/debug/status?debug=1');
      if (!res.ok) return;
      const st = await res.json();
      if (lastBootId && st.boot_id && st.boot_id !== lastBootId) {
        document.getElementById('vc-live').textContent = 'Server reloaded · refreshing…';
        repoCatalog = null;
        await loadConsole();
      }
      lastBootId = st.boot_id || lastBootId;
    } catch (_) {
      /* ignore */
    }
  }

  async function boot() {
    const gate = document.getElementById('vc-gate');
    const app = document.getElementById('vc-app');
    if (!debugEnabled()) {
      gate.hidden = false;
      return;
    }
    app.hidden = false;

    try {
      const pr = await api('/api/v1/ppie/debug/presets?debug=1');
      if (pr.ok) {
        const data = await pr.json();
        fillPresets(data.presets || []);
        if (data.default) activePreset = data.default;
        document.getElementById('vc-preset').value = activePreset;
      } else {
        fillPresets(FALLBACK_PRESETS);
      }
    } catch (_) {
      fillPresets(FALLBACK_PRESETS);
    }

    document.getElementById('vc-refresh').addEventListener('click', () => loadConsole());
    wireSearch();
    wireExport();
    await loadConsole();
    setInterval(pollStatus, 3000);
  }

  boot().catch(err => {
    console.error(err);
    const gate = document.getElementById('vc-gate');
    const app = document.getElementById('vc-app');
    if (app) app.hidden = false;
    if (gate) gate.hidden = true;
    showLoadError(
      'Boot failed',
      err && err.message ? err.message : String(err),
      { stack: err && err.stack }
    );
  });
})();
