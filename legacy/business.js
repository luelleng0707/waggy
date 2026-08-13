(function () {
  'use strict';

  var API_KEY = window.WAGTOPIA_API_KEY || 'wagtopia-demo-key';
  var ACCESS_KEY = new URLSearchParams(window.location.search).get('access_key') || '';
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

  function display(v) {
    return v == null || v === '' ? 'NOT AVAILABLE' : String(v);
  }

  async function run() {
    var headers = {
      'Content-Type': 'application/json',
      Accept: 'application/json',
      'x-api-key': API_KEY
    };
    if (ACCESS_KEY) headers['x-wagtopia-access-key'] = ACCESS_KEY;
    var res = await fetch('/api/v1/presentation/three-surfaces', {
      method: 'POST',
      headers: headers,
      body: JSON.stringify(DOLLY)
    });
    if (!res.ok) {
      throw new Error('Business analysis failed: ' + res.status);
    }
    var payload = await res.json();
    render(payload.business || {}, payload.analysis_signature || 'NOT AVAILABLE');
  }

  function metric(label, value) {
    return '<div class="metric"><div class="label">' + esc(label) + '</div><div class="value">' + esc(display(value)) + '</div></div>';
  }

  function render(business, signature) {
    var overview = business.overview || {};
    document.getElementById('overview-grid').innerHTML = [
      metric('Dogs analyzed', overview.dogs_analyzed),
      metric('Priority health opportunities', overview.priority_health_opportunities),
      metric('Product coverage', overview.product_count),
      metric('Package opportunities', overview.package_count),
      metric('Estimated business opportunity', overview.estimated_business_opportunity),
      metric('Analysis signature', signature)
    ].join('');

    var portfolio = business.portfolio || {};
    document.getElementById('portfolio-grid').innerHTML =
      '<p><strong>Product gaps:</strong> ' + esc(display(portfolio.product_gaps)) + '</p>' +
      '<p><strong>Portfolio expansion:</strong> ' + esc(display(portfolio.portfolio_expansion)) + '</p>' +
      '<p><strong>Products:</strong> ' + esc((portfolio.products || []).length) + '</p>' +
      '<p><strong>Packages:</strong> ' + esc((portfolio.packages || []).length) + '</p>';

    var healthRows = (business.health_opportunities || [])
      .map(function (h) {
        return '<tr>' +
          '<td>' + esc(display(h.condition)) + '</td>' +
          '<td>' + esc(display(h.observed_prevalence)) + '</td>' +
          '<td>' + esc(display(h.estimated_prevalence)) + '</td>' +
          '<td>' + esc(display(h.evidence_status)) + '</td>' +
          '<td>' + esc(display(h.breed_relevance)) + '</td>' +
          '<td>' + esc(display(h.business_relevance)) + '</td>' +
          '</tr>';
      })
      .join('');
    document.getElementById('health-grid').innerHTML =
      '<table><thead><tr><th>Condition</th><th>Observed</th><th>Estimated</th><th>Evidence</th><th>Breed relevance</th><th>Business relevance</th></tr></thead><tbody>' +
      (healthRows || '<tr><td colspan="6">NOT AVAILABLE</td></tr>') +
      '</tbody></table>';

    var finance = business.financial_model || {};
    document.getElementById('financial-grid').innerHTML = [
      metric('Monthly total', finance.monthly_total),
      metric('Yearly total', finance.yearly_total),
      metric('Discount', finance.discount),
      metric('Recurring price', finance.recurring_price),
      metric('Margin', finance.margin)
    ].join('');

    document.getElementById('evidence-grid').innerHTML =
      '<p>Scientific and market research status depends on runtime evidence payload.</p>' +
      '<p><strong>Status:</strong> ' + esc((business.health_opportunities || []).some(function (h) { return h.evidence_status === 'AVAILABLE'; }) ? 'PARTIAL' : 'NOT AVAILABLE') + '</p>';
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
