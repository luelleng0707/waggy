/* Wagtopia AI — Demo Interactions */

(function () {
  'use strict';

  // ── Navigation ──
  const pages = document.querySelectorAll('.page');
  const navItems = document.querySelectorAll('.nav-item');

  function showPage(name) {
    pages.forEach(p => p.classList.remove('active'));
    navItems.forEach(n => n.classList.remove('active'));
    const page = document.getElementById('page-' + name);
    const nav = document.querySelector('[data-page="' + name + '"]');
    if (page) page.classList.add('active');
    if (nav) nav.classList.add('active');
    const activePage = document.querySelector('.page.active');
    if (activePage) activePage.scrollTop = 0;
  }

  navItems.forEach(btn => {
    btn.addEventListener('click', () => showPage(btn.dataset.page));
  });

  document.querySelectorAll('.quick-card[data-nav]').forEach(card => {
    card.addEventListener('click', () => showPage(card.dataset.nav));
  });

  // ── Image pools (Unsplash) ──
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

  const productImgs = [
    'https://images.unsplash.com/photo-1601758228041-f3b2795255f1?w=200&q=80',
    'https://images.unsplash.com/photo-1583337130417-3346a1be7dee?w=200&q=80',
    'https://images.unsplash.com/photo-1583511655857-d19b40a7a54e?w=200&q=80',
    'https://images.unsplash.com/photo-1598133894008-61f7c073fd69?w=200&q=80',
    'https://images.unsplash.com/photo-1616190179415-1c81e4e8f882?w=200&q=80',
    'https://images.unsplash.com/photo-1588943211346-0908a1e0c696?w=200&q=80'
  ];

  // ── Grooming Sessions ──
  const sessions = {
    jul12: {
      date: 'July 12, 2025',
      groomer: 'Emma Chen',
      duration: '2h 15min',
      services: 'Full Groom · Hydration · Ear Care',
      groomerNote: "Dolly's coat softness has improved significantly since her last visit. We recommend continued weekly eye-care maintenance and additional hydration support during summer months. She was a star today — extra bakery treat earned!",
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
      productsUsed: [
        { name: 'Silk Coat Shampoo', brand: 'Wagtopia Lab', desc: 'Gentle oat formula', price: '$28' },
        { name: 'Deep Hydration Conditioner', brand: 'Wagtopia Lab', desc: 'Summer moisture boost', price: '$32' },
        { name: 'Paw Recovery Balm', brand: 'PawLux', desc: 'Post-trim protection', price: '$18' },
        { name: 'Tear Care Wipes', brand: 'EyeBright', desc: 'Daily eye maintenance', price: '$14' },
        { name: 'Ear Cleansing Solution', brand: 'Wagtopia Lab', desc: 'pH balanced', price: '$16' },
        { name: 'Calming Duck Treats', brand: 'Wagtopia Bakery', desc: 'Session reward', price: '$12' },
        { name: 'Finishing Mist Spray', brand: 'SilkPaw', desc: 'Coat shine finish', price: '$24' },
        { name: 'Filtered Spa Water', brand: 'Wagtopia', desc: 'Hydration during session', price: '$0' }
      ]
    },
    jul18: {
      date: 'July 18, 2025',
      groomer: 'Sarah Kim',
      duration: '1h 45min',
      services: 'Express Bath · Eye Care · Paw Trim',
      groomerNote: "Quick refresh session for Dolly before the weekend social event. Eye area looking much clearer — keep up the daily wipe routine at home. She loved the frozen yogurt reward!",
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
      productsUsed: [
        { name: 'Express Refresh Shampoo', brand: 'Wagtopia Lab', desc: 'Quick cleanse formula', price: '$22' },
        { name: 'Tear Care Wipes', brand: 'EyeBright', desc: 'Eye corner care', price: '$14' },
        { name: 'Paw Recovery Balm', brand: 'PawLux', desc: 'Moisture lock', price: '$18' },
        { name: 'Frozen Yogurt Bites', brand: 'Wagtopia Bakery', desc: 'Dolly\'s favorite', price: '$10' },
        { name: 'Coat Gloss Serum', brand: 'SilkPaw', desc: 'Instant shine', price: '$26' }
      ]
    },
    aug2: {
      date: 'August 2, 2025',
      groomer: 'Emma Chen',
      duration: '2h 30min',
      services: 'Premium Full Groom · De-shed · Spa Package',
      groomerNote: "Our most comprehensive session yet! Dolly's summer coat is shedding heavily — de-shed treatment removed significant undercoat. Skin underneath looks healthy. Recommend bi-weekly brushing and our hydration supplement during peak summer.",
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
      productsUsed: [
        { name: 'De-Shedding Shampoo', brand: 'Wagtopia Lab', desc: 'Seasonal formula', price: '$34' },
        { name: 'Undercoat Rake Treatment', brand: 'Wagtopia Spa', desc: 'Professional de-shed', price: '$45' },
        { name: 'Hydration Mask', brand: 'SilkPaw', desc: 'Deep moisture therapy', price: '$38' },
        { name: 'Ear Deep Clean Kit', brand: 'Wagtopia Lab', desc: 'Post-swim care', price: '$22' },
        { name: 'Paw Pad Repair Cream', brand: 'PawLux', desc: 'Hot weather protection', price: '$20' },
        { name: 'Salmon Crisp Treats', brand: 'Wagtopia Bakery', desc: 'Premium reward', price: '$15' },
        { name: 'Calming Lavender Spray', brand: 'ZenPaw', desc: 'Post-groom relaxation', price: '$19' },
        { name: 'UV Coat Protector', brand: 'SilkPaw', desc: 'Summer shield', price: '$28' },
        { name: 'Spa Mineral Water', brand: 'Wagtopia', desc: 'Session hydration', price: '$0' }
      ]
    },
    aug15: {
      date: 'August 15, 2025',
      groomer: 'Marcus Lee',
      duration: '1h 30min',
      services: 'Maintenance Trim · Nail Care · Dental Refresh',
      groomerNote: "Maintenance visit — Dolly is maintaining beautifully from August's spa session. Nails trimmed, quick dental refresh with our enzymatic chew. She's building great trust with the blow dryer now!",
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
      productsUsed: [
        { name: 'Enzymatic Dental Chew', brand: 'BrightBite', desc: 'Tartar control', price: '$16' },
        { name: 'Nail Smoothing File', brand: 'Wagtopia Spa', desc: 'Gentle finish', price: '$8' },
        { name: 'Coat Refresh Spray', brand: 'SilkPaw', desc: 'Between-groom care', price: '$18' },
        { name: 'Duck Training Treats', brand: 'Wagtopia Bakery', desc: 'Blow dryer reward', price: '$12' }
      ]
    }
  };

  const recCategories = [
    {
      title: 'Joint Wellness',
      products: [
        { name: 'Joint Support Plus', brand: 'VitaPaw', desc: 'Large breed formula', price: '$42' },
        { name: 'Mobility Chews Daily', brand: 'FlexiDog', desc: 'Glucosamine blend', price: '$36' },
        { name: 'Omega Support D', brand: 'PurePet', desc: 'Fish oil capsules', price: '$28' },
        { name: 'Hip & Joint Soft Chews', brand: 'Wagtopia Wellness', desc: 'Dolly\'s blend', price: '$38' }
      ]
    },
    {
      title: 'Eye Care',
      products: [
        { name: 'Eye Care Wipes 03', brand: 'EyeBright', desc: 'Daily maintenance', price: '$14' },
        { name: 'Tear Stain Support', brand: 'ClearEye', desc: 'Preventative formula', price: '$22' },
        { name: 'Gentle Eye Wash', brand: 'Wagtopia Lab', desc: 'Weekly rinse', price: '$16' }
      ]
    },
    {
      title: 'Coat Support',
      products: [
        { name: 'Silk Coat Supplement', brand: 'SilkPaw', desc: 'Biotin enriched', price: '$32' },
        { name: 'Hydration Booster', brand: 'Wagtopia Lab', desc: 'Summer essential', price: '$26' },
        { name: 'De-Shed Support Chews', brand: 'CoatCare', desc: 'Seasonal shedding', price: '$24' }
      ]
    },
    {
      title: 'Gut Health',
      products: [
        { name: 'Probiotic Daily', brand: 'GutGuard', desc: 'Digestive balance', price: '$30' },
        { name: 'Pumpkin Fiber Blend', brand: 'Wagtopia Wellness', desc: 'Gentle support', price: '$18' }
      ]
    },
    {
      title: 'Dental Care',
      products: [
        { name: 'Dental Stick Premium', brand: 'BrightBite', desc: 'Daily dental care', price: '$16' },
        { name: 'Enzymatic Tooth Gel', brand: 'SmilePaw', desc: 'Weekly application', price: '$14' }
      ]
    },
    {
      title: 'Calming Treats',
      products: [
        { name: 'Freeze-Dried Duck Treats', brand: 'Wagtopia Bakery', desc: 'Single ingredient', price: '$15' },
        { name: 'Calm & Comfort Chews', brand: 'ZenPaw', desc: 'Grooming day support', price: '$20' },
        { name: 'Lavender Honey Bites', brand: 'Wagtopia Bakery', desc: 'Artisan calming', price: '$12' }
      ]
    }
  ];

  function productCardHTML(p, idx) {
    const img = productImgs[idx % productImgs.length];
    return `
      <div class="product-card">
        <img src="${img}" alt="${p.name}" loading="lazy">
        <div class="product-card-body">
          <h4>${p.name}</h4>
          <div class="product-brand">${p.brand}</div>
          <div class="product-desc">${p.desc}</div>
          <div class="product-price">${p.price}</div>
          <button class="product-btn">Add to Cart</button>
        </div>
      </div>`;
  }

  function renderReport(sessionId) {
    const s = sessions[sessionId];
    if (!s) return;

    const reportEl = document.getElementById('grooming-report');
    reportEl.classList.remove('loaded');
    void reportEl.offsetWidth;

    const beforePhotos = dogMessy.slice(0, 6).map((src, i) => {
      const cls = i < 2 ? ' before-label' : '';
      return `<img src="${src}" alt="Before treatment ${i + 1}" class="${cls.trim()}" loading="lazy">`;
    }).join('');

    const afterPhotos = dogClean.slice(0, 6).map((src, i) => {
      const cls = i < 2 ? ' after-highlight' : '';
      return `<img src="${src}" alt="After treatment ${i + 1}" class="${cls.trim()}" loading="lazy">`;
    }).join('');

    const problemsHTML = s.problems.map(p =>
      `<div class="problem-card">
        <img src="${p.img}" alt="" loading="lazy">
        <p>${p.text}</p>
      </div>`
    ).join('');

    const resultsHTML = s.results.map(r =>
      `<div class="result-card">
        <img src="${r.img}" alt="" loading="lazy">
        <div class="result-card-content">
          <p>${r.text}</p>
          <span class="status-pill ${r.status}">${r.status.charAt(0).toUpperCase() + r.status.slice(1)}</span>
        </div>
      </div>`
    ).join('');

    const productsHTML = s.productsUsed.map((p, i) => productCardHTML(p, i)).join('');

    const recsHTML = recCategories.map(cat => `
      <div class="rec-category">
        <h3>${cat.title}</h3>
        <div class="product-carousel">
          ${cat.products.map((p, i) => productCardHTML(p, i + 2)).join('')}
        </div>
      </div>
    `).join('');

    reportEl.innerHTML = `
      <div class="report-header">
        <h2>Grooming Report</h2>
        <p>${s.date} · with ${s.groomer}</p>
        <div class="report-meta">
          <span>⏱ ${s.duration}</span>
          <span>✂️ ${s.services}</span>
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
        <h3 class="report-section-title">Products Used During Dolly's Session</h3>
        <div class="product-carousel">${productsHTML}</div>
      </div>

      <div class="report-section">
        <h3 class="report-section-title">Groomer Suggestions</h3>
        <div class="groomer-note">
          <p>"${s.groomerNote}"</p>
          <span class="author">— ${s.groomer}, Wagtopia Grooming</span>
        </div>
      </div>

      <div class="report-section">
        <h3 class="report-section-title">Recommended for Dolly</h3>
        <div class="rec-intro">
          <p>Based on Dolly's breed mix and grooming history, large-breed mixes may experience increased joint sensitivity and recurring eye irritation over time. These curated selections support her unique wellness profile.</p>
        </div>
        ${recsHTML}
      </div>
    `;

    reportEl.classList.add('loaded');
    reportEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  // Calendar interactions
  const calDays = document.querySelectorAll('.cal-day.has-session');
  calDays.forEach(day => {
    day.addEventListener('click', () => {
      calDays.forEach(d => d.classList.remove('active'));
      day.classList.add('active');
      renderReport(day.dataset.session);
    });
  });

  // Initial report
  renderReport('jul12');

  // ── Shop Products ──
  const shopProducts = [
    { name: 'Salmon & Sweet Potato Bowl', cat: 'meals', price: '$12.99', img: 'https://images.unsplash.com/photo-1589924691995-400dc9ecc119?w=300&q=80' },
    { name: 'Free-Range Chicken Feast', cat: 'meals', price: '$11.99', img: 'https://images.unsplash.com/photo-1622277797420-5853c3470e45?w=300&q=80' },
    { name: 'Beef & Quinoa Medley', cat: 'meals', price: '$13.99', img: 'https://images.unsplash.com/photo-1601758228041-f3b2795255f1?w=300&q=80' },
    { name: 'Joint Support Plus', cat: 'supplements', price: '$42.00', img: 'https://images.unsplash.com/photo-1583511655857-d19b40a7a54e?w=300&q=80' },
    { name: 'Omega-3 Fish Oil', cat: 'supplements', price: '$28.00', img: 'https://images.unsplash.com/photo-1598133894008-61f7c073fd69?w=300&q=80' },
    { name: 'Probiotic Daily Chews', cat: 'supplements', price: '$30.00', img: 'https://images.unsplash.com/photo-1616190179415-1c81e4e8f882?w=300&q=80' },
    { name: 'Silk Coat Shampoo', cat: 'grooming', price: '$28.00', img: 'https://images.unsplash.com/photo-1588943211346-0908a1e0c696?w=300&q=80' },
    { name: 'Hydration Conditioner', cat: 'grooming', price: '$32.00', img: 'https://images.unsplash.com/photo-1608093273550-f3318751143e?w=300&q=80' },
    { name: 'Tear Care Wipes', cat: 'grooming', price: '$14.00', img: 'https://images.unsplash.com/photo-1546527868-ccb7ee7dfa6a?w=300&q=80' },
    { name: 'Paw Recovery Balm', cat: 'grooming', price: '$18.00', img: 'https://images.unsplash.com/photo-1583337130417-3346a1be7dee?w=300&q=80' },
    { name: 'Salmon Crisp Treats', cat: 'bakery', price: '$15.00', img: 'https://images.unsplash.com/photo-1587300003388-59208cc962cb?w=300&q=80' },
    { name: 'Duck Training Bites', cat: 'bakery', price: '$12.00', img: 'https://images.unsplash.com/photo-1558787533-047edbf9612a?w=300&q=80' },
    { name: 'Frozen Yogurt Bites', cat: 'bakery', price: '$10.00', img: 'https://images.unsplash.com/photo-1561037404-61cd46aa615c?w=300&q=80' },
    { name: 'Birthday Pupcake', cat: 'bakery', price: '$8.00', img: 'https://images.unsplash.com/photo-1548199973-03cce0bbc87b?w=300&q=80' },
    { name: 'Plush Comfort Toy', cat: 'toys', price: '$22.00', img: 'https://images.unsplash.com/photo-1530281700549-e82e7bf110d6?w=300&q=80' },
    { name: 'Interactive Puzzle Ball', cat: 'toys', price: '$18.00', img: 'https://images.unsplash.com/photo-1477884213360-49e9a8e46e03?w=300&q=80' },
    { name: 'Rope Tug Premium', cat: 'toys', price: '$16.00', img: 'https://images.unsplash.com/photo-1516734212186-a967f81ad0d4?w=300&q=80' },
    { name: 'Calm & Comfort Chews', cat: 'wellness', price: '$20.00', img: 'https://images.unsplash.com/photo-1633722715463-d30f4f325e24?w=300&q=80' },
    { name: 'Lavender Relaxation Spray', cat: 'wellness', price: '$19.00', img: 'https://images.unsplash.com/photo-1596492784531-6e8551225179?w=300&q=80' },
    { name: 'Dental Stick Premium', cat: 'wellness', price: '$16.00', img: 'https://images.unsplash.com/photo-1583511655857-d19b40a7a54e?w=300&q=80' },
    { name: 'Summer Cooling Bandana', cat: 'seasonal', price: '$24.00', img: 'https://images.unsplash.com/photo-1587300003388-59208cc962cb?w=300&q=80' },
    { name: 'Holiday Gift Box', cat: 'seasonal', price: '$45.00', img: 'https://images.unsplash.com/photo-1558787533-047edbf9612a?w=300&q=80' },
    { name: 'Autumn Spice Treats', cat: 'seasonal', price: '$14.00', img: 'https://images.unsplash.com/photo-1561037404-61cd46aa615c?w=300&q=80' },
    { name: 'UV Coat Protector', cat: 'seasonal', price: '$28.00', img: 'https://images.unsplash.com/photo-1548199973-03cce0bbc87b?w=300&q=80' }
  ];

  const productGrid = document.getElementById('product-grid');
  const catBtns = document.querySelectorAll('.cat-btn');

  function renderShop(category) {
    const filtered = category === 'all'
      ? shopProducts
      : shopProducts.filter(p => p.cat === category);

    productGrid.innerHTML = filtered.map(p => `
      <div class="shop-product">
        <img src="${p.img}" alt="${p.name}" loading="lazy">
        <div class="shop-product-info">
          <span class="cat-tag">${p.cat}</span>
          <h4>${p.name}</h4>
          <div class="price">${p.price}</div>
        </div>
      </div>
    `).join('');
  }

  catBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      catBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      renderShop(btn.dataset.cat);
    });
  });

  renderShop('all');
})();
