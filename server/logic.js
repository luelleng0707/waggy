/**
 * Wagtopia Pet Intelligence — deterministic recommendation engine
 * Loads from CSV (always) with optional Prisma sync
 */

const fs = require('fs');
const path = require('path');
const { parse } = require('csv-parse/sync');

const DATA_DIR = path.join(__dirname, '..', 'data');

const GROOMER_BOOST_MAP = {
  limping: { conditions: ['Hip Dysplasia', 'Joint Sensitivity', 'IVDD'], priorityBoost: 35, category: 'joint' },
  limps: { conditions: ['Hip Dysplasia', 'Joint Sensitivity', 'IVDD'], priorityBoost: 35, category: 'joint' },
  'eye discharge': { conditions: ['Cataracts', 'Eye Care Needs'], priorityBoost: 25, category: 'eye' },
  eyes: { conditions: ['Cataracts', 'Eye Care Needs'], priorityBoost: 25, category: 'eye' },
  scratching: { conditions: ['Skin Barrier Issues'], priorityBoost: 20, category: 'coat' },
  'dry skin': { conditions: ['Skin Barrier Issues'], priorityBoost: 20, category: 'coat' },
  skin: { conditions: ['Skin Barrier Issues', 'Digestive Sensitivity'], priorityBoost: 20, category: 'coat' },
  'tear stains': { conditions: ['Eye Care Needs'], priorityBoost: 15, category: 'eye' },
  odor: { conditions: ['Ear Infection'], priorityBoost: 15, category: 'coat' },
  'ear redness': { conditions: ['Ear Infection'], priorityBoost: 15, category: 'coat' },
  ears: { conditions: ['Ear Infection'], priorityBoost: 15, category: 'coat' },
  'bad breath': { conditions: ['Digestive Sensitivity'], priorityBoost: 20, category: 'gut' },
  teeth: { conditions: ['Digestive Sensitivity'], priorityBoost: 20, category: 'dental' },
  shedding: { conditions: ['Skin Barrier Issues'], priorityBoost: 12, category: 'coat' },
  'anal gland': { conditions: ['Digestive Sensitivity'], priorityBoost: 15, category: 'gut' }
};

const GROOMER_BOOST_FACTOR = 1.4;

const PRIORITY_CATEGORIES = {
  joint: { title: 'Joint Protection', conditions: ['Hip Dysplasia', 'Joint Sensitivity', 'IVDD'] },
  eye: { title: 'Eye Support', conditions: ['Cataracts', 'Eye Care Needs'] },
  gut: { title: 'Gut Health', conditions: ['Digestive Sensitivity', 'Obesity'] },
  coat: { title: 'Coat Support', conditions: ['Skin Barrier Issues', 'Ear Infection'] },
  dental: { title: 'Dental Care', conditions: ['Digestive Sensitivity'] }
};

const KIBBLE_FACTORS = { puppy: 28, adult: 20, senior: 18 };

const TYPE_PRIORITY = { kibble: 1, supplement: 2, treat: 3, aftercare: 4 };

let store = null;

function readCsv(filename) {
  const filePath = path.join(DATA_DIR, filename);
  if (!fs.existsSync(filePath)) return [];
  const raw = fs.readFileSync(filePath, 'utf8');
  return parse(raw, { columns: true, skip_empty_lines: true, trim: true });
}

function toBool(val) {
  if (typeof val === 'boolean') return val;
  return String(val).toLowerCase() === 'true';
}

function toNum(val, fallback = 0) {
  const n = parseFloat(val);
  return Number.isFinite(n) ? n : fallback;
}

