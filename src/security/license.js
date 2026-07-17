'use strict';

function validateLicense() {
  const key = process.env.ENGINE_LICENSE_KEY;
  if (!key) {
    console.warn('[PPIE] No ENGINE_LICENSE_KEY — running in demo mode');
    return { valid: true, mode: 'demo' };
  }
  const expected = process.env.ENGINE_LICENSE_EXPECTED || 'wagtopia-ppie-licensed';
  if (key !== expected) {
    throw new Error('[PPIE] Invalid ENGINE_LICENSE_KEY — engine startup rejected');
  }
  return { valid: true, mode: 'licensed' };
}

module.exports = { validateLicense };
