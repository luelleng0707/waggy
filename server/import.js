const fs = require('fs');
const path = require('path');
const { parse } = require('csv-parse/sync');
const { PrismaClient } = require('@prisma/client');

const DATA_DIR = path.join(__dirname, '..', 'data');
const prisma = new PrismaClient();

function readCsv(filename) {
  const filePath = path.join(DATA_DIR, filename);
  if (!fs.existsSync(filePath)) return [];
  return parse(fs.readFileSync(filePath, 'utf8'), {
    columns: true,
    skip_empty_lines: true,
    trim: true
  });
}

async function importAll() {
  console.log('Importing CSV data to database...');

  const breeds = readCsv('breeds.csv');
  for (const r of breeds) {
    await prisma.breed.upsert({
      where: { name: r.name },
      update: {
        sizeClass: r.size_class,
        avgWeightMin: parseFloat(r.avg_weight_min),
        avgWeightMax: parseFloat(r.avg_weight_max),
        coatType: r.coat_type
      },
      create: {
        name: r.name,
        sizeClass: r.size_class,
        avgWeightMin: parseFloat(r.avg_weight_min),
        avgWeightMax: parseFloat(r.avg_weight_max),
        coatType: r.coat_type
      }
    });
  }
  console.log(`  breeds: ${breeds.length}`);

  const breedConditions = readCsv('breed_conditions.csv');
  for (const r of breedConditions) {
    await prisma.breedCondition.upsert({
      where: {
        breedName_conditionName: {
          breedName: r.breed_name,
          conditionName: r.condition_name
        }
      },
      update: {
        riskPercent: parseFloat(r.risk_percent),
        sourceName: r.source_name,
        sourceQuote: r.source_quote,
        sourceUrl: r.source_url
      },
      create: {
        breedName: r.breed_name,
        conditionName: r.condition_name,
        riskPercent: parseFloat(r.risk_percent),
        sourceName: r.source_name,
        sourceQuote: r.source_quote,
        sourceUrl: r.source_url
      }
    });
  }
  console.log(`  breed_conditions: ${breedConditions.length}`);

  const ageConditions = readCsv('age_conditions.csv');
  for (const r of ageConditions) {
    await prisma.ageCondition.upsert({
      where: {
        ageStage_conditionName: {
          ageStage: r.age_stage,
          conditionName: r.condition_name
        }
      },
      update: {
        riskPercent: parseFloat(r.risk_percent),
        sourceName: r.source_name,
        sourceQuote: r.source_quote,
        sourceUrl: r.source_url
      },
      create: {
        ageStage: r.age_stage,
        conditionName: r.condition_name,
        riskPercent: parseFloat(r.risk_percent),
        sourceName: r.source_name,
        sourceQuote: r.source_quote,
        sourceUrl: r.source_url
      }
    });
  }
  console.log(`  age_conditions: ${ageConditions.length}`);

  const ingredients = readCsv('ingredients.csv');
  for (const r of ingredients) {
    await prisma.ingredient.upsert({
      where: { ingredientName: r.ingredient_name },
      update: {
        benefits: r.benefits,
        evidenceQuote: r.evidence_quote,
        sourceName: r.source_name,
        sourceUrl: r.source_url
      },
      create: {
        ingredientName: r.ingredient_name,
        benefits: r.benefits,
        evidenceQuote: r.evidence_quote,
        sourceName: r.source_name,
        sourceUrl: r.source_url
      }
    });
  }
  console.log(`  ingredients: ${ingredients.length}`);

  const conditionIngredients = readCsv('condition_ingredients.csv');
  for (const r of conditionIngredients) {
    await prisma.conditionIngredient.upsert({
      where: {
        conditionName_ingredientName: {
          conditionName: r.condition_name,
          ingredientName: r.ingredient_name
        }
      },
      update: { dailyTargetMg: parseFloat(r.daily_target_mg) },
      create: {
        conditionName: r.condition_name,
        ingredientName: r.ingredient_name,
        dailyTargetMg: parseFloat(r.daily_target_mg)
      }
    });
  }
  console.log(`  condition_ingredients: ${conditionIngredients.length}`);

  const products = readCsv('products.csv');
  for (const r of products) {
    await prisma.product.upsert({
      where: { productName: r.product_name },
      update: {
        brand: r.brand,
        productType: r.product_type,
        price: parseFloat(r.price),
        weightG: r.weight_g ? parseFloat(r.weight_g) : null,
        unitCount: r.unit_count ? parseInt(r.unit_count, 10) : null,
        shelfLifeDays: r.shelf_life_days ? parseInt(r.shelf_life_days, 10) : null,
        freshBool: r.fresh_bool === 'true',
        kcalPerPiece: r.kcal_per_piece ? parseFloat(r.kcal_per_piece) : null
      },
      create: {
        productName: r.product_name,
        brand: r.brand,
        productType: r.product_type,
        price: parseFloat(r.price),
        weightG: r.weight_g ? parseFloat(r.weight_g) : null,
        unitCount: r.unit_count ? parseInt(r.unit_count, 10) : null,
        shelfLifeDays: r.shelf_life_days ? parseInt(r.shelf_life_days, 10) : null,
        freshBool: r.fresh_bool === 'true',
        kcalPerPiece: r.kcal_per_piece ? parseFloat(r.kcal_per_piece) : null
      }
    });
  }
  console.log(`  products: ${products.length}`);

  const productIngredients = readCsv('product_ingredients.csv');
  for (const r of productIngredients) {
    await prisma.productIngredient.upsert({
      where: {
        productName_ingredientName: {
          productName: r.product_name,
          ingredientName: r.ingredient_name
        }
      },
      update: { amountPerUnitMg: parseFloat(r.amount_per_unit_mg) },
      create: {
        productName: r.product_name,
        ingredientName: r.ingredient_name,
        amountPerUnitMg: parseFloat(r.amount_per_unit_mg)
      }
    });
  }
  console.log(`  product_ingredients: ${productIngredients.length}`);

  const observations = readCsv('groomer_observations.csv').filter(r => r.pet_name);
  await prisma.groomerObservation.deleteMany();
  for (const r of observations) {
    await prisma.groomerObservation.create({
      data: {
        petName: r.pet_name,
        observation: r.observation,
        severity: r.severity,
        photoUrl: r.photo_url || null
      }
    });
  }
  console.log(`  groomer_observations: ${observations.length}`);
  console.log('Import complete.');
}

if (require.main === module) {
  importAll()
    .catch(err => {
      console.error('Import failed:', err.message);
      process.exit(1);
    })
    .finally(() => prisma.$disconnect());
}

module.exports = { importAll };