function loadFromCsv() {
  const breeds = readCsv('breeds.csv').map(r => ({
    name: r.name,
    sizeClass: r.size_class,
    avgWeightMin: toNum(r.avg_weight_min),
    avgWeightMax: toNum(r.avg_weight_max),
    coatType: r.coat_type
  }));

  const breedConditions = readCsv('breed_conditions.csv').map(r => ({
    breedName: r.breed_name,
    conditionName: r.condition_name,
    riskPercent: toNum(r.risk_percent),
    sourceName: r.source_name,
    sourceQuote: r.source_quote,
    sourceUrl: r.source_url
  }));

  const ageConditions = readCsv('age_conditions.csv').map(r => ({
    ageStage: r.age_stage,
    conditionName: r.condition_name,
    riskPercent: toNum(r.risk_percent),
    sourceName: r.source_name,
    sourceQuote: r.source_quote,
    sourceUrl: r.source_url
  }));

  const ingredients = readCsv('ingredients.csv').map(r => ({
    ingredientName: r.ingredient_name,
    benefits: r.benefits,
    evidenceQuote: r.evidence_quote,
    sourceName: r.source_name,
    sourceUrl: r.source_url
  }));

  const conditionIngredients = readCsv('condition_ingredients.csv').map(r => ({
    conditionName: r.condition_name,
    ingredientName: r.ingredient_name,
    dailyTargetMg: toNum(r.daily_target_mg)
  }));

  const products = readCsv('products.csv').map(r => ({
    productName: r.product_name,
    brand: r.brand,
    productType: r.product_type,
    price: toNum(r.price),
    weightG: r.weight_g ? toNum(r.weight_g) : null,
    unitCount: r.unit_count ? parseInt(r.unit_count, 10) : null,
    shelfLifeDays: r.shelf_life_days ? parseInt(r.shelf_life_days, 10) : null,
    freshBool: toBool(r.fresh_bool),
    kcalPerPiece: r.kcal_per_piece ? toNum(r.kcal_per_piece) : null
  }));

  const productIngredients = readCsv('product_ingredients.csv').map(r => ({
    productName: r.product_name,
    ingredientName: r.ingredient_name,
    amountPerUnitMg: toNum(r.amount_per_unit_mg)
  }));

  const groomerObservations = readCsv('groomer_observations.csv')
    .filter(r => r.pet_name)
    .map(r => ({
      petName: r.pet_name,
      observation: r.observation,
      severity: r.severity,
      photoUrl: r.photo_url || null
    }));

  return {
    breeds,
    breedConditions,
    ageConditions,
    ingredients,
    conditionIngredients,
    products,
    productIngredients,
    groomerObservations
  };
}

function getStore() {
  if (!store) store = loadFromCsv();
  return store;
}

function reloadStore() {
  store = loadFromCsv();
  return store;
}

function addGroomerObservation(obs) {
  const s = getStore();
  s.groomerObservations.push(obs);
  const line = `${obs.petName},${obs.observation},${obs.severity},${obs.photoUrl || ''}\n`;
  fs.appendFileSync(path.join(DATA_DIR, 'groomer_observations.csv'), line);
}

function getAgeStage(birthday) {
  const birth = new Date(birthday);
  const today = new Date();
  const ageDays = (today - birth) / (1000 * 60 * 60 * 24);
  const ageYears = ageDays / 365.25;
  let stage = 'adult';
  if (ageYears < 1) stage = 'puppy';
  else if (ageYears >= 7) stage = 'senior';
  return { ageDays, ageYears, stage };
}

function sizeBracket(kg) {
  if (kg < 8) return 'small';
  if (kg < 18) return 'medium';
  if (kg < 35) return 'large';
  return 'giant';
}

function estimateWeight(breeds, breedNames) {
  const s = getStore();
  const weight = 1 / breedNames.length;
  let total = 0;
  const details = [];
  for (const name of breedNames) {
    const breed = s.breeds.find(b => b.name === name);
    if (breed) {
      const avg = (breed.avgWeightMin + breed.avgWeightMax) / 2;
      total += avg * weight;
      details.push({ breed: name, avgWeight: avg });
    }
  }
  return { estimatedWeightKg: Math.round(total * 10) / 10, details };
}

