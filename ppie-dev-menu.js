/**
 * Floating Developer menu — only when PPIE_DEBUG / ?debug=1.
 * Never mounts in production without the debug gate.
 */
(function () {
  'use strict';

  function debugEnabled() {
    if (/(?:\?|&)(?:debug|dev)=(?:1|true)\b/i.test(location.search)) return true;
    try {
      return sessionStorage.getItem('PPIE_DEBUG') === '1';
    } catch (_) {
      return false;
    }
  }

  function mount() {
    if (!debugEnabled()) return;
    if (document.getElementById('ppie-dev-menu')) return;

    const root = document.createElement('div');
    root.id = 'ppie-dev-menu';
    root.className = 'ppie-dev-menu';
    root.innerHTML = `
      <button type="button" class="ppie-dev-menu__fab" id="ppie-dev-fab" title="Developer tools">Dev</button>
      <div class="ppie-dev-menu__panel" id="ppie-dev-panel" hidden>
        <p class="ppie-dev-menu__title">Developer</p>
        <a href="/?debug=1">Dashboard</a>
        <a href="/?debug=1#assessment">Clinical Assessment</a>
        <a href="/?debug=1" data-trace>Engine Trace</a>
        <a href="/debug/calculation?debug=1">Calculation Inspector</a>
        <a href="/debug/calculation?debug=1#repository">Repository Browser</a>
        <a href="/debug/calculation?debug=1#packages">Package Optimizer</a>
        <a href="/docs" target="_blank" rel="noopener">API Explorer</a>
        <a href="/debug/calculation?debug=1#runtime">Performance</a>
        <a href="/debug/calculation?debug=1#validation">Validation</a>
        <a href="/debug/calculation?debug=1" data-export>Export Trace</a>
        <a href="/debug/calculation?debug=1#compare">Compare (side-by-side)</a>
      </div>
    `;
    document.body.appendChild(root);

    if (!document.getElementById('ppie-dev-menu-style')) {
      const style = document.createElement('style');
      style.id = 'ppie-dev-menu-style';
      style.textContent = `
        .ppie-dev-menu { position: fixed; right: 16px; bottom: 16px; z-index: 99999; font-family: DM Sans, system-ui, sans-serif; }
        .ppie-dev-menu__fab {
          border: none; border-radius: 999px; width: 52px; height: 52px;
          background: #b3266a; color: #fff; font-weight: 700; cursor: pointer;
          box-shadow: 0 8px 24px rgba(0,0,0,.35);
        }
        .ppie-dev-menu__panel {
          position: absolute; right: 0; bottom: 60px; width: 240px;
          background: #241c28; color: #f4eef2; border-radius: 14px; padding: 12px;
          border: 1px solid rgba(255,255,255,.1); display: flex; flex-direction: column; gap: 4px;
        }
        .ppie-dev-menu__title { margin: 0 0 6px; font-size: 11px; letter-spacing: .08em; text-transform: uppercase; color: #f0a0c4; }
        .ppie-dev-menu__panel a {
          color: #f4eef2; text-decoration: none; padding: 8px 10px; border-radius: 8px; font-size: 13px;
        }
        .ppie-dev-menu__panel a:hover { background: rgba(179,38,106,.28); }
      `;
      document.head.appendChild(style);
    }

    const fab = document.getElementById('ppie-dev-fab');
    const panel = document.getElementById('ppie-dev-panel');
    fab.addEventListener('click', () => {
      panel.hidden = !panel.hidden;
    });
    document.addEventListener('click', e => {
      if (!root.contains(e.target)) panel.hidden = true;
    });

    const traceLink = root.querySelector('[data-trace]');
    if (traceLink) {
      traceLink.addEventListener('click', e => {
        if (location.pathname === '/' || location.pathname.endsWith('index.html')) {
          e.preventDefault();
          const btn = document.getElementById('module-trace');
          if (btn) btn.click();
          else location.href = '/?debug=1';
        }
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', mount);
  } else {
    mount();
  }
})();
