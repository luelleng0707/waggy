(function () {
  'use strict';

  var API_KEY = window.WAGTOPIA_API_KEY || '';
  var DOLLY = {
    name: 'Dolly',
    pet_name: 'Dolly',
    breeds: ['Golden Retriever', 'Labrador Retriever'],
    primary_breed: 'Golden Retriever',
    secondary_breed: 'Labrador Retriever',
    breed_split_pct: 50,
    birthday: '2021-03-15',
    weight: 30,
    sex: 'Female',
    activity_level: 'High',
    current_environment: 'Shanghai Summer',
    observed_conditions: []
  };

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  }

  function na(v) {
    return v == null || v === '' || (Array.isArray(v) && !v.length) ? 'NOT AVAILABLE FROM RUNTIME' : String(v);
  }

  function money(v) {
    if (v == null || v === '' || v === 'NOT AVAILABLE' || v === 'NOT AVAILABLE FROM RUNTIME') {
      return 'NOT AVAILABLE FROM RUNTIME';
    }
    var n = Number(v);
    return Number.isNaN(n) ? 'NOT AVAILABLE FROM RUNTIME' : '¥' + n.toLocaleString();
  }

  function productRows(items) {
    if (!items || !items.length) {
      return '<p>NOT AVAILABLE FROM RUNTIME</p>';
    }
    return '<table><thead><tr><th>Product</th><th>Brand</th><th>Category</th><th>Reason / match</th><th>Price</th><th>Monthly</th></tr></thead><tbody>' +
      items.map(function (p) {
        return '<tr>' +
          '<td>' + esc(na(p.name || p.product_name)) + '</td>' +
          '<td>' + esc(na(p.brand)) + '</td>' +
          '<td>' + esc(na(p.category || p.product_type)) + '</td>' +
          '<td>' + esc(na(p.reason || p.why_selected)) + '</td>' +
          '<td>' + esc(money(p.price || p.list_price)) + '</td>' +
          '<td>' + esc(money(p.monthly_cost)) + '</td>' +
          '</tr>';
      }).join('') +
      '</tbody></table>';
  }

  function packageBlocks(composition) {
    if (!composition || !composition.length) {
      return '<p>NOT AVAILABLE FROM RUNTIME</p>';
    }
    return composition.map(function (pkg) {
      var products = pkg.products || [];
      var productHtml = products.length
        ? '<ul>' + products.map(function (p) {
            return '<li><strong>' + esc(na(p.name)) + '</strong>' +
              ' · ' + esc(na(p.brand)) +
              ' · qty ' + esc(na(p.quantity || (p.consumption && p.consumption.daily_serving))) +
              ' · monthly ' + esc(money(p.monthly_cost)) +
              '</li>';
          }).join('') + '</ul>'
        : '<p>' + esc(na(pkg.composition_status)) + '</p>';
      return '<article class="package-block">' +
        '<h3>' + esc(na(pkg.title)) + (pkg.recommended ? ' · recommended' : '') + '</h3>' +
        '<p>' + esc(na(pkg.purpose)) + '</p>' +
        '<p>Monthly ' + esc(money(pkg.monthly_cost)) +
        ' · Yearly ' + esc(money(pkg.yearly_cost)) +
        ' · Savings ' + esc(money(pkg.savings)) +
        ' · Discount ' + esc(pkg.discount_percent == null || pkg.discount_percent === 'NOT AVAILABLE FROM RUNTIME' ? 'NOT AVAILABLE FROM RUNTIME' : pkg.discount_percent + '%') +
        '</p>' +
        productHtml +
        '</article>';
    }).join('');
  }

  async function run() {
    var headers = {
      'Content-Type': 'application/json',
      Accept: 'application/json'
    };
    if (API_KEY) headers['x-api-key'] = API_KEY;
    var res = await fetch('/api/v1/presentation/three-surfaces', {
      method: 'POST',
      headers: headers,
      body: JSON.stringify(DOLLY)
    });
    if (!res.ok) {
      throw new Error('Business analysis failed: ' + res.status);
    }
    var payload = await res.json();
    var demoOn = Boolean(payload.demo_catalog || (payload.business && payload.business.demo_catalog));
    var banner = document.getElementById('demo-catalog-banner');
    if (banner) banner.hidden = !demoOn;
    render(payload.business || {}, payload.analysis_signature || 'NOT AVAILABLE', demoOn);
  }

  function metric(label, value) {
    return '<div class="metric"><div class="label">' + esc(label) + '</div><div class="value">' + esc(na(value)) + '</div></div>';
  }

  function render(business, signature, demoOn) {
    var overview = business.overview || {};
    document.getElementById('overview-grid').innerHTML = [
      metric('Dogs analyzed', overview.dogs_analyzed),
      metric('Priority health opportunities', overview.priority_health_opportunities),
      metric('Product coverage', overview.product_count),
      metric('Package opportunities', overview.package_count),
      metric('Estimated business opportunity', overview.estimated_business_opportunity),
      metric('Analysis signature', signature)
    ].join('') + (demoOn ? '<p class="demo-catalog-banner">Demo catalog — synthetic commercial data</p>' : '');

    var portfolio = business.portfolio || {};
    document.getElementById('portfolio-grid').innerHTML =
      '<p><strong>Number of products:</strong> ' + esc(na(overview.product_count)) + '</p>' +
      '<p><strong>Brands:</strong> ' + esc(na(Array.isArray(portfolio.brands) ? portfolio.brands.join(', ') : portfolio.brands)) + '</p>' +
      '<p><strong>Categories:</strong> ' + esc(na(Array.isArray(portfolio.categories) ? portfolio.categories.join(', ') : portfolio.categories)) + '</p>' +
      '<p><strong>Recommended products:</strong> ' + esc((portfolio.recommended_products || portfolio.products || []).length) + '</p>' +
      '<p><strong>PRODUCT GAP ANALYSIS:</strong> ' + esc(na(portfolio.product_gaps)) + '</p>' +
      '<p><strong>Portfolio expansion:</strong> ' + esc(na(portfolio.portfolio_expansion)) + '</p>' +
      '<p><strong>Packages:</strong> ' + esc((portfolio.package_composition || portfolio.packages || []).length) + '</p>' +
      (demoOn ? '<p>Demo catalog — synthetic commercial data. Not actual market performance.</p>' : '');

    document.getElementById('products-grid').innerHTML = productRows(
      portfolio.recommended_products && portfolio.recommended_products.length
        ? portfolio.recommended_products
        : portfolio.products
    );
    document.getElementById('packages-grid').innerHTML = packageBlocks(
      portfolio.package_composition && portfolio.package_composition.length
        ? portfolio.package_composition
        : (business.financial_model && business.financial_model.package_pricing) || []
    );

    var healthRows = (business.health_opportunities || [])
      .map(function (h) {
        return '<tr>' +
          '<td>' + esc(na(h.condition)) + '</td>' +
          '<td>' + esc(na(h.observed_prevalence)) + '</td>' +
          '<td>' + esc(na(h.estimated_prevalence)) + '</td>' +
          '<td>' + esc(na(h.evidence_status)) + '</td>' +
          '<td>' + esc(na(h.breed_relevance)) + '</td>' +
          '<td>' + esc(na(h.business_relevance)) + '</td>' +
          '</tr>';
      })
      .join('');
    document.getElementById('health-grid').innerHTML =
      '<table><thead><tr><th>Condition</th><th>Observed</th><th>Estimated</th><th>Evidence</th><th>Breed relevance</th><th>Business relevance</th></tr></thead><tbody>' +
      (healthRows || '<tr><td colspan="6">NOT AVAILABLE FROM RUNTIME</td></tr>') +
      '</tbody></table>';

    var finance = business.financial_model || {};
    document.getElementById('financial-grid').innerHTML = [
      metric('Monthly total', finance.monthly_total),
      metric('Yearly total', finance.yearly_total),
      metric('Discount', finance.discount),
      metric('Recurring price', finance.recurring_price),
      metric('Margin', finance.margin)
    ].join('') + packageBlocks(finance.package_pricing || []);

    document.getElementById('evidence-grid').innerHTML =
      '<p>Scientific and market research status depends on runtime evidence payload.</p>' +
      '<p><strong>Status:</strong> ' + esc((business.health_opportunities || []).some(function (h) { return h.evidence_status === 'AVAILABLE'; }) ? 'PARTIAL' : 'NOT AVAILABLE FROM RUNTIME') + '</p>';
  }

  document.getElementById('run-analysis').addEventListener('click', function () {
    run().catch(function (err) {
      document.getElementById('overview-grid').innerHTML = metric('Error', err.message || String(err));
    });
  });

  run().catch(function (err) {
    document.getElementById('overview-grid').innerHTML = metric('Error', err.message || String(err));
  });
})();
