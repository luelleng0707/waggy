'use strict';

const { analyze } = require('../engine');
const { getEvidenceForCondition, getProductsForCondition } = require('../engine/evidenceEngine');
const { apiMiddleware } = require('./middleware');

const groomerSessions = new Map();

function registerRoutes(app, io) {
  app.post('/api/v1/analyze', apiMiddleware, async (req, res) => {
    try {
      const petKey = (req.body.pet_name || req.body.petName || '').toLowerCase();
      const session = groomerSessions.get(petKey);
      const observed = [
        ...(req.body.observed_conditions || []),
        ...(session?.observed_conditions || [])
      ];
      const result = await analyze({ ...req.body, observed_conditions: observed });
      res.json(result);
    } catch (err) {
      console.error('[PPIE] analyze error:', err);
      res.status(500).json({ error: err.message });
    }
  });

  app.post('/api/v1/groomer/update', apiMiddleware, (req, res) => {
    try {
      const { pet_id, pet_name, observed_conditions = [], notes, weight, height } = req.body;
      const id = pet_id || pet_name;
      if (!id) return res.status(400).json({ error: 'pet_id or pet_name required' });

      const session = groomerSessions.get(id.toLowerCase()) || { observed_conditions: [] };
      session.observed_conditions = [
        ...new Set([...session.observed_conditions, ...observed_conditions])
      ];
      session.notes = notes;
      session.weight = weight;
      session.height = height;
      session.updated_at = new Date().toISOString();
      groomerSessions.set(id.toLowerCase(), session);

      const payload = {
        pet_id: id,
        pet_name: pet_name || id,
        observed_conditions: session.observed_conditions,
        notes,
        weight,
        height,
        timestamp: session.updated_at
      };

      io.to(`pet:${id.toLowerCase()}`).emit('recommendation:update', payload);
      io.emit('update_pet_profile', payload);

      res.json({ success: true, payload });
    } catch (err) {
      res.status(500).json({ error: err.message });
    }
  });

  app.get('/api/v1/evidence/:condition', apiMiddleware, (req, res) => {
    const evidence = getEvidenceForCondition(req.params.condition.replace(/-/g, '_'));
    res.json({ condition: req.params.condition, evidence });
  });

  app.get('/api/v1/products/:condition', apiMiddleware, (req, res) => {
    const weight = parseFloat(req.query.weight) || 20;
    const products = getProductsForCondition(req.params.condition.replace(/-/g, '_'), weight);
    res.json({ condition: req.params.condition, products });
  });

  app.get('/api/v1/groomer/session/:petId', apiMiddleware, (req, res) => {
    const session = groomerSessions.get(req.params.petId.toLowerCase());
    res.json(session || { observed_conditions: [] });
  });

  app.get('/api/breeds', (req, res) => {
    const { getStore } = require('./db/queries');
    const q = (req.query.search || req.query.q || '').toLowerCase();
    const breeds = getStore().breeds;
    const names = breeds
      .filter(b => !q || b.breed_name.toLowerCase().includes(q))
      .map(b => b.breed_name)
      .slice(0, 15);
    res.json(names);
  });

  app.post('/api/recommendations', apiMiddleware, async (req, res) => {
    const body = {
      ...req.body,
      observed_conditions: req.body.observed_conditions || getGroomerObs(req.body.dogName)
    };
    try {
      const result = await analyze({
        pet_name: body.dogName,
        breeds: body.breeds,
        birthday: body.birthday,
        weight: body.weight,
        observed_conditions: body.observed_conditions
      });
      res.json(mapLegacyResponse(result));
    } catch (err) {
      res.status(500).json({ error: err.message });
    }
  });

  app.post('/api/groomer/submit', (req, res) => {
    req.headers['x-api-key'] = req.headers['x-api-key'] || 'wagtopia-demo-key';
    const { pet_name, petName, checklist = [], weight, height } = req.body;
    const id = pet_name || petName;
    if (!id) return res.status(400).json({ error: 'pet_name required' });

    const session = groomerSessions.get(id.toLowerCase()) || { observed_conditions: [] };
    session.observed_conditions = [...new Set([...session.observed_conditions, ...checklist])];
    session.weight = weight;
    session.height = height;
    session.updated_at = new Date().toISOString();
    groomerSessions.set(id.toLowerCase(), session);

    const payload = {
      pet_id: id,
      pet_name: id,
      observed_conditions: session.observed_conditions,
      weight,
      height,
      timestamp: session.updated_at
    };

    io.to(`pet:${id.toLowerCase()}`).emit('recommendation:update', payload);
    io.emit('update_pet_profile', payload);
    res.json({ success: true, payload });
  });

  function getGroomerObs(petName) {
    if (!petName) return [];
    const session = groomerSessions.get(petName.toLowerCase());
    return session?.observed_conditions || [];
  }
}

function mapLegacyResponse(r) {
  return {
    pet: {
      dogName: r.pet.pet_name,
      breeds: r.pet.breeds,
      birthday: r.pet.birthday,
      ageYears: r.pet.age_years,
      ageStage: r.pet.age_stage,
      estimatedWeightKg: r.pet.weight_kg,
      sizeBracket: r.pet.weight_kg < 18 ? 'medium' : 'large'
    },
    wellnessScore: r.wellness_score,
    priorities: r.risks.slice(0, 5).map(risk => ({
      id: risk.condition_key,
      title: risk.condition.replace(/Dysplasia/i, 'Protection').replace(/Ivdd/i, 'Spine Care'),
      priorityLevel: risk.risk_percent >= 25 ? 'High Priority' : 'Moderate Priority',
      priorityScore: risk.risk_percent,
      riskReasoning: risk.source_quote || risk.why,
      whyProfile: { breeds: r.pet.breeds, ageYears: r.pet.age_years, weightKg: r.pet.weight_kg },
      breedEvidence: risk.source_url ? { sourceName: risk.source_name, quote: risk.source_quote, url: risk.source_url } : null,
      ingredients: r.ingredients.filter(i => i.for_conditions.includes(risk.condition)).map(i => ({
        name: i.ingredient, targetMgPerDay: parseInt(i.daily_dose), evidenceQuote: i.evidence_quote, sourceName: i.source_name, sourceUrl: i.source_url
      })),
      products: r.products.filter(p => p.ingredient_name).slice(0, 2)
    })),
    healthRisks: r.risks.map(x => ({ conditionName: x.condition, riskPercent: x.risk_percent, why: x.why, sources: [{ sourceName: x.source_name, sourceQuote: x.source_quote, sourceUrl: x.source_url }] })),
    activeIngredients: r.ingredients,
    recommendedProducts: r.products,
    monthlyPack: { title: r.monthly_plan.title, items: r.monthly_plan.items, totalCost: r.monthly_plan.total_cost, schedule: r.monthly_plan.items, productCount: r.monthly_plan.product_count },
    yearlyPack: { title: r.yearly_plan.title, items: r.yearly_plan.items, totalCost: r.yearly_plan.total_cost, monthlyEquivalent: r.yearly_plan.monthly_equivalent, savings: r.yearly_plan.savings, savingsPercent: r.yearly_plan.savings_percent, kibbleUpgrade: r.yearly_plan.kibble_upgrade },
    evidenceLibrary: r.evidence,
    groomerLive: r.groomer,
    groomerNotes: r.groomer.filter(g => g.status === 'flagged').map(g => ({ observation: g.key, severity: 'moderate' }))
  };
}

module.exports = { registerRoutes, groomerSessions };
