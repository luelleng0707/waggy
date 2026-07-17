'use strict';

const jwt = require('jsonwebtoken');

const SECRET = process.env.JWT_SECRET || 'ppie-admin-jwt-demo-secret';

function signAdmin(payload, expiresIn = '8h') {
  return jwt.sign(payload, SECRET, { expiresIn });
}

function verifyAdmin(req, res, next) {
  const auth = req.headers.authorization;
  if (!auth?.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Admin JWT required' });
  }
  try {
    req.admin = jwt.verify(auth.slice(7), SECRET);
    next();
  } catch {
    return res.status(401).json({ error: 'Invalid admin token' });
  }
}

module.exports = { signAdmin, verifyAdmin };
