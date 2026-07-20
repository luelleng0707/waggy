/**
 * Care Recommendation Pages — full-screen clinical pathway experience.
 * Renders existing PPIE analyze output only. No recalculation.
 */
(function (global) {
  'use strict';

  const Catalog = global.CatalogService;
  const esc = Catalog?.escapeHtml || (s => String(s ?? ''));
  const PLACEHOLDER = 'Placeholder — data not yet available';

  function bar(pct, tone) {
    const n = Number(pct);
    const w = Number.isFinite(n) ? Math.max(0, Math.min(100, n <= 1 && n > 0 ? n * 100 : n)) : 0;
    const t = tone || (w >= 95 ? 'good' : w >= 70 ? 'accent' : 'warn');
    return `<div class="cr5-bar" role="progressbar" aria-valuenow="${Math.round(w)}"><div class="cr5-bar__fill cr5-bar__fill--${t}" style="width:${w}%"></div></div>`;
  }

  function paperLink(url, label) {
    if (!url) return `<span class="cr5-placeholder">Source · Placeholder (No linked publication yet.)</span>`;
    const isPm = /pubmed|ncbi\.nlm|pmc\.ncbi/i.test(url);
    return `<a class="${isPm ? 'cr5-badge-pubmed' : 'cr5-link'}" href="${esc(url)}" target="_blank" rel="noopener">${isPm ? 'View Paper →' : esc(label || 'View Paper →')}</a>`;
  }

  function roleOf(product, analysis) {
    const cat = String(product.category || product.type || analysis?.category || '').toLowerCase();
    if (/staple|fresh|food|kibble/.test(cat)) return 'Primary Staple';
    if (/treat|bakery/.test(cat)) return 'Behavior Reward';
    if (/supplement/.test(cat)) return 'Joint / Support Supplement';
    return 'Clinical Product';
  }

  function profileBits(report) {
    const p = report.profile || report.pet || {};
    const breeds = p.breeds || [];
    return {
      name: p.pet_name || p.name || 'Dolly',
      breeds,
      breedLabel: breeds.length ? breeds.join(' × ') : 'Mixed breed',
      weight: p.weight_kg ?? p.weight ?? 30,
      env: p.current_environment || 'Current environment',
      activity: p.activity_level || 'High',
      age: p.age_years ?? '—'
    };
  }

  function whyParagraphs(pkg, report) {
    const pet = profileBits(report);
    const risks = (report.healthInsights || []).slice(0, 4);
    const overview = pkg.overview || pkg.package_summary || '';
    const why = pkg.why_fits || pkg.description || '';
    const supports = (pkg.nutrition_coverage || []).map(c => c.title).filter(Boolean);

    const p1 = `${pet.name} is a ${pet.breedLabel} living in ${pet.env}. At ${pet.weight} kg with a ${pet.activity} activity profile, PPIE evaluated breed biology, environmental load, and nutrient gaps to assemble this pathway.`;

    const riskBits = risks.length
      ? risks.map(r => `${r.title || r.goal_id}${r.biological_risk_percent != null ? ` (${r.biological_risk_percent}% biological risk)` : ''}`).join(', ')
      : 'profile-linked clinical priorities';

    const p2 = why || `Her breed combination and lifestyle elevate attention to ${riskBits}.`;

    const p3 = supports.length
      ? `This package therefore prioritizes ${supports.slice(0, 5).join(', ').toLowerCase()}—not as a shopping list, but as a constrained clinical pathway from the PPIE engine.`
      : overview || PLACEHOLDER;

    return [p1, p2, overview && overview !== why ? overview : null, p3].filter(Boolean);
  }

  function coverageRows(pkg) {
    return (pkg.nutrition_coverage || []).map(c => ({
      id: c.goal_id || c.title,
      title: c.title || c.goal_id || 'Target',
      pct: Math.round(Number(c.coverage_percent) || 0)
    }));
  }

  function nutrientDetail(pkg, goalTitle) {
    const nutrients = pkg.full_nutrition_report || pkg.daily_nutrition_intake || [];
    const key = String(goalTitle || '').toLowerCase();
    const related = nutrients.filter(n => {
      const name = String(n.nutrient || '').toLowerCase();
      if (/joint/.test(key)) return /glucosamine|msm|chondroitin|epa|dha|omega/.test(name);
      if (/skin|coat|derm/.test(key)) return /omega|zinc|epa|dha/.test(name);
      if (/digest/.test(key)) return /probiotic|fiber|carnitine/.test(name);
      if (/dental/.test(key)) return /seaweed|kelp/.test(name);
      if (/cardio|heart|cardiac/.test(key)) return /taurine/.test(name);
      if (/immune/.test(key)) return /zinc|omega|vitamin/.test(name);
      if (/weight/.test(key)) return /carnitine|fat|calorie|protein/.test(name);
      return false;
    });
    return related.length ? related : nutrients.slice(0, 3);
  }

  function evidenceCards(pkg, report, filterNutrient) {
    const notes = pkg.research_notes || [];
    const filtered = filterNutrient
      ? notes.filter(n => String(n.nutrient || '').toLowerCase().includes(String(filterNutrient).toLowerCase().split(' ')[0]))
      : notes;
    const list = filtered.length ? filtered : notes;
    if (!list.length) {
      return `<p class="cr5-placeholder">Source · Placeholder (No linked publication yet.)</p>`;
    }
    return list
      .slice(0, 6)
      .map(n => {
        const url = n.source_url || '';
        return `<article class="care-paper">
          <h5>${esc(n.nutrient || 'Clinical evidence')}</h5>
          <p class="care-paper__quote">"${esc(n.quote || PLACEHOLDER)}"</p>
          <p class="cr5-muted">${esc(n.source_name || 'Journal pending')}${n.year ? ` · ${esc(n.year)}` : ''}</p>
          <div class="care-paper__actions">${paperLink(url, n.source_name)}</div>
        </article>`;
      })
      .join('');
  }

  function mixedBreedBlock(report) {
    const pet = profileBits(report);
    const breeds = pet.breeds;
    const insights = report.healthInsights || [];
    const hip = insights.find(i => /joint|hip|ortho/i.test(`${i.title} ${i.goal_id}`)) || insights[0];
    if (!breeds.length || breeds.length < 2) {
      return hip
        ? `<p class="cr5-lead">${esc(hip.title)} · biological risk ${esc(hip.biological_risk_percent)}% · observed ${esc(hip.observed_prevalence_percent)}%.</p>`
        : `<p class="cr5-muted">${PLACEHOLDER}</p>`;
    }
    const conds = hip?.supporting_conditions || [];
    const traits = hip?.supporting_traits || [];
    return `
      <div class="care-mixed">
        <div class="care-mixed__parents">
          <div class="care-mixed__breed"><strong>${esc(breeds[0])}</strong><span>Parent A</span></div>
          <div class="care-mixed__plus">+</div>
          <div class="care-mixed__breed"><strong>${esc(breeds[1])}</strong><span>Parent B</span></div>
        </div>
        <p class="cr5-lead">Estimated combined priority for <strong>${esc(hip?.title || 'primary risk')}</strong>: <strong>${esc(hip?.biological_risk_percent ?? '—')}%</strong> biological risk (PPIE mixed-breed model).</p>
        ${conds.length ? `<p class="cr5-muted">Supporting conditions: ${esc(conds.join(', '))}</p>` : ''}
        ${traits.length ? `<p class="cr5-muted">Supporting traits: ${esc(traits.join(', '))}</p>` : ''}
        <p class="cr5-muted">Calculation · Weighted using PPIE mixed-breed model from BREEDS.csv and BREED_CONDITIONS.csv.</p>
      </div>`;
  }

  function productCards(pkg, report) {
    const analyses = report.productAnalyses || {};
    return (pkg.products_included || [])
      .map(p => {
        const id = p.product_id;
        const live = Catalog.resolve(p) || {};
        const a = analyses[id] || {};
        const name = live.product_name || p.name || p.product_name || id;
        const role = roleOf(p, a);
        const why = (a.why_included || []).length
          ? a.why_included
          : [p.why_selected || a.overview || 'Selected to close a measured nutrient gap.'];
        const actives = a.active_ingredients || p.active_ingredients || [];
        const contrib = actives
          .slice(0, 4)
          .map(x => {
            const cov = x.coverage_percent != null ? Math.round(x.coverage_percent) : null;
            const label = x.name || x.ingredient_name || 'Nutrient';
            const amt = x.amount != null ? `${x.amount}${x.unit || ''}` : '';
            return `<div class="care-contrib">
              <div class="care-contrib__head"><span>${esc(label)}</span><strong>${cov != null ? `${cov}%` : esc(amt)}</strong></div>
              ${cov != null ? bar(cov) : ''}
            </div>`;
          })
          .join('');
        const provides = actives
          .map(x => {
            const amt = typeof x.amount === 'number' ? `${x.amount}${x.unit || ''}` : x.amount;
            return amt ? `${amt} ${x.name || ''}`.trim() : x.name;
          })
          .filter(Boolean);

        return `<article class="care-product-card">
          <div class="care-product-card__media">${Catalog.imageHtml(live, name)}</div>
          <div class="care-product-card__body">
            <p class="care-product-card__role">${esc(role)}</p>
            <h4>${esc(name)}</h4>
            <p class="cr5-muted">${esc(live.brand || p.brand || '')}</p>
            <h5>Included because</h5>
            <ul class="cr5-bullets">${why.map(w => `<li><span class="cr5-mark">•</span>${esc(w)}</li>`).join('')}</ul>
            ${provides.length ? `<h5>Provides</h5><ul class="cr5-bullets">${provides.map(x => `<li><span class="cr5-mark">•</span>${esc(x)}</li>`).join('')}</ul>` : ''}
            ${contrib ? `<h5>This product contributes</h5><div class="care-contrib-stack">${contrib}</div>` : ''}
            <div class="care-product-card__footer">
              <span>${esc(p.serving_size || p.daily_amount || a.serving?.daily || '')}</span>
              <span>${esc(Catalog.formatPrice(live.product_id ? live : { list_price_rmb: p.price || p.monthly_cost || 0 }))}</span>
            </div>
            <a class="care-btn" href="#/product/${esc(id)}" data-product-route="${esc(id)}">View Product Analysis →</a>
          </div>
        </article>`;
      })
      .join('');
  }

  function whySelectedBlocks(pkg, report) {
    const analyses = report.productAnalyses || {};
    return (pkg.products_included || [])
      .map(p => {
        const id = p.product_id;
        const a = analyses[id] || {};
        const name = p.name || p.product_name || id;
        const why = (a.why_included || []).concat(p.why_selected ? [p.why_selected] : []);
        const alts = a.alternatives || [];
        return `<details class="cr5-acc" open>
          <summary class="cr5-acc__sum"><span class="cr5-acc__cat">Selection</span><span class="cr5-acc__val">${esc(name)}</span></summary>
          <div class="cr5-acc__body">
            <h5>Why selected</h5>
            <ul class="cr5-bullets">${(why.length ? why : [a.overview || PLACEHOLDER]).map(w => `<li><span class="cr5-mark">•</span>${esc(w)}</li>`).join('')}</ul>
            ${alts.length ? `<h5>Chosen over alternatives because</h5><ul class="cr5-bullets">${alts.map(x => `<li><span class="cr5-mark">•</span>${esc(x.product_name)} — ${esc(x.reason)}</li>`).join('')}</ul>` : ''}
            ${a.scientific_evidence?.length ? `<h5>Embedded evidence</h5>${a.scientific_evidence.slice(0, 2).map(ev => `<article class="care-paper"><p class="care-paper__quote">"${esc(ev.summary || ev.mechanism || PLACEHOLDER)}"</p><p class="cr5-muted">${esc(ev.journal || '')}${ev.year ? ` · ${esc(ev.year)}` : ''}</p>${paperLink(ev.source_url)}</article>`).join('')}` : ''}
          </div>
        </details>`;
      })
      .join('');
  }

  function alternativesSection(pkg, report) {
    const analyses = report.productAnalyses || {};
    const included = new Set((pkg.products_included || []).map(p => p.product_id));
    const rows = [];
    Object.values(analyses).forEach(a => {
      (a.alternatives || []).forEach(alt => {
        if (rows.find(r => r.name === alt.product_name)) return;
        const inPkg = (pkg.products_included || []).some(
          p => String(p.name || p.product_name).toLowerCase() === String(alt.product_name || '').toLowerCase()
        );
        if (inPkg) return;
        rows.push({ name: alt.product_name, reason: alt.reason, kind: 'rejected' });
      });
    });
    (report.wellnessPackages || []).forEach(other => {
      if (other.tier === pkg.tier) return;
      (other.products_included || []).forEach(p => {
        if (included.has(p.product_id)) return;
        const name = p.name || p.product_name;
        if (!name || rows.find(r => r.name === name)) return;
        rows.push({
          name,
          reason: `Available in ${other.title || other.tier} · not required to meet this pathway's coverage target (${Math.round(Number(pkg.coverage_score) || 0)}%).`,
          kind: 'alternative',
          cov: other.coverage_score,
          cost: other.monthly_cost
        });
      });
    });

    if (!rows.length) return `<p class="cr5-muted">${PLACEHOLDER}</p>`;
    return rows
      .slice(0, 8)
      .map(
        r => `<article class="care-alt ${r.kind === 'rejected' ? 'care-alt--reject' : ''}">
        <div class="care-alt__tag">${r.kind === 'rejected' ? 'Rejected' : 'Alternative'}</div>
        <h4>${esc(r.name)}</h4>
        ${r.cov != null ? `<p class="cr5-muted">Pathway coverage context · ${Math.round(r.cov)}%</p>` : ''}
        <p>${esc(r.reason)}</p>
      </article>`
      )
      .join('');
  }

  function feedingSection(pkg) {
    const strategies = pkg.feeding_strategies || [];
    const complete = strategies.find(s => /complete/i.test(String(s.id || s.title || ''))) || strategies[strategies.length - 1];
    const items = (complete && complete.items) || [];
    const products = pkg.products_included || [];
    const morning = [];
    const evening = [];
    const supplements = [];
    const treats = [];

    if (items.length) {
      items.forEach((line, i) => {
        const l = String(line).toLowerCase();
        if (/treat/.test(l)) treats.push(line);
        else if (/chew|capsule|softgel|supplement/.test(l)) supplements.push(line);
        else if (i % 2 === 0) morning.push(line);
        else evening.push(line);
      });
    } else {
      products.forEach((p, i) => {
        const line = `${p.serving_size || p.daily_amount || '1 serving'} · ${p.name || p.product_name}`;
        const cat = String(p.category || p.type || '').toLowerCase();
        if (/treat/.test(cat)) treats.push(line);
        else if (/supplement/.test(cat)) supplements.push(line);
        else if (i % 2 === 0) morning.push(line);
        else evening.push(line);
      });
    }

    const nutrients = pkg.full_nutrition_report || pkg.daily_nutrition_intake || [];
    const table = nutrients
      .map(n => {
        const cov = Math.round(Number(n.coverage_percent) || 0);
        const target = n.target != null ? n.target : n.target_daily;
        const provided = n.provided;
        const diff = Number(provided) - Number(target);
        const cls = !Number.isFinite(diff) ? '' : diff < 0 ? 'is-deficit' : diff > 0 ? 'is-surplus' : 'is-ok';
        const diffLabel = !Number.isFinite(diff)
          ? '—'
          : diff === 0
            ? 'On target'
            : diff > 0
              ? `+${Math.round(diff)}${n.unit || ''}`
              : `${Math.round(diff)}${n.unit || ''}`;
        return `<tr class="${cls}">
          <td>${esc(n.nutrient)}</td>
          <td>${esc(target)}${esc(n.unit || '')}</td>
          <td>${esc(provided)}${esc(n.unit || '')}</td>
          <td>${esc(diffLabel)}</td>
          <td>${cov}%</td>
        </tr>`;
      })
      .join('');

    return `
      <div class="care-schedule">
        <div class="care-schedule__block"><h5>Breakfast</h5><ul>${(morning.length ? morning : ['No breakfast items returned']).map(i => `<li>${esc(i)}</li>`).join('')}</ul></div>
        <div class="care-schedule__block"><h5>Dinner</h5><ul>${(evening.length ? evening : ['No dinner items returned']).map(i => `<li>${esc(i)}</li>`).join('')}</ul></div>
        <div class="care-schedule__block"><h5>Supplements</h5><ul>${(supplements.length ? supplements : ['None in this pathway']).map(i => `<li>${esc(i)}</li>`).join('')}</ul></div>
        <div class="care-schedule__block"><h5>Treats</h5><ul>${(treats.length ? treats : ['None in this pathway']).map(i => `<li>${esc(i)}</li>`).join('')}</ul></div>
      </div>
      <h5>Totals · Need vs Provided</h5>
      <div class="cr5-table-wrap">
        <table class="cr5-table care-nutrient-table">
          <thead><tr><th>Nutrient</th><th>Need</th><th>Provided</th><th>Difference</th><th>Coverage</th></tr></thead>
          <tbody>${table || `<tr><td colspan="5">${PLACEHOLDER}</td></tr>`}</tbody>
        </table>
      </div>`;
  }

  function confidenceBlock(pkg, report) {
    const traits = (report.biology?.trait_summary || []).length;
    const targets = (pkg.daily_nutrition_intake || pkg.full_nutrition_report || []).length;
    const evidence = (pkg.research_notes || []).length;
    const env = (report.management || report.environment) ? 1 : 0;
    const cov = Math.round(Number(pkg.coverage_score) || 0);
    const level = cov >= 90 ? 'High' : cov >= 75 ? 'Moderate' : 'Developing';
    return `
      <div class="care-confidence">
        <div class="care-confidence__level"><span>Confidence</span><strong>${esc(level)}</strong></div>
        <ul class="cr5-bullets">
          <li><span class="cr5-mark">✓</span>${traits || '—'} breed traits</li>
          <li><span class="cr5-mark">✓</span>${targets || '—'} nutrition targets</li>
          <li><span class="cr5-mark">✓</span>${evidence || '—'} evidence sources</li>
          <li><span class="cr5-mark">✓</span>${env ? 'Environmental modifiers applied' : 'Environment pending'}</li>
          <li><span class="cr5-mark">✓</span>Product composition + feeding rules</li>
        </ul>
      </div>`;
  }

  function finalSummary(pkg, report) {
    const pet = profileBits(report);
    const supports = (pkg.nutrition_coverage || []).filter(c => Number(c.coverage_percent) >= 90).map(c => c.title);
    const items = [
      supports.length ? `Strong coverage on ${supports.slice(0, 3).join(', ')}` : 'Addresses priority nutrient pathways',
      `Matches ${pet.env}`,
      `Supports ${pet.activity} activity level`,
      pkg.package_summary || 'Optimizes long-term preventative care from deterministic PPIE outputs'
    ];
    return `<ul class="cr5-bullets care-achieves">${items.map(i => `<li><span class="cr5-mark">✓</span>${esc(i)}</li>`).join('')}</ul>`;
  }

  function renderPage(pkg, report) {
    const pet = profileBits(report);
    const covRows = coverageRows(pkg);
    const paragraphs = whyParagraphs(pkg, report);

    return `
      <header class="care-hero">
        <button type="button" class="care-back" data-care-close>← Back</button>
        <p class="cr5-kicker">${pkg.recommended ? 'Recommended pathway' : 'Care pathway'}</p>
        <h1>${esc(pkg.title || pkg.tier)}</h1>
        <p class="care-hero__sub">Designed specifically for ${esc(pet.name)}</p>
        <p class="care-hero__calc">Calculated from · Breed · Weight · Environment · Lifestyle · Clinical evidence · Nutrition gaps · Product portfolio</p>
        <div class="care-hero__meta">
          <div><span>Monthly</span><strong>¥${Number(pkg.monthly_cost || 0).toLocaleString('en-US')}</strong></div>
          <div><span>Yearly</span><strong>¥${Number(pkg.yearly_cost || 0).toLocaleString('en-US')}</strong></div>
          <div><span>Products</span><strong>${(pkg.products_included || []).length}</strong></div>
          <div><span>Pathway coverage</span><strong>${Math.round(Number(pkg.coverage_score) || 0)}%</strong><small>of priority nutrient targets</small></div>
        </div>
      </header>

      <nav class="care-toc" aria-label="Recommendation sections">
        <a href="#care-why">Why</a>
        <a href="#care-coverage">Coverage</a>
        <a href="#care-products">Products</a>
        <a href="#care-nutrition">Nutrition</a>
        <a href="#care-selection">Selection</a>
        <a href="#care-alts">Alternatives</a>
        <a href="#care-science">Science</a>
        <a href="#care-summary">Summary</a>
      </nav>

      <section class="care-section" id="care-why">
        <h2>Why this package exists</h2>
        <div class="care-panel">${paragraphs.map(p => `<p class="care-prose">${esc(p)}</p>`).join('')}
          <h3>Mixed-breed risk context</h3>
          ${mixedBreedBlock(report)}
        </div>
      </section>

      <section class="care-section" id="care-coverage">
        <h2>Coverage Dashboard</h2>
        <p class="cr5-muted">Each bar measures fulfillment of a PPIE priority goal for this pathway. Tap a row for targets, sources, and evidence.</p>
        <div class="care-panel">
          ${(covRows.length ? covRows : [{ title: 'Core wellness', pct: Math.round(Number(pkg.coverage_score) || 0), id: 'core' }])
            .map(
              r => `<details class="care-cov">
              <summary>
                <div class="care-cov__label"><strong>${esc(r.title)}</strong><span>${r.pct}%</span></div>
                ${bar(r.pct)}
              </summary>
              <div class="care-cov__body">
                <h5>Why?</h5>
                <p class="cr5-lead">${esc(pkg.why_fits || `This goal is part of ${pet.name}'s deterministic priority set.`)}</p>
                <h5>Related nutrients</h5>
                ${nutrientDetail(pkg, r.title)
                  .map(n => {
                    const sources = (n.sources || []).map(s => s.product_name).filter(Boolean);
                    return `<div class="care-nutrient-detail">
                      <strong>${esc(n.nutrient)}</strong>
                      <p>Target ${esc(n.target ?? n.target_daily)}${esc(n.unit || '')} · Provided ${esc(n.provided)}${esc(n.unit || '')}</p>
                      ${sources.length ? `<p class="cr5-muted">Provided by · ${esc(sources.join(', '))}</p>` : ''}
                      ${n.evidence ? `<article class="care-paper"><p class="care-paper__quote">"${esc(n.evidence.quote || PLACEHOLDER)}"</p><p class="cr5-muted">${esc(n.evidence.source_name || '')}${n.evidence.year ? ` · ${esc(n.evidence.year)}` : ''}</p>${paperLink(n.evidence.source_url)}</article>` : `<p class="cr5-placeholder">Source · Placeholder (No linked publication yet.)</p>`}
                    </div>`;
                  })
                  .join('') || `<p class="cr5-muted">${PLACEHOLDER}</p>`}
              </div>
            </details>`
            )
            .join('')}
        </div>
      </section>

      <section class="care-section" id="care-products">
        <h2>Included Products</h2>
        <div class="care-product-grid">${productCards(pkg, report) || `<p class="cr5-muted">${PLACEHOLDER}</p>`}</div>
      </section>

      <section class="care-section" id="care-nutrition">
        <h2>Daily Nutrition Breakdown</h2>
        <div class="care-panel">${feedingSection(pkg)}</div>
      </section>

      <section class="care-section" id="care-selection">
        <h2>Why each product was selected</h2>
        <div class="cr5-acc-stack">${whySelectedBlocks(pkg, report) || `<p class="cr5-muted">${PLACEHOLDER}</p>`}</div>
      </section>

      <section class="care-section" id="care-alts">
        <h2>Alternative Products</h2>
        <div class="care-alt-grid">${alternativesSection(pkg, report)}</div>
      </section>

      <section class="care-section" id="care-science">
        <h2>Scientific Support</h2>
        <p class="cr5-muted">Evidence is embedded beside each claim — not a separate page.</p>
        <div class="care-panel">
          ${mixedBreedBlock(report)}
          <h3>Supporting literature</h3>
          <div class="care-paper-stack">${evidenceCards(pkg, report)}</div>
        </div>
      </section>

      <section class="care-section" id="care-confidence">
        <h2>Recommendation Confidence</h2>
        <div class="care-panel">${confidenceBlock(pkg, report)}</div>
      </section>

      <section class="care-section" id="care-summary">
        <h2>What this package achieves</h2>
        <div class="care-panel">${finalSummary(pkg, report)}</div>
      </section>
    `;
  }

  function ensureShell() {
    let root = document.getElementById('care-page');
    if (root) return root;
    root = document.createElement('div');
    root.id = 'care-page';
    root.className = 'care-page';
    root.hidden = true;
    root.innerHTML = `<div class="care-page__scroll" id="care-page-body"></div>`;
    document.body.appendChild(root);
    return root;
  }

  function ensureProductStub() {
    let root = document.getElementById('product-analysis-page');
    if (root) return root;
    root = document.createElement('div');
    root.id = 'product-analysis-page';
    root.className = 'care-page product-analysis-page';
    root.hidden = true;
    root.innerHTML = `<div class="care-page__scroll" id="product-analysis-body"></div>`;
    document.body.appendChild(root);
    return root;
  }

  function openCare(tier, report) {
    const pkgs = report?.wellnessPackages || [];
    const pkg = pkgs.find(p => String(p.tier).toLowerCase() === String(tier).toLowerCase());
    if (!pkg) return;
    const shell = ensureShell();
    const body = document.getElementById('care-page-body');
    body.innerHTML = renderPage(pkg, report);
    shell.hidden = false;
    document.body.classList.add('care-page-open');
    shell.scrollTop = 0;
    body.scrollTop = 0;

    body.querySelector('[data-care-close]')?.addEventListener('click', closeCare);
    body.querySelectorAll('[data-product-route]').forEach(a => {
      a.addEventListener('click', e => {
        e.preventDefault();
        const id = a.getAttribute('data-product-route');
        openProductStub(id, report);
      });
    });
  }

  function closeCare() {
    const shell = document.getElementById('care-page');
    if (shell) shell.hidden = true;
    document.body.classList.remove('care-page-open');
    if (location.hash.startsWith('#/care/')) {
      history.replaceState(null, '', location.pathname + location.search);
    }
  }

  function openProductStub(productId, report) {
    const live = Catalog.get(productId) || {};
    const analysis = (report.productAnalyses || {})[productId] || {};
    const name = live.product_name || analysis.product_name || productId;
    const shell = ensureProductStub();
    const body = document.getElementById('product-analysis-body');
    body.innerHTML = `
      <header class="care-hero">
        <button type="button" class="care-back" data-product-close>← Back to recommendation</button>
        <p class="cr5-kicker">Product analysis</p>
        <h1>${esc(name)}</h1>
        <p class="care-hero__sub">/product/${esc(productId)}</p>
      </header>
      <section class="care-section">
        <div class="care-panel">
          <p class="care-prose">Full scientific product analysis — ingredient ranking, formulation quality, dosage analysis, and manufacturing detail — will live on this route.</p>
          <p class="cr5-muted">Navigation is prepared. Content page not implemented in this release.</p>
          ${analysis.overview ? `<p class="cr5-lead">${esc(analysis.overview)}</p>` : ''}
          ${(analysis.why_included || []).length ? `<ul class="cr5-bullets">${analysis.why_included.map(w => `<li><span class="cr5-mark">•</span>${esc(w)}</li>`).join('')}</ul>` : ''}
        </div>
      </section>`;
    shell.hidden = false;
    body.querySelector('[data-product-close]')?.addEventListener('click', () => {
      shell.hidden = true;
      if (location.hash.startsWith('#/product/')) {
        const tier = (report.wellnessPackages || []).find(p =>
          (p.products_included || []).some(x => x.product_id === productId)
        )?.tier;
        if (tier) location.hash = `#/care/${tier}`;
        else shell.hidden = true;
      }
    });
    location.hash = `#/product/${productId}`;
  }

  function renderEntryCards(report) {
    const packages = report.wellnessPackages || [];
    if (!packages.length) {
      return `<div class="empty-state">No packages returned from analysis.</div>`;
    }
    return `<div class="care-entry-stack">
      ${packages
        .map(pkg => {
          const supports = (pkg.nutrition_coverage || []).slice(0, 4).map(c => c.title).filter(Boolean);
          return `<button type="button" class="care-entry" data-open-care="${esc(pkg.tier)}">
            <div class="care-entry__top">
              <div>
                <p class="cr5-kicker">${pkg.recommended ? 'Recommended' : 'Pathway'}</p>
                <h3>${esc(pkg.title || pkg.tier)}</h3>
              </div>
              <span class="care-entry__arrow">→</span>
            </div>
            <p class="care-prose">${esc(pkg.package_summary || pkg.overview || pkg.tagline || '')}</p>
            <div class="care-entry__meta">
              <span>¥${Number(pkg.monthly_cost || 0).toLocaleString('en-US')}/mo</span>
              <span>${(pkg.products_included || []).length} products</span>
            </div>
            ${supports.length ? `<div class="cr5-chips">${supports.map(s => `<div class="cr5-chip"><span class="cr5-chip__dot"></span>${esc(s)}</div>`).join('')}</div>` : ''}
            <span class="care-entry__cta">Open clinical recommendation</span>
          </button>`;
        })
        .join('')}
    </div>`;
  }

  function bindHashRouting(report) {
    const apply = () => {
      const h = location.hash || '';
      const care = h.match(/^#\/care\/([a-z]+)/i);
      const prod = h.match(/^#\/product\/([^/?#]+)/i);
      if (care) openCare(care[1], report);
      else if (prod) openProductStub(decodeURIComponent(prod[1]), report);
      else {
        closeCare();
        const stub = document.getElementById('product-analysis-page');
        if (stub) stub.hidden = true;
      }
    };
    window.addEventListener('hashchange', apply);
    apply();
  }

  function mount(report, rootEl) {
    const root = rootEl || document.getElementById('packages-root');
    if (!root || !report) return;
    root.innerHTML = renderEntryCards(report);
    root.querySelectorAll('[data-open-care]').forEach(btn => {
      btn.addEventListener('click', () => {
        const tier = btn.getAttribute('data-open-care');
        location.hash = `#/care/${tier}`;
      });
    });
    // Clinical report teaser buttons
    document.querySelectorAll('[data-open-care]').forEach(btn => {
      if (btn.closest('#packages-root')) return;
      btn.addEventListener('click', () => {
        location.hash = `#/care/${btn.getAttribute('data-open-care')}`;
      });
    });
    bindHashRouting(report);
  }

  global.CareRecommendation = { mount, openCare, closeCare, renderEntryCards };
})(window);
