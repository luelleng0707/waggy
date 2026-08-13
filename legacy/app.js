/* Wagtopia — pure API renderer (products from /api/v1/store + /api/v1/analyze) */

(function () {
  'use strict';

  const Catalog = window.CatalogService;
  const { API_BASE, API_KEY } = window.WagtopiaAPI || {
    API_BASE: window.location.origin,
    API_KEY: ''
  };
  const esc = Catalog.escapeHtml;
  const CANONICAL_DEMO_PROFILE = Object.freeze({
    name: 'Dolly',
    pet_name: 'Dolly',
    breeds: ['Labrador Retriever', 'Golden Retriever'],
    primary_breed: 'Labrador Retriever',
    secondary_breed: 'Golden Retriever',
    breed_split_pct: 50,
    birthday: '2021-04-15',
    weight: 30,
    height_cm: 60,
    sex: 'Female',
    activity_level: 'Moderate',
    current_environment: 'Temperate Outdoor',
    bcs: 5.5,
    observed_conditions: ['joint_stiffness', 'itching'],
    groomer_observations: ''
  });

  let analysis = null;
  let bootPromise = null;
  let activeProfile = JSON.parse(JSON.stringify(CANONICAL_DEMO_PROFILE));

  function emptyState(message) {
    return `<div class="empty-state" role="status">${esc(message)}</div>`;
  }

  // Photo pools for grooming narrative only (not products).
  const dogClean = [
    'https://images.unsplash.com/photo-1587300003388-59208cc962cb?w=400&q=80',
    'https://images.unsplash.com/photo-1633722715463-d30f4f325e24?w=400&q=80',
    'https://images.unsplash.com/photo-1558787533-047edbf9612a?w=400&q=80',
    'https://images.unsplash.com/photo-1561037404-61cd46aa615c?w=400&q=80',
    'https://images.unsplash.com/photo-1548199973-03cce0bbc87b?w=400&q=80',
    'https://images.unsplash.com/photo-1583511655857-d19b40a7a54e?w=400&q=80'
  ];
  const dogMessy = [
    'https://images.unsplash.com/photo-1530281700549-e82e7bf110d6?w=400&q=80',
    'https://images.unsplash.com/photo-1477884213360-49e9a8e46e03?w=400&q=80',
    'https://images.unsplash.com/photo-1601758228041-f3b2795255f1?w=400&q=80',
    'https://images.unsplash.com/photo-1516734212186-a967f81ad0d4?w=400&q=80',
    'https://images.unsplash.com/photo-1583337130417-3346a1be7dee?w=400&q=80',
    'https://images.unsplash.com/photo-1596492784531-6e8551225179?w=400&q=80'
  ];
  const detailShots = [
    'https://images.unsplash.com/photo-1616190179415-1c81e4e8f882?w=200&q=80',
    'https://images.unsplash.com/photo-1588943211346-0908a1e0c696?w=200&q=80',
    'https://images.unsplash.com/photo-1598133894008-61f7c073fd69?w=200&q=80',
    'https://images.unsplash.com/photo-1608093273550-f3318751143e?w=200&q=80',
    'https://images.unsplash.com/photo-1546527868-ccb7ee7dfa6a?w=200&q=80'
  ];

  // Grooming narrative metadata only — products are catalog product_id lists.
  const sessions = {
    jul12: {
      date: 'July 12, 2025',
      groomer: 'Emma Chen',
      duration: '2h 15min',
      services: 'Full Groom · Hydration · Ear Care',
      groomerNote:
        "Dolly's coat softness has improved significantly since her last visit. We recommend continued weekly eye-care maintenance and additional hydration support during summer months.",
      problems: [
        { img: detailShots[0], text: 'Recurring teary eyes observed around inner corners' },
        { img: detailShots[1], text: 'Dirty ears noted during initial cleaning assessment' },
        { img: detailShots[2], text: 'Overgrown paw fur trapping moisture between pads' },
        { img: detailShots[3], text: 'Mild coat dryness near back and shoulder area' },
        { img: detailShots[4], text: 'Light tangling around hind leg feathering' }
      ],
      results: [
        { img: dogClean[1], text: 'Teary eyes resolved', status: 'resolved' },
        { img: dogClean[2], text: 'Ear cleaning completed', status: 'completed' },
        { img: dogClean[3], text: 'Paw fur trimmed & moisturized', status: 'completed' },
        { img: dogClean[4], text: 'Hydration treatment applied', status: 'improved' },
        { img: dogClean[5], text: 'Coat softness improved', status: 'improved' }
      ],
      productIds: ['TR007', 'TR003', 'TR005', 'TR001', 'TR011']
    },
    jul18: {
      date: 'July 18, 2025',
      groomer: 'Sarah Kim',
      duration: '1h 45min',
      services: 'Express Bath · Eye Care · Paw Trim',
      groomerNote:
        'Quick refresh session for Dolly before the weekend social event. Eye area looking much clearer.',
      problems: [
        { img: detailShots[1], text: 'Light tear residue returning after 5 days' },
        { img: detailShots[2], text: 'Paw pads slightly dry from park walks' },
        { img: detailShots[0], text: 'Minor coat dullness from outdoor play' }
      ],
      results: [
        { img: dogClean[0], text: 'Eye area refreshed', status: 'resolved' },
        { img: dogClean[2], text: 'Paw balm applied', status: 'completed' },
        { img: dogClean[1], text: 'Coat revitalized with gloss treatment', status: 'improved' }
      ],
      productIds: ['TR007', 'TR003', 'TR005', 'TR002']
    },
    aug2: {
      date: 'August 2, 2025',
      groomer: 'Emma Chen',
      duration: '2h 30min',
      services: 'Premium Full Groom · De-shed · Spa Package',
      groomerNote:
        "Comprehensive session — summer coat shedding heavily. Recommend bi-weekly brushing and hydration support.",
      problems: [
        { img: detailShots[3], text: 'Heavy seasonal shedding across torso' },
        { img: detailShots[4], text: 'Tangled undercoat behind ears' },
        { img: detailShots[0], text: 'Sun-exposed coat dryness on back' },
        { img: detailShots[1], text: 'Ear wax buildup from swimming' },
        { img: detailShots[2], text: 'Cracked paw pad edges from hot pavement' }
      ],
      results: [
        { img: dogClean[3], text: 'De-shed treatment complete', status: 'completed' },
        { img: dogClean[4], text: 'Undercoat detangled', status: 'resolved' },
        { img: dogClean[5], text: 'Deep hydration mask applied', status: 'improved' },
        { img: dogClean[0], text: 'Ears deep cleaned', status: 'completed' },
        { img: dogClean[1], text: 'Paw pads restored & protected', status: 'improved' }
      ],
      productIds: ['TR007', 'TR005', 'TR006', 'TR004', 'TR011']
    },
    aug15: {
      date: 'August 15, 2025',
      groomer: 'Marcus Lee',
      duration: '1h 30min',
      services: 'Maintenance Trim · Nail Care · Dental Refresh',
      groomerNote:
        'Maintenance visit — Dolly is maintaining beautifully. Recommend continued functional treats from her care plan.',
      problems: [
        { img: detailShots[2], text: 'Nails slightly overgrown from active play' },
        { img: detailShots[4], text: 'Minor tartar buildup on rear molars' },
        { img: detailShots[0], text: 'Slight coat fuzziness between grooms' }
      ],
      results: [
        { img: dogClean[2], text: 'Nails trimmed & filed smooth', status: 'completed' },
        { img: dogClean[3], text: 'Dental refresh completed', status: 'completed' },
        { img: dogClean[4], text: 'Coat touch-up & brush out', status: 'improved' }
      ],
      productIds: ['TR003', 'TR005', 'TR011', 'TR001']
    }
  };

  function productCardHTML(product, reason) {
    if (!product) return '';
    const name = product.product_name || product.name || product.product_id;
    const category = [product.category, product.subcategory].filter(Boolean).join(' · ');
    const desc =
      reason ||
      product.short_description ||
      product.description ||
      Catalog.feedingDisplay(product) ||
      'Matched from live catalog for Dolly’s care plan.';
    return `
      <div class="product-card" data-product-id="${esc(product.product_id)}" role="button" tabindex="0">
        ${Catalog.imageHtml(product, name)}
        <div class="product-card-body">
          <h4>${esc(name)}</h4>
          <div class="product-category">${esc(category || 'Catalog')}</div>
          <div class="product-price">${esc(Catalog.formatPrice(product))}</div>
          <div class="product-desc">${esc(desc)}</div>
          <button type="button" class="product-btn" data-product-id="${esc(product.product_id)}" onclick="event.stopPropagation()">View details</button>
        </div>
      </div>`;
  }

  function safeImg(src, alt, className) {
    const cls = className ? ` class="${esc(className)}"` : '';
    return `<img src="${esc(src)}" alt="${esc(alt || '')}"${cls} loading="lazy" onerror="this.onerror=null;this.src='data:image/svg+xml,'+encodeURIComponent('<svg xmlns=&quot;http://www.w3.org/2000/svg&quot; width=&quot;400&quot; height=&quot;280&quot;><rect fill=&quot;%23F2E9EF&quot; width=&quot;100%&quot; height=&quot;100%&quot;/><text x=&quot;50%&quot; y=&quot;50%&quot; text-anchor=&quot;middle&quot; fill=&quot;%23B3266A&quot; font-family=&quot;sans-serif&quot; font-size=&quot;28&quot; dy=&quot;.3em&quot;>?</text></svg>')">`;
  }

  function collectAnalysisProductIds(report) {
    const ids = new Set();
    (report.productRecommendations || report.products || []).forEach(p => {
      if (p && p.product_id) ids.add(String(p.product_id));
    });
    (report.wellnessPackages || []).forEach(pkg => {
      (pkg.products_included || []).forEach(p => {
        if (p && p.product_id) ids.add(String(p.product_id));
      });
    });
    const details = report.packageDetails || {};
    Object.values(details).forEach(detail => {
      (detail.product_cards || []).forEach(p => {
        if (p && p.product_id) ids.add(String(p.product_id));
      });
    });
    const analyses = report.productAnalyses || {};
    if (analyses && typeof analyses === 'object' && !Array.isArray(analyses)) {
      Object.keys(analyses).forEach(id => ids.add(String(id)));
    }
    (report.monthly_plan && report.monthly_plan.items ? report.monthly_plan.items : []).forEach(item => {
      const resolved = Catalog.resolve(item);
      if (resolved) ids.add(resolved.product_id);
    });
    (report.yearly_plan && report.yearly_plan.items ? report.yearly_plan.items : []).forEach(item => {
      const resolved = Catalog.resolve(item);
      if (resolved) ids.add(resolved.product_id);
    });
    return [...ids];
  }

  function renderSuggestedFromAnalysis(report) {
    const ids = collectAnalysisProductIds(report);
    let products = ids.map(id => Catalog.get(id)).filter(Boolean);
    if (!products.length) {
      // Fall back to featured / first store products so UI stays catalog-driven.
      products = Catalog.all().slice(0, 12);
    }
    const byCategory = new Map();
    products.forEach(p => {
      const cat = p.category || 'General';
      if (!byCategory.has(cat)) byCategory.set(cat, []);
      byCategory.get(cat).push(p);
    });
    return [...byCategory.entries()]
      .map(
        ([title, items]) => `
      <div class="rec-category">
        <h3>${esc(title)}</h3>
        <div class="product-carousel">${items.map(p => productCardHTML(p, `Recommended for Dolly · ${title}`)).join('')}</div>
      </div>`
      )
      .join('');
  }

  function renderDiarySession(sessionId, rootEl) {
    const s = sessions[sessionId];
    if (!s) return;
    const reportEl =
      rootEl ||
      document.getElementById('diary-session-root') ||
      document.getElementById('grooming-report');
    if (!reportEl) return;
    reportEl.classList.remove('loaded');
    void reportEl.offsetWidth;

    const beforePhotos = dogMessy
      .slice(0, 6)
      .map((src, i) => {
        const cls = i < 2 ? 'before-label' : '';
        return safeImg(src, `Before treatment ${i + 1}`, cls);
      })
      .join('');
    const afterPhotos = dogClean
      .slice(0, 6)
      .map((src, i) => {
        const cls = i < 2 ? 'after-highlight' : '';
        return safeImg(src, `After treatment ${i + 1}`, cls);
      })
      .join('');
    const problemsHTML = s.problems
      .map(
        p =>
          `<div class="problem-card">${safeImg(p.img, '')}<p>${esc(p.text)}</p></div>`
      )
      .join('');
    const resultsHTML = s.results
      .map(
        r => `<div class="result-card">
        ${safeImg(r.img, '')}
        <div class="result-card-content">
          <p>${esc(r.text)}</p>
          <span class="status-pill ${esc(r.status)}">${esc(r.status)}</span>
        </div>
      </div>`
      )
      .join('');

    const usedProducts = (s.productIds || [])
      .map(id => Catalog.get(id))
      .filter(Boolean);
    const productsHTML = usedProducts
      .map(p => productCardHTML(p, 'Used during this grooming session'))
      .join('');
    const recsHTML = analysis
      ? renderSuggestedFromAnalysis(analysis)
      : emptyState('Loading recommendations from analysis…');

    reportEl.innerHTML = `
      <div class="report-header">
        <h2>Grooming Report</h2>
        <p>${esc(s.date)} · with ${esc(s.groomer)}</p>
        <div class="report-meta">
          <span>⏱ ${esc(s.duration)}</span>
          <span>✂️ ${esc(s.services)}</span>
        </div>
      </div>
      <div class="report-section">
        <h3 class="report-section-title">Before Treatment</h3>
        <div class="photo-grid large">${beforePhotos}</div>
        <p class="subsection-label">Problems Requiring Detailed Attention</p>
        <div class="problem-cards">${problemsHTML}</div>
      </div>
      <div class="report-section">
        <h3 class="report-section-title">After Treatment</h3>
        <div class="photo-grid large">${afterPhotos}</div>
        <p class="subsection-label">Treatment Results</p>
        <div class="result-cards">${resultsHTML}</div>
      </div>
      <div class="report-section">
        <h3 class="report-section-title">Products Used During Session</h3>
        <div class="product-carousel">${productsHTML || emptyState('No catalog products linked to this session.')}</div>
      </div>
      <div class="report-section">
        <h3 class="report-section-title">Groomer Suggestions</h3>
        <div class="groomer-note">
          <p>"${esc(s.groomerNote)}"</p>
          <span class="author">— ${esc(s.groomer)}, Wagtopia Grooming</span>
        </div>
      </div>
      <div class="report-section">
        <h3 class="report-section-title">Recommended for Dolly</h3>
        <div class="rec-intro">
          <p>Suggested products are aligned to Dolly’s clinical priorities from her wellness analysis.</p>
        </div>
        ${recsHTML}
      </div>
    `;
    reportEl.classList.add('loaded');
    bindProductCardClicks(reportEl);
  }

  function openProductModal(productId) {
    const product = Catalog.get(productId);
    const modal = document.getElementById('product-modal');
    const body = document.getElementById('product-modal-body');
    if (!modal || !body || !product) return;

    const comps = Catalog.componentsList(product)
      .map(
        c => `<li><strong>${esc(c.component_name)}</strong>
          ${c.value ? ` · ${esc(c.value)}${esc(c.unit || '')}` : ''}
          <span class="muted">(${esc(c.component_type)})</span></li>`
      )
      .join('');
    const rules = (product.feeding_rules || [])
      .map(
        r =>
          `<li>${esc(r.min_weight_kg)}–${esc(r.max_weight_kg)} kg → ${esc(r.display || `${r.daily_amount}${r.daily_unit}/day`)}</li>`
      )
      .join('');
    const supp = product.supplement
      ? `<p><strong>Supplement</strong> · ${esc(product.supplement.supplement_type || '')}
         · storage ${esc(product.supplement.storage_method || '—')}
         · shelf life ${esc(product.supplement.shelf_life_days || '—')} days</p>`
      : '';
    const bakery = product.bakery
      ? `<p><strong>Bakery / Treat</strong> · ${esc(product.bakery.texture || '')}
         · protein ${esc(product.bakery.protein_source || '')}
         · ${esc(product.bakery.weight_g || '')}g
         · storage ${esc(product.bakery.storage_method || '—')}</p>`
      : '';
    const funcs = (product.functions || [])
      .map(f => `<li>${esc(f.function)}</li>`)
      .join('');

    body.innerHTML = `
      <div class="product-modal-hero">${Catalog.imageHtml(product)}</div>
      <h2 id="product-modal-title">${esc(product.product_name || product.name)}</h2>
      <p class="muted">${esc(product.brand)} · ${esc(product.product_id)} · ${esc(product.category)}${
        product.subcategory ? ` / ${esc(product.subcategory)}` : ''
      }</p>
      <p class="price">${esc(Catalog.formatPrice(product))} <span class="muted">/ ${esc(product.unit_label || 'unit')}</span></p>
      <p>${esc(product.description || product.short_description || '')}</p>
      <h3>Feeding</h3>
      <p>${esc(Catalog.feedingDisplay(product) || 'No feeding rule for current weight')}</p>
      <ul>${rules || '<li class="muted">No PRODUCT_FEEDING_RULES rows</li>'}</ul>
      <h3>Components</h3>
      <ul>${comps || '<li class="muted">No PRODUCT_COMPONENTS rows</li>'}</ul>
      ${supp}
      ${bakery}
      ${funcs ? `<h3>Functions</h3><ul>${funcs}</ul>` : ''}
      ${
        product.purchase_url
          ? `<p><a href="${esc(product.purchase_url)}" target="_blank" rel="noopener">Purchase →</a></p>`
          : ''
      }
    `;
    modal.hidden = false;
  }

  function closeProductModal() {
    const modal = document.getElementById('product-modal');
    if (modal) modal.hidden = true;
  }

  function bindProductCardClicks(root) {
    if (!root) return;
    root.querySelectorAll('[data-product-id]').forEach(el => {
      if (el.dataset.ccpBound) return;
      el.dataset.ccpBound = '1';
      const handler = evt => {
        const id = el.getAttribute('data-product-id');
        if (!id) return;
        evt.preventDefault();
        evt.stopPropagation();
        openProductModal(id);
      };
      el.addEventListener('click', handler);
      el.addEventListener('keydown', e => {
        if (e.key === 'Enter' || e.key === ' ') handler(e);
      });
    });
  }

  function setActiveProfile(profile) {
    activeProfile = JSON.parse(JSON.stringify(profile || CANONICAL_DEMO_PROFILE));
    if (!activeProfile.name) activeProfile.name = activeProfile.pet_name || 'Dolly';
    if (!activeProfile.pet_name) activeProfile.pet_name = activeProfile.name;
    if (!Array.isArray(activeProfile.breeds) || !activeProfile.breeds.length) {
      const primary = activeProfile.primary_breed || 'Labrador Retriever';
      const secondary = activeProfile.secondary_breed || '';
      activeProfile.breeds = [primary].concat(secondary ? [secondary] : []);
    }
    window.__WAGTOPIA_ACTIVE_PROFILE__ = activeProfile;
    const generated = document.getElementById('module-generated');
    if (generated) generated.textContent = `Profile · ${activeProfile.pet_name || activeProfile.name || 'Dog'}`;
  }

  function openProfileEditor() {
    const panel = document.getElementById('profile-editor-panel');
    const form = document.getElementById('profile-editor-form');
    if (!panel || !form) return;
    form.elements.name.value = activeProfile.name || '';
    form.elements.primary_breed.value = activeProfile.primary_breed || activeProfile.breeds?.[0] || '';
    form.elements.secondary_breed.value = activeProfile.secondary_breed || activeProfile.breeds?.[1] || '';
    form.elements.breed_split_pct.value = activeProfile.breed_split_pct ?? '';
    form.elements.birthday.value = activeProfile.birthday || '';
    form.elements.weight.value = activeProfile.weight ?? '';
    form.elements.height_cm.value = activeProfile.height_cm ?? '';
    form.elements.sex.value = activeProfile.sex || '';
    form.elements.activity_level.value = activeProfile.activity_level || '';
    form.elements.current_environment.value = activeProfile.current_environment || '';
    form.elements.bcs.value = activeProfile.bcs ?? '';
    form.elements.observed_conditions.value = (activeProfile.observed_conditions || []).join(', ');
    form.elements.groomer_observations.value = activeProfile.groomer_observations || '';
    panel.hidden = false;
  }

  function closeProfileEditor() {
    const panel = document.getElementById('profile-editor-panel');
    if (panel) panel.hidden = true;
  }

  function profileFromForm() {
    const form = document.getElementById('profile-editor-form');
    const split = val => String(val || '').split(',').map(x => x.trim()).filter(Boolean);
    const primary = String(form.elements.primary_breed.value || '').trim();
    const secondary = String(form.elements.secondary_breed.value || '').trim();
    return {
      name: String(form.elements.name.value || '').trim() || 'Dolly',
      pet_name: String(form.elements.name.value || '').trim() || 'Dolly',
      primary_breed: primary,
      secondary_breed: secondary,
      breeds: [primary || 'Labrador Retriever'].concat(secondary ? [secondary] : []),
      breed_split_pct: Number(form.elements.breed_split_pct.value || 0) || undefined,
      birthday: String(form.elements.birthday.value || '').trim() || undefined,
      weight: Number(form.elements.weight.value || 0) || 30,
      height_cm: Number(form.elements.height_cm.value || 0) || undefined,
      sex: String(form.elements.sex.value || '').trim() || undefined,
      activity_level: String(form.elements.activity_level.value || '').trim() || undefined,
      current_environment: String(form.elements.current_environment.value || '').trim() || undefined,
      bcs: Number(form.elements.bcs.value || 0) || undefined,
      observed_conditions: split(form.elements.observed_conditions.value),
      groomer_observations: String(form.elements.groomer_observations.value || '').trim()
    };
  }

  async function loadClinicalReport(profile) {
    const debugOn =
      /(?:\?|&)(?:debug|dev)=1\b/i.test(location.search) ||
      /(?:\?|&)(?:debug|dev)=true\b/i.test(location.search);
    const bodyProfile = profile || activeProfile || CANONICAL_DEMO_PROFILE;
    const requestBody = {
      ...bodyProfile,
      pet_name: bodyProfile.pet_name || bodyProfile.name,
      name: bodyProfile.name || bodyProfile.pet_name,
      breeds:
        bodyProfile.breeds && bodyProfile.breeds.length
          ? bodyProfile.breeds
          : [bodyProfile.primary_breed].filter(Boolean),
      observed_conditions: Array.isArray(bodyProfile.observed_conditions)
        ? bodyProfile.observed_conditions
        : []
    };
    const url = `${API_BASE}/api/v1/clinical-report${debugOn ? '?debug=1' : ''}`;
    const headers = {
      'Content-Type': 'application/json',
      Accept: 'application/json'
    };
    if (API_KEY) headers['x-api-key'] = API_KEY;
    const res = await fetch(url, {
      method: 'POST',
      headers,
      body: JSON.stringify(requestBody)
    });
    if (!res.ok) throw new Error(`clinical-report HTTP ${res.status}`);
    const payload = await res.json();
    analysis = payload.analyze;
    window.__PPIE_LAST__ = analysis;
    window.__STANDARD_REPORT__ = payload.report || null;
    window.__REPORT_MODELS__ = payload.reportModels || null;
    window.__CLINICAL_REPORT__ = payload.clinicalReport || null;
    window.__CLINICAL_ASSESSMENT__ = payload.assessment || null;
    window.__ENGINE_TRACE__ = payload.trace || payload.assessment?.trace || null;

    if (window.PpieShell) {
      window.PpieShell.mount({
        assessment: payload.assessment || null,
        report: payload.report || null,
        analyze: analysis,
        models: payload.reportModels || null,
        trace: window.__ENGINE_TRACE__
      });
    } else if (payload.report && window.StandardReportRenderer) {
      window.StandardReportRenderer.mount(payload.report, 'page-dashboard');
    }
    return payload;
  }

  function showAnalyzeError(err) {
    console.error('[Wagtopia] analyze failed', err);
    const msg = 'Analysis unavailable — ensure the API is running and refresh.';
    if (window.PpieShell?.showError) {
      window.PpieShell.showError(msg);
    } else {
      const dash = document.getElementById('page-dashboard');
      if (dash) dash.innerHTML = emptyState(msg);
    }
  }

  function classifyError(err) {
    const text = String(err && (err.message || err) || '').toLowerCase();
    if (text.includes('401') || text.includes('403')) return 'authentication/configuration failure';
    if (text.includes('failed to fetch') || text.includes('networkerror') || text.includes('network')) return 'network failure';
    if (text.includes('http 5')) return 'service unavailable';
    return 'unavailable';
  }

  function showBootState(kind, detail) {
    const root = document.getElementById('page-module');
    if (!root) return;
    const message = detail ? `${kind}: ${detail}` : kind;
    root.innerHTML = `<div class="empty-state" role="status">
      <p><strong>${esc(message)}</strong></p>
      <p>Retry the analysis when the service is available.</p>
      <button type="button" id="wagtopia-retry-boot" class="module-ghost">Retry</button>
    </div>`;
    const retry = document.getElementById('wagtopia-retry-boot');
    retry?.addEventListener('click', () => {
      boot(true).catch((bootErr) => console.error('[Wagtopia] retry failed', bootErr));
    });
  }

  async function boot(forceReload) {
    if (bootPromise && !forceReload) return bootPromise;
    bootPromise = (async () => {
      const weight = Number(activeProfile.weight || 30) || 30;
      showBootState('loading');
      try {
        await Catalog.load(weight);
      } catch (err) {
        showBootState(classifyError(err), String(err && err.message || err));
        throw err;
      }
      try {
        await loadClinicalReport(activeProfile);
      } catch (err) {
        showBootState(classifyError(err), String(err && err.message || err));
        showAnalyzeError(err);
      }
    })();
    return bootPromise;
  }

  window.WagtopiaApp = {
    renderDiarySession,
    boot,
    getAnalysis: () => analysis,
    getProfile: () => activeProfile
  };

  document.querySelectorAll('[data-close-modal]').forEach(el => {
    el.addEventListener('click', closeProductModal);
  });
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') closeProductModal();
  });

  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible' && Catalog.ready) {
      const weight = Number(activeProfile.weight || 30) || 30;
      Catalog.load(weight).catch(err => console.warn('[Wagtopia] catalog refresh failed', err));
    }
  });

  function bindProfileActions() {
    setActiveProfile(CANONICAL_DEMO_PROFILE);
    const loadDemo = document.getElementById('module-load-demo');
    const analyzeBtn = document.getElementById('module-analyze');
    const profileBtn = document.getElementById('module-profile');
    const closeBtn = document.getElementById('profile-editor-close');
    const loadDemoForm = document.getElementById('profile-load-demo');
    const profileForm = document.getElementById('profile-editor-form');

    loadDemo?.addEventListener('click', () => {
      setActiveProfile(CANONICAL_DEMO_PROFILE);
      boot(true).catch(err => console.error('[Wagtopia] demo load failed', err));
    });
    analyzeBtn?.addEventListener('click', () => {
      boot(true).catch(err => console.error('[Wagtopia] analyze failed', err));
    });
    profileBtn?.addEventListener('click', openProfileEditor);
    closeBtn?.addEventListener('click', closeProfileEditor);
    loadDemoForm?.addEventListener('click', () => {
      setActiveProfile(CANONICAL_DEMO_PROFILE);
      openProfileEditor();
    });
    profileForm?.addEventListener('submit', evt => {
      evt.preventDefault();
      setActiveProfile(profileFromForm());
      closeProfileEditor();
      boot(true).catch(err => console.error('[Wagtopia] analyze failed', err));
    });
  }

  bindProfileActions();
  boot().catch(err => console.error('[Wagtopia] boot failed', err));
})();
