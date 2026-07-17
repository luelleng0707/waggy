function initSocket(io) {
  io.on('connection', socket => {
    console.log('Client connected:', socket.id);

    socket.on('subscribe_pet', petName => {
      if (petName) socket.join(`pet:${petName.toLowerCase()}`);
    });

    socket.on('disconnect', () => {
      console.log('Client disconnected:', socket.id);
    });
  });

  return io;
}

module.exports = { initSocket };
