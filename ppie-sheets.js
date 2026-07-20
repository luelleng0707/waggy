/**
 * PPIE Sheets — embedded Wagtopia module chrome.
 * Stacked bottom sheets / drawers. Presentation only.
 */
(function (global) {
  'use strict';

  const esc = global.CatalogService?.escapeHtml || (s => String(s ?? ''));
  const RR = () => global.StandardReportRenderer;
  const AWAITING = 'Clinical detail is being prepared for this section.';
  const PENDING_REF = 'Scientific reference currently being curated.';
  const scrub = t => (global.StandardReportRenderer?.scrub ? global.StandardReportRenderer.scrub(t) : String(t ?? ''));
  const scrubEsc = t => esc(scrub(t));

  let host = null;
  let stack = [];
  let savedScroll = 0;
  let scrollEl = null;
  let report = null;
  let analyze = null;

  function ensureHost() {
    if (host) return host;
    const app = document.querySelector('.phone-app') || document.body;
    host = document.getElementById('ppie-sheet-host');
    if (!host) {
      host = document.createElement('div');
      host.id = 'ppie-sheet-host';
      host.className = 'ppie-sheet-host';
      host.setAttribute('aria-live', 'polite');
      app.appendChild(host);
    }
    scrollEl = document.getElementById('shell-main');
    return host;
  }

  function renderWidgets(widgets) {
    const render = RR()?.renderWidget;
    if (!render || !widgets?.length) return `<p class="shell-muted">${AWAITING}</p>`;
    return widgets.map(w => render(w)).join('');
  }

  function exclusiveAccordions(root) {
    root.querySelectorAll('details.sheet-acc').forEach(d => {
      d.addEventListener('toggle', () => {
        if (!d.open) return;
        root.querySelectorAll('details.sheet-acc').forEach(other => {
          if (other !== d) other.open = false;
        });
      });
    });
  }

  function accordion(title, bodyHtml, open) {
    if (!bodyHtml) return '';
    return `<details class="sheet-acc"${open ? ' open' : ''}>
      <summary class="sheet-acc__sum"><span>${esc(title)}</span><span class="sheet-acc__chev" aria-hidden="true"></span></summary>
      <div class="sheet-acc__body">${bodyHtml}</div>
    </details>`;
  }

  function bullets(items, mark) {
    if (!items?.length) return '';
    return `<ul class="cr5-bullets">${items
      .map(x => {
        const label = typeof x === 'string' ? x : x.label || x.title || x.name || '';
        return `<li><span class="cr5-mark">${esc(mark || '•')}</span>${esc(label)}</li>`;
      })
      .join('')}</ul>`;
  }

  function productRow(p) {
    const id = p.product_id || p.id || '';
    const name = scrub(p.name || p.product_name || p.title || id);
    const meta = [p.serving_size || p.daily_amount || p.serving, p.monthly_cost != null ? `¥${Number(p.monthly_cost).toLocaleString()}` : '']
      .filter(Boolean)
      .join(' · ');
    return `<button type="button" class="sheet-row" data-sheet-product="${esc(id)}">
      <div>
        <strong>${esc(name)}</strong>
        ${meta ? `<span class="sheet-row__meta">${esc(meta)}</span>` : ''}
        ${p.why_selected ? `<span class="sheet-row__why">${scrubEsc(String(p.why_selected).slice(0, 140))}</span>` : ''}
      </div>
      <span class="sheet-row__go" aria-hidden="true">›</span>
    </button>`;
  }

  function packageSheetHtml(tier) {
    const nested = (report?.package_reports || {})[tier];
    const pkg =
      (analyze?.wellnessPackages || []).find(p => String(p.tier || p.package_id) === String(tier)) ||
      null;
    const hero = nested?.hero || {};
    const title = hero.title || pkg?.title || tier;
    const coverage = pkg?.coverage_score ?? hero.metrics?.find?.(m => /cover/i.test(m.label || ''))?.value;
    const monthly = pkg?.monthly_cost;
    const yearly = pkg?.yearly_cost;
    const products = pkg?.products_included || [];

    const sections = nested?.sections || [];
    const byTitle = key => sections.find(s => new RegExp(key, 'i').test(s.title || s.id || ''));

    const why = byTitle('why|overview|rationale|selected');
    const coverageSec = byTitle('cover|nutrient');
    const contrib = byTitle('product|contribution');
    const cost = byTitle('cost');
    const science = byTitle('science|evidence|research');
    const schedule = byTitle('365|feeding|schedule|annual|plan');

    return `
      <div class="sheet-hero">
        <p class="shell-kicker">${pkg?.recommended ? 'Clinically prioritized' : 'Care pathway'}</p>
        <h2>${scrubEsc(title)}</h2>
        <div class="sheet-hero__stats">
          <div><span>Coverage</span><strong>${coverage != null ? esc(coverage) + '%' : '—'}</strong></div>
          <div><span>Monthly</span><strong>${monthly != null ? '¥' + Number(monthly).toLocaleString() : '—'}</strong></div>
          <div><span>Yearly</span><strong>${yearly != null ? '¥' + Number(yearly).toLocaleString() : '—'}</strong></div>
        </div>
        ${pkg?.package_summary || hero.subtitle ? `<p class="sheet-hero__sum">${scrubEsc((pkg?.package_summary || hero.subtitle || '').slice(0, 220))}</p>` : ''}
      </div>
      ${accordion('Products included', products.length ? products.map(productRow).join('') : AWAITING)}
      ${accordion('Why this pathway?', why ? renderWidgets(why.widgets) : scrubEsc(pkg?.package_summary || AWAITING))}
      ${accordion('Nutrient coverage', coverageSec ? renderWidgets(coverageSec.widgets) : AWAITING)}
      ${accordion('Product contributions', contrib ? renderWidgets(contrib.widgets) : products.map(p => `<p class="care-prose"><strong>${scrubEsc(p.name || p.product_name)}</strong> — ${scrubEsc(p.why_selected || AWAITING)}</p>`).join(''))}
      ${accordion('Cost breakdown', cost ? renderWidgets(cost.widgets) : `<p class="care-prose">¥${Number(monthly || 0).toLocaleString()}/mo · ¥${Number(yearly || 0).toLocaleString()}/yr</p>`)}
      ${accordion('Scientific rationale', science ? renderWidgets(science.widgets) : AWAITING)}
      ${accordion('365-day feeding plan', schedule ? renderWidgets(schedule.widgets) : renderAnnualForTier(tier))}
    `;
  }

  function renderAnnualForTier(tier) {
    const annual = global.__REPORT_MODELS__?.annual_plan;
    const widgets = (annual?.widgets || []).filter(w =>
      new RegExp(tier, 'i').test(String(w.title || ''))
    );
    return widgets.length ? renderWidgets(widgets) : AWAITING;
  }

  function productSheetHtml(productId) {
    const nested = (report?.product_reports || {})[productId];
    const catalog = global.CatalogService?.get?.(productId);
    const hero = nested?.hero || {};
    const title = hero.title || catalog?.product_name || catalog?.name || productId;
    const img = catalog ? global.CatalogService.imageHtml?.(catalog, title) || '' : '';
    const sections = nested?.sections || [];

    let ingredientsHtml = '';
    const ingSec = sections.find(s => /ingredient/i.test(s.title || s.id || ''));
    if (ingSec) {
      ingredientsHtml = renderWidgets(ingSec.widgets);
    } else if (catalog?.ingredients || catalog?.active_ingredients) {
      const list = catalog.ingredients || catalog.active_ingredients || [];
      ingredientsHtml = list
        .map(i => {
          const name = typeof i === 'string' ? i : i.name || i.ingredient || '';
          return `<button type="button" class="sheet-row" data-sheet-ingredient="${esc(name)}"><strong>${esc(name)}</strong><span class="sheet-row__go">›</span></button>`;
        })
        .join('');
    }

    const used = new Set();
    const pick = re => {
      const s = sections.find(x => re.test(x.title || x.id || ''));
      if (s) used.add(s);
      return s;
    };
    const overview = pick(/overview|summary|purpose|clinical/i);
    const nutrition = pick(/nutrition|analysis|guaranteed/i);
    const functions = pick(/function|benefit/i);
    const evidence = pick(/evidence|research|science/i);
    const feeding = pick(/feeding|dose|guide/i);
    const why = pick(/why|recommend/i);

    return `
      <div class="sheet-hero sheet-hero--product">
        ${img || ''}
        <p class="shell-kicker">${esc(catalog?.category || hero.kicker || 'Product')}</p>
        <h2>${esc(title)}</h2>
        <p class="sheet-hero__sum">${esc(hero.subtitle || catalog?.short_description || catalog?.description || '')}</p>
        ${
          catalog
            ? `<p class="sheet-hero__price">${esc(global.CatalogService.formatPrice?.(catalog) || '')}</p>`
            : ''
        }
      </div>
      ${accordion('Overview', overview ? renderWidgets(overview.widgets) : esc(hero.subtitle || AWAITING), true)}
      ${accordion('Ingredients', ingredientsHtml || AWAITING)}
      ${accordion('Nutrition / analysis', nutrition ? renderWidgets(nutrition.widgets) : AWAITING)}
      ${accordion('Clinical functions', functions ? renderWidgets(functions.widgets) : AWAITING)}
      ${accordion('Why recommended', why ? renderWidgets(why.widgets) : AWAITING)}
      ${accordion('Research', evidence ? renderWidgets(evidence.widgets) : AWAITING)}
      ${accordion('Feeding guide', feeding ? renderWidgets(feeding.widgets) : esc(global.CatalogService?.feedingDisplay?.(catalog) || AWAITING))}
      ${sections
        .filter(s => !used.has(s))
        .map(s => accordion(s.title || s.id, renderWidgets(s.widgets)))
        .join('')}
    `;
  }

  function riskSheetHtml(risk) {
    const w = typeof risk === 'string' ? findRisk(risk) : risk;
    if (!w) return `<p class="shell-muted">${AWAITING}</p>`;
    return `
      <div class="sheet-hero">
        <p class="shell-kicker">Health risk</p>
        <h2>${esc(w.title)}</h2>
        <div class="sheet-hero__stats">
          <div><span>Probability</span><strong>${w.probability != null ? esc(w.probability) + '%' : '—'}</strong></div>
        </div>
        <p class="sheet-hero__sum">${scrubEsc(w.summary || w.finding || '')}</p>
      </div>
      ${accordion('Overview', `<p class="care-prose">${scrubEsc(w.summary || AWAITING)}</p>${w.finding ? `<p class="care-prose"><strong>Finding</strong> · ${scrubEsc(w.finding)}</p>` : ''}`, true)}
      ${accordion('Why?', RR()?.renderWidget ? traceOrText(w) : scrubEsc(w.finding || AWAITING))}
      ${accordion('Contributing traits', bullets(w.contributing_traits, '◇') || AWAITING)}
      ${accordion('Contributing environment', bullets(w.contributing_environment, '◇') || AWAITING)}
      ${accordion('Early signs', bullets(w.early_warnings, '!') || AWAITING)}
      ${accordion('Prevention', bullets(w.prevention, '→') || AWAITING)}
      ${accordion(
        'Related nutrients',
        (w.relevant_nutrients || [])
          .map(
            n =>
              `<button type="button" class="sheet-row" data-sheet-ingredient="${esc(n)}"><strong>${esc(n)}</strong><span class="sheet-row__go">›</span></button>`
          )
          .join('') || AWAITING
      )}
      ${accordion(
        'Related products',
        (w.relevant_products || [])
          .map(p => {
            const id = typeof p === 'string' ? p : p.product_id || p;
            const name = typeof p === 'string' ? p : p.name || p.product_id || id;
            return `<button type="button" class="sheet-row" data-sheet-product="${esc(id)}"><strong>${esc(name)}</strong><span class="sheet-row__go">›</span></button>`;
          })
          .join('') || AWAITING
      )}
      ${accordion('Evidence', refsBlock(w.references))}
    `;
  }

  function refsBlock(refs) {
    if (!refs?.length) return `<p class="shell-muted">${PENDING_REF}</p>`;
    return refs
      .map(r => {
        if (r.status === 'placeholder' || !r.source_url) {
          return `<p class="shell-muted">${esc(PENDING_REF)}</p>`;
        }
        const journal = scrub(r.source_name || r.label || 'Veterinary literature');
        const year = r.year ? ` · ${r.year}` : '';
        return `<a class="shell-link" href="${esc(r.source_url)}" target="_blank" rel="noopener">${esc(journal)}${esc(year)} — Open publication →</a>`;
      })
      .join('');
  }

  function traceOrText(w) {
    const steps = w.trace || [];
    if (global.StandardReportRenderer?.isDevMode?.() && steps.length) {
      return `<ol class="sheet-trace">${steps.map(s => `<li><strong>${scrubEsc(s.label)}</strong> · ${scrubEsc(s.value)}</li>`).join('')}</ol>`;
    }
    const readable = steps
      .filter(s => s && !/\.csv|CSV|hash|schema/i.test(`${s.label} ${s.value}`))
      .slice(0, 4);
    if (readable.length) {
      return `<div class="rr-clinical-why"><p class="rr-clinical-why__label">Clinical reasoning</p><ul>${readable
        .map(s => `<li>${scrubEsc(s.label)}: ${scrubEsc(s.value)}</li>`)
        .join('')}</ul></div>`;
    }
    return `<p class="care-prose">${scrubEsc(w.finding || w.summary || AWAITING)}</p>`;
  }

  function findRisk(titleOrId) {
    const risks = (report?.sections || []).find(s => s.id === 'risk_analysis')?.widgets || [];
    return risks.find(
      w =>
        w.type === 'risk' &&
        (w.title === titleOrId || w.id === titleOrId || String(w.title).toLowerCase() === String(titleOrId).toLowerCase())
    );
  }

  function breedSheetHtml() {
    const breed = (report?.sections || []).find(s => s.id === 'breed_analysis');
    const traits = (report?.sections || []).find(s => s.id === 'trait_analysis');
    const env = (report?.sections || []).find(s => s.id === 'environment_analysis');
    const name = analyze?.profile?.pet_name || analyze?.profile?.name || 'Your dog';
    return `
      <div class="sheet-hero">
        <p class="shell-kicker">Breed profile</p>
        <h2>${esc(name)}</h2>
        <p class="sheet-hero__sum">${esc(breed?.summary || '')}</p>
      </div>
      ${accordion('Overview', renderWidgets(breed?.widgets), true)}
      ${accordion('Trait breakdown', renderWidgets(traits?.widgets))}
      ${accordion('Shanghai adaptation', renderWidgets(env?.widgets))}
      ${accordion('Scientific evidence', refsBlock(breed?.references))}
    `;
  }

  function ingredientSheetHtml(name) {
    const risks = ((report?.sections || []).find(s => s.id === 'risk_analysis')?.widgets || []).filter(
      w => w.type === 'risk' && (w.relevant_nutrients || []).some(n => String(n).toLowerCase() === String(name).toLowerCase())
    );
    const products = [];
    for (const pkg of analyze?.wellnessPackages || []) {
      for (const p of pkg.products_included || []) {
        const hay = `${p.name || ''} ${p.why_selected || ''} ${(p.active_ingredients || []).join(' ')}`;
        if (new RegExp(name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'i').test(hay)) {
          products.push(p);
        }
      }
    }
    const nut = ((report?.sections || []).find(s => s.id === 'nutrition_analysis')?.widgets || []).find(
      w => /ingredient|nutrient|target/i.test(w.type || '') && new RegExp(name, 'i').test(w.title || w.body || '')
    );
    return `
      <div class="sheet-hero">
        <p class="shell-kicker">Ingredient</p>
        <h2>${esc(name)}</h2>
        <p class="sheet-hero__sum">Clinical role and linked products from this report.</p>
      </div>
      ${accordion('Clinical role', nut ? RR()?.renderWidget(nut) : `<p class="care-prose">${esc(name)} appears in this dog’s care pathway.</p>`, true)}
      ${accordion(
        'Related risks',
        risks.length
          ? risks
              .map(
                r =>
                  `<button type="button" class="sheet-row" data-sheet-risk="${esc(r.title)}"><strong>${esc(r.title)}</strong><span class="sheet-row__go">›</span></button>`
              )
              .join('')
          : AWAITING
      )}
      ${accordion(
        'Products',
        products.length
          ? products.map(productRow).join('')
          : AWAITING
      )}
      ${accordion('Evidence', refsBlock(w.references))}
    `;
  }

  function activitySheetHtml() {
    const act = ((report?.sections || []).find(s => s.id === 'activity_analysis')?.widgets || []).find(
      w => w.type === 'activity'
    );
    return `
      <div class="sheet-hero">
        <p class="shell-kicker">Today’s activity</p>
        <h2>Walk & recovery</h2>
      </div>
      ${accordion('Schedule', act ? RR()?.renderWidget(act) : AWAITING, true)}
    `;
  }

  function nutritionPeekHtml() {
    const nut = (report?.sections || []).find(s => s.id === 'nutrition_analysis');
    return `
      <div class="sheet-hero">
        <p class="shell-kicker">Nutrition</p>
        <h2>Daily targets</h2>
        <p class="sheet-hero__sum">${esc(nut?.summary || '')}</p>
      </div>
      ${accordion('Targets & coverage', renderWidgets(nut?.widgets), true)}
    `;
  }

  function updateChrome() {
    const crumbs = document.getElementById('shell-crumbs');
    if (!crumbs) return;
    if (!stack.length) {
      crumbs.hidden = true;
      crumbs.innerHTML = '';
      document.querySelector('.phone-app')?.classList.remove('sheets-open');
      return;
    }
    document.querySelector('.phone-app')?.classList.add('sheets-open');
    crumbs.hidden = false;
    const pageLabel = 'Analysis';
    const parts = [{ label: pageLabel, idx: -1 }].concat(stack.map((s, i) => ({ label: scrub(s.title), idx: i })));
    crumbs.innerHTML = parts
      .map((p, i) => {
        if (i === parts.length - 1) return `<span>${esc(p.label)}</span>`;
        return `<button type="button" class="sheet-crumb" data-sheet-pop-to="${p.idx}">${esc(p.label)}</button>`;
      })
      .join('<span class="shell-crumbs__sep">/</span>');
    crumbs.querySelectorAll('[data-sheet-pop-to]').forEach(btn => {
      btn.addEventListener('click', () => {
        const idx = Number(btn.getAttribute('data-sheet-pop-to'));
        if (idx < 0) clear();
        else popTo(idx);
      });
    });
  }

  function paint() {
    ensureHost();
    host.innerHTML = '';
    stack.forEach((entry, i) => {
      const layer = document.createElement('div');
      layer.className = `ppie-sheet-layer${i === stack.length - 1 ? ' is-top' : ''}`;
      layer.style.zIndex = String(40 + i);
      layer.innerHTML = `
        <div class="ppie-sheet-backdrop" data-sheet-backdrop></div>
        <div class="ppie-sheet" role="dialog" aria-modal="true" aria-label="${esc(entry.title)}">
          <div class="ppie-sheet__handle" data-sheet-handle><span></span></div>
          <div class="ppie-sheet__toolbar">
            <button type="button" class="ppie-sheet__close" data-sheet-close aria-label="Close">Close</button>
          </div>
          <div class="ppie-sheet__scroll">${entry.html}</div>
        </div>`;
      host.appendChild(layer);
      wireSheet(layer);
    });
    updateChrome();
  }

  function wireSheet(layer) {
    exclusiveAccordions(layer);
    layer.querySelector('[data-sheet-close]')?.addEventListener('click', () => pop());
    layer.querySelector('[data-sheet-backdrop]')?.addEventListener('click', () => pop());
    layer.querySelectorAll('[data-sheet-product]').forEach(btn => {
      btn.addEventListener('click', () => openProduct(btn.getAttribute('data-sheet-product')));
    });
    layer.querySelectorAll('[data-sheet-ingredient]').forEach(btn => {
      btn.addEventListener('click', () => openIngredient(btn.getAttribute('data-sheet-ingredient')));
    });
    layer.querySelectorAll('[data-sheet-risk]').forEach(btn => {
      btn.addEventListener('click', () => openRisk(btn.getAttribute('data-sheet-risk')));
    });
    bindSwipe(layer.querySelector('[data-sheet-handle]'), layer.querySelector('.ppie-sheet'));
  }

  function bindSwipe(handle, sheet) {
    if (!handle || !sheet) return;
    let startY = 0;
    let dy = 0;
    const onStart = e => {
      startY = (e.touches ? e.touches[0].clientY : e.clientY) || 0;
      dy = 0;
      sheet.classList.add('is-dragging');
    };
    const onMove = e => {
      const y = (e.touches ? e.touches[0].clientY : e.clientY) || 0;
      dy = Math.max(0, y - startY);
      sheet.style.transform = `translateY(${dy}px)`;
    };
    const onEnd = () => {
      sheet.classList.remove('is-dragging');
      if (dy > 120) {
        sheet.style.transform = '';
        pop();
      } else {
        sheet.style.transform = '';
      }
    };
    handle.addEventListener('touchstart', onStart, { passive: true });
    handle.addEventListener('touchmove', onMove, { passive: true });
    handle.addEventListener('touchend', onEnd);
  }

  function push(entry) {
    ensureHost();
    if (stack.length && stack[stack.length - 1].id === entry.id) {
      return;
    }
    if (!stack.length && scrollEl) {
      savedScroll = scrollEl.scrollTop;
    }
    stack.push(entry);
    paint();
  }

  function pop() {
    if (!stack.length) return;
    stack.pop();
    paint();
    if (!stack.length && scrollEl) {
      scrollEl.scrollTop = savedScroll;
    }
  }

  function popTo(idx) {
    if (idx < 0) {
      clear();
      return;
    }
    stack = stack.slice(0, idx + 1);
    paint();
  }

  function clear() {
    stack = [];
    paint();
    if (scrollEl) scrollEl.scrollTop = savedScroll;
  }

  function openPackage(tier) {
    if (!tier) return;
    push({ id: `pkg:${tier}`, title: titleForPackage(tier), html: packageSheetHtml(tier) });
  }

  function titleForPackage(tier) {
    const pkg = (analyze?.wellnessPackages || []).find(p => String(p.tier || p.package_id) === String(tier));
    return pkg?.title || report?.package_reports?.[tier]?.hero?.title || String(tier);
  }

  function openProduct(productId) {
    if (!productId) return;
    const nested = report?.product_reports?.[productId];
    const catalog = global.CatalogService?.get?.(productId);
    const title = nested?.hero?.title || catalog?.product_name || catalog?.name || productId;
    push({ id: `prod:${productId}`, title, html: productSheetHtml(productId) });
  }

  function openRisk(titleOrWidget) {
    const w = typeof titleOrWidget === 'string' ? findRisk(titleOrWidget) : titleOrWidget;
    if (!w) return;
    push({ id: `risk:${w.title}`, title: w.title, html: riskSheetHtml(w) });
  }

  function openIngredient(name) {
    if (!name) return;
    push({ id: `ing:${name}`, title: name, html: ingredientSheetHtml(name) });
  }

  function openBreed() {
    push({ id: 'breed', title: 'Breed', html: breedSheetHtml() });
  }

  function openActivity() {
    push({ id: 'activity', title: 'Activity', html: activitySheetHtml() });
  }

  function openNutrition() {
    push({ id: 'nutrition', title: 'Nutrition', html: nutritionPeekHtml() });
  }

  function setContext({ report: r, analyze: a, assessment: assess }) {
    report = r || null;
    analyze = a || null;
    if (assess) global.__CLINICAL_ASSESSMENT__ = assess;
  }

  function depth() {
    return stack.length;
  }

  global.PpieSheets = {
    setContext,
    openPackage,
    openProduct,
    openRisk,
    openIngredient,
    openBreed,
    openActivity,
    openNutrition,
    push,
    pop,
    clear,
    depth
  };
})(window);
