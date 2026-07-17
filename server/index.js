require('dotenv').config();
const path = require('path');
const express = require('express');
const http = require('http');
const cors = require('cors');
const { Server } = require('socket.io');
const { createRoutes } = require('./routes');
const { initSocket } = require('./socket');
const { loadFromCsv, reloadStore } = require('./logic');

const PORT = process.env.PORT || 3000;
const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: { origin: '*', methods: ['GET', 'POST'] }
});

app.use(cors());
app.use(express.json({ limit: '10mb' }));
app.use(express.static(path.join(__dirname, '..')));

reloadStore();
console.log('Loaded data from CSV:', {
  breeds: loadFromCsv().breeds.length,
  products: loadFromCsv().products.length
});

createRoutes(app, io);
initSocket(io);

app.get('/groomer', (req, res) => {
  res.sendFile(path.join(__dirname, '..', 'groomer.html'));
});

server.listen(PORT, () => {
  console.log(`Wagtopia Pet Intelligence running at http://localhost:${PORT}`);
  console.log(`Groomer portal: http://localhost:${PORT}/groomer`);
});
