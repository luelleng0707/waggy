/**
 * PPIE Calculation Trace — developer-only audit UI.
 * Renders EngineTrace sections. No clinical math.
 */
(function (global) {
  'use strict';

  const esc = global.CatalogService?.escapeHtml || (s => String(s ?? ''));

  function pre(obj) {
    try {
      return `<pre class="tr-pre">${esc(JSON.stringify(obj, null, 2))}</pre>`;
    } catch (_) {
      return `<pre class="tr-pre">${esc(String(obj))}</pre>`;
    }
  }

  function tabBtn(id, label, active) {
    return `<button type="button" class="tr-tab${active ? ' is-active' : ''}" data-tr-tab="${esc(id)}">${esc(label)}</button>`;
  }

  function sectionPanel(id, title, body) {
    return `<section class="tr-panel" data-tr-panel="${esc(id)}" hidden>
      <h2 class="tr-h2">${esc(title)}</h2>
      ${body}
    </section>`;
  }

  function stageMeta(sec) {
    if (!sec) return `<p class="tr-muted">No section data.</p>`;
    return `<div class="tr-meta">
      <span class="tr-pill">formula · ${esc(sec.formula_id || '—')}</span>
      <span class="tr-pill">alg · ${esc(sec.algorithm_version || '—')}</span>
      ${sec.elapsed_ms != null ? `<span class="tr-pill">${esc(sec.elapsed_ms)} ms</span>` : ''}
      <span class="tr-pill">equations · hidden</span>
    </div>
    ${(sec.csv_sources || []).length ? `<p class="tr-csv"><strong>CSV</strong> · ${(sec.csv_sources || []).map(c => esc(c.table)).join(', ')}</p>` : ''}
    ${(sec.missing || []).length ? `<div class="tr-warn"><strong>Missing / fallback</strong>${pre(sec.missing)}</div>` : ''}
    <h3 class="tr-h3">Inputs</h3>${pre(sec.inputs)}
    <h3 class="tr-h3">Outputs</h3>${pre(sec.outputs)}`;
  }

  function risksBody(sec) {
    const risks = (sec?.outputs?.risks) || [];
    if (!risks.length) return stageMeta(sec);
    return `${stageMeta({ ...sec, outputs: { count: risks.length } })}
      ${risks
        .map(
          r => `<article class="tr-card">
            <h3>${esc(r.condition)} · ${r.outputs?.final_risk_percent != null ? esc(r.outputs.final_risk_percent) + '%' : '—'}</h3>
            <p class="tr-muted">${esc(r.formula_id)}</p>
            <h4>Intermediates (emitted fields only)</h4>${pre(r.intermediates)}
            <h4>Traits</h4>${pre(r.trait_contributions)}
            <h4>Published evidence rows</h4>${pre(r.published_evidence)}
            ${(r.notes || []).map(n => `<p class="tr-note">${esc(n)}</p>`).join('')}
          </article>`
        )
        .join('')}`;
  }

  function timelineBody(trace) {
    const rows = trace.timeline || [];
    return `<ol class="tr-timeline">${rows
      .map(
        r =>
          `<li><strong>${esc(r.stage)}</strong>${r.elapsed_ms != null ? ` · ${esc(r.elapsed_ms)} ms` : ''}${
            r.formula_id ? ` · <code>${esc(r.formula_id)}</code>` : ''
          }</li>`
      )
      .join('')}</ol>
      <h3 class="tr-h3">Consistency</h3>
      ${(trace.consistency_warnings || []).length ? pre(trace.consistency_warnings) : `<p class="tr-ok">No consistency warnings.</p>`}
      <h3 class="tr-h3">Meta</h3>${pre(trace.meta)}`;
  }

  function render(trace) {
    if (!trace || !trace.sections) {
      return `<div class="tr-empty"><p>No EngineTrace loaded.</p>
        <p class="tr-muted">Enable <code>PPIE_DEBUG=true</code> or open with <code>?debug=1</code> and reload assessment.</p></div>`;
    }
    const secs = trace.sections;
    const tabs = [
      ['profile', 'Profile'],
      ['breed', 'Breed'],
      ['traits', 'Traits'],
      ['risks', 'Risks'],
      ['nutrition', 'Nutrition'],
      ['activity', 'Activity'],
      ['grooming', 'Grooming'],
      ['products', 'Products'],
      ['packages', 'Packages'],
      ['evidence', 'Evidence'],
      ['validation', 'Validation'],
      ['runtime', 'Runtime']
    ];
    return `<div class="tr-root">
      <header class="tr-head">
        <p class="tr-kicker">Developer · Calculation Trace</p>
        <h1>EngineTrace</h1>
        <p class="tr-muted">${esc(trace.engine)} · alg ${esc(trace.algorithm_version)} · data ${esc(trace.data_version)} · ${esc(trace.equation_policy)}</p>
        <p class="tr-muted">Formula identifiers only — proprietary equations are never shown.</p>
        <p class="tr-muted"><a href="/debug/calculation?debug=1">Open Validation Console</a> (Explain Why · full audit)</p>
      </header>
      <nav class="tr-tabs">${tabs.map((t, i) => tabBtn(t[0], t[1], i === 0)).join('')}</nav>
      ${sectionPanel('profile', 'Profile', stageMeta(secs.profile))}
      ${sectionPanel('breed', 'Breed resolution', stageMeta(secs.breed))}
      ${sectionPanel('traits', 'Traits', stageMeta(secs.traits))}
      ${sectionPanel('risks', 'Risks', risksBody(secs.risks))}
      ${sectionPanel('nutrition', 'Nutrition', stageMeta(secs.nutrition))}
      ${sectionPanel('activity', 'Activity', stageMeta(secs.activity))}
      ${sectionPanel('grooming', 'Grooming', stageMeta(secs.grooming))}
      ${sectionPanel('products', 'Products', stageMeta(secs.products))}
      ${sectionPanel('packages', 'Packages', stageMeta(secs.packages))}
      ${sectionPanel('evidence', 'Evidence', stageMeta(secs.evidence))}
      ${sectionPanel('validation', 'Validation', stageMeta(secs.validation))}
      ${sectionPanel('runtime', 'Runtime / timeline', timelineBody(trace))}
    </div>`;
  }

  function showTab(root, id) {
    root.querySelectorAll('.tr-tab').forEach(b => b.classList.toggle('is-active', b.getAttribute('data-tr-tab') === id));
    root.querySelectorAll('.tr-panel').forEach(p => {
      p.hidden = p.getAttribute('data-tr-panel') !== id;
    });
  }

  function mount(trace, hostId) {
    const host = document.getElementById(hostId || 'page-module');
    if (!host) return;
    host.innerHTML = render(trace);
    const root = host.querySelector('.tr-root') || host;
    showTab(root, 'profile');
    root.querySelectorAll('[data-tr-tab]').forEach(btn => {
      btn.addEventListener('click', () => showTab(root, btn.getAttribute('data-tr-tab')));
    });
  }

  global.PpieTrace = { mount, render };
})(window);
