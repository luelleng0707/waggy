/**
 * CatalogService — single frontend source of truth for CSV-backed products.
 * Loads GET /api/v1/store (joined catalog + pricing + components + feeding + extensions).
 */
(function (global) {
  'use strict';

  const API_BASE = global.location.origin;
  const API_KEY = (global.WagtopiaAPI && global.WagtopiaAPI.API_KEY) || '';

  const CatalogService = {
    products: [],
    byId: Object.create(null),
    byName: Object.create(null),
    meta: { count: 0, csv_hash: '', data_version: '', loaded_at: '' },
    weightKg: 30,
    ready: false,
    _loadPromise: null,

    async load(weightKg) {
      if (weightKg != null) this.weightKg = Number(weightKg);
      if (this._loadPromise) return this._loadPromise;
      this._loadPromise = this._fetchStore().finally(() => {
        this._loadPromise = null;
      });
      return this._loadPromise;
    },

    async _fetchStore() {
      const url = new URL(`${API_BASE}/api/v1/store`);
      if (this.weightKg != null && !Number.isNaN(this.weightKg)) {
        url.searchParams.set('weight_kg', String(this.weightKg));
      }
      const headers = { Accept: 'application/json' };
      if (API_KEY) headers['x-api-key'] = API_KEY;
      const res = await fetch(url.toString(), {
        headers,
        cache: 'no-store'
      });
      if (!res.ok) throw new Error(`store HTTP ${res.status}`);
      const data = await res.json();
      this.products = Array.isArray(data.products) ? data.products : [];
      this.byId = Object.create(null);
      this.byName = Object.create(null);
      this.products.forEach(p => {
        const id = String(p.product_id || '');
        if (id) this.byId[id] = p;
        const name = String(p.product_name || p.name || '').toLowerCase();
        if (name) this.byName[name] = p;
      });
      this.meta = {
        count: Number(data.count || this.products.length),
        csv_hash: String(data.csv_hash || ''),
        data_version: String(data.data_version || ''),
        loaded_at: String(data.loaded_at || '')
      };
      this.ready = true;
      return this.products;
    },

    get(productId) {
      if (!productId) return null;
      return this.byId[String(productId)] || null;
    },

    getByName(name) {
      if (!name) return null;
      return this.byName[String(name).toLowerCase()] || null;
    },

    resolve(ref) {
      if (!ref) return null;
      if (typeof ref === 'string') {
        return this.get(ref) || this.getByName(ref);
      }
      const id = ref.product_id || ref.id;
      if (id && this.get(id)) return this.get(id);
      const name = ref.product_name || ref.name;
      if (name && this.getByName(name)) return this.getByName(name);
      return null;
    },

    all() {
      return this.products.slice();
    },

    search(query) {
      const q = String(query || '').trim().toLowerCase();
      if (!q) return this.all();
      return this.products.filter(p => {
        const hay = [
          p.product_name, p.name, p.product_id, p.brand, p.category,
          p.subcategory, p.tags, p.short_description, p.description
        ].map(v => String(v || '').toLowerCase()).join(' ');
        return hay.includes(q);
      });
    },

    categories() {
      return [...new Set(this.products.map(p => p.category).filter(Boolean))].sort();
    },

    formatPrice(p) {
      const amount = Number((p && (p.list_price_rmb ?? p.price_rmb)) || 0);
      return `¥${amount.toLocaleString('en-US')}`;
    },

    imageHtml(p, alt) {
      const url = String((p && p.image_url) || '').trim();
      const label = alt || (p && (p.product_name || p.name)) || '?';
      const initial = escapeHtml((label.charAt(0) || '?').toUpperCase());
      const placeholder = `<div class="product-media-placeholder" aria-hidden="true">${initial}</div>`;
      if (!url) return placeholder;
      return (
        `<img class="product-media" src="${escapeHtml(url)}" alt="${escapeHtml(label)}" loading="lazy" ` +
        `onerror="this.onerror=null;var d=document.createElement('div');d.className='product-media-placeholder';d.setAttribute('aria-hidden','true');d.textContent=(this.alt||'?').charAt(0).toUpperCase();this.replaceWith(d);">`
      );
    },

    feedingDisplay(p) {
      if (!p) return '';
      if (p.feeding_for_weight && p.feeding_for_weight.display) {
        return p.feeding_for_weight.display;
      }
      const rules = p.feeding_rules || [];
      if (!rules.length) return '';
      return rules[0].display || `${rules[0].daily_amount}${rules[0].daily_unit}/day`;
    },

    componentsList(p) {
      return (p && p.components) || [];
    }
  };

  function escapeHtml(text) {
    return String(text || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  CatalogService.escapeHtml = escapeHtml;
  global.CatalogService = CatalogService;
  global.WagtopiaAPI = { API_BASE, API_KEY };
})(window);
