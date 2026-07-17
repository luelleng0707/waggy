const {
  computeRecommendations,
  searchBreeds,
  addGroomerObservation,
  reloadStore,
  getStore
} = require('./logic');

function createRoutes(app, io) {
  app.get('/api/breeds', (req, res) => {
    const q = req.query.search || req.query.q || '';
    res.json(searchBreeds(q));
  });

  app.get('/api/breeds/all', (req, res) => {
    res.json(getStore().breeds);
  });

  app.post('/api/recommendations', (req, res) => {
    try {
      const { dogName, breeds, birthday, weight } = req.body;
      if (!dogName || !breeds?.length || !birthday) {
        return res.status(400).json({ error: 'dogName, breeds, and birthday are required' });
      }
      const result = computeRecommendations({
        dogName,
        breeds: breeds.slice(0, 5),
        birthday,
        weight: weight ? parseFloat(weight) : null
      });
      res.json(result);
    } catch (err) {
      console.error(err);
      res.status(500).json({ error: err.message });
    }
  });

  app.get('/api/recommendations/:petName', (req, res) => {
    try {
      const petName = req.params.petName;
      const obs = getStore().groomerObservations.filter(
        o => o.petName.toLowerCase() === petName.toLowerCase()
      );
      res.json({ groomerNotes: obs });
    } catch (err) {
      res.status(500).json({ error: err.message });
    }
  });

  app.post('/api/groomer/submit', (req, res) => {
    try {
      const {
        pet_name,
        petName,
        weight,
        height,
        checklist = [],
        before_photo,
        after_photo
      } = req.body;

      const name = pet_name || petName;
      if (!name) return res.status(400).json({ error: 'pet_name is required' });

      const observations = [];
      for (const item of checklist) {
        const obs = {
          petName: name,
          observation: item,
          severity: 'moderate',
          photoUrl: before_photo || after_photo || null
        };
        addGroomerObservation(obs);
        observations.push(obs);
      }

      if (weight || height) {
        addGroomerObservation({
          petName: name,
          observation: `weight:${weight || 'unknown'} height:${height || 'unknown'}`,
          severity: 'info',
          photoUrl: null
        });
      }

      reloadStore();

      const payload = {
        petName: name,
        observations,
        weight,
        height,
        before_photo,
        after_photo,
        timestamp: new Date().toISOString()
      };

      io.emit('update_pet_profile', payload);

      res.json({ success: true, payload });
    } catch (err) {
      console.error(err);
      res.status(500).json({ error: err.message });
    }
  });

  app.post('/api/reload', (req, res) => {
    reloadStore();
    res.json({ ok: true });
  });
}

module.exports = { createRoutes };
