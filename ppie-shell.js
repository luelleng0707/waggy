/**
 * PPIE Shell — Phase 18 premium product experience.
 * Clinical dashboard → explore → decide. Presentation only.
 * Consumes ClinicalAssessment; no clinical math / invented fields.
 */
(function (global) {
  'use strict';

  const UI = () => global.PpieUI;
  const Sheets = () => global.PpieSheets;
  const esc = (...a) => (UI()?.esc || (s => String(s ?? '')))(...a);
  const scrub = (...a) => (UI()?.scrub || (t => String(t ?? '')))(...a);

  let state = {
    assessment: null,
    analyze: null,
    report: null,
    models: null,
    trace: null,
    view: 'home',
    detailKey: null,
    _prevPackage: null
  };
  let chromeBound = false;

  function A() {
    return state.assessment || {};
  }
  function mod(id) {
    return (A().modules && A().modules[id]) || { data: A()[id] || {}, summary: '', title: id };
  }
  function data(id) {
    return mod(id).data || {};
  }
  function petName() {
    return data('profile').display_name || 'Your dog';
  }
  function recommendedPackage() {
    const tiers = data('packages').tiers || [];
    const recId = data('packages').recommended_tier;
    return tiers.find(t => t.tier === recId) || tiers.find(t => t.recommended) || tiers[0] || null;
  }
  function validationFor(title) {
    const items = data('validation').items || [];
    return items.find(v => String(v.subject?.title || '').toLowerCase() === String(title || '').toLowerCase());
  }
  function formatGeneratedAt() {
    const raw = A().meta?.generated_at;
    if (!raw) return 'Updated today';
    try {
      const d = new Date(raw);
      if (Number.isNaN(d.getTime())) return 'Updated today';
      return `Updated ${d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}`;
    } catch (_) {
      return 'Updated today';
    }
  }
  function confidenceLabel() {
    const c = data('confidence');
    const parts = [];
    if (c.breed_resolution) parts.push(`Breed · ${c.breed_resolution}`);
    if (c.evidence_coverage) parts.push(`Evidence · ${c.evidence_coverage}`);
    return parts.join(' · ') || c.notes || 'Confidence assessed';
  }
  function breedOneLiners() {
    const descriptors = data('breed').descriptors || [];
    const lines = [];
    for (const d of descriptors) {
      if (d.function_group && d.energy) {
        lines.push(`${d.function_group} lineage · ${d.energy} energy`);
      }
      if (d.coat_type) lines.push(`${d.coat_type} — climate-aware care`);
      if (d.weakness_group) lines.push(`${d.weakness_group} predisposition`);
      if (d.body_type && d.size) lines.push(`${d.size} · ${d.body_type} build`);
    }
    return [...new Set(lines)].slice(0, 3);
  }
  function categorizeProducts(products) {
    const list = products || [];
    const staple = list.filter(p => /staple|food|fresh|kibble/i.test(String(p.category || '')));
    const treats = list.filter(p => /treat/i.test(String(p.category || '')));
    const rest = list.filter(p => !staple.includes(p) && !treats.includes(p));
    return { staple, treats, supplements: rest };
  }

  /* ── Level 1 Home ───────────────────────────────── */

  function renderHome() {
    const U = UI();
    if (!U) return `<p class="px-muted">UI kit unavailable.</p>`;

    const name = petName();
    const profile = data('profile');
    const health = data('health');
    const nutrition = data('nutrition');
    const activity = data('activity');
    const pkg = recommendedPackage();
    const priorities = (health.priorities || []).slice(0, 3);
    const score = health.summary_score;
    const dims = (health.coverage?.dimensions || []).slice(0, 5);
    const { staple, treats, supplements } = categorizeProducts(pkg?.products);
    const meal = staple[0] || (pkg?.products || [])[0];
    const breedLines = breedOneLiners();
    const evidence = data('evidence').items || [];

    return `
      <div class="px-home">
        <!-- 1 Clinical Snapshot -->
        <section class="px-section px-snapshot" data-level="1">
          <div class="px-snapshot__identity">
            <div class="px-avatar" aria-hidden="true">${esc((name || 'D').charAt(0))}</div>
            <div>
              <p class="px-kicker">Clinical dashboard</p>
              <h1 class="px-snapshot__name">${esc(name)}</h1>
              <p class="px-snapshot__breed">${esc(profile.breed_label || '—')}</p>
            </div>
          </div>
          <div class="px-snapshot__chips">
            <span>${esc(profile.age_years != null ? profile.age_years + ' yrs' : '—')}</span>
            <span>${esc(profile.weight_kg != null ? profile.weight_kg + ' kg' : '—')}</span>
            <span>${esc(profile.environment || '—')}</span>
          </div>
          <div class="px-snapshot__stats">
            ${U.statCard('Health score', score?.value != null ? score.value + (score.unit || '') : '—', score?.label || 'Wellness')}
            ${U.statCard("Today's focus", priorities[0]?.title || '—', priorities[0]?.probability_pct != null ? priorities[0].probability_pct + '%' : '')}
            ${U.statCard('Confidence', confidenceLabel().split(' · ')[0] || '—', confidenceLabel().split(' · ')[1] || '')}
            ${U.statCard('Last updated', formatGeneratedAt(), '')}
          </div>
        </section>

        <!-- 2 Today's Care Plan -->
        <section class="px-section" data-level="1">
          ${U.sectionHeader("Today's care plan", 'Do this today')}
          <div class="px-panel">
            ${U.planRow('Meal', scrub(meal?.name || 'See care package') + (meal?.serving ? ` · ${meal.serving}` : ''), meal?.product_id ? `<button type="button" class="px-link" data-product-page="${esc(meal.product_id)}">Details</button>` : '')}
            ${U.planRow('Walk', activity.daily_exercise || (activity.morning_min != null ? `${activity.morning_min}+${activity.evening_min || '—'} min` : '—'), `<button type="button" class="px-link" data-sheet="activity">Schedule</button>`)}
            ${U.planRow('Treats', treats.length ? scrub(treats.map(t => t.name).join(' · ')) + (treats[0]?.serving ? ` · ${treats[0].serving}` : '') : 'As listed in care package', treats[0]?.product_id ? `<button type="button" class="px-link" data-product-page="${esc(treats[0].product_id)}">Details</button>` : '')}
            ${U.planRow('Supplements', supplements.length ? scrub(supplements.map(s => s.name).join(' · ')) : meal || treats.length ? 'Included in pathway products' : '—', '')}
          </div>
        </section>

        <!-- 3 Priority Health Risks -->
        <section class="px-section" data-level="1">
          ${U.sectionHeader('Top health priorities', health.headline || '')}
          <div class="px-stack">
            ${
              priorities.length
                ? priorities
                    .map(r => {
                      const card = U.riskCard(r, { benchmark: validationFor(r.title) });
                      const ev = U.evidenceForTopic(evidence, r.title)[0];
                      return `<div class="px-risk-wrap">${card}${ev ? U.evidenceBlock(ev) : ''}</div>`;
                    })
                    .join('')
                : `<p class="px-muted">No elevated priorities flagged.</p>`
            }
          </div>
        </section>

        <!-- 4 Nutrition Summary -->
        <section class="px-section" data-level="1">
          ${U.sectionHeader('Nutrition summary', health.coverage?.subtitle || 'Daily nutritional goals')}
          <div class="px-panel">
            ${
              dims.length
                ? U.coverageChart(dims, 5)
                : `<p class="px-muted">${esc(mod('nutrition').summary || 'Nutrition targets')}</p>`
            }
            ${
              (nutrition.targets || []).length
                ? `<div class="px-nutrient-pills">${(nutrition.targets || [])
                    .slice(0, 4)
                    .map(t => `<span class="px-pill">${esc(t.name)}${t.daily_target ? ` · ${esc(String(t.daily_target))}` : ''}</span>`)
                    .join('')}</div>`
                : ''
            }
            <button type="button" class="px-link px-link--block" data-sheet="nutrition">Nutrition analysis</button>
          </div>
        </section>

        <!-- 5 Recommended Care Package -->
        <section class="px-section" data-level="1">
          ${U.sectionHeader('Recommended care package', 'Your pathway')}
          ${pkg ? U.packageCard(pkg) : `<p class="px-muted">Care pathway pending.</p>`}
          ${(data('packages').tiers || []).length > 1 ? `<button type="button" class="px-link px-link--block" data-sheet="pathways">Compare other pathways</button>` : ''}
        </section>

        <!-- 6 Breed & Biology (short) -->
        <section class="px-section" data-level="1">
          ${U.sectionHeader('Breed & biology', profile.breed_label || '')}
          <button type="button" class="px-panel px-panel--tap" data-sheet="breed">
            ${
              breedLines.length
                ? `<ul class="px-bullets">${breedLines.map(l => `<li>${esc(l)}</li>`).join('')}</ul>`
                : `<p>${esc(scrub((mod('breed').summary || '').slice(0, 160)) || 'Breed composition shapes predisposition and care priorities.')}</p>`
            }
            <span class="px-link">Explore biology</span>
          </button>
        </section>

        <!-- 7 Activity Summary -->
        <section class="px-section" data-level="1">
          ${U.sectionHeader('Daily activity', mod('activity').summary || '')}
          <div class="px-panel">
            <div class="px-snapshot__stats px-snapshot__stats--compact">
              ${U.statCard('Daily', activity.daily_exercise || (activity.daily_km != null ? activity.daily_km + ' km' : '—'), '')}
              ${U.statCard('Physical', (activity.suggested_physical || []).slice(0, 2).join(' · ') || '—', '')}
              ${U.statCard('Mental', (activity.suggested_mental || []).slice(0, 2).join(' · ') || '—', '')}
              ${U.statCard('Recovery', activity.recovery ? String(activity.recovery).slice(0, 40) + (String(activity.recovery).length > 40 ? '…' : '') : '—', '')}
            </div>
            <button type="button" class="px-link px-link--block" data-sheet="activity">Activity analysis</button>
          </div>
        </section>

        <!-- Level 2 — Understanding (sheets / light expand) -->
        <section class="px-section px-section--secondary" data-level="2">
          ${U.sectionHeader('Understand why', 'Tap to explore')}
          <div class="px-explore-grid">
            ${U.exploreTile('Health analysis', `${priorities.length} priorities`, 'health')}
            ${U.exploreTile('Nutrition analysis', `${(nutrition.targets || []).length} targets`, 'nutrition')}
            ${U.exploreTile('Activity analysis', activity.daily_exercise || 'Plan', 'activity')}
            ${U.exploreTile('Environment', data('environment').label || 'Context', 'environment')}
            ${U.exploreTile('Behavior', data('behavior').activity_level || 'Lifestyle', 'behavior')}
            ${U.exploreTile('Breed & biology', profile.breed_label || 'Traits', 'breed')}
          </div>
        </section>
      </div>
    `;
  }

  /* ── Package detail (Level 3 page) ──────────────── */

  function renderPackagePage(tier) {
    const U = UI();
    const pkg = (data('packages').tiers || []).find(t => String(t.tier) === String(tier)) || recommendedPackage();
    if (!pkg || !U) {
      return `<p class="px-muted">Package not found.</p><button type="button" class="px-link" data-view="home">← Back</button>`;
    }
    const products = pkg.products || [];
    const detail = pkg.detail || {};
    const dims = (data('health').coverage?.dimensions || []).slice(0, 6);
    const tiers = data('packages').tiers || [];
    const essential = tiers.find(t => /essential/i.test(String(t.tier || t.title || '')));
    let compareNote = '';
    if (essential && pkg.yearly_cost != null && essential.yearly_cost != null && essential.tier !== pkg.tier) {
      const delta = Number(essential.yearly_cost) - Number(pkg.yearly_cost);
      if (delta > 0) compareNote = `¥${delta.toLocaleString()} less per year than ${essential.title}`;
      else if (delta < 0) compareNote = `¥${Math.abs(delta).toLocaleString()} more per year than ${essential.title}`;
    }
    const plan365 = detail.plan_365;
    const planProducts = plan365 && typeof plan365 === 'object' ? plan365.products || [] : [];
    const evidence = data('evidence').items || [];
    const topEv = U.evidenceForTopic(evidence, data('health').priorities?.[0]?.title)[0];
    const { staple, treats, supplements } = categorizeProducts(products);

    return `
      <article class="px-detail px-detail--pkg">
        <header class="px-detail__hero">
          <button type="button" class="px-link" data-view="home">← Dashboard</button>
          <p class="px-kicker">${pkg.recommended ? 'Best match for this dog' : 'Care pathway'}</p>
          <h1>${esc(scrub(pkg.title))}</h1>
          <p class="px-detail__lede">${esc(scrub(pkg.summary || ''))}</p>
          <div class="px-snapshot__stats">
            ${U.statCard('Coverage', pkg.coverage_score != null ? pkg.coverage_score + '%' : '—', 'Pathway score')}
            ${U.statCard('Monthly', pkg.monthly_cost != null ? '¥' + Number(pkg.monthly_cost).toLocaleString() : '—', '')}
            ${U.statCard('Yearly', pkg.yearly_cost != null ? '¥' + Number(pkg.yearly_cost).toLocaleString() : '—', compareNote || '365-day')}
          </div>
        </header>

        <section class="px-section">
          ${U.sectionHeader('Clinical coverage', data('health').coverage?.label || 'Preventative priorities')}
          <div class="px-panel">${U.coverageChart(dims, 6)}</div>
        </section>

        <section class="px-section">
          ${U.sectionHeader('Why we chose this package')}
          <div class="px-panel">
            <p class="px-prose">${esc(scrub(detail.rationale || pkg.summary || 'Selected to balance coverage, clinical priorities, and long-term cost.'))}</p>
          </div>
        </section>

        <section class="px-section">
          ${U.sectionHeader('Products included', `${products.length} items`)}
          <div class="px-stack px-stack--products">
            ${products.map(p => U.productCard(p, { showImage: true })).join('') || `<p class="px-muted">No products listed.</p>`}
          </div>
        </section>

        <section class="px-section">
          ${U.sectionHeader('Daily feeding schedule')}
          <div class="px-panel">
            ${staple.map(p => U.planRow('Staple', `${scrub(p.name)}${p.serving ? ' · ' + p.serving : ''}`, '')).join('')}
            ${treats.map(p => U.planRow('Treats', `${scrub(p.name)}${p.serving ? ' · ' + p.serving : ''}`, '')).join('')}
            ${supplements.map(p => U.planRow('Supplements', `${scrub(p.name)}${p.serving ? ' · ' + p.serving : ''}`, '')).join('')}
            ${!products.length ? `<p class="px-muted">Feeding schedule follows product servings above.</p>` : ''}
          </div>
        </section>

        <section class="px-section">
          ${U.sectionHeader('Annual plan')}
          <div class="px-panel">
            <p>Monthly · <strong>¥${Number(pkg.monthly_cost || 0).toLocaleString()}</strong></p>
            <p>Yearly (365-day) · <strong>¥${Number(pkg.yearly_cost || 0).toLocaleString()}</strong></p>
            ${compareNote ? `<p class="px-muted">${esc(compareNote)}</p>` : ''}
            ${
              planProducts.length
                ? `<ul class="px-bullets">${planProducts
                    .slice(0, 6)
                    .map(
                      p =>
                        `<li>${esc(scrub(p.product_name || p.name))} · ${esc(p.daily_serving || '')}${
                          p.yearly_cost != null ? ` · ¥${Number(p.yearly_cost).toLocaleString()}/yr` : ''
                        }</li>`
                    )
                    .join('')}</ul>`
                : ''
            }
          </div>
        </section>

        <section class="px-section">
          ${U.sectionHeader('Scientific basis')}
          <div class="px-panel">
            ${topEv ? U.evidenceBlock(topEv) : `<p class="px-muted">Supporting literature is linked on each health priority.</p>`}
          </div>
        </section>

        ${
          tiers.filter(t => t.tier !== pkg.tier).length
            ? `<section class="px-section px-section--secondary">
                ${U.sectionHeader('Other pathways')}
                <div class="px-stack">
                  ${tiers
                    .filter(t => t.tier !== pkg.tier)
                    .map(
                      t =>
                        `<button type="button" class="px-explore" data-package-page="${esc(t.tier)}">
                          <span class="px-explore__title">${esc(scrub(t.title))}</span>
                          <span class="px-explore__preview">¥${Number(t.monthly_cost || 0).toLocaleString()}/mo</span>
                          <span class="px-explore__go">›</span>
                        </button>`
                    )
                    .join('')}
                </div>
              </section>`
            : ''
        }
      </article>
    `;
  }

  /* ── Product detail (Level 3 page) ──────────────── */

  function renderProductPage(productId) {
    const U = UI();
    const byId = data('products').by_id || {};
    let p = byId[productId];
    if (!p) {
      for (const tier of data('packages').tiers || []) {
        const hit = (tier.products || []).find(x => String(x.product_id) === String(productId));
        if (hit) {
          p = { ...hit, analysis: byId[productId]?.analysis };
          break;
        }
      }
    }
    const catalog = global.CatalogService?.get?.(productId);
    const analysis = p?.analysis || byId[productId]?.analysis || {};
    const name = scrub(p?.name || analysis.product_name || catalog?.product_name || productId);
    const comps = catalog ? global.CatalogService.componentsList?.(catalog) || [] : [];
    const funcs = catalog?.functions || [];
    const serving = analysis.serving || {};
    const evidence = data('evidence').items || [];
    const topic = (p?.why_selected || funcs[0] || name || '').toString();
    const relatedEv = U.evidenceForTopic(evidence, topic).slice(0, 2);
    const related = (recommendedPackage()?.products || []).filter(x => String(x.product_id) !== String(productId)).slice(0, 3);

    return `
      <article class="px-detail px-detail--product">
        <header class="px-detail__hero">
          <button type="button" class="px-link" data-back-detail>← Back</button>
          <p class="px-kicker">${esc(scrub(analysis.brand || p?.category || catalog?.category || 'Product'))}</p>
          <h1>${esc(name)}</h1>
          <p class="px-detail__lede">${esc(scrub(analysis.overview || p?.summary || catalog?.short_description || catalog?.description || ''))}</p>
          ${catalog ? `<div class="px-detail__media">${global.CatalogService.imageHtml?.(catalog, name) || ''}</div>` : ''}
          ${catalog ? `<p class="px-price">${esc(global.CatalogService.formatPrice?.(catalog) || '')}</p>` : ''}
        </header>

        <section class="px-section">
          ${U.sectionHeader('Benefits')}
          <div class="px-panel">
            <p class="px-prose">${esc(scrub(p?.why_selected || analysis.overview || 'Matched to this dog’s clinical priorities.'))}</p>
          </div>
        </section>

        <section class="px-section">
          ${U.sectionHeader('Clinical functions')}
          <div class="px-panel">
            ${
              funcs.length
                ? `<ul class="px-bullets">${funcs.map(f => `<li>${esc(typeof f === 'string' ? f : f.function || f.name)}</li>`).join('')}</ul>`
                : `<p class="px-muted">${esc(scrub(p?.why_selected || 'Supports the active care pathway.'))}</p>`
            }
          </div>
        </section>

        <section class="px-section">
          ${U.sectionHeader('Ingredients & actives')}
          <div class="px-panel">
            ${
              comps.length
                ? `<ul class="px-bullets">${comps
                    .map(
                      c =>
                        `<li><strong>${esc(c.component_name)}</strong>${c.value ? ` · ${esc(c.value)}${esc(c.unit || '')}` : ''}${
                          c.component_type ? ` <span class="px-muted">${esc(c.component_type)}</span>` : ''
                        }</li>`
                    )
                    .join('')}</ul>`
                : (analysis.active_ingredients || []).length
                  ? `<ul class="px-bullets">${analysis.active_ingredients.map(x => `<li>${esc(typeof x === 'string' ? x : x.name || JSON.stringify(x))}</li>`).join('')}</ul>`
                  : `<p class="px-muted">Composition detail is being prepared.</p>`
            }
          </div>
        </section>

        <section class="px-section">
          ${U.sectionHeader('Feeding guide')}
          <div class="px-panel">
            ${U.planRow('Daily', serving.daily || p?.serving || global.CatalogService?.feedingDisplay?.(catalog) || '—', '')}
            ${serving.calories_kcal != null ? U.planRow('Calories', `${serving.calories_kcal} kcal`, '') : ''}
            ${serving.weight_g != null ? U.planRow('Weight', `${serving.weight_g} g`, '') : ''}
            ${serving.container_lasts_days != null ? U.planRow('Container lasts', `${serving.container_lasts_days} days`, '') : ''}
          </div>
        </section>

        <section class="px-section">
          ${U.sectionHeader('Scientific support')}
          <div class="px-panel">
            ${
              relatedEv.length
                ? relatedEv.map(e => U.evidenceBlock(e)).join('')
                : `<p class="px-muted">Evidence is shown alongside the health priorities this product supports.</p>`
            }
          </div>
        </section>

        ${
          related.length
            ? `<section class="px-section px-section--secondary">
                ${U.sectionHeader('Related products')}
                <div class="px-stack px-stack--products">${related.map(r => U.productCard(r, { showImage: false })).join('')}</div>
              </section>`
            : ''
        }

        ${
          analysis && Object.keys(analysis).length
            ? UI().inlineExpand(
                'Technical detail',
                'Structured analysis',
                `<pre class="px-pre">${esc(JSON.stringify(analysis, null, 2).slice(0, 1800))}</pre>`
              )
            : ''
        }
      </article>
    `;
  }

  /* ── Level 2 sheets ─────────────────────────────── */

  function openAnalysisSheet(kind) {
    const U = UI();
    if (!U || !Sheets()?.push) return;

    if (kind === 'health') {
      const priorities = data('health').priorities || [];
      const evidence = data('evidence').items || [];
      Sheets().push({
        id: 'analysis:health',
        title: 'Health analysis',
        html: `
          <div class="px-sheet-body">
            ${(priorities || [])
              .map(r => {
                const ev = U.evidenceForTopic(evidence, r.title)[0];
                const tech = (r.technical_reasoning || [])
                  .map(t => `<li>${esc(t.label)} · ${esc(scrub(String(t.value)))}</li>`)
                  .join('');
                return `
                  <article class="px-sheet-card">
                    <h3>${esc(r.title)} · ${r.probability_pct != null ? esc(r.probability_pct) + '%' : '—'}</h3>
                    <p>${esc(scrub(r.explanation || ''))}</p>
                    ${
                      r.contributing_traits?.length
                        ? `<p class="px-muted">Traits · ${esc(r.contributing_traits.slice(0, 4).join(' · '))}</p>`
                        : ''
                    }
                    ${ev ? U.evidenceBlock(ev) : ''}
                    ${
                      tech
                        ? `<details class="px-inline"><summary><span>Technical reasoning</span></summary><div class="px-inline__body"><ul class="px-tech">${tech}</ul></div></details>`
                        : ''
                    }
                  </article>`;
              })
              .join('') || `<p class="px-muted">No priorities.</p>`}
          </div>`
      });
      return;
    }

    if (kind === 'nutrition') {
      const targets = data('nutrition').targets || [];
      const dims = data('health').coverage?.dimensions || [];
      Sheets().push({
        id: 'analysis:nutrition',
        title: 'Nutrition analysis',
        html: `
          <div class="px-sheet-body">
            <div class="px-panel">${U.coverageChart(dims, 8)}</div>
            <ul class="px-bullets">${targets
              .map(
                t =>
                  `<li><strong>${esc(t.name)}</strong>${t.daily_target ? ` · ${esc(String(t.daily_target))}/day` : ''}${
                    t.supports?.length ? `<br><span class="px-muted">${esc([...new Set(t.supports)].slice(0, 3).join(', '))}</span>` : ''
                  }</li>`
              )
              .join('')}</ul>
          </div>`
      });
      return;
    }

    if (kind === 'activity') {
      const activity = data('activity');
      Sheets().push({
        id: 'analysis:activity',
        title: 'Activity analysis',
        html: `
          <div class="px-sheet-body">
            <div class="px-panel">
              ${U.planRow('Daily exercise', activity.daily_exercise || '—', '')}
              ${U.planRow('Physical', (activity.suggested_physical || []).join(' · ') || '—', '')}
              ${U.planRow('Mental', (activity.suggested_mental || []).join(' · ') || '—', '')}
            </div>
            ${activity.recovery ? `<p class="px-prose">${esc(scrub(activity.recovery))}</p>` : ''}
          </div>`
      });
      return;
    }

    if (kind === 'breed') {
      const descriptors = data('breed').descriptors || [];
      const traits = (data('traits').items || []).slice(0, 8);
      Sheets().push({
        id: 'analysis:breed',
        title: 'Breed & biology',
        html: `
          <div class="px-sheet-body">
            <p class="px-prose">${esc(scrub(mod('breed').summary || ''))}</p>
            ${descriptors
              .map(
                d => `<article class="px-sheet-card">
                  <h3>${esc(d.breed || 'Breed')}</h3>
                  <ul class="px-bullets">
                    ${d.size ? `<li>Size · ${esc(d.size)}</li>` : ''}
                    ${d.body_type ? `<li>Build · ${esc(d.body_type)}</li>` : ''}
                    ${d.coat_type ? `<li>Coat · ${esc(d.coat_type)}</li>` : ''}
                    ${d.energy ? `<li>Energy · ${esc(d.energy)}</li>` : ''}
                    ${d.function_group ? `<li>Lineage · ${esc(d.function_group)}</li>` : ''}
                    ${d.weakness_group ? `<li>Focus · ${esc(d.weakness_group)}</li>` : ''}
                  </ul>
                </article>`
              )
              .join('')}
            ${
              traits.length
                ? `<h3 class="px-sheet-h">Traits</h3><ul class="px-bullets">${traits
                    .map(t => `<li><strong>${esc(t.title)}</strong>${t.category ? ` · ${esc(t.category)}` : ''}</li>`)
                    .join('')}</ul>`
                : ''
            }
          </div>`
      });
      return;
    }

    if (kind === 'environment') {
      const env = data('environment');
      Sheets().push({
        id: 'analysis:environment',
        title: 'Environment',
        html: `<div class="px-sheet-body"><div class="px-panel">${U.planRow('Current', env.label || '—', '')}${U.planRow('Activity level', env.activity_level || '—', '')}</div>${env.notes ? `<p class="px-prose">${esc(scrub(env.notes))}</p>` : `<p class="px-muted">Environment shapes heat, humidity, and activity load for this dog.</p>`}</div>`
      });
      return;
    }

    if (kind === 'behavior') {
      const b = data('behavior');
      Sheets().push({
        id: 'analysis:behavior',
        title: 'Behavior & lifestyle',
        html: `<div class="px-sheet-body"><div class="px-panel">${U.planRow('Activity level', b.activity_level || '—', '')}</div>${b.energy_notes ? `<p class="px-prose">${esc(scrub(b.energy_notes))}</p>` : `<p class="px-muted">Lifestyle guidance follows activity level and breed energy.</p>`}</div>`
      });
      return;
    }

    if (kind === 'pathways') {
      const tiers = data('packages').tiers || [];
      Sheets().push({
        id: 'analysis:pathways',
        title: 'Care pathways',
        html: `<div class="px-sheet-body">${tiers
          .map(
            t => `<button type="button" class="px-explore" data-package-page="${esc(t.tier)}">
              <span class="px-explore__title">${esc(scrub(t.title))}${t.recommended ? ' · Recommended' : ''}</span>
              <span class="px-explore__preview">¥${Number(t.monthly_cost || 0).toLocaleString()}/mo · ${t.coverage_score != null ? t.coverage_score + '%' : ''}</span>
              <span class="px-explore__go">›</span>
            </button>`
          )
          .join('')}</div>`
      });
      // Wire package buttons inside sheet after paint
      setTimeout(() => {
        document.querySelectorAll('#ppie-sheet-host [data-package-page]').forEach(el => {
          el.addEventListener('click', e => {
            e.preventDefault();
            Sheets()?.clear?.();
            showView('package', el.getAttribute('data-package-page'));
          });
        });
      }, 0);
    }
  }

  function openHealthSheet(riskId) {
    const U = UI();
    const r = (data('health').priorities || []).find(x => String(x.id) === String(riskId));
    if (!r || !Sheets()?.push) return;
    const bench = validationFor(r.title);
    const ev = U.evidenceForTopic(data('evidence').items || [], r.title)[0];
    const tech = (r.technical_reasoning || [])
      .map(t => `<li>${esc(t.label)} · ${esc(scrub(String(t.value)))}</li>`)
      .join('');
    Sheets().push({
      id: `health:${r.id}`,
      title: r.title,
      html: `
        <div class="px-sheet-body">
          <div class="px-snapshot__stats">
            ${U.statCard('Likelihood', r.probability_pct != null ? r.probability_pct + '%' : '—', 'Estimate')}
            ${U.statCard(
              'Published',
              bench?.status === 'compared' && bench.published_benchmark_pct != null ? bench.published_benchmark_pct + '%' : '—',
              bench?.status === 'unavailable' ? 'Pending' : 'Benchmark'
            )}
          </div>
          <p class="px-prose">${esc(scrub(r.explanation || ''))}</p>
          ${
            r.contributing_traits?.length
              ? `<h3 class="px-sheet-h">Contributing biology</h3><ul class="px-bullets">${r.contributing_traits
                  .map(t => `<li>${esc(t)}</li>`)
                  .join('')}</ul>`
              : ''
          }
          ${
            r.prevention?.length
              ? `<h3 class="px-sheet-h">Prevention</h3><ul class="px-bullets">${r.prevention.map(t => `<li>${esc(t)}</li>`).join('')}</ul>`
              : ''
          }
          ${ev ? `<h3 class="px-sheet-h">Supporting evidence</h3>${U.evidenceBlock(ev)}` : ''}
          ${
            tech
              ? `<details class="px-inline"><summary><span>Technical reasoning</span></summary><div class="px-inline__body"><ul class="px-tech">${tech}</ul></div></details>`
              : ''
          }
        </div>`
    });
  }

  /* ── Navigation ─────────────────────────────────── */

  function showView(view, detailKey) {
    if (Sheets()?.depth?.() > 0 && view !== state.view) Sheets().clear();
    state.view = view;
    state.detailKey = detailKey || null;
    const root = document.getElementById('page-module');
    if (!root) return;
    if (view === 'package' && detailKey) root.innerHTML = renderPackagePage(detailKey);
    else if (view === 'product' && detailKey) root.innerHTML = renderProductPage(detailKey);
    else if (view === 'trace') {
      if (global.PpieTrace?.mount) global.PpieTrace.mount(state.trace || state.assessment?.trace, 'page-module');
      else root.innerHTML = `<p class="px-muted">Trace UI not loaded. Include ppie-trace.js and enable debug.</p>`;
    } else root.innerHTML = renderHome();
    if (view !== 'trace') wirePage(root);
    document.getElementById('shell-main')?.scrollTo({ top: 0, behavior: 'smooth' });
    updateCrumbs();
  }

  function updateCrumbs() {
    const el = document.getElementById('shell-crumbs');
    if (!el) return;
    if (state.view === 'home' || !state.view) {
      el.hidden = true;
      el.innerHTML = '';
      return;
    }
    el.hidden = false;
    const parts = [{ label: 'Dashboard', view: 'home' }];
    if (state.view === 'package') parts.push({ label: scrub(recommendedPackage()?.title || 'Care package') });
    if (state.view === 'product') parts.push({ label: 'Product' });
    if (state.view === 'trace') parts.push({ label: 'Calculation Trace' });
    el.innerHTML = parts
      .map((p, i) => {
        if (i === parts.length - 1) return `<span>${esc(p.label)}</span>`;
        return `<button type="button" class="sheet-crumb" data-view="${esc(p.view || 'home')}">${esc(p.label)}</button>`;
      })
      .join('<span class="shell-crumbs__sep">/</span>');
    el.querySelectorAll('[data-view]').forEach(btn => {
      btn.addEventListener('click', () => showView(btn.getAttribute('data-view')));
    });
  }

  function wirePage(root) {
    root.querySelectorAll('[data-view]').forEach(el => {
      el.addEventListener('click', e => {
        e.preventDefault();
        showView(el.getAttribute('data-view'));
      });
    });
    root.querySelectorAll('[data-package-page]').forEach(el => {
      el.addEventListener('click', e => {
        e.preventDefault();
        showView('package', el.getAttribute('data-package-page'));
      });
    });
    root.querySelectorAll('[data-product-page]').forEach(el => {
      el.addEventListener('click', e => {
        e.preventDefault();
        if (state.view === 'package') state._prevPackage = state.detailKey;
        showView('product', el.getAttribute('data-product-page'));
      });
    });
    root.querySelectorAll('[data-back-detail]').forEach(el => {
      el.addEventListener('click', () => {
        if (state.view === 'product' && state._prevPackage) showView('package', state._prevPackage);
        else showView('home');
      });
    });
    root.querySelectorAll('[data-health-id]').forEach(el => {
      el.addEventListener('click', e => {
        e.preventDefault();
        openHealthSheet(el.getAttribute('data-health-id'));
      });
    });
    root.querySelectorAll('[data-sheet]').forEach(el => {
      el.addEventListener('click', e => {
        e.preventDefault();
        openAnalysisSheet(el.getAttribute('data-sheet'));
      });
    });
  }

  function bindChrome() {
    if (chromeBound) return;
    chromeBound = true;
    document.getElementById('module-back')?.addEventListener('click', () => {
      showView('home');
      Sheets()?.clear?.();
    });
    document.getElementById('shell-search-btn')?.addEventListener('click', () => {
      const panel = document.getElementById('shell-search-panel');
      panel.hidden = false;
      document.getElementById('shell-search-input')?.focus();
      runSearch('');
    });
    document.getElementById('shell-search-close')?.addEventListener('click', () => {
      document.getElementById('shell-search-panel').hidden = true;
    });
    document.getElementById('shell-search-input')?.addEventListener('input', e => runSearch(e.target.value));
    document.getElementById('module-share')?.addEventListener('click', () => {
      if (navigator.share) navigator.share({ title: 'Wagtopia Wellness', text: `Clinical dashboard for ${petName()}` }).catch(() => {});
    });
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape' && Sheets()?.depth?.() > 0) Sheets().pop();
    });
  }

  function ensureTraceButton() {
    const actions = document.querySelector('.module-header__actions');
    if (!actions || document.getElementById('module-trace')) return;
    const hasTrace = !!(state.trace || state.assessment?.trace);
    const debugUrl = /(?:\?|&)(?:debug|dev)=/i.test(location.search);
    if (!hasTrace && !debugUrl) return;
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'module-ghost';
    btn.id = 'module-trace';
    btn.textContent = 'Trace';
    btn.title = 'Developer calculation trace';
    actions.insertBefore(btn, actions.firstChild);
    btn.addEventListener('click', () => showView('trace'));
    if (!document.getElementById('ppie-vc-link')) {
      const a = document.createElement('a');
      a.id = 'ppie-vc-link';
      a.href = '/debug/calculation?debug=1';
      a.textContent = 'Console';
      a.className = 'module-ghost';
      a.style.marginLeft = '0.5rem';
      a.title = 'Internal Validation Console';
      btn.insertAdjacentElement('afterend', a);
    }
  }

  function runSearch(q) {
    const root = document.getElementById('shell-search-results');
    if (!root) return;
    const query = String(q || '').trim().toLowerCase();
    if (!query) {
      root.innerHTML = `<p class="px-muted">Search conditions, nutrients, products…</p>`;
      return;
    }
    const hits = [];
    for (const r of data('health').priorities || []) {
      if (String(r.title).toLowerCase().includes(query)) hits.push({ kind: 'health', key: r.id, label: r.title, type: 'Health' });
    }
    for (const t of data('packages').tiers || []) {
      if (String(t.title).toLowerCase().includes(query)) hits.push({ kind: 'package', key: t.tier, label: t.title, type: 'Pathway' });
      for (const p of t.products || []) {
        if (String(p.name).toLowerCase().includes(query)) hits.push({ kind: 'product', key: p.product_id, label: p.name, type: 'Product' });
      }
    }
    root.innerHTML = hits.length
      ? hits
          .slice(0, 20)
          .map(
            h =>
              `<button type="button" class="shell-search-hit" data-search-kind="${esc(h.kind)}" data-search-key="${esc(h.key)}"><span>${esc(h.type)}</span><strong>${esc(h.label)}</strong></button>`
          )
          .join('')
      : `<p class="px-muted">No matches.</p>`;
    root.querySelectorAll('[data-search-kind]').forEach(el => {
      el.addEventListener('click', () => {
        document.getElementById('shell-search-panel').hidden = true;
        const kind = el.getAttribute('data-search-kind');
        const key = el.getAttribute('data-search-key');
        if (kind === 'package') showView('package', key);
        else if (kind === 'product') showView('product', key);
        else if (kind === 'health') openHealthSheet(key);
      });
    });
  }

  function mount({ assessment, analyze, report, models, trace }) {
    state.assessment = assessment || null;
    state.analyze = analyze || null;
    state.report = report || null;
    state.models = models || null;
    state.trace = trace || assessment?.trace || null;
    window.__CLINICAL_ASSESSMENT__ = assessment;
    window.__PPIE_LAST__ = analyze;
    window.__STANDARD_REPORT__ = report;
    window.__REPORT_MODELS__ = models;
    window.__ENGINE_TRACE__ = state.trace;
    Sheets()?.setContext?.({ report, analyze, assessment });
    bindChrome();
    ensureTraceButton();
    const gen = document.getElementById('module-generated');
    if (gen) gen.textContent = formatGeneratedAt();
    const title = document.querySelector('.module-title');
    if (title) title.textContent = 'Clinical dashboard';
    showView('home');
  }

  function showError(msg) {
    const root = document.getElementById('page-module');
    if (root) root.innerHTML = `<div class="empty-state" role="alert">${esc(msg)}</div>`;
  }

  global.PpieShell = { mount, showError, showView };
})(window);