function computeRisks(breeds, ageStage, groomerObs = []) {
  const s = getStore();
  const breedWeight = 1 / breeds.length;
  const conditionMap = {};

  for (const breedName of breeds) {
    const conditions = s.breedConditions.filter(c => c.breedName === breedName);
    for (const c of conditions) {
      if (!conditionMap[c.conditionName]) {
        conditionMap[c.conditionName] = {
          combined: 0,
          overlapCount: 0,
          breeds: [],
          sources: []
        };
      }
      conditionMap[c.conditionName].combined += c.riskPercent * breedWeight;
      conditionMap[c.conditionName].overlapCount += 1;
      conditionMap[c.conditionName].breeds.push(breedName);
      conditionMap[c.conditionName].sources.push({
        sourceName: c.sourceName,
        sourceQuote: c.sourceQuote,
        sourceUrl: c.sourceUrl,
        breed: breedName
      });
    }
  }

  const ageConds = s.ageConditions.filter(c => c.ageStage === ageStage);
  for (const ac of ageConds) {
    if (!conditionMap[ac.conditionName]) {
      conditionMap[ac.conditionName] = { combined: 0, overlapCount: 0, breeds: [], sources: [] };
    }
    conditionMap[ac.conditionName].combined += ac.riskPercent * 0.3;
    conditionMap[ac.conditionName].sources.push({
      sourceName: ac.sourceName,
      sourceQuote: ac.sourceQuote,
      sourceUrl: ac.sourceUrl,
      breed: `age:${ageStage}`
    });
  }

  const groomerBoosts = {};
  const groomerCategoryBoosts = {};
  for (const obs of groomerObs) {
    const key = (obs.observation || '').toLowerCase().trim();
    const boost = GROOMER_BOOST_MAP[key];
    if (boost) {
      for (const cond of boost.conditions) {
        groomerBoosts[cond] = (groomerBoosts[cond] || 0) + 1;
      }
      groomerCategoryBoosts[boost.category] = (groomerCategoryBoosts[boost.category] || 0) + boost.priorityBoost;
    }
  }

  const results = [];
  for (const [name, data] of Object.entries(conditionMap)) {
    let risk = data.combined;
    if (data.overlapCount > 1) {
      risk = risk * (1 + data.overlapCount * 0.15);
    }
    if (ageStage === 'adult') risk *= 1.15;
    else if (ageStage === 'senior') risk *= 1.35;

    let why = '';
    if (data.breeds.length > 1) {
      why = `This condition appears in ${data.breeds.join(' and ')} lineage.`;
    } else if (data.breeds.length === 1) {
      why = `Elevated risk documented in ${data.breeds[0]} breed data.`;
    } else {
      why = `Age-related risk factor for ${ageStage} dogs.`;
    }

    if (groomerBoosts[name]) {
      risk *= GROOMER_BOOST_FACTOR;
      why += ` Groomer observed related signs — care priority elevated.`;
    }

    results.push({
      conditionName: name,
      riskPercent: Math.round(risk * 10) / 10,
      why,
      breeds: data.breeds,
      overlapCount: data.overlapCount,
      groomerBoosted: !!groomerBoosts[name],
      sources: data.sources
    });
  }

  return { risks: results.sort((a, b) => b.riskPercent - a.riskPercent), groomerCategoryBoosts };
}

function matchIngredients(topConditions) {
  const s = getStore();
  const ingredientMap = {};

  for (const cond of topConditions.slice(0, 5)) {
    const links = s.conditionIngredients.filter(ci => ci.conditionName === cond.conditionName);
    for (const link of links) {
      if (!ingredientMap[link.ingredientName]) {
        const ing = s.ingredients.find(i => i.ingredientName === link.ingredientName);
        ingredientMap[link.ingredientName] = {
          ingredientName: link.ingredientName,
          dailyTargetMg: 0,
          forConditions: [],
          benefits: ing?.benefits || '',
          evidenceQuote: ing?.evidenceQuote || '',
          sourceName: ing?.sourceName || '',
          sourceUrl: ing?.sourceUrl || ''
        };
      }
      ingredientMap[link.ingredientName].dailyTargetMg += link.dailyTargetMg;
      ingredientMap[link.ingredientName].forConditions.push(cond.conditionName);
    }
  }

  return Object.values(ingredientMap).sort((a, b) => b.dailyTargetMg - a.dailyTargetMg);
}

