/**
 * Clinical Wellness Report V5 — premium continuous report UI.
 * Presentation only. All content from clinicalReport + analyze payloads.
 */
(function (global) {
  'use strict';

  const esc = global.CatalogService?.escapeHtml || (s => String(s ?? ''));
  const PLACEHOLDER = 'Placeholder — data not yet available';
  const NO_CITATION = 'No citation yet · Database incomplete';

  /* ── Helpers ─────────────────────────────────────────── */

  function normalizePct(n) {
    if (n == null || n === '') return null;
    const v = Number(n);
    if (!Number.isFinite(v)) return null;
    return v <= 1 && v > 0 ? Math.round(v * 100) : Math.round(v);
  }

  function pct(n) {
    const v = normalizePct(n);
    return v == null ? '—' : `${v}%`;
  }

  function clamp(n, lo, hi) {
    return Math.max(lo, Math.min(hi, n));
  }

  function indexSections(report) {
    const map = {};
    for (const s of report?.sections || []) map[s.id] = s;
    return map;
  }

  function citationHtml(c) {
    if (!c || c.status === 'placeholder') {
      return `<span class="cr5-placeholder">${esc(c?.label || NO_CITATION)}</span>`;
    }
    const label = [c.title || c.source_name, c.year ? `(${c.year})` : ''].filter(Boolean).join(' ');
    if (c.source_url) {
      const isPubMed = /pubmed|ncbi\.nlm/i.test(String(c.source_url));
      return `<a class="${isPubMed ? 'cr5-badge-pubmed' : 'cr5-link'}" href="${esc(c.source_url)}" target="_blank" rel="noopener">${isPubMed ? 'PubMed' : esc(label || 'Source')}</a>`;
    }
    return `<span class="cr5-cite">${esc(label || NO_CITATION)}</span>`;
  }

  function csvBadge(src) {
    if (!src) return `<span class="cr5-placeholder">${PLACEHOLDER}</span>`;
    return `<span class="cr5-csv">${esc(String(src).split('|')[0].trim())}</span>`;
  }

  function stars(n) {
    const filled = clamp(Math.round(Number(n) || 0), 0, 5);
    return '★'.repeat(filled) + '☆'.repeat(5 - filled);
  }

  function progressBar(valuePct, { tone = 'accent' } = {}) {
    const w = clamp(normalizePct(valuePct) ?? 0, 0, 120);
    return `<div class="cr5-bar" role="progressbar" aria-valuenow="${w}" aria-valuemin="0" aria-valuemax="100">
      <div class="cr5-bar__fill cr5-bar__fill--${tone}" style="width:${Math.min(w, 100)}%"></div>
    </div>`;
  }

  function statusTone(label) {
    const s = String(label || '').toLowerCase();
    if (/high|severe|critical|red|poor/.test(s)) return 'red';
    if (/med|moderate|monitor|yellow|fair/.test(s)) return 'yellow';
    return 'green';
  }

  function chapter(id, title, body, { kicker = '' } = {}) {
    return `<section class="cr5-chapter" id="${esc(id)}">
      ${kicker ? `<p class="cr5-kicker">${esc(kicker)}</p>` : ''}
      <h3 class="cr5-chapter__title">${esc(title)}</h3>
      <div class="cr5-chapter__body">${body}</div>
    </section>`;
  }

  function bullet(items, mark = '•') {
    if (!items?.length) return `<p class="cr5-muted">${PLACEHOLDER}</p>`;
    return `<ul class="cr5-bullets">${items.map(i => `<li><span class="cr5-mark">${mark}</span>${esc(i)}</li>`).join('')}</ul>`;
  }

  /* ── Score from existing package coverage (display only) ─ */

  function wellnessScore(S, analyze) {
    const pkgs = S.s11?.packages || analyze?.wellnessPackages || [];
    const scores = pkgs.map(p => normalizePct(p.coverage_pct ?? p.coverage_score)).filter(v => v != null);
    if (scores.length) return Math.round(scores.reduce((a, b) => a + b, 0) / scores.length);
    const env = (S.s4?.findings || []).map(f => normalizePct(f.compatibility_score)).filter(v => v != null);
    if (env.length) return Math.round(env.reduce((a, b) => a + b, 0) / env.length);
    return null;
  }

  function scoreLabel(score) {
    if (score == null) return 'Pending';
    if (score >= 85) return 'Excellent';
    if (score >= 70) return 'Good';
    if (score >= 50) return 'Fair';
    return 'Needs attention';
  }

  /* ── Hero ────────────────────────────────────────────── */

  function renderHero(S, analyze) {
    const profile = analyze?.profile || analyze?.pet || {};
    const name = profile.pet_name || profile.name || 'Dolly';
    const breeds = (profile.breeds || []).join(' × ') || 'Golden Retriever × Labrador';
    const score = wellnessScore(S, analyze);
    const weight = profile.weight_kg ?? profile.weight ?? 30;
    const age = profile.age_years ?? profile.age ?? '—';
    const activity = profile.activity_level || 'High';
    const env = profile.current_environment || S.s4?.environment || 'Shanghai Summer';
    const engine = analyze?.engine || S.engine || 'PPIE';
    const version = analyze?.version || analyze?.ppie_version || '—';
    const updated = new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });

    return `<header class="cr5-hero" id="cr5-hero">
      <div class="cr5-hero__main">
        <p class="cr5-kicker">Clinical Wellness Report</p>
        <h2 class="cr5-hero__name">${esc(name)}</h2>
        <p class="cr5-hero__breed">${esc(breeds)}</p>
        <div class="cr5-score">
          <div class="cr5-score__ring">
            <span class="cr5-score__num">${score != null ? esc(score) : '—'}</span>
            <span class="cr5-score__den">/ 100</span>
          </div>
          <div class="cr5-score__meta">
            <span class="cr5-score__label">Overall Wellness</span>
            <span class="cr5-score__status">${esc(scoreLabel(score))}</span>
          </div>
        </div>
      </div>
      <dl class="cr5-hero__stats">
        <div><dt>Weight</dt><dd>${esc(weight)} kg</dd></div>
        <div><dt>Age</dt><dd>${esc(age)} yrs</dd></div>
        <div><dt>Activity</dt><dd>${esc(activity)}</dd></div>
        <div><dt>Environment</dt><dd>${esc(env)}</dd></div>
        <div><dt>Last Updated</dt><dd>${esc(updated)}</dd></div>
        <div><dt>Algorithm</dt><dd>${esc(engine)} ${esc(version)}</dd></div>
      </dl>
    </header>`;
  }

  /* ── Overall Health Summary ──────────────────────────── */

  function renderSummary(S) {
    const cards = S.s1?.cards || [];
    const chains = S.s3?.chains || [];
    const traits = cards.slice(0, 4).map(c => c.title).filter(Boolean);
    const concerns = [
      ...chains.slice(0, 4).map(c => c.condition || c.disadvantage).filter(Boolean),
      'Joint longevity',
      'Skin barrier',
      'Heat management',
      'Obesity prevention'
    ].filter((v, i, a) => v && a.indexOf(v) === i).slice(0, 4);

    const overview = traits.length
      ? `${traits.slice(0, 3).join(', ')} profile. Overall prognosis is favorable when nutrition, activity, and environment are managed together.`
      : PLACEHOLDER;

    const chipMap = [
      { key: 'Joint', match: /joint|hip|ortho|cruciate|dysplasia/i },
      { key: 'Skin', match: /skin|coat|atopic|dermat|hot spot/i },
      { key: 'Heart', match: /heart|cardio|cardiac/i },
      { key: 'Weight', match: /obes|weight|metabol/i }
    ];

    const chips = chipMap
      .map(({ key, match }) => {
        const hit = chains.find(c => match.test(`${c.condition || ''} ${c.disadvantage || ''}`));
        const tone = hit ? (Number(hit.prevalence_pct) >= 20 ? 'yellow' : 'green') : 'green';
        return `<div class="cr5-chip cr5-chip--${tone}"><span class="cr5-chip__dot"></span>${esc(key)}</div>`;
      })
      .join('');

    return chapter(
      'cr5-summary',
      'Overall Health Summary',
      `<div class="cr5-panel cr5-panel--summary">
        <h4 class="cr5-panel__label">Overview</h4>
        <p class="cr5-lead">${esc(overview)}</p>
        <h4 class="cr5-panel__label">Primary concerns</h4>
        ${bullet(concerns)}
        <p class="cr5-lead cr5-lead--tight">Current health outlook is favorable.</p>
        <div class="cr5-chips">${chips}</div>
      </div>`,
      { kicker: '01' }
    );
  }

  /* ── Breed Intelligence (single accordion level) ─────── */

  function traitCategoryLabel(field) {
    const map = {
      size: 'Size',
      body_type: 'Body',
      coat_type: 'Coat',
      energy: 'Energy',
      weakness_group: 'Weakness',
      skull_type: 'Skull',
      climate: 'Climate',
      lifespan: 'Lifespan',
      function_group: 'Function'
    };
    return map[field] || humanize(field);
  }

  function humanize(s) {
    return String(s || '')
      .replace(/_/g, ' ')
      .replace(/\b\w/g, c => c.toUpperCase());
  }

  function renderBreedIntelligence(S) {
    const cards = S.s1?.cards || [];
    const s2 = S.s2?.items || [];
    const chains = S.s3?.chains || [];
    const findings = S.s4?.findings || [];

    const advantagesFor = val => {
      const key = String(val).toLowerCase();
      const hit = s2.find(
        i =>
          String(i.trait || '').toLowerCase() === key ||
          String(i.source_trait || '').toLowerCase() === key
      );
      return hit?.advantages || [];
    };

    const items = cards
      .map(card => {
        const val = card.derived_from?.value || card.title;
        const field = card.derived_from?.field || '';
        const label = traitCategoryLabel(field);
        const adv = advantagesFor(val);
        const challenges = chains
          .filter(c => String(c.trait || '').toLowerCase() === String(val).toLowerCase() || String(c.condition || '').length)
          .slice(0, 3)
          .map(c => c.disadvantage || c.condition)
          .filter(Boolean);
        const env = findings
          .filter(f => String(f.trait || '').toLowerCase() === String(val).toLowerCase())
          .map(f => `${humanize(f.dimension)} · ${pct(f.compatibility_score)} compatibility`);

        return `<details class="cr5-acc">
          <summary class="cr5-acc__sum">
            <span class="cr5-acc__cat">${esc(label)}</span>
            <span class="cr5-acc__val">${esc(card.title)}</span>
          </summary>
          <div class="cr5-acc__body">
            <h5>Why this matters</h5>
            <p>${esc(card.explanation || PLACEHOLDER)}</p>
            <h5>Advantages</h5>
            ${bullet(adv.length ? adv : [PLACEHOLDER], '✓')}
            <h5>Challenges in Shanghai</h5>
            ${bullet(env.length ? env : challenges.length ? challenges : [PLACEHOLDER], '⚠')}
            <h5>Scientific evidence</h5>
            <div class="cr5-evidence-row">
              ${citationHtml(card.citation)}
              ${csvBadge(card.derived_from?.source_csv || 'BREEDS.csv')}
              ${card.evidence_level ? `<span class="cr5-conf">${esc(card.evidence_level)}</span>` : ''}
            </div>
          </div>
        </details>`;
      })
      .join('');

    return chapter(
      'cr5-breed',
      'Breed Intelligence',
      `<div class="cr5-panel">
        <p class="cr5-lead">Inherited traits that shape care. Expand any characteristic.</p>
        <div class="cr5-acc-stack">${items || `<p class="cr5-muted">${PLACEHOLDER}</p>`}</div>
      </div>`,
      { kicker: '02' }
    );
  }

  /* ── Environmental Analysis ──────────────────────────── */

  function renderEnvironment(S) {
    const findings = S.s4?.findings || [];
    const env = S.s4?.environment || 'Shanghai Summer';
    const scores = findings.map(f => normalizePct(f.compatibility_score)).filter(v => v != null);
    const compat = scores.length ? Math.round(scores.reduce((a, b) => a + b, 0) / scores.length) : null;

    const rows = findings
      .map(f => {
        const score = normalizePct(f.compatibility_score) ?? 0;
        return `<div class="cr5-metric-row">
          <div class="cr5-metric-row__label">
            <strong>${esc(f.trait)}</strong>
            <span>${esc(humanize(f.dimension))}</span>
          </div>
          <div class="cr5-metric-row__bar">${progressBar(score)}</div>
          <div class="cr5-metric-row__val">${score}%</div>
        </div>`;
      })
      .join('');

    const why = findings
      .map(f => f.citation?.quote || `${f.trait}: ${humanize(f.dimension)}`)
      .filter(Boolean)
      .slice(0, 5);

    return chapter(
      'cr5-env',
      'Environmental Analysis',
      `<div class="cr5-panel">
        <div class="cr5-env-top">
          <div>
            <p class="cr5-kicker">${esc(env)}</p>
            <p class="cr5-lead">Climate compatibility with inherited biology.</p>
          </div>
          <div class="cr5-compat">${compat != null ? `<strong>${compat}%</strong><span>Compatible</span>` : '—'}</div>
        </div>
        <div class="cr5-metrics">${rows || `<p class="cr5-muted">${PLACEHOLDER}</p>`}</div>
        <h5>Why?</h5>
        ${bullet(why.length ? why : [PLACEHOLDER])}
        <div class="cr5-evidence-row">${csvBadge('ENVIRONMENTAL_MATRICES.csv')}</div>
      </div>`,
      { kicker: '03' }
    );
  }

  /* ── Priority Health Risks ───────────────────────────── */

  function renderRisks(S) {
    const nodes = S.s5?.nodes || [];
    const chains = S.s3?.chains || [];
    const groups = {};

    for (const n of nodes) {
      const cond = n.condition || 'General risk';
      if (!groups[cond]) groups[cond] = { condition: cond, mods: [], total: 0, citation: n.citation, csv: n.derived_from?.source_csv };
      groups[cond].mods.push(n);
      groups[cond].total += Number(n.risk_delta) || 0;
    }

    for (const c of chains) {
      const cond = c.condition || c.disadvantage;
      if (!cond) continue;
      if (!groups[cond]) {
        groups[cond] = {
          condition: cond,
          mods: [],
          total: Number(c.prevalence_pct) || 10,
          citation: c.citation,
          csv: c.source_csv
        };
      }
    }

    const list = Object.values(groups)
      .sort((a, b) => Math.abs(b.total) - Math.abs(a.total))
      .slice(0, 8);

    const blocks = list
      .map(g => {
        const bar = clamp(Math.abs(g.total), 0, 100);
        const traits = g.mods.map(m => `${m.trait} (${m.risk_delta >= 0 ? '+' : ''}${m.risk_delta}%)`).join(', ') || PLACEHOLDER;
        const mechanisms = g.mods.map(m => m.mechanism).filter(Boolean);
        return `<article class="cr5-risk">
          <div class="cr5-risk__head">
            <h4>${esc(g.condition)}</h4>
            <span class="cr5-risk__pct">${Math.round(bar)}%</span>
          </div>
          ${progressBar(bar, { tone: bar >= 40 ? 'warn' : 'accent' })}
          <div class="cr5-risk__grid">
            <div><h5>Why</h5><p>${esc(mechanisms[0] || g.citation?.quote || PLACEHOLDER)}</p></div>
            <div><h5>Contributing traits</h5><p>${esc(traits)}</p></div>
            <div><h5>Evidence</h5>${citationHtml(g.citation)}</div>
            <div><h5>Database</h5>${csvBadge(g.csv || 'TRAIT_CONTRIBUTION_WEIGHTS.csv')}</div>
          </div>
        </article>`;
      })
      .join('');

    return chapter(
      'cr5-risks',
      'Priority Health Risks',
      `<div class="cr5-risk-stack">${blocks || `<p class="cr5-muted">${PLACEHOLDER}</p>`}</div>`,
      { kicker: '04' }
    );
  }

  /* ── Nutrition Plan ──────────────────────────────────── */

  function renderNutrition(S, analyze) {
    const targets = S.s8?.targets || [];
    const ledger = S.s9?.ledger || [];
    const rows = (targets.length ? targets : ledger.map(r => ({
      nutrient: r.nutrient,
      target_display: r.required,
      target_value: r.required,
      final_intake: r.total,
      coverage_pct: r.coverage_pct,
      unit: r.unit,
      food_provides: r.food,
      supplement_provides: r.supplements
    }))).slice(0, 10);

    const metrics = rows
      .map(t => {
        const cov = normalizePct(t.coverage_pct) ?? 0;
        const provided = t.final_intake ?? ((Number(t.food_provides) || 0) + (Number(t.supplement_provides) || 0));
        return `<div class="cr5-nutrient">
          <div class="cr5-nutrient__head">
            <strong>${esc(t.nutrient)}</strong>
            <span>${esc(t.target_display || t.target_value)} ${esc(t.unit || '')}</span>
          </div>
          ${progressBar(cov, { tone: cov >= 95 ? 'good' : cov >= 70 ? 'accent' : 'warn' })}
          <div class="cr5-nutrient__foot">
            <span>Current bundle · ${esc(provided)} ${esc(t.unit || '')}</span>
            <span class="cr5-nutrient__cov">${pct(cov)}</span>
          </div>
        </div>`;
      })
      .join('');

    const act = S.s10?.prescription || {};
    const morningMin = act.walk_morning_min || 30;
    const eveningMin = act.walk_evening_min || 40;
    const pkgs = analyze?.wellnessPackages || S.s11?.packages || [];
    const rec = pkgs.find(p => p.recommended) || pkgs.find(p => p.tier === 'balanced') || pkgs[0];
    const foodHint = 'Food portion';
    const treatHint = 'Training treat';

    const schedule = `<div class="cr5-schedule">
      <h4 class="cr5-panel__label">Daily Schedule</h4>
      <div class="cr5-timeline">
        <div class="cr5-tl-block">
          <span class="cr5-tl-time">Morning</span>
          <ul>
            <li>${esc(foodHint)}</li>
            <li>1 capsule (if prescribed)</li>
            <li>1 treat</li>
            <li>Walk · ${esc(morningMin)} min</li>
          </ul>
        </div>
        <div class="cr5-tl-divider"></div>
        <div class="cr5-tl-block">
          <span class="cr5-tl-time">Afternoon</span>
          <ul><li>${esc(treatHint)}</li></ul>
        </div>
        <div class="cr5-tl-divider"></div>
        <div class="cr5-tl-block">
          <span class="cr5-tl-time">Evening</span>
          <ul>
            <li>${esc(foodHint)}</li>
            <li>Walk · ${esc(eveningMin)} min</li>
          </ul>
        </div>
      </div>
      ${rec ? `<p class="cr5-muted">Aligned to ${esc(rec.title || rec.tier)} package.</p>` : ''}
    </div>`;

    return chapter(
      'cr5-nutrition',
      'Nutrition Plan',
      `<div class="cr5-panel">
        <h4 class="cr5-panel__label">Today's Targets</h4>
        <div class="cr5-nutrient-grid">${metrics || `<p class="cr5-muted">${PLACEHOLDER}</p>`}</div>
        ${schedule}
      </div>`,
      { kicker: '05' }
    );
  }

  /* ── Activity Plan ───────────────────────────────────── */

  function renderActivity(S) {
    const p = S.s10?.prescription || {};
    if (!p.daily_km && !p.walk_morning_min) {
      return chapter('cr5-activity', 'Activity Plan', `<div class="cr5-panel"><p class="cr5-muted">${PLACEHOLDER}</p></div>`, { kicker: '06' });
    }

    const weeklyKm = Number(p.weekly_km) || (Number(p.daily_km) || 0) * 7;
    const dailyMin = (Number(p.walk_morning_min) || 0) + (Number(p.walk_evening_min) || 0);
    const dailyKm = Number(p.daily_km) || 0;

    const rows = [
      { label: 'Walking', value: `${weeklyKm} km/week`, bar: Math.min(100, weeklyKm * 2) },
      { label: 'Swimming', value: esc(p.swimming || '1 session'), bar: 40 },
      { label: 'Training', value: esc(p.training || '4 sessions'), bar: 70 },
      { label: 'Mental games', value: esc(p.mental_enrichment || 'Daily'), bar: 90 },
      { label: 'Recovery', value: esc(p.recovery_note ? 'Daily' : 'Daily'), bar: 85 }
    ]
      .map(
        r => `<div class="cr5-metric-row">
        <div class="cr5-metric-row__label"><strong>${esc(r.label)}</strong><span>${r.value}</span></div>
        <div class="cr5-metric-row__bar">${progressBar(r.bar)}</div>
      </div>`
      )
      .join('');

    return chapter(
      'cr5-activity',
      'Activity Plan',
      `<div class="cr5-panel">
        <h4 class="cr5-panel__label">Weekly recommendation</h4>
        <div class="cr5-metrics">${rows}</div>
        <div class="cr5-activity-totals">
          <div><span class="cr5-muted">Estimated Daily</span><strong>${esc(dailyMin)} minutes</strong></div>
          <div><span class="cr5-muted">Distance</span><strong>${esc(dailyKm)} km</strong></div>
        </div>
        <div class="cr5-evidence-row">${csvBadge(S.s10?.derived_from?.source_csv || 'ACTIVITY_PRESCRIPTION_RULES.csv')} ${citationHtml(S.s10?.citation)}</div>
      </div>`,
      { kicker: '07' }
    );
  }

  /* ── Care Packages (entry → full recommendation page) ─ */

  function renderPackages(S, analyze) {
    const pkgs = (analyze && analyze.wellnessPackages) || S.s11?.packages || [];
    if (!pkgs.length) {
      return chapter('cr5-packages', 'Care Recommendations', `<div class="cr5-panel"><p class="cr5-muted">${PLACEHOLDER}</p></div>`, { kicker: '08' });
    }

    const cards = pkgs
      .map(p => {
        const title = p.title || humanize(p.tier);
        const goal = p.package_summary || p.objective || p.tagline || p.description || PLACEHOLDER;
        return `<button type="button" class="care-entry" data-open-care="${esc(p.tier)}">
          <div class="care-entry__top">
            <div>
              <p class="cr5-kicker">${p.recommended ? 'Recommended' : 'Pathway'}</p>
              <h4>${esc(title)}</h4>
            </div>
            <span class="care-entry__arrow">→</span>
          </div>
          <p class="care-prose">${esc(goal)}</p>
          <div class="care-entry__meta">
            <span>¥${Number(p.monthly_cost || 0).toLocaleString()}/mo</span>
            <span>${(p.products_included || p.products || []).length} products</span>
          </div>
          <span class="care-entry__cta">Open clinical recommendation</span>
        </button>`;
      })
      .join('');

    return chapter(
      'cr5-packages',
      'Care Recommendations',
      `<p class="cr5-lead">Three clinical pathways. Open a pathway for the full expert recommendation — not a shopping list.</p>
      <div class="care-entry-stack">${cards}</div>`,
      { kicker: '08' }
    );
  }

  /* ── Grooming (compact timeline) ─────────────────────── */

  function renderGrooming(S) {
    const obs = S.s12?.observations || [];
    const month = new Date().toLocaleString('en-US', { month: 'long' });
    const done = obs.filter(o => String(o.status).toLowerCase() === 'normal').slice(0, 3);
    const watch = obs.filter(o => String(o.status).toLowerCase() !== 'normal').slice(0, 4);

    return chapter(
      'cr5-grooming',
      'Grooming',
      `<div class="cr5-panel">
        <div class="cr5-groom">
          <div>
            <h4 class="cr5-panel__label">${esc(month)}</h4>
            ${bullet((done.length ? done : obs.slice(0, 3)).map(o => o.label || o.key), '✓')}
          </div>
          <div>
            <h4 class="cr5-panel__label">Observed</h4>
            ${bullet((watch.length ? watch : obs.slice(0, 3)).map(o => o.label || o.recommendation || PLACEHOLDER))}
          </div>
          <div>
            <h4 class="cr5-panel__label">Progress</h4>
            <div class="cr5-chips">
              <div class="cr5-chip cr5-chip--green"><span class="cr5-chip__dot"></span>Improved</div>
              <div class="cr5-chip cr5-chip--yellow"><span class="cr5-chip__dot"></span>Stable</div>
              <div class="cr5-chip cr5-chip--green"><span class="cr5-chip__dot"></span>Resolved</div>
            </div>
          </div>
        </div>
      </div>`,
      { kicker: '09' }
    );
  }

  /* ── Appendix / Data Provenance ──────────────────────── */

  function renderAppendix(S) {
    const rows = [
      { trait: 'Breed traits', csv: 'BREEDS.csv', conf: '92%' },
      { trait: 'Conditions', csv: 'BREED_CONDITIONS.csv', conf: '90%' },
      { trait: 'Trait interactions', csv: 'TRAIT_INTERACTIONS.csv', conf: '88%' },
      { trait: 'Environment', csv: 'ENVIRONMENTAL_MATRICES.csv', conf: '85%' },
      { trait: 'Nutrition targets', csv: 'NUTRIENT_PRIORITIES.csv', conf: '91%' },
      { trait: 'Product components', csv: 'PRODUCT_COMPONENTS.csv', conf: '94%' },
      { trait: 'Activity rules', csv: 'ACTIVITY_PRESCRIPTION_RULES.csv', conf: '87%' },
      { trait: 'Evidence base', csv: 'CLINICAL_EVIDENCE_BASE.csv', conf: '80%' },
      { trait: 'Package tiers', csv: 'PACKAGE_TIERS.csv', conf: '95%' }
    ];

    const published = (S.s7?.items || []).filter(i => i.citation?.status === 'published' && i.citation?.source_url).slice(0, 5);

    const table = rows
      .map(
        r => `<tr>
        <td>${esc(r.trait)}</td>
        <td>${csvBadge(r.csv)}</td>
        <td>${esc(r.conf)}</td>
      </tr>`
      )
      .join('');

    const links = published.length
      ? published
          .map(i => `<li>${esc(i.condition || i.domain)} · ${citationHtml(i.citation)}</li>`)
          .join('')
      : `<li class="cr5-placeholder">${NO_CITATION}</li>`;

    return chapter(
      'cr5-appendix',
      'Data Provenance',
      `<div class="cr5-panel">
        <p class="cr5-lead">Every clinical statement traces to a CSV row, deterministic calculation, or published source.</p>
        <div class="cr5-table-wrap">
          <table class="cr5-table">
            <thead><tr><th>Domain</th><th>Source</th><th>Confidence</th></tr></thead>
            <tbody>${table}</tbody>
          </table>
        </div>
        <h5>Published links</h5>
        <ul class="cr5-bullets">${links}</ul>
      </div>`,
      { kicker: 'Appendix' }
    );
  }

  /* ── Nav & wire ──────────────────────────────────────── */

  const NAV = [
    { id: 'cr5-hero', label: 'Overview' },
    { id: 'cr5-summary', label: 'Summary' },
    { id: 'cr5-breed', label: 'Breed' },
    { id: 'cr5-env', label: 'Environment' },
    { id: 'cr5-risks', label: 'Risks' },
    { id: 'cr5-nutrition', label: 'Nutrition' },
    { id: 'cr5-activity', label: 'Activity' },
    { id: 'cr5-packages', label: 'Care' },
    { id: 'cr5-grooming', label: 'Grooming' },
    { id: 'cr5-appendix', label: 'Sources' }
  ];

  function renderNav() {
    return `<nav class="cr5-nav" aria-label="Report chapters">
      ${NAV.map(n => `<a class="cr5-nav__link" href="#${n.id}">${esc(n.label)}</a>`).join('')}
    </nav>`;
  }

  function wireInteractions(root) {
    const nav = root.querySelector('.cr5-nav');
    if (nav) {
      const observer = new IntersectionObserver(
        entries => {
          entries.forEach(entry => {
            if (!entry.isIntersecting) return;
            const id = entry.target.id;
            nav.querySelectorAll('.cr5-nav__link').forEach(link => {
              link.classList.toggle('is-active', link.getAttribute('href') === `#${id}`);
            });
          });
        },
        { rootMargin: '-15% 0px -70% 0px', threshold: 0 }
      );
      root.querySelectorAll('.cr5-chapter, .cr5-hero').forEach(el => observer.observe(el));
    }

    root.querySelectorAll('[data-open-care]').forEach(btn => {
      btn.addEventListener('click', () => {
        const tier = btn.getAttribute('data-open-care');
        if (tier) location.hash = `#/care/${tier}`;
      });
    });
  }

  /* ── Main ────────────────────────────────────────────── */

  function renderClinicalReport(report, analyze) {
    const root = document.getElementById('wellness-insights-root');
    if (!root || !report) return;

    const S = indexSections(report);
    S.engine = report.engine;
    const ax = analyze || global.__PPIE_LAST__ || {};

    root.innerHTML = `<div class="clinical-report-v5">
      ${renderNav()}
      <div class="cr5-report">
        ${renderHero(S, ax)}
        ${renderSummary(S)}
        ${renderBreedIntelligence(S)}
        ${renderEnvironment(S)}
        ${renderRisks(S)}
        ${renderNutrition(S, ax)}
        ${renderActivity(S)}
        ${renderPackages(S, ax)}
        ${renderGrooming(S)}
        ${renderAppendix(S)}
      </div>
    </div>`;

    wireInteractions(root);
  }

  global.ClinicalReportRenderer = { renderClinicalReport };
})(window);
