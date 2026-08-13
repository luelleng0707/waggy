/**
 * PPIE UI kit — Phase 18 reusable presentation components.
 * No clinical math. Consumes ClinicalAssessment-shaped data only.
 */
(function (global) {
  'use strict';

  const esc = global.CatalogService?.escapeHtml || (s => String(s ?? ''));
  const scrub = t => (global.StandardReportRenderer?.scrub ? global.StandardReportRenderer.scrub(t) : String(t ?? ''));

  function sectionHeader(title, subtitle, opts) {
    const action = opts?.actionHtml || '';
    return `<div class="px-section__head">
      <div>
        <h2 class="px-section__title">${esc(title)}</h2>
        ${subtitle ? `<p class="px-section__sub">${esc(subtitle)}</p>` : ''}
      </div>
      ${action}
    </div>`;
  }

  function statCard(label, value, caption) {
    return `<div class="px-stat">
      <span class="px-stat__label">${esc(label)}</span>
      <strong class="px-stat__value">${esc(value)}</strong>
      ${caption ? `<span class="px-stat__cap">${esc(caption)}</span>` : ''}
    </div>`;
  }

  function progressBar(label, pct, opts) {
    const n = Math.max(0, Math.min(100, Number(pct) || 0));
    const tone = opts?.tone || (n >= 90 ? 'high' : n >= 75 ? 'mid' : 'low');
    return `<div class="px-bar" data-tone="${esc(tone)}">
      <div class="px-bar__row">
        <span class="px-bar__label">${esc(label)}</span>
        <span class="px-bar__pct">${esc(Math.round(n))}%</span>
      </div>
      <div class="px-bar__track" role="progressbar" aria-valuenow="${esc(n)}" aria-valuemin="0" aria-valuemax="100" aria-label="${esc(label)}">
        <div class="px-bar__fill" style="width:${n}%"></div>
      </div>
    </div>`;
  }

  function coverageChart(dimensions, limit) {
    const rows = (dimensions || []).slice(0, limit || 6);
    if (!rows.length) return `<p class="px-muted">Coverage detail is not available for this assessment.</p>`;
    return `<div class="px-coverage">${rows
      .map(d => progressBar(d.title || d.label || 'Target', d.coverage_percent ?? d.coverage_pct ?? d.pct))
      .join('')}</div>`;
  }

  function riskCard(risk, opts) {
    const bench = opts?.benchmark;
    const prob = risk.probability_pct != null ? `${risk.probability_pct}%` : '—';
    const rawExp = String(risk.explanation || '');
    const exp = scrub(rawExp.slice(0, 140)) + (rawExp.length > 140 ? '…' : '');
    return `<button type="button" class="px-risk" data-health-id="${esc(risk.id)}">
      <div class="px-risk__top">
        <strong>${esc(scrub(risk.title))}</strong>
        <span class="px-risk__prob">${esc(prob)}</span>
      </div>
      <p class="px-risk__exp">${esc(exp)}</p>
      <div class="px-risk__meta">
        ${risk.priority_rank ? `<span>Priority ${esc(risk.priority_rank)}</span>` : ''}
        ${
          bench && bench.status === 'compared' && bench.published_benchmark_pct != null
            ? `<span>Published · ${esc(bench.published_benchmark_pct)}%</span>`
            : bench && bench.status === 'unavailable'
              ? `<span class="px-muted">Benchmark pending</span>`
              : ''
        }
      </div>
    </button>`;
  }

  function packageCard(pkg, opts) {
    const products = (pkg.products || []).slice(0, opts?.productLimit || 4);
    const rawSum = String(pkg.summary || '');
    const sum = scrub(rawSum.slice(0, 180)) + (rawSum.length > 180 ? '…' : '');
    return `<article class="px-pkg">
      <p class="px-kicker">${pkg.recommended ? 'Recommended for you' : 'Care pathway'}</p>
      <h3 class="px-pkg__title">${esc(scrub(pkg.title))}</h3>
      <p class="px-pkg__sum">${esc(sum)}</p>
      <div class="px-pkg__metrics">
        ${statCard('Coverage', pkg.coverage_score != null ? pkg.coverage_score + '%' : '—', 'Pathway')}
        ${statCard('Monthly', pkg.monthly_cost != null ? '¥' + Number(pkg.monthly_cost).toLocaleString() : '—', '')}
        ${statCard('Products', String((pkg.products || []).length), 'Included')}
      </div>
      ${
        products.length
          ? `<ul class="px-pkg__products">${products
              .map(p => `<li>${esc(scrub(p.name))}${p.serving ? ` · ${esc(p.serving)}` : ''}</li>`)
              .join('')}</ul>`
          : ''
      }
      <button type="button" class="px-btn px-btn--primary" data-package-page="${esc(pkg.tier)}">Open package</button>
    </article>`;
  }

  function productCard(p, opts) {
    const id = p.product_id || '';
    const catalog = id && global.CatalogService?.get?.(id);
    const name = scrub(p.name || catalog?.product_name || id);
    const rawWhy = scrub(p.why_selected || p.summary || p.serving || '');
    const why = rawWhy.slice(0, 120) + (rawWhy.length > 120 ? '…' : '');
    const img = opts?.showImage && catalog ? global.CatalogService.imageHtml?.(catalog, name) || '' : '';
    return `<button type="button" class="px-product" data-product-page="${esc(id)}">
      ${img ? `<div class="px-product__media">${img}</div>` : ''}
      <div class="px-product__body">
        <strong>${esc(name)}</strong>
        ${p.category ? `<span class="px-kicker">${esc(scrub(String(p.category).replace(/_/g, ' ')))}</span>` : ''}
        ${why ? `<p>${esc(why)}</p>` : ''}
        <div class="px-product__meta">
          ${p.serving ? `<span>${esc(p.serving)}</span>` : ''}
          ${p.monthly_cost != null ? `<span>¥${Number(p.monthly_cost).toLocaleString()}/mo</span>` : ''}
        </div>
      </div>
      <span class="px-product__go" aria-hidden="true">›</span>
    </button>`;
  }

  function evidenceBlock(ev) {
    if (!ev) return '';
    const pending = ev.status === 'pending' || !ev.url;
    return `<article class="px-evidence">
      <p class="px-evidence__quote">${esc(scrub(ev.quoted_finding || ev.title || 'Scientific reference currently being curated.'))}</p>
      <div class="px-evidence__cite">
        <span>${esc(scrub(ev.journal || ev.title || 'Veterinary literature'))}</span>
        ${ev.year ? `<span>${esc(ev.year)}</span>` : ''}
      </div>
      ${
        pending
          ? `<span class="px-muted">Reference being curated</span>`
          : `<a class="px-link" href="${esc(ev.url)}" target="_blank" rel="noopener">View paper</a>`
      }
    </article>`;
  }

  /** Match evidence to a topic using existing supports[] or text overlap — no invented papers. */
  function evidenceForTopic(evidenceItems, topic) {
    const q = String(topic || '')
      .toLowerCase()
      .replace(/[^a-z0-9\s]/g, ' ')
      .trim();
    if (!q) return [];
    const tokens = q.split(/\s+/).filter(t => t.length > 3);
    const items = evidenceItems || [];
    const scored = [];
    for (const ev of items) {
      const supports = (ev.supports || []).map(s => String(s).toLowerCase());
      if (supports.some(s => s.includes(q) || q.includes(s))) {
        scored.push({ ev, score: 3 });
        continue;
      }
      const blob = `${ev.quoted_finding || ''} ${ev.title || ''} ${ev.journal || ''}`.toLowerCase();
      const hits = tokens.filter(t => blob.includes(t)).length;
      if (hits) scored.push({ ev, score: hits });
    }
    scored.sort((a, b) => b.score - a.score);
    return scored.map(s => s.ev);
  }

  function planRow(label, value, actionHtml) {
    return `<div class="px-plan-row">
      <div>
        <span class="px-plan-row__label">${esc(label)}</span>
        <strong class="px-plan-row__value">${esc(value)}</strong>
      </div>
      ${actionHtml || ''}
    </div>`;
  }

  function exploreTile(title, preview, sheetId) {
    return `<button type="button" class="px-explore" data-sheet="${esc(sheetId)}">
      <span class="px-explore__title">${esc(title)}</span>
      <span class="px-explore__preview">${esc(preview || 'Explore')}</span>
      <span class="px-explore__go" aria-hidden="true">›</span>
    </button>`;
  }

  function inlineExpand(title, preview, bodyHtml) {
    return `<details class="px-inline">
      <summary>
        <span>${esc(title)}</span>
        <span class="px-inline__preview">${esc(preview || 'Details')}</span>
      </summary>
      <div class="px-inline__body">${bodyHtml}</div>
    </details>`;
  }

  global.PpieUI = {
    esc,
    scrub,
    sectionHeader,
    statCard,
    progressBar,
    coverageChart,
    riskCard,
    packageCard,
    productCard,
    evidenceBlock,
    evidenceForTopic,
    planRow,
    exploreTile,
    inlineExpand
  };
})(window);