function scoreProduct(product, ingredientName, dailyTarget, conditionMatch) {
  const s = getStore();
  const pi = s.productIngredients.find(
    p => p.productName === product.productName && p.ingredientName === ingredientName
  );
  if (!pi || pi.amountPerUnitMg <= 0) return null;

  const density = Math.min(pi.amountPerUnitMg / dailyTarget, 1);
  const shelfFit = product.shelfLifeDays ? Math.min(product.shelfLifeDays / 90, 1) : 0.5;
  const priceEff = product.price > 0 ? Math.min(50 / product.price, 1) : 0;
  const brandBoost = product.brand.toLowerCase().includes('wagtopia') ? 0.15 : 0;
  const freshBoost = product.freshBool ? 0.1 : 0;

  const score =
    conditionMatch * 0.4 +
    density * 0.3 +
    shelfFit * 0.2 +
    priceEff * 0.1 +
    brandBoost +
    freshBoost;

  const requiredUnits = dailyTarget / pi.amountPerUnitMg;
  const intervalDays = requiredUnits >= 1 ? 1 : Math.max(1, Math.round(1 / requiredUnits));

  return {
    ...product,
    ingredientName,
    amountPerUnitMg: pi.amountPerUnitMg,
    score: Math.round(score * 1000) / 1000,
    intervalDays,
    schedule: requiredUnits >= 1
      ? `${Math.ceil(requiredUnits)} unit(s) daily`
      : `1 unit every ${intervalDays} day(s)`
  };
}

function matchProducts(ingredients, topConditions) {
  const s = getStore();
  const results = [];
  const seen = new Set();

  for (const ing of ingredients) {
    const conditionMatch = topConditions.find(c =>
      ing.forConditions.includes(c.conditionName)
    )?.riskPercent || 10;
    const normalized = conditionMatch / 100;

    const productLinks = s.productIngredients.filter(pi => pi.ingredientName === ing.ingredientName);
    for (const link of productLinks) {
      const product = s.products.find(p => p.productName === link.productName);
      if (!product) continue;
      const key = `${product.productName}:${ing.ingredientName}`;
      if (seen.has(key)) continue;

      const scored = scoreProduct(product, ing.ingredientName, ing.dailyTargetMg, normalized);
      if (scored) {
        seen.add(key);
        results.push(scored);
      }
    }
  }

  return results.sort((a, b) => {
    const typeDiff = (TYPE_PRIORITY[a.productType] || 9) - (TYPE_PRIORITY[b.productType] || 9);
    if (typeDiff !== 0) return typeDiff;
    if (a.brand.includes('Wagtopia') && !b.brand.includes('Wagtopia')) return -1;
    if (!a.brand.includes('Wagtopia') && b.brand.includes('Wagtopia')) return 1;
    return b.score - a.score;
  });
}

function computeKibblePlan(weightKg, ageStage) {
  const s = getStore();
  const factor = KIBBLE_FACTORS[ageStage] || 20;
  const dailyGrams = Math.round(weightKg * factor);
  const monthlyGrams = dailyGrams * 30;

  const kibbles = s.products.filter(p => p.productType === 'kibble');
  const ranked = kibbles.sort((a, b) => {
    if (a.brand.includes('Wagtopia')) return -1;
    if (b.brand.includes('Wagtopia')) return 1;
    if (a.freshBool && !b.freshBool) return -1;
    return a.price - b.price;
  });

  const chosen = ranked[0];
  if (!chosen || !chosen.weightG) return null;

  const bags = Math.ceil(monthlyGrams / chosen.weightG);
  return {
    product: chosen,
    dailyGrams,
    monthlyGrams,
    quantity: bags,
    unit: 'bag(s)',
    duration: '30 days',
    totalCost: Math.round(bags * chosen.price * 100) / 100,
    note: `${dailyGrams}g/day for ${weightKg}kg ${ageStage} dog`
  };
}

function computeTreatPlan(weightKg, ageStage) {
  const s = getStore();
  const dailyCalories = weightKg * 30;
  const treatBudget = dailyCalories * 0.1;
  const treats = s.products.filter(p => p.productType === 'treat' && p.kcalPerPiece);

  const ranked = treats.sort((a, b) => {
    if (a.brand.includes('Wagtopia')) return -1;
    if (b.brand.includes('Wagtopia')) return 1;
    return 0;
  });

  const chosen = ranked.slice(0, 2);
  return chosen.map(t => {
    const dailyPieces = Math.floor(treatBudget / t.kcalPerPiece);
    let maxPurchase = dailyPieces * 30;
    if (t.freshBool && t.shelfLifeDays) {
      maxPurchase = Math.min(maxPurchase, dailyPieces * t.shelfLifeDays);
    }
    const monthlyQty = Math.min(dailyPieces * 30, maxPurchase);
    const packs = Math.ceil(monthlyQty / (t.unitCount || 30));
    return {
      product: t,
      dailyPieces,
      quantity: packs,
      unit: 'pack(s)',
      duration: '30 days',
      totalCost: Math.round(packs * t.price * 100) / 100,
      note: `Up to ${dailyPieces} pieces/day (${Math.round(treatBudget)} kcal treat budget)`
    };
  });
}

