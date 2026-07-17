'use strict';

const crypto = require('crypto');

const CLIENTS = {
  wagtopia: {
    clientId: 'wagtopia',
    secret: process.env.CLIENT_SECRET || 'wagtopia-hmac-secret-demo'
  }
};

const MAX_SKEW_MS = 5 * 60 * 1000;

function verifyHmac(req, res, next) {
  const clientId = req.headers['x-client-id'];
  const signature = req.headers['x-signature'];
  const timestamp = req.headers['x-timestamp'];

  if (!clientId || !signature || !timestamp) {
    return next();
  }

  const client = CLIENTS[clientId];
  if (!client) {
    return res.status(401).json({ error: 'Unknown client' });
  }

  const ts = parseInt(timestamp, 10);
  if (Math.abs(Date.now() - ts) > MAX_SKEW_MS) {
    return res.status(401).json({ error: 'Timestamp expired' });
  }

  const payload = timestamp + JSON.stringify(req.body || {});
  const expected = crypto
    .createHmac('sha256', client.secret)
    .update(payload)
    .digest('hex');

  if (!crypto.timingSafeEqual(Buffer.from(signature), Buffer.from(expected))) {
    return res.status(401).json({ error: 'Invalid HMAC signature' });
  }

  req.clientId = clientId;
  next();
}

module.exports = { verifyHmac, CLIENTS };
