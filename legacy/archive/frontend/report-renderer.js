/**
 * Standard Report Renderer — clinical presentation layer.
 * Renders backend widgets by type. No business logic.
 * Engineering artifacts (CSV, hashes, traces) hidden unless Developer Mode.
 */
(function (global) {
  'use strict';

  const esc = global.CatalogService?.escapeHtml || (s => String(s ?? ''));
  const PLACEHOLDER = 'Scientific reference currently being curated.';
  const AWAITING_DATA = 'Clinical detail is being prepared for this section.';

  function isDevMode() {
    try {
      if (new URLSearchParams(location.search).get('dev') === '1') return true;
      if (global.localStorage?.getItem('ppie_dev_mode') === '1') return true;
    } catch (_) {
      /* ignore */
    }
    return false;
  }

  /** Strip implementation leaks from any user-facing string. */
  function scrub(text) {
    let t = String(text ?? '');
    if (!t) return '';
    t = t.replace(/\b[\w./-]+\.csv\b/gi, '');
    t = t.replace(/\bmanifest\.ya?ml\b/gi, '');
    t = t.replace(/\b(CSV|DATABASE|HealthInsights|schema_version|csv_hash)\b[:\s]*/gi, '');
    t = t.replace(/\bPPIE\s+selected\b/gi, 'Our analysis selected');
    t = t.replace(/\bPPIE\b/gi, 'Our clinical analysis');
    t = t.replace(/Selected as package staple from[^.]*\./gi, 'Selected as the staple food for this care pathway.');
    t = t.replace(/Clinical function\s*«([^»]+)»\s*supports/gi, 'Supports');
    t = t.replace(/Clinical function\s*«([^»]+)»/gi, '$1');
    t = t.replace(/Computed from[^.]*\./gi, '');
    t = t.replace(/Objective:\s*/gi, '');
    t = t.replace(/Maximize nutrient coverage[^.]*\./gi, 'Prioritized for nutrient coverage with controlled cost.');
    t = t.replace(/Did not improve tier objective[^.]*\./gi, 'Not selected for this pathway after clinical and cost review.');
    t = t.replace(/Alternate staple not chosen[^.]*\./gi, 'An alternate staple was considered and not prioritized for this pathway.');
    t = t.replace(/PRODUCT_[A-Z_]+/g, '');
    t = t.replace(/PACKAGE_TIERS?/gi, '');
    t = t.replace(/\|\s*/g, ' · ');
    t = t.replace(/\s{2,}/g, ' ').replace(/\s+([.,;])/g, '$1').trim();
    return t;
  }

  function scrubEsc(text) {
    return esc(scrub(text));
  }

  function evidenceLabel(level) {
    const l = String(level || '').toLowerCase();
    if (/high|strong|a\b/.test(l)) return 'Strong clinical evidence';
    if (/moderate|medium|b\b/.test(l)) return 'Moderate clinical evidence';
    if (/low|limited|c\b/.test(l)) return 'Emerging clinical evidence';
    if (level) return scrub(level);
    return 'Peer-reviewed veterinary literature';
  }

  function refHtml(ref) {
    if (!ref || ref.status === 'placeholder') {
      return `<div class="rr-evidence rr-evidence--pending"><p>${esc(PLACEHOLDER)}</p></div>`;
    }
    const url = ref.source_url || '';
    const isPm = /pubmed|ncbi\.nlm|pmc\.ncbi/i.test(url);
    const journal = scrub(ref.source_name || ref.journal || ref.label || '');
    const year = ref.year ? String(ref.year) : '';
    const finding = scrub(ref.finding || ref.quote || ref.title || '');
    const strength = evidenceLabel(ref.evidence_level || ref.evidence_strength);
    const doi = ref.doi ? String(ref.doi) : '';

    const open =
      url
        ? `<a class="${isPm ? 'cr5-badge-pubmed' : 'cr5-link'}" href="${esc(url)}" target="_blank" rel="noopener">${isPm ? 'Open PubMed →' : 'Open publication →'}</a>`
        : '';

    return `<article class="rr-evidence">
      ${finding ? `<p class="rr-evidence__finding">${esc(finding)}</p>` : ''}
      <div class="rr-evidence__meta">
        <span>${esc(journal || 'Veterinary literature')}</span>
        ${year ? `<span>${esc(year)}</span>` : ''}
        <span>${esc(strength)}</span>
        ${doi ? `<span>DOI ${esc(doi)}</span>` : ''}
      </div>
      ${open}
      ${isDevMode() && ref.csv_source ? `<p class="rr-dev">Source table · ${esc(ref.csv_source)}</p>` : ''}
    </article>`;
  }

  function refsHtml(refs) {
    if (!refs?.length) {
      return `<div class="rr-evidence rr-evidence--pending"><p>${esc(PLACEHOLDER)}</p></div>`;
    }
    return refs.map(refHtml).join('');
  }

  function bar(value, max) {
    const m = Number(max) || 100;
    const v = Math.max(0, Math.min(m, Number(value) || 0));
    const pct = m ? (v / m) * 100 : 0;
    const tone = pct >= 95 ? 'good' : pct >= 70 ? 'accent' : 'warn';
    return `<div class="cr5-bar"><div class="cr5-bar__fill cr5-bar__fill--${tone}" style="width:${pct}%"></div></div>`;
  }

  function traceHtml(steps) {
    if (!isDevMode() || !steps?.length) return '';
    return `<details class="rr-trace rr-dev"><summary>Developer · calculation trace</summary><ol>${steps
      .map(s => `<li><strong>${scrubEsc(s.label)}</strong> · ${scrubEsc(s.value)}</li>`)
      .join('')}</ol></details>`;
  }

  function clinicalWhy(steps, fallback) {
    if (!steps?.length) {
      return fallback ? `<p class="care-prose">${scrubEsc(fallback)}</p>` : '';
    }
    if (isDevMode()) return traceHtml(steps);
    const readable = steps
      .filter(s => s && s.label && !/\.csv|CSV|hash|schema/i.test(`${s.label} ${s.value}`))
      .slice(0, 4)
      .map(s => `<li>${scrubEsc(s.label)}: ${scrubEsc(s.value)}</li>`)
      .join('');
    if (!readable) return fallback ? `<p class="care-prose">${scrubEsc(fallback)}</p>` : '';
    return `<div class="rr-clinical-why"><p class="rr-clinical-why__label">Clinical reasoning</p><ul>${readable}</ul></div>`;
  }

  const RENDERERS = {
    text(w) {
      return `<div class="rr-widget rr-text">${w.title ? `<h4>${scrubEsc(w.title)}</h4>` : ''}<p class="care-prose">${scrubEsc(w.body || '')}</p>${refsHtml(w.references)}${traceHtml(w.trace)}</div>`;
    },
    metric(w) {
      return `<div class="rr-widget rr-metric"><span class="label">${scrubEsc(w.title || '')}</span><strong>${scrubEsc(w.value)}</strong><p class="cr5-muted">${scrubEsc(w.caption || '')}</p>${refsHtml(w.references)}</div>`;
    },
    metrics(w) {
      return `<div class="rr-metrics">${(w.items || [])
        .map(i => `<div class="rr-metric"><span class="label">${scrubEsc(i.label)}</span><strong>${scrubEsc(i.value)}</strong>${i.caption ? `<small>${scrubEsc(i.caption)}</small>` : ''}</div>`)
        .join('')}</div>`;
    },
    chips(w) {
      return `<div class="rr-widget">${w.title ? `<h4 class="cr5-panel__label">${scrubEsc(w.title)}</h4>` : ''}<div class="cr5-chips">${(w.items || [])
        .map(i => `<div class="cr5-chip cr5-chip--${esc(i.tone || 'green')}"><span class="cr5-chip__dot"></span>${scrubEsc(i.label)}</div>`)
        .join('')}</div></div>`;
    },
    list(w) {
      return `<div class="rr-widget">${w.title ? `<h4 class="cr5-panel__label">${scrubEsc(w.title)}</h4>` : ''}<ul class="cr5-bullets">${(w.items || [])
        .map(i => {
          const label = typeof i === 'string' ? i : i.label;
          const mark = typeof i === 'string' ? '•' : i.mark || '•';
          return `<li><span class="cr5-mark">${esc(mark)}</span>${scrubEsc(label)}</li>`;
        })
        .join('')}</ul></div>`;
    },
    accordion(w) {
      return `<details class="cr5-acc">
        <summary class="cr5-acc__sum"><span class="cr5-acc__cat">${scrubEsc(w.subtitle || 'Detail')}</span><span class="cr5-acc__val">${scrubEsc(w.title)}</span></summary>
        <div class="cr5-acc__body"><p>${scrubEsc(w.body || '')}</p>
        ${w.items?.length ? `<ul class="cr5-bullets">${w.items.map(i => `<li><span class="cr5-mark">${esc(i.mark || '•')}</span>${scrubEsc(i.label)}</li>`).join('')}</ul>` : ''}
        ${refsHtml(w.references)}${traceHtml(w.trace)}</div>
      </details>`;
    },
    progress(w) {
      return `<div class="rr-widget rr-progress">
        <div class="care-cov__label"><strong>${scrubEsc(w.title)}</strong><span>${scrubEsc(w.display || `${w.value}%`)}</span></div>
        ${bar(w.value, w.max || 100)}
        ${w.caption ? `<p class="cr5-muted">${scrubEsc(w.caption)}</p>` : ''}
        ${refsHtml(w.references)}${traceHtml(w.trace)}
      </div>`;
    },
    timeline(w) {
      return `<div class="rr-widget"><h4 class="cr5-panel__label">${scrubEsc(w.title || 'Timeline')}</h4>${(w.stages || [])
        .map(
          s => `<div class="rr-stage${s.current ? ' is-current' : ''}"><strong>${scrubEsc(s.stage)}</strong>${(s.entries || [])
            .map(e => `<div class="rr-stage__entry"><p><strong>${scrubEsc(e.title)}</strong></p><p class="cr5-muted">${scrubEsc(e.caption || '')}</p></div>`)
            .join('')}</div>`
        )
        .join('')}</div>`;
    },
    comparison(w) {
      const tag = w.status === 'rejected' ? 'Not prioritized' : scrub(w.status || 'Alternative');
      return `<article class="care-alt${w.status === 'rejected' ? ' care-alt--reject' : ''}">
        <div class="care-alt__tag">${esc(tag)}</div>
        <h4>${scrubEsc(w.title)}</h4><p>${scrubEsc(w.body || '')}</p>${refsHtml(w.references)}
      </article>`;
    },
    warning(w) {
      return `<div class="rr-widget rr-warning"><strong>${scrubEsc(w.title || 'Notice')}</strong><p>${scrubEsc(w.body || AWAITING_DATA)}</p></div>`;
    },
    trait(w) {
      const list = (items, mark) =>
        items?.length
          ? `<ul class="cr5-bullets">${items
              .map(b => `<li><span class="cr5-mark">${esc(mark)}</span>${scrubEsc(b.title || b)}</li>`)
              .join('')}</ul>`
          : '';
      return `<details class="cr5-acc">
        <summary class="cr5-acc__sum"><span class="cr5-acc__cat">${scrubEsc(w.category || 'Trait')}</span><span class="cr5-acc__val">${scrubEsc(w.title)}</span></summary>
        <div class="cr5-acc__body">
          <p>${scrubEsc(w.summary || AWAITING_DATA)}</p>
          ${w.benefits?.length ? `<h5>Advantages</h5>${list(w.benefits, '✓')}` : ''}
          ${w.risks?.length ? `<h5>Potential challenges</h5>${list(w.risks, '!')}` : ''}
          ${w.shanghai_context?.length ? `<h5>Shanghai context</h5><ul class="cr5-bullets">${w.shanghai_context.map(s => `<li><span class="cr5-mark">◇</span>${scrubEsc(s)}</li>`).join('')}</ul>` : ''}
          ${w.management?.length ? `<h5>Management</h5><ul class="cr5-bullets">${w.management.map(s => `<li><span class="cr5-mark">→</span>${scrubEsc(s)}</li>`).join('')}</ul>` : ''}
          ${w.related_conditions?.length ? `<div class="cr5-chips">${w.related_conditions.map(c => `<div class="cr5-chip"><span class="cr5-chip__dot"></span>${scrubEsc(c)}</div>`).join('')}</div>` : ''}
          ${isDevMode() && w.csv_sources?.length ? `<p class="rr-dev">Source tables · ${esc(w.csv_sources.join(' · '))}</p>` : ''}
          ${refsHtml(w.references)}${traceHtml(w.trace)}
        </div>
      </details>`;
    },
    risk(w) {
      const bullets = (arr, mark) =>
        arr?.length
          ? `<ul class="cr5-bullets">${arr.map(x => `<li><span class="cr5-mark">${esc(mark)}</span>${scrubEsc(x)}</li>`).join('')}</ul>`
          : '';
      return `<article class="cr5-risk">
        <div class="cr5-risk__head"><h4>${scrubEsc(w.title)}</h4><span class="cr5-risk__pct">${w.probability != null ? `${esc(w.probability)}%` : '—'}</span></div>
        ${w.probability != null ? bar(w.probability, 100) : ''}
        <p class="cr5-lead">${scrubEsc(w.summary || AWAITING_DATA)}</p>
        ${w.finding ? `<p><strong>Finding</strong> · ${scrubEsc(w.finding)}</p>` : ''}
        ${w.contributing_traits?.length ? `<p class="cr5-muted">Breed traits · ${scrubEsc(w.contributing_traits.join(', '))}</p>` : ''}
        ${w.contributing_conditions?.length ? `<p class="cr5-muted">Related conditions · ${scrubEsc(w.contributing_conditions.join(', '))}</p>` : ''}
        ${w.contributing_environment?.length ? `<p class="cr5-muted">Environment · ${scrubEsc(w.contributing_environment.join(', '))}</p>` : ''}
        ${w.prevention?.length ? `<h5>Prevention</h5>${bullets(w.prevention, '→')}` : ''}
        ${w.early_warnings?.length ? `<h5>Early signs</h5>${bullets(w.early_warnings, '!')}` : ''}
        ${w.relevant_nutrients?.length ? `<h5>Nutrients</h5>${bullets(w.relevant_nutrients, '◆')}` : ''}
        ${w.relevant_activities?.length ? `<h5>Activities</h5>${bullets(w.relevant_activities, '◇')}` : ''}
        ${w.relevant_products?.length ? `<h5>Products</h5>${bullets(w.relevant_products, '●')}` : ''}
        ${clinicalWhy(w.trace, w.finding)}
        ${refsHtml(w.references)}
      </article>`;
    },
    activity(w) {
      return `<div class="rr-widget care-panel">
        <div class="care-schedule">
          <div class="care-schedule__block"><h5>Morning</h5><ul><li>Walk · ${esc(w.morning_min)} min</li></ul></div>
          <div class="care-schedule__block"><h5>Evening</h5><ul><li>Walk · ${esc(w.evening_min)} min</li></ul></div>
          <div class="care-schedule__block"><h5>Daily</h5><ul><li>${esc(w.daily_km)} km</li></ul></div>
          <div class="care-schedule__block"><h5>Weekly</h5><ul><li>${esc(w.weekly_km)} km</li><li>Swim · ${esc(w.swimming || '—')}</li><li>Fetch · ${esc(w.fetch || '—')}</li><li>Training · ${esc(w.training || '—')}</li></ul></div>
        </div>
        <p class="cr5-muted">${scrubEsc(w.recovery || w.mental || '')}</p>
        ${refsHtml(w.references)}${traceHtml(w.trace)}
      </div>`;
    },
    ledger(w) {
      return `<div class="rr-widget"><h4 class="cr5-panel__label">${scrubEsc(w.title || 'Annual plan')}</h4>
        <div class="cr5-table-wrap"><table class="cr5-table"><thead><tr>${(w.columns || []).map(c => `<th>${scrubEsc(c)}</th>`).join('')}</tr></thead>
        <tbody>${(w.rows || []).map(r => `<tr>${r.map(c => `<td>${scrubEsc(c)}</td>`).join('')}</tr>`).join('')}</tbody></table></div></div>`;
    },
    evidence(w) {
      return `<article class="care-paper">
        <h5>${scrubEsc(w.title)}</h5>
        <p class="care-paper__quote">${scrubEsc(w.body || '')}</p>
        ${refsHtml(w.references)}
      </article>`;
    },
    package(w) {
      return `<button type="button" class="care-entry" data-package-id="${esc(w.id)}">
        <div class="care-entry__top"><div><p class="cr5-kicker">${w.recommended ? 'Clinically prioritized' : 'Care pathway'}</p><h3>${scrubEsc(w.title)}</h3></div><span class="care-entry__arrow">›</span></div>
        <p class="care-prose">${scrubEsc(w.summary || '')}</p>
        <div class="care-entry__meta">
          <span>¥${Number(w.monthly_cost || 0).toLocaleString()}/mo</span>
          <span>${(w.products || []).length} products</span>
          ${w.coverage_score != null ? `<span>${esc(w.coverage_score)}% coverage</span>` : ''}
        </div>
        <span class="care-entry__cta">Review recommendation →</span>
      </button>`;
    },
    product(w) {
      return `<article class="care-product-card">
        <p class="care-product-card__role">${scrubEsc(w.subtitle || 'Product')}</p>
        <h4>${scrubEsc(w.title)}</h4>
        <p class="care-prose">${scrubEsc(w.summary || '')}</p>
        ${w.coverage != null ? `<div class="rr-progress"><div class="care-cov__label"><span>Coverage contribution</span><strong>${esc(w.coverage)}%</strong></div>${bar(w.coverage, 100)}</div>` : ''}
        <div class="care-product-card__footer"><span>${scrubEsc(w.serving || '')}</span><span>${w.monthly_cost != null ? `¥${Number(w.monthly_cost).toLocaleString()}` : ''}</span></div>
        ${w.route ? `<button type="button" class="care-btn" data-product-id="${esc(w.product_id)}">Review product →</button>` : ''}
        ${traceHtml(w.trace)}
      </article>`;
    },
    chart(w) {
      return RENDERERS.progress(w);
    },
    nav(w) {
      return `<nav class="care-toc">${(w.items || []).map(i => `<a href="#${esc(i.id)}">${scrubEsc(i.label)}</a>`).join('')}</nav>`;
    },
    trace(w) {
      return clinicalWhy(w.steps || w.trace);
    }
  };

  function renderWidget(w) {
    if (!w || !w.type) return '';
    const fn = RENDERERS[w.type];
    return fn ? fn(w) : '';
  }

  function renderSection(section) {
    const score = section.score
      ? `<div class="rr-section-score"><strong>${esc(section.score.value)}${esc(section.score.unit || '')}</strong><span>${scrubEsc(section.score.label || '')}</span></div>`
      : '';
    return `<section class="cr5-chapter rr-section" id="rr-${esc(section.id)}">
      <h3 class="cr5-chapter__title">${scrubEsc(section.title)}</h3>
      ${score}
      ${section.summary ? `<p class="cr5-lead">${scrubEsc(section.summary)}</p>` : ''}
      <div class="cr5-chapter__body rr-widgets">${(section.widgets || []).map(renderWidget).join('')}</div>
      ${section.references?.length ? `<div class="rr-section-refs">${refsHtml(section.references)}</div>` : ''}
    </section>`;
  }

  function renderNav(report) {
    const items = report.navigation || (report.sections || []).map(s => ({ id: `rr-${s.id}`, label: s.title }));
    return `<nav class="cr5-nav" aria-label="Report sections">${items
      .map(n => {
        const href = n.id.startsWith('rr-') ? n.id : `rr-${n.id}`;
        return `<a class="cr5-nav__link" href="#${esc(href)}">${scrubEsc(n.label)}</a>`;
      })
      .join('')}</nav>`;
  }

  function renderReport(report, rootEl) {
    const root = typeof rootEl === 'string' ? document.getElementById(rootEl) : rootEl;
    if (!root || !report) return;
    const meta = isDevMode()
      ? `<p class="rr-dev rr-meta">schema ${esc(report.schema_version)} · data ${esc(report.data_version)} · hash ${esc(String(report.csv_hash || '').slice(0, 12))}</p>`
      : '';
    root.innerHTML = `<div class="clinical-report-v5 rr-report">
      ${renderNav(report)}
      <div class="cr5-report">${meta}${(report.sections || []).map(renderSection).join('')}</div>
    </div>`;
    wireNav(root);
    wireRoutes(root, report);
  }

  function renderNestedReport(report, shellBody, { onBack } = {}) {
    if (!shellBody || !report) return;
    const hero = report.hero || {};
    shellBody.innerHTML = `
      <header class="care-hero">
        <button type="button" class="care-back" data-rr-back>← Back</button>
        <p class="cr5-kicker">${scrubEsc(hero.kicker || 'Clinical detail')}</p>
        <h1>${scrubEsc(hero.title || 'Detail')}</h1>
        <p class="care-hero__sub">${scrubEsc(hero.subtitle || '')}</p>
        ${
          hero.calculated_from
            ? `<p class="care-hero__calc">Assessed from · ${scrubEsc((hero.calculated_from || []).join(' · '))}</p>`
            : ''
        }
        ${hero.metrics ? `<div class="care-hero__meta">${hero.metrics.map(m => `<div><span>${scrubEsc(m.label)}</span><strong>${scrubEsc(m.value)}</strong>${m.caption ? `<small>${scrubEsc(m.caption)}</small>` : ''}</div>`).join('')}</div>` : ''}
      </header>
      <div class="care-sections">${(report.sections || []).map(renderSection).join('')}</div>`;
    shellBody.querySelector('[data-rr-back]')?.addEventListener('click', () => onBack && onBack());
    wireRoutes(shellBody, report);
  }

  function wireNav(root) {
    const nav = root.querySelector('.cr5-nav');
    if (!nav) return;
    const observer = new IntersectionObserver(
      entries => {
        entries.forEach(entry => {
          if (!entry.isIntersecting) return;
          nav.querySelectorAll('.cr5-nav__link').forEach(link => {
            link.classList.toggle('is-active', link.getAttribute('href') === `#${entry.target.id}`);
          });
        });
      },
      { rootMargin: '-15% 0px -70% 0px', threshold: 0 }
    );
    root.querySelectorAll('.rr-section').forEach(el => observer.observe(el));
  }

  function ensureOverlay(id) {
    let el = document.getElementById(id);
    if (el) return el;
    el = document.createElement('div');
    el.id = id;
    el.className = 'care-page';
    el.hidden = true;
    el.innerHTML = `<div class="care-page__scroll" id="${id}-body"></div>`;
    document.body.appendChild(el);
    return el;
  }

  function openPackage(report, tier) {
    if (global.PpieSheets) {
      global.PpieSheets.setContext({ report, analyze: global.__PPIE_LAST__ });
      global.PpieSheets.openPackage(tier);
      return;
    }
    const nested = (report.package_reports || {})[tier];
    if (!nested) return;
    const shell = ensureOverlay('care-page');
    const body = document.getElementById('care-page-body');
    document.body.classList.add('care-page-open');
    shell.hidden = false;
    renderNestedReport(nested, body, {
      onBack: () => {
        shell.hidden = true;
        document.body.classList.remove('care-page-open');
      }
    });
  }

  function openProduct(report, productId) {
    if (global.PpieSheets) {
      global.PpieSheets.setContext({ report, analyze: global.__PPIE_LAST__ });
      global.PpieSheets.openProduct(productId);
      return;
    }
    const nested = (report.product_reports || {})[productId];
    const shell = ensureOverlay('product-analysis-page');
    const body = document.getElementById('product-analysis-page-body');
    shell.hidden = false;
    if (!nested) {
      body.innerHTML = `<header class="care-hero"><button type="button" class="care-back" data-rr-back>← Back</button><h1>${esc(productId)}</h1><p class="care-prose">${PLACEHOLDER}</p></header>`;
      body.querySelector('[data-rr-back]')?.addEventListener('click', () => {
        shell.hidden = true;
      });
      return;
    }
    renderNestedReport(nested, body, {
      onBack: () => {
        shell.hidden = true;
      }
    });
  }

  function wireRoutes(root, report) {
    root.querySelectorAll('[data-report-route], [data-package-id], [data-product-id]').forEach(el => {
      if (el.dataset.rrBound) return;
      el.dataset.rrBound = '1';
      el.addEventListener('click', e => {
        const route = el.getAttribute('data-report-route') || el.getAttribute('href') || '';
        const pkg = el.getAttribute('data-package-id');
        const prod = el.getAttribute('data-product-id');
        if (pkg || /#\/(care|packages)\//.test(route)) {
          e.preventDefault();
          e.stopPropagation();
          const tier = pkg || route.split('/').pop();
          openPackage(report, tier);
        } else if (prod || /#\/products?\//.test(route)) {
          e.preventDefault();
          e.stopPropagation();
          const id = prod || decodeURIComponent(route.split('/').pop());
          openProduct(report, id);
        }
      });
    });
  }

  function mount(report, rootId) {
    renderReport(report, rootId || 'wellness-insights-root');
  }

  function bindRoutes(report, rootEl) {
    const root = rootEl
      ? typeof rootEl === 'string'
        ? document.getElementById(rootEl) || document.body
        : rootEl
      : document.body;
    wireRoutes(root, report);
  }

  global.StandardReportRenderer = {
    mount,
    renderReport,
    renderWidget,
    bindRoutes,
    openPackage,
    openProduct,
    scrub,
    isDevMode
  };
})(window);