function buildMonthlyPack(weightKg, ageStage, supplements, aftercare) {
  const kibble = computeKibblePlan(weightKg, ageStage);
  const treats = computeTreatPlan(weightKg, ageStage);

  const topSupps = supplements
    .filter(p => p.productType === 'supplement')
    .slice(0, 2);

  const topAftercare = aftercare
    .filter(p => p.productType === 'aftercare')
    .slice(0, 1);

  const items = [];
  if (kibble) items.push(kibble);

  for (const sup of topSupps) {
    const unitsPerMonth = sup.intervalDays ? Math.ceil(30 / sup.intervalDays) : 30;
    items.push({
      product: sup,
      quantity: Math.min(unitsPerMonth, sup.unitCount || unitsPerMonth),
      unit: 'unit(s)',
      duration: '30 days',
      totalCost: Math.round(Math.min(unitsPerMonth, sup.unitCount || unitsPerMonth) * (sup.price / (sup.unitCount || 30)) * 100) / 100,
      schedule: sup.schedule,
      note: sup.schedule
    });
  }

  for (const tr of treats) items.push(tr);

  for (const ac of topAftercare) {
    items.push({
      product: ac,
      quantity: 1,
      unit: 'unit',
      duration: '30 days',
      totalCost: ac.price,
      note: 'Grooming aftercare essentials'
    });
  }

  const totalCost = Math.round(items.reduce((s, i) => s + i.totalCost, 0) * 100) / 100;

  return { title: 'Monthly Wellness Plan', items, totalCost };
}

function enrichProductUsage(product, ingredientName, dailyTargetMg) {
  const s = getStore();
  const pi = s.productIngredients.find(
    p => p.productName === product.productName && p.ingredientName === ingredientName
  );
  const amountPerUnit = pi?.amountPerUnitMg || 0;
  const requiredUnits = amountPerUnit > 0 ? dailyTargetMg / amountPerUnit : 1;
  const perDay = requiredUnits >= 1 ? Math.ceil(requiredUnits) : 1;
  const intervalDays = requiredUnits >= 1 ? 1 : Math.max(1, Math.round(1 / requiredUnits));
  const perMonth = intervalDays === 1 ? perDay * 30 : Math.ceil(30 / intervalDays);
  const servingsPerPack = product.unitCount || 30;
  const packsNeeded = Math.ceil(perMonth / servingsPerPack);
  const coverage = amountPerUnit > 0 ? Math.min(100, Math.round((amountPerUnit / dailyTargetMg) * 100)) : 100;
  const activeIngredients = s.productIngredients
    .filter(p => p.productName === product.productName)
    .map(p => ({ name: p.ingredientName, amountMg: p.amountPerUnitMg }));

  return {
    productName: product.productName,
    brand: product.brand,
    productType: product.productType,
    price: product.price,
    shelfLifeDays: product.shelfLifeDays,
    freshBool: product.freshBool,
    weightG: product.weightG,
    unitCount: product.unitCount,
    activeIngredients,
    dosagePerServing: amountPerUnit ? `${amountPerUnit}mg` : '—',
    servingsPerPack,
    suggestedUsage: intervalDays === 1 ? `${perDay}/day` : `1 every ${intervalDays} days`,
    perDay,
    perMonth,
    durationDays: 30,
    packsNeeded,
    coveragePercent: coverage,
    freshWarning: product.freshBool && product.shelfLifeDays
      ? `Shelf life: ${product.shelfLifeDays} days · Use within ${product.shelfLifeDays - 2} days`
      : null
  };
}

