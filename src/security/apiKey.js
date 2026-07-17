'use strict';

const VALID_KEYS = new Set(
  (process.env.API_KEYS || 'wagtopia-demo-key,ppie-dev-key')
    .split(',')
    .map(k => k.trim())
    .filter(Boolean)
);

function verifyApiKey(req, res, next) {
  const key = req.headers['x-api-key'];
  if (!key || !VALID_KEYS.has(key)) {
    return res.status(401).json({ error: 'Invalid or missing x-api-key' });
  }
  req.apiKey = key;
  next();
}

module.exports = { verifyApiKey, VALID_KEYS };
