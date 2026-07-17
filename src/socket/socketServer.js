'use strict';

function initSocket(io) {
  io.on('connection', socket => {
    console.log('[PPIE] Client connected:', socket.id);

    socket.on('subscribe_pet', petId => {
      if (petId) {
        socket.join(`pet:${petId.toLowerCase()}`);
        console.log('[PPIE] Subscribed to pet:', petId);
      }
    });

    socket.on('disconnect', () => {
      console.log('[PPIE] Client disconnected:', socket.id);
    });
  });

  return io;
}

module.exports = { initSocket };