function buildPriorities(pet, risks, groomerCategoryBoosts, allProducts, activeIngredients) {
  const s = getStore();
  const categories = [];

  for (const [catKey, catMeta] of Object.entries(PRIORITY_CATEGORIES)) {
    const catRisks = risks.filter(r => catMeta.conditions.includes(r.conditionName));
    if (!catRisks.length) continue;

    const baseScore = Math.max(...catRisks.map(r => r.riskPercent));
    const groomerBoost = groomerCategoryBoosts[catKey] || 0;
    const priorityScore = baseScore + groomerBoost;
    const topRisk = catRisks[0];
    const breedSource = topRisk.sources.find(src => !src.breed?.startsWith('age:')) || topRisk.sources[0];

    const catIngredients = activeIngredients.filter(ing =>
      ing.forConditions.some(c => catMeta.conditions.includes(c))
    ).slice(0, 2);

    const catProducts = allProducts
      .filter(p => catIngredients.some(ing => ing.ingredientName === p.ingredientName))
      .filter(p => p.productType === 'supplement' || p.productType === 'aftercare')
      .slice(0, 2)
      .map(p => {
        const ing = catIngredients.find(i => i.ingredientName === p.ingredientName);
        return enrichProductUsage(p, p.ingredientName, ing?.dailyTargetMg || 100);
      });

    const riskReasoning = topRisk.breeds.length
      ? `${topRisk.breeds.join(' and ')} show elevated predisposition to ${topRisk.conditionName.toLowerCase()}.`
      : `Age-related ${topRisk.conditionName.toLowerCase()} risk for ${pet.ageStage} dogs.`;

    categories.push({
      id: catKey,
      title: catMeta.title,
      priorityLevel: priorityScore >= 30 ? 'High Priority' : priorityScore >= 18 ? 'Moderate Priority' : 'Watch',
      priorityScore: Math.round(priorityScore * 10) / 10,
      groomerBoost,
      conditions: catRisks.map(r => r.conditionName),
      topCondition: topRisk.conditionName,
      riskPercent: topRisk.riskPercent,
      riskReasoning,
      whyProfile: {
        breeds: pet.breeds,
        ageYears: pet.ageYears,
        weightKg: pet.estimatedWeightKg
      },
      breedEvidence: breedSource ? {
        sourceName: breedSource.sourceName,
        quote: breedSource.sourceQuote,
        url: breedSource.sourceUrl
      } : null,
      ingredients: catIngredients.map(ing => ({
        name: ing.ingredientName,
        targetMgPerDay: ing.dailyTargetMg,
        benefits: ing.benefits,
        evidenceQuote: ing.evidenceQuote,
        sourceName: ing.sourceName,
        sourceUrl: ing.sourceUrl
      })),
      products: catProducts
    });
  }

  return categories.sort((a, b) => b.priorityScore - a.priorityScore).slice(0, 5);
}

function buildKibbleUpgrade(currentKibble, targetIngredient) {
  const s = getStore();
  if (!currentKibble) return null;
  const currentPi = s.productIngredients.find(
    p => p.productName === currentKibble.productName && p.ingredientName === targetIngredient
  );
  const upgrades = s.products
    .filter(p => p.productType === 'kibble' && p.productName !== currentKibble.productName)
    .map(p => {
      const pi = s.productIngredients.find(
        x => x.productName === p.productName && x.ingredientName === targetIngredient
      );
      return { product: p, amount: pi?.amountPerUnitMg || 0 };
    })
    .filter(u => u.amount > (currentPi?.amountPerUnitMg || 0))
    .sort((a, b) => b.amount - a.amount);

  if (!upgrades.length) return null;
  const best = upgrades[0];
  const currentAmt = currentPi?.amountPerUnitMg || 1;
  const glucosamineBoost = targetIngredient === 'Glucosamine'
    ? Math.round(((best.amount - currentAmt) / currentAmt) * 100)
    : null;
  const omegaPi = s.productIngredients.find(
    x => x.productName === best.product.productName && x.ingredientName === 'Omega-3'
  );
  const currentOmega = s.productIngredients.find(
    x => x.productName === currentKibble.productName && x.ingredientName === 'Omega-3'
  );
  const omegaBoost = omegaPi && currentOmega
    ? Math.round(((omegaPi.amountPerUnitMg - currentOmega.amountPerUnitMg) / currentOmega.amountPerUnitMg) * 100)
    : null;

  return {
    current: currentKibble.productName,
    recommended: best.product.productName,
    reason: [
      glucosamineBoost ? `Higher glucosamine density (+${glucosamineBoost}%)` : null,
      omegaBoost ? `Omega-3 content (+${omegaBoost}%)` : null
    ].filter(Boolean).join(' · ') || 'Better nutrient density for your dog\'s profile'
  };
}

