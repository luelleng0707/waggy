'use strict';

require('dotenv').config();
const path = require('path');
const express = require('express');
const http = require('http');
const cors = require('cors');
const { Server } = require('socket.io');
const { validateLicense } = require('./src/security/license');
const { initDb } = require('./src/api/db/queries');
const { registerRoutes } = require('./src/api/routes');
const { initSocket } = require('./src/socket/socketServer');

const PORT = process.env.PORT || 3000;

async function boot() {
  validateLicense();
  await initDb();

  const app = express();
  const server = http.createServer(app);
  const io = new Server(server, { cors: { origin: '*', methods: ['GET', 'POST'] } });

  app.use(cors());
  app.use(express.json({ limit: '10mb' }));
  app.use(express.static(path.join(__dirname)));

  registerRoutes(app, io);
  initSocket(io);

  app.get('/groomer', (req, res) => {
    res.sendFile(path.join(__dirname, 'groomer.html'));
  });

  app.get('/health', (req, res) => {
    res.json({ status: 'ok', engine: 'PPIE', version: '2.0.0' });
  });

  server.listen(PORT, () => {
    console.log(`[PPIE] Wagtopia Portable Pet Intelligence Engine`);
    console.log(`[PPIE] Running at http://localhost:${PORT}`);
    console.log(`[PPIE] API: POST /api/v1/analyze`);
    console.log(`[PPIE] Groomer: http://localhost:${PORT}/groomer`);
  });
}

boot().catch(err => {
  console.error('[PPIE] Startup failed:', err.message);
  process.exit(1);
});
