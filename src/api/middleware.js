'use strict';

const { VALID_KEYS } = require('../security/apiKey');
const { verifyHmac } = require('../security/hmacVerify');

function apiMiddleware(req, res, next) {
  const key = req.headers['x-api-key'];
  if (!key || !VALID_KEYS.has(key)) {
    return res.status(401).json({ error: 'Invalid or missing x-api-key' });
  }
  req.apiKey = key;
  verifyHmac(req, res, next);
}

module.exports = { apiMiddleware };