function enrichMonthlyPack(pack, weightKg, ageStage) {
  const schedule = pack.items.map(item => {
    const p = item.product;
    const name = p.productName || p.name;
    let daily = '';
    let monthly = '';
    let depletion = '';
    let freshWarning = null;

    if (p.productType === 'kibble') {
      daily = `${item.dailyGrams || Math.round(weightKg * (KIBBLE_FACTORS[ageStage] || 20))}g/day`;
      monthly = `${item.monthlyGrams || ''}g/month`;
      depletion = `${item.quantity} bag(s) exactly`;
    } else if (p.productType === 'supplement') {
      daily = item.schedule || '1/day';
      monthly = `${item.quantity} units/month`;
      depletion = `1 jar exactly`;
    } else if (p.productType === 'treat') {
      daily = `${item.dailyPieces || 2}/day`;
      monthly = `${(item.dailyPieces || 2) * 30}/month`;
      if (p.freshBool && p.shelfLifeDays) {
        freshWarning = `Shelf life: ${p.shelfLifeDays} days · Use within ${p.shelfLifeDays - 2} days`;
      }
      depletion = `${item.quantity} pack(s)`;
    } else {
      daily = 'As needed';
      monthly = '1 unit';
      depletion = '1 unit';
    }

    return { name, daily, monthly, depletion, freshWarning, cost: item.totalCost };
  });

  return { ...pack, schedule, productCount: pack.items.length };
}

function buildGroomerLive(observations) {
  const fields = [
    { key: 'eyes', label: 'Eyes', obs: ['eyes', 'eye discharge', 'tear stains'] },
    { key: 'ears', label: 'Ears', obs: ['ears', 'ear redness', 'odor'] },
    { key: 'skin', label: 'Skin', obs: ['skin', 'dry skin', 'scratching'] },
    { key: 'teeth', label: 'Teeth', obs: ['teeth', 'bad breath'] },
    { key: 'limps', label: 'Limps', obs: ['limps', 'limping'] },
    { key: 'shedding', label: 'Shedding', obs: ['shedding'] },
    { key: 'anal gland', label: 'Anal Gland', obs: ['anal gland'] }
  ];

  const obsLower = observations.map(o => (o.observation || '').toLowerCase().trim());

  return fields.map(f => {
    const flagged = f.obs.some(o => obsLower.includes(o));
    const latest = observations.find(o => f.obs.includes((o.observation || '').toLowerCase().trim()));
    return {
      key: f.key,
      label: f.label,
      status: flagged ? 'flagged' : 'clear',
      severity: latest?.severity || null,
      updatedAt: latest ? 'Live' : null
    };
  });
}

function buildYearlyPack(monthlyPack, supplements, kibbleUpgrade) {
  const items = monthlyPack.items.map(item => {
    if (item.product.productType === 'supplement' && item.product.unitCount) {
      const daysPerUnit = item.product.unitCount * (item.schedule?.includes('every') ? parseInt(item.schedule.match(/\d+/)?.[0] || '1', 10) : 1);
      const yearlyUnits = Math.ceil(365 / Math.max(daysPerUnit, 30));
      return {
        ...item,
        quantity: yearlyUnits,
        duration: '365 days',
        totalCost: Math.round(yearlyUnits * item.product.price * 100) / 100,
        note: `Optimized: ${yearlyUnits} bottle(s)/year instead of 12`
      };
    }
    if (item.product.productType === 'kibble') {
      const yearlyBags = item.quantity * 12;
      return { ...item, quantity: yearlyBags, duration: '365 days', totalCost: Math.round(yearlyBags * item.product.price * 100) / 100 };
    }
    const yearlyQty = item.quantity * 12;
    return { ...item, quantity: yearlyQty, duration: '365 days', totalCost: Math.round(yearlyQty * item.product.price * 100) / 100 };
  });

  const totalCost = Math.round(items.reduce((s, i) => s + i.totalCost, 0) * 100) / 100;
  const monthlyEquivalent = Math.round((totalCost / 12) * 100) / 100;
  const naiveMonthly = monthlyPack.totalCost * 12;
  const savings = Math.round((naiveMonthly - totalCost) * 100) / 100;

  return {
    title: 'Annual Optimized Plan',
    items,
    totalCost,
    monthlyEquivalent,
    savings: Math.max(0, savings),
    savingsPercent: naiveMonthly > 0 ? Math.round((savings / naiveMonthly) * 100) : 0,
    kibbleUpgrade
  };
}

function computeRecommendations(petProfile) {
  const { dogName, breeds, birthday, weight } = petProfile;
  const s = getStore();
  const { ageYears, stage } = getAgeStage(birthday);

  const weightInfo = weight
    ? { estimatedWeightKg: weight, details: [] }
    : estimateWeight(s.breeds, breeds);

  const groomerObs = s.groomerObservations.filter(
    o => o.petName.toLowerCase() === dogName.toLowerCase()
  );

  const { risks: riskList, groomerCategoryBoosts } = computeRisks(breeds, stage, groomerObs);
  const topConditions = riskList.slice(0, 8);
  const activeIngredients = matchIngredients(topConditions);
  const recommendedProducts = matchProducts(activeIngredients, topConditions);
  const aftercare = recommendedProducts.filter(p => p.productType === 'aftercare');
  const monthlyPackRaw = buildMonthlyPack(
    weightInfo.estimatedWeightKg,
    stage,
    recommendedProducts,
    aftercare.length ? aftercare : s.products.filter(p => p.productType === 'aftercare')
  );
  const kibbleItem = monthlyPackRaw.items.find(i => i.product?.productType === 'kibble');
  const kibbleUpgrade = buildKibbleUpgrade(kibbleItem?.product, 'Glucosamine');
  const monthlyPack = enrichMonthlyPack(monthlyPackRaw, weightInfo.estimatedWeightKg, stage);
  const yearlyPack = buildYearlyPack(monthlyPackRaw, recommendedProducts, kibbleUpgrade);

  const pet = {
    dogName,
    breeds,
    birthday,
    ageYears: Math.round(ageYears * 10) / 10,
    ageStage: stage,
    estimatedWeightKg: weightInfo.estimatedWeightKg,
    sizeBracket: sizeBracket(weightInfo.estimatedWeightKg)
  };

  const priorities = buildPriorities(pet, riskList, groomerCategoryBoosts, recommendedProducts, activeIngredients);
  const groomerLive = buildGroomerLive(groomerObs);

  const evidenceLibrary = [];
  const seenEvidence = new Set();
  for (const risk of topConditions) {
    for (const src of risk.sources) {
      const key = src.sourceUrl + src.sourceQuote;
      if (!seenEvidence.has(key)) {
        seenEvidence.add(key);
        evidenceLibrary.push({
          type: 'breed',
          condition: risk.conditionName,
          breed: src.breed,
          sourceName: src.sourceName,
          quote: src.sourceQuote,
          url: src.sourceUrl
        });
      }
    }
  }
  for (const ing of activeIngredients) {
    const key = ing.sourceUrl + ing.evidenceQuote;
    if (!seenEvidence.has(key)) {
      seenEvidence.add(key);
      evidenceLibrary.push({
        type: 'ingredient',
        condition: ing.ingredientName,
        breed: null,
        sourceName: ing.sourceName,
        quote: ing.evidenceQuote,
        url: ing.sourceUrl
      });
    }
  }

  const evidence = evidenceLibrary.map(e => ({
    sourceName: e.sourceName,
    sourceQuote: e.quote,
    sourceUrl: e.url,
    conditionName: e.condition
  }));

  const wellnessScore = Math.max(60, Math.min(98, Math.round(95 - topConditions[0]?.riskPercent * 0.3)));

  return {
    pet,
    wellnessScore,
    priorities,
    healthRisks: topConditions,
    activeIngredients,
    recommendedProducts: recommendedProducts.slice(0, 12),
    monthlyPack,
    yearlyPack,
    evidence,
    evidenceLibrary,
    groomerLive,
    groomerNotes: groomerObs
  };
}

function searchBreeds(query) {
  const s = getStore();
  const q = (query || '').toLowerCase().trim();
  if (!q) return s.breeds.map(b => b.name).slice(0, 20);
  return s.breeds
    .filter(b => b.name.toLowerCase().includes(q))
    .map(b => b.name)
    .slice(0, 15);
}

module.exports = {
  getStore,
  reloadStore,
  loadFromCsv,
  addGroomerObservation,
  computeRecommendations,
  searchBreeds,
  getAgeStage,
  GROOMER_BOOST_MAP
};
