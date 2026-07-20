# Data Dictionary (Current Schema)

**Status:** Official reference for columns as they exist **today** under data/.  
**Target schema:** [DATA_ARCHITECTURE_V2.md](DATA_ARCHITECTURE_V2.md) · [DATA_NORMALIZATION.md](DATA_NORMALIZATION.md)  
**Policy:** Planning documents only — no runtime change in this phase.

## How to read

| Field | Meaning |
|-------|---------|
| Ownership | Scientific / Clinical / Product / Reference / Parser / Algorithm / Derived / Display / Metadata |
| Intern edit? | Whether an intern should change the value in CSV |
| Disposition | KEEP (normalize later) / MOVE→Python / REVIEW / DERIVE or DROP |

Foreign keys and PKs today are declared in data/manifest.yaml where present.

Validation: empty strings are common; numeric fields often stored as strings in CSV.

---

## Conventions (current — to be canonicalized)

| Concept | Names seen today | Target |
|---------|------------------|--------|
| Ingredient | ingredient, ingredient_name, canonical_ingredient, canonical_key | ingredient_key |
| Condition | condition, condition_name | condition_key |
| Dose | recommended_daily_dose, target_dose | daily_target |
| Unit | dose_unit, target_unit, unit | unit |
| Citation | inline source_* columns | evidence_id → EVIDENCE |

---

## Column catalog by file


### `data/breed_analysis/1_biological_traits/BREED_ALIASES.csv`

Rows: **4** · Columns: **2**

| Column | Type | Example | Ownership | Nullable | Intern edit? | Disposition |
|--------|------|---------|-----------|----------|--------------|-------------|
| `alias` | str | lab | Parser | Often | No | MOVE→Python / DELETE |
| `canonical_breed` | str | Labrador Retriever | Parser | Often | No | MOVE→Python / DELETE |

### `data/breed_analysis/1_biological_traits/BREEDS.csv`

Rows: **48** · Columns: **10**

| Column | Type | Example | Ownership | Nullable | Intern edit? | Disposition |
|--------|------|---------|-----------|----------|--------------|-------------|
| `breed` | str | Alaskan Malamute | Scientific | Often | Yes | KEEP (normalize name) |
| `size` | str | Giant | Scientific | Often | Yes | KEEP (normalize name) |
| `body_type` | str | Athletic | Scientific | Often | Yes | KEEP (normalize name) |
| `coat_type` | str | Double Coat | Scientific | Often | Yes | KEEP (normalize name) |
| `energy` | str | High | Scientific | Often | Yes | KEEP (normalize name) |
| `weakness_group` | str | Joint Heavy | Scientific | Often | Yes | KEEP (normalize name) |
| `skull_type` | str | Mesocephalic | Scientific | Often | Yes | KEEP (normalize name) |
| `climate` | str | Cold Tolerant | Scientific | Often | Yes | KEEP (normalize name) |
| `lifespan` | str | Medium | Scientific | Often | Yes | KEEP (normalize name) |
| `function_group` | str | Working | Scientific | Often | Yes | KEEP (normalize name) |

### `data/breed_analysis/1_biological_traits/MIXED_BREED_INTERACTIONS.csv`

Rows: **10** · Columns: **7**

| Column | Type | Example | Ownership | Nullable | Intern edit? | Disposition |
|--------|------|---------|-----------|----------|--------------|-------------|
| `trait_a` | str | Deep Chested | Scientific | Often | Yes | KEEP (normalize name) |
| `trait_b` | str | Giant | Scientific | Often | Yes | KEEP (normalize name) |
| `condition` | str | GDV | Clinical | Often | Yes | KEEP (normalize name) |
| `interaction` | str | increase | Scientific | Often | Yes | KEEP (normalize name) |
| `factor` | number|str | 1.42 | Scientific | Often | Yes | KEEP (normalize name) |
| `reason` | str | Thoracic depth and gastric mobility amplify volvulus ri | Clinical | Often | Yes | KEEP (normalize name) |
| `source` | str | Emergency GI Outcomes Group 2022 | Reference | Often | Yes | KEEP (normalize name) |

### `data/breed_analysis/1_biological_traits/MIXED_BREED_MATRIX.csv`

Rows: **5** · Columns: **7**

| Column | Type | Example | Ownership | Nullable | Intern edit? | Disposition |
|--------|------|---------|-----------|----------|--------------|-------------|
| `breed_a` | str | Siberian Husky | Scientific | Often | Yes | KEEP (normalize name) |
| `breed_b` | str | Pembroke Welsh Corgi | Scientific | Often | Yes | KEEP (normalize name) |
| `condition` | str | Hip Dysplasia | Clinical | Often | Yes | KEEP (normalize name) |
| `factor` | number|str | 1.07 | Scientific | Often | Yes | KEEP (normalize name) |
| `source_name` | str | Canine Mixed-Breed Orthopedic Study | Reference | Often | Yes | KEEP (normalize name) |
| `source_quote` | str | Husky × Corgi crosses showed modestly elevated hip dysp | Reference | Often | Yes | KEEP (normalize name) |
| `source_url` | str | https://pubmed.ncbi.nlm.nih.gov/30123701 | Reference | Often | Yes | KEEP (normalize name) |

### `data/breed_analysis/2_evolutionary_profiles/ENVIRONMENTAL_MATRICES.csv`

Rows: **6** · Columns: **10**

| Column | Type | Example | Ownership | Nullable | Intern edit? | Disposition |
|--------|------|---------|-----------|----------|--------------|-------------|
| `trait_category` | str | coat_type | Scientific | Often | Yes | KEEP (normalize name) |
| `trait_value` | number|str | Double Coat | Scientific | Often | Yes | KEEP (normalize name) |
| `trait` | str | Double Coat | Derived | Often | No | MOVE→Python / DELETE |
| `climate_context` | str | Shanghai Summer | Scientific | Often | Yes | KEEP (normalize name) |
| `dimension` | str | humidity | Scientific | Often | Yes | KEEP (normalize name) |
| `compatibility_score` | number|str | 0.62 | Algorithm | Often | Careful | REVIEW (algo/display) |
| `management_note` | str | Humidity increases coat moisture retention — increase g | Clinical | Often | Yes | KEEP (normalize name) |
| `source_name` | str | European Veterinary Dermatology Consortium | Reference | Often | Yes | KEEP (normalize name) |
| `source_quote` | str | Humid summers elevate moist dermatitis risk in double-c | Reference | Often | Yes | KEEP (normalize name) |
| `source_url` | str | https://pubmed.ncbi.nlm.nih.gov/30123504 | Reference | Often | Yes | KEEP (normalize name) |

### `data/breed_analysis/2_evolutionary_profiles/TRAIT_ATTRIBUTE_EXPLANATIONS.csv`

Rows: **10** · Columns: **10**

| Column | Type | Example | Ownership | Nullable | Intern edit? | Disposition |
|--------|------|---------|-----------|----------|--------------|-------------|
| `trait_category` | str | size | Scientific | Often | Yes | KEEP (normalize name) |
| `trait_value` | number|str | Large | Scientific | Often | Yes | KEEP (normalize name) |
| `card_title` | str | Large Breed | Display | Often | No | MOVE→Python / DELETE |
| `explanation` | str | Increased skeletal loading and joint torque versus smal | Clinical | Often | Yes | KEEP (normalize name) |
| `related_conditions` | str | Hip Dysplasia/Obesity/Cruciate Ligament Rupture | Derived | Often | No | DERIVE or DROP |
| `evidence_level` | str | high | Reference | Often | Yes | KEEP (normalize name) |
| `evidence_id` | str | EVD-ORTHO-001 | Reference | Often | Yes | KEEP (normalize name) |
| `source_csv` | str | BREEDS.csv | Metadata | Often | No | MOVE→Python / DELETE |
| `source_name` | str | OFA Functional Group Analysis | Reference | Often | Yes | KEEP (normalize name) |
| `source_url` | str | https://pubmed.ncbi.nlm.nih.gov/30123501 | Reference | Often | Yes | KEEP (normalize name) |

### `data/breed_analysis/2_evolutionary_profiles/TRAIT_PURPOSES.csv`

Rows: **5** · Columns: **7**

| Column | Type | Example | Ownership | Nullable | Intern edit? | Disposition |
|--------|------|---------|-----------|----------|--------------|-------------|
| `trait_category` | str | function_group | Scientific | Often | Yes | KEEP (normalize name) |
| `trait_value` | number|str | Sporting | Scientific | Often | Yes | KEEP (normalize name) |
| `biological_purpose` | str | Retrieval and field work selection | Clinical | Often | Yes | KEEP (normalize name) |
| `advantage_summary` | str | Highly trainable/Strong endurance/Excellent human bondi | Clinical | Often | Yes | KEEP (normalize name) |
| `source_name` | str | Working Dog Performance Review | Reference | Often | Yes | KEEP (normalize name) |
| `source_quote` | str | Sporting breeds demonstrate superior trainability and s | Reference | Often | Yes | KEEP (normalize name) |
| `source_url` | str | https://pubmed.ncbi.nlm.nih.gov/30123641 | Reference | Often | Yes | KEEP (normalize name) |

### `data/breed_analysis/3_management_considerations/BODYTYPE_CONDITIONS.csv`

Rows: **10** · Columns: **10**

| Column | Type | Example | Ownership | Nullable | Intern edit? | Disposition |
|--------|------|---------|-----------|----------|--------------|-------------|
| `body_type` | str | Athletic | Scientific | Often | Yes | KEEP (normalize name) |
| `condition` | str | Hip Dysplasia | Clinical | Often | Yes | KEEP (normalize name) |
| `prevalence` | str | 0.08 | Scientific | Often | Yes | KEEP (normalize name) |
| `sample_population` | str | Athletic breed screening cohort | Reference | Often | Yes | KEEP (normalize name) |
| `sample_size` | str | 2700 | Reference | Often | Yes | KEEP (normalize name) |
| `source_name` | str | Journal of Veterinary Medicine | Reference | Often | Yes | KEEP (normalize name) |
| `source_quote` | str | Athletic breed groups exhibited moderate hip dysplasia  | Reference | Often | Yes | KEEP (normalize name) |
| `source_url` | str | https://pmc.ncbi.nlm.nih.gov/articles/PMC5366211/ | Reference | Often | Yes | KEEP (normalize name) |
| `year` | str | 2017 | Reference | Often | Yes | KEEP (normalize name) |
| `confidence_level` | str | medium | Reference | Often | Yes | KEEP (normalize name) |

### `data/breed_analysis/3_management_considerations/BREED_CONDITIONS.csv`

Rows: **16** · Columns: **10**

| Column | Type | Example | Ownership | Nullable | Intern edit? | Disposition |
|--------|------|---------|-----------|----------|--------------|-------------|
| `breed` | str | Labrador Retriever | Scientific | Often | Yes | KEEP (normalize name) |
| `condition` | str | Hip Dysplasia | Clinical | Often | Yes | KEEP (normalize name) |
| `prevalence` | str | 0.127 | Scientific | Often | Yes | KEEP (normalize name) |
| `sample_population` | str | Labrador registry cohort | Reference | Often | Yes | KEEP (normalize name) |
| `sample_size` | str | 4200 | Reference | Often | Yes | KEEP (normalize name) |
| `source_name` | str | BMC Genomics | Reference | Often | Yes | KEEP (normalize name) |
| `source_quote` | str | Labrador Retrievers showed consistently elevated hip dy | Reference | Often | Yes | KEEP (normalize name) |
| `source_url` | str | https://pmc.ncbi.nlm.nih.gov/articles/PMC7818755/ | Reference | Often | Yes | KEEP (normalize name) |
| `year` | str | 2021 | Reference | Often | Yes | KEEP (normalize name) |
| `confidence_level` | str | high | Reference | Often | Yes | KEEP (normalize name) |

### `data/breed_analysis/3_management_considerations/CLIMATE_CONDITIONS.csv`

Rows: **10** · Columns: **10**

| Column | Type | Example | Ownership | Nullable | Intern edit? | Disposition |
|--------|------|---------|-----------|----------|--------------|-------------|
| `climate` | str | Cold Tolerant | Scientific | Often | Yes | KEEP (normalize name) |
| `condition` | str | Atopic Dermatitis | Clinical | Often | Yes | KEEP (normalize name) |
| `prevalence` | str | 0.11 | Scientific | Often | Yes | KEEP (normalize name) |
| `sample_population` | str | Cold climate registry | Reference | Often | Yes | KEEP (normalize name) |
| `sample_size` | str | 2800 | Reference | Often | Yes | KEEP (normalize name) |
| `source_name` | str | Frontiers in Veterinary Science | Reference | Often | Yes | KEEP (normalize name) |
| `source_quote` | str | Cold-adapted breed populations still exhibited measurab | Reference | Often | Yes | KEEP (normalize name) |
| `source_url` | str | https://pmc.ncbi.nlm.nih.gov/articles/PMC12221898/ | Reference | Often | Yes | KEEP (normalize name) |
| `year` | str | 2024 | Reference | Often | Yes | KEEP (normalize name) |
| `confidence_level` | str | medium | Reference | Often | Yes | KEEP (normalize name) |

### `data/breed_analysis/3_management_considerations/CLINICAL_RISK_TIMELINE.csv`

Rows: **6** · Columns: **7**

| Column | Type | Example | Ownership | Nullable | Intern edit? | Disposition |
|--------|------|---------|-----------|----------|--------------|-------------|
| `age_stage` | str | Puppy | Clinical | Often | Yes | KEEP (normalize name) |
| `trait_or_breed` | str | Large | Clinical | Often | Yes | KEEP (normalize name) |
| `condition` | str | Hip Dysplasia | Clinical | Often | Yes | KEEP (normalize name) |
| `risk_level` | str | monitor | Clinical | Often | Yes | KEEP (normalize name) |
| `monitoring` | str | Growth plate radiographs at 12–18 months | Clinical | Often | Yes | KEEP (normalize name) |
| `prevention` | str | Controlled calorie growth diet/Avoid high-impact jumpin | Clinical | Often | Yes | KEEP (normalize name) |
| `evidence_id` | str | EVD-ORTHO-001 | Reference | Often | Yes | KEEP (normalize name) |

### `data/breed_analysis/3_management_considerations/COATTYPE_CONDITIONS.csv`

Rows: **10** · Columns: **10**

| Column | Type | Example | Ownership | Nullable | Intern edit? | Disposition |
|--------|------|---------|-----------|----------|--------------|-------------|
| `coat_type` | str | Double Coat | Scientific | Often | Yes | KEEP (normalize name) |
| `condition` | str | Atopic Dermatitis | Clinical | Often | Yes | KEEP (normalize name) |
| `prevalence` | str | 0.14 | Scientific | Often | Yes | KEEP (normalize name) |
| `sample_population` | str | Double coat registry | Reference | Often | Yes | KEEP (normalize name) |
| `sample_size` | str | 3140 | Reference | Often | Yes | KEEP (normalize name) |
| `source_name` | str | European Veterinary Dermatology Consortium | Reference | Often | Yes | KEEP (normalize name) |
| `source_quote` | str | Dense undercoat cohorts showed higher recurrent dermati | Reference | Often | Yes | KEEP (normalize name) |
| `source_url` | str | https://pubmed.ncbi.nlm.nih.gov/30123421 | Reference | Often | Yes | KEEP (normalize name) |
| `year` | str | 2021 | Reference | Often | Yes | KEEP (normalize name) |
| `confidence_level` | str | medium | Reference | Often | Yes | KEEP (normalize name) |

### `data/breed_analysis/3_management_considerations/ENERGY_CONDITIONS.csv`

Rows: **10** · Columns: **10**

| Column | Type | Example | Ownership | Nullable | Intern edit? | Disposition |
|--------|------|---------|-----------|----------|--------------|-------------|
| `energy` | str | Low | Scientific | Often | Yes | KEEP (normalize name) |
| `condition` | str | Obesity | Clinical | Often | Yes | KEEP (normalize name) |
| `prevalence` | str | 0.24 | Scientific | Often | Yes | KEEP (normalize name) |
| `sample_population` | str | Low activity cohort | Reference | Often | Yes | KEEP (normalize name) |
| `sample_size` | str | 4150 | Reference | Often | Yes | KEEP (normalize name) |
| `source_name` | str | Frontiers in Veterinary Science | Reference | Often | Yes | KEEP (normalize name) |
| `source_quote` | str | Low-activity sedentary dog populations carried signific | Reference | Often | Yes | KEEP (normalize name) |
| `source_url` | str | https://pmc.ncbi.nlm.nih.gov/articles/PMC10713818/ | Reference | Often | Yes | KEEP (normalize name) |
| `year` | str | 2023 | Reference | Often | Yes | KEEP (normalize name) |
| `confidence_level` | str | high | Reference | Often | Yes | KEEP (normalize name) |

### `data/breed_analysis/3_management_considerations/FUNCTIONGROUP_CONDITIONS.csv`

Rows: **10** · Columns: **10**

| Column | Type | Example | Ownership | Nullable | Intern edit? | Disposition |
|--------|------|---------|-----------|----------|--------------|-------------|
| `function_group` | str | Working | Scientific | Often | Yes | KEEP (normalize name) |
| `condition` | str | Hip Dysplasia | Clinical | Often | Yes | KEEP (normalize name) |
| `prevalence` | str | 0.14 | Scientific | Often | Yes | KEEP (normalize name) |
| `sample_population` | str | Working breed registry | Reference | Often | Yes | KEEP (normalize name) |
| `sample_size` | str | 2420 | Reference | Often | Yes | KEEP (normalize name) |
| `source_name` | str | Journal of Veterinary Medicine | Reference | Often | Yes | KEEP (normalize name) |
| `source_quote` | str | Working breed groups maintained elevated hip dysplasia  | Reference | Often | Yes | KEEP (normalize name) |
| `source_url` | str | https://pmc.ncbi.nlm.nih.gov/articles/PMC5366211/ | Reference | Often | Yes | KEEP (normalize name) |
| `year` | str | 2017 | Reference | Often | Yes | KEEP (normalize name) |
| `confidence_level` | str | high | Reference | Often | Yes | KEEP (normalize name) |

### `data/breed_analysis/3_management_considerations/LIFESPAN_CONDITIONS.csv`

Rows: **10** · Columns: **10**

| Column | Type | Example | Ownership | Nullable | Intern edit? | Disposition |
|--------|------|---------|-----------|----------|--------------|-------------|
| `lifespan` | str | Short | Scientific | Often | Yes | KEEP (normalize name) |
| `condition` | str | Dilated Cardiomyopathy | Clinical | Often | Yes | KEEP (normalize name) |
| `prevalence` | str | 0.10 | Scientific | Often | Yes | KEEP (normalize name) |
| `sample_population` | str | Short-lifespan breed cohort | Reference | Often | Yes | KEEP (normalize name) |
| `sample_size` | str | 1110 | Reference | Often | Yes | KEEP (normalize name) |
| `source_name` | str | Frontiers in Veterinary Science | Reference | Often | Yes | KEEP (normalize name) |
| `source_quote` | str | Short-lifespan large and giant breed cohorts showed ele | Reference | Often | Yes | KEEP (normalize name) |
| `source_url` | str | https://pmc.ncbi.nlm.nih.gov/articles/PMC8606013/ | Reference | Often | Yes | KEEP (normalize name) |
| `year` | str | 2021 | Reference | Often | Yes | KEEP (normalize name) |
| `confidence_level` | str | medium | Reference | Often | Yes | KEEP (normalize name) |

### `data/breed_analysis/3_management_considerations/SIZE_CONDITIONS.csv`

Rows: **10** · Columns: **10**

| Column | Type | Example | Ownership | Nullable | Intern edit? | Disposition |
|--------|------|---------|-----------|----------|--------------|-------------|
| `size` | str | Toy | Scientific | Often | Yes | KEEP (normalize name) |
| `condition` | str | Dental Disease | Clinical | Often | Yes | KEEP (normalize name) |
| `prevalence` | str | 0.362 | Scientific | Often | Yes | KEEP (normalize name) |
| `sample_population` | str | Toy breed cohort | Reference | Often | Yes | KEEP (normalize name) |
| `sample_size` | str | 1840 | Reference | Often | Yes | KEEP (normalize name) |
| `source_name` | str | Smith et al. Journal of Small Animal Dentistry | Reference | Often | Yes | KEEP (normalize name) |
| `source_quote` | str | Toy breeds showed significantly higher periodontal burd | Reference | Often | Yes | KEEP (normalize name) |
| `source_url` | str | https://pubmed.ncbi.nlm.nih.gov/30123401 | Reference | Often | Yes | KEEP (normalize name) |
| `year` | str | 2021 | Reference | Often | Yes | KEEP (normalize name) |
| `confidence_level` | str | high | Reference | Often | Yes | KEEP (normalize name) |

### `data/breed_analysis/3_management_considerations/SKULLTYPE_CONDITIONS.csv`

Rows: **10** · Columns: **10**

| Column | Type | Example | Ownership | Nullable | Intern edit? | Disposition |
|--------|------|---------|-----------|----------|--------------|-------------|
| `skull_type` | str | Brachycephalic | Scientific | Often | Yes | KEEP (normalize name) |
| `condition` | str | BOAS | Clinical | Often | Yes | KEEP (normalize name) |
| `prevalence` | str | 0.487 | Scientific | Often | Yes | KEEP (normalize name) |
| `sample_population` | str | Brachycephalic multicenter cohort | Reference | Often | Yes | KEEP (normalize name) |
| `sample_size` | str | 2010 | Reference | Often | Yes | KEEP (normalize name) |
| `source_name` | str | Royal Veterinary College BOAS Program | Reference | Often | Yes | KEEP (normalize name) |
| `source_quote` | str | Brachycephalic conformation showed markedly elevated BO | Reference | Often | Yes | KEEP (normalize name) |
| `source_url` | str | https://pubmed.ncbi.nlm.nih.gov/30123441 | Reference | Often | Yes | KEEP (normalize name) |
| `year` | str | 2023 | Reference | Often | Yes | KEEP (normalize name) |
| `confidence_level` | str | high | Reference | Often | Yes | KEEP (normalize name) |

### `data/breed_analysis/3_management_considerations/TRAIT_CONTRIBUTION_WEIGHTS.csv`

Rows: **7** · Columns: **8**

| Column | Type | Example | Ownership | Nullable | Intern edit? | Disposition |
|--------|------|---------|-----------|----------|--------------|-------------|
| `trait_category` | str | size | Scientific | Often | Yes | KEEP (normalize name) |
| `trait_value` | number|str | Large | Scientific | Often | Yes | KEEP (normalize name) |
| `condition` | str | Hip Dysplasia | Clinical | Often | Yes | KEEP (normalize name) |
| `risk_delta` | number|str | 12 | Algorithm | Often | Careful | REVIEW (algo/display) |
| `unit` | str | percent | Scientific | Often | Yes | KEEP (normalize name) |
| `source_csv` | str | BREEDS.csv/SIZE_CONDITIONS.csv | Metadata | Often | No | MOVE→Python / DELETE |
| `evidence_id` | str | EVD-ORTHO-001 | Reference | Often | Yes | KEEP (normalize name) |
| `mechanism_note` | str | Increased skeletal loading on hip joints | Clinical | Often | Yes | KEEP (normalize name) |

### `data/breed_analysis/3_management_considerations/TRAIT_INTERACTIONS.csv`

Rows: **10** · Columns: **7**

| Column | Type | Example | Ownership | Nullable | Intern edit? | Disposition |
|--------|------|---------|-----------|----------|--------------|-------------|
| `trait_a` | str | Deep Chested | Scientific | Often | Yes | KEEP (normalize name) |
| `trait_b` | str | Giant | Scientific | Often | Yes | KEEP (normalize name) |
| `condition` | str | GDV | Clinical | Often | Yes | KEEP (normalize name) |
| `interaction` | str | increase | Scientific | Often | Yes | KEEP (normalize name) |
| `factor` | number|str | 1.42 | Scientific | Often | Yes | KEEP (normalize name) |
| `reason` | str | Thoracic depth and gastric mobility amplify volvulus ri | Clinical | Often | Yes | KEEP (normalize name) |
| `source` | str | Emergency GI Outcomes Group 2022 | Reference | Often | Yes | KEEP (normalize name) |

### `data/breed_analysis/3_management_considerations/WEAKNESSGROUP_CONDITIONS.csv`

Rows: **10** · Columns: **10**

| Column | Type | Example | Ownership | Nullable | Intern edit? | Disposition |
|--------|------|---------|-----------|----------|--------------|-------------|
| `weakness_group` | str | Joint Heavy | Scientific | Often | Yes | KEEP (normalize name) |
| `condition` | str | Hip Dysplasia | Clinical | Often | Yes | KEEP (normalize name) |
| `prevalence` | str | 0.217 | Scientific | Often | Yes | KEEP (normalize name) |
| `sample_population` | str | Joint-heavy breed strata | Reference | Often | Yes | KEEP (normalize name) |
| `sample_size` | str | 3010 | Reference | Often | Yes | KEEP (normalize name) |
| `source_name` | str | OFA Functional Group Analysis | Reference | Often | Yes | KEEP (normalize name) |
| `source_quote` | str | Joint-heavy group classification strongly associated wi | Reference | Often | Yes | KEEP (normalize name) |
| `source_url` | str | https://pubmed.ncbi.nlm.nih.gov/30123471 | Reference | Often | Yes | KEEP (normalize name) |
| `year` | str | 2022 | Reference | Often | Yes | KEEP (normalize name) |
| `confidence_level` | str | high | Reference | Often | Yes | KEEP (normalize name) |

### `data/breed_analysis/4_preventative_interventions/ACTIVITY_EVIDENCE.csv`

Rows: **10** · Columns: **5**

| Column | Type | Example | Ownership | Nullable | Intern edit? | Disposition |
|--------|------|---------|-----------|----------|--------------|-------------|
| `activity_name` | str | Hydrotherapy treadmill | Clinical | Often | Yes | KEEP (normalize name) |
| `source_name` | str | A Survey of Canine Hydrotherapy Centres and Underwater  | Reference | Often | Yes | KEEP (normalize name) |
| `source_quote` | str | Reduces peak limb loading by 47% with 92% of clinics re | Reference | Often | Yes | KEEP (normalize name) |
| `source_url` | str | https://pubmed.ncbi.nlm.nih.gov/29666221/ | Reference | Often | Yes | KEEP (normalize name) |
| `year` | str | 2018 | Reference | Often | Yes | KEEP (normalize name) |

### `data/breed_analysis/4_preventative_interventions/ACTIVITY_PRESCRIPTION_RULES.csv`

Rows: **4** · Columns: **15**

| Column | Type | Example | Ownership | Nullable | Intern edit? | Disposition |
|--------|------|---------|-----------|----------|--------------|-------------|
| `energy` | str | High | Scientific | Often | Yes | KEEP (normalize name) |
| `size` | str | Large | Scientific | Often | Yes | KEEP (normalize name) |
| `body_type` | str | Athletic | Scientific | Often | Yes | KEEP (normalize name) |
| `age_stage` | str | Adult | Clinical | Often | Yes | KEEP (normalize name) |
| `daily_km` | number|str | 8.5 | Clinical | Often | Yes | KEEP (normalize name) |
| `walk_morning_min` | number|str | 35 | Clinical | Often | Yes | KEEP (normalize name) |
| `walk_evening_min` | number|str | 40 | Clinical | Often | Yes | KEEP (normalize name) |
| `weekly_km` | number|str | 59.5 | Clinical | Often | Yes | KEEP (normalize name) |
| `mental_enrichment` | str | daily | Clinical | Often | Yes | KEEP (normalize name) |
| `swimming` | number|str | weekly | Clinical | Often | Yes | KEEP (normalize name) |
| `fetch` | str | 3x weekly | Clinical | Often | Yes | KEEP (normalize name) |
| `training` | str | daily | Clinical | Often | Yes | KEEP (normalize name) |
| `recovery_note` | str | 48h low-impact after intense sessions | Clinical | Often | Yes | KEEP (normalize name) |
| `source_name` | str | Working Dog Performance Review | Reference | Often | Yes | KEEP (normalize name) |
| `source_url` | str | https://pubmed.ncbi.nlm.nih.gov/30123641 | Reference | Often | Yes | KEEP (normalize name) |

### `data/breed_analysis/4_preventative_interventions/CONDITION_ACTIVITIES.csv`

Rows: **10** · Columns: **7**

| Column | Type | Example | Ownership | Nullable | Intern edit? | Disposition |
|--------|------|---------|-----------|----------|--------------|-------------|
| `condition` | str | Hip Dysplasia | Clinical | Often | Yes | KEEP (normalize name) |
| `activity_name` | str | Hydrotherapy treadmill | Clinical | Often | Yes | KEEP (normalize name) |
| `frequency` | str | weekly | Clinical | Often | Yes | KEEP (normalize name) |
| `duration_minutes` | number|str | 30 | Clinical | Often | Yes | KEEP (normalize name) |
| `source_name` | str | Animals | Reference | Often | Yes | KEEP (normalize name) |
| `source_quote` | str | Underwater treadmill hydrotherapy improved joint range  | Reference | Often | Yes | KEEP (normalize name) |
| `source_url` | str | https://pmc.ncbi.nlm.nih.gov/articles/PMC12607352/ | Reference | Often | Yes | KEEP (normalize name) |

### `data/breed_analysis/4_preventative_interventions/GROOMING_OBSERVATION_DEFS.csv`

Rows: **10** · Columns: **8**

| Column | Type | Example | Ownership | Nullable | Intern edit? | Disposition |
|--------|------|---------|-----------|----------|--------------|-------------|
| `observation_key` | str | eyes | Clinical | Often | Yes | KEEP (normalize name) |
| `label` | str | Eyes | Display | Often | No | MOVE→Python / DELETE |
| `normal_criteria` | str | Clear without discharge | Clinical | Often | Yes | KEEP (normalize name) |
| `monitor_criteria` | str | Light tear staining returning | Clinical | Often | Yes | KEEP (normalize name) |
| `attention_criteria` | str | Persistent redness or swelling | Clinical | Often | Yes | KEEP (normalize name) |
| `severity_scale` | str | 0-3 | Clinical | Often | Yes | KEEP (normalize name) |
| `recommendation_template` | str | Continue weekly eye-area cleaning per grooming protocol | Display | Often | No | MOVE→Python / DELETE |
| `source_csv` | str | GROOMING_SESSIONS | Metadata | Often | No | MOVE→Python / DELETE |

### `data/breed_analysis/4_preventative_interventions/TRAIT_BENEFITS.csv`

Rows: **10** · Columns: **6**

| Column | Type | Example | Ownership | Nullable | Intern edit? | Disposition |
|--------|------|---------|-----------|----------|--------------|-------------|
| `trait_a` | str | Athletic | Scientific | Often | Yes | KEEP (normalize name) |
| `trait_b` | str | Joint Heavy | Scientific | Often | Yes | KEEP (normalize name) |
| `condition` | str | Hip Dysplasia | Clinical | Often | Yes | KEEP (normalize name) |
| `reduction_factor` | number|str | 0.86 | Scientific | Often | Yes | KEEP (normalize name) |
| `reason` | str | Stronger periarticular musculature lowers joint instabi | Clinical | Often | Yes | KEEP (normalize name) |
| `source` | str | Canine Biomechanics Review 2022 | Reference | Often | Yes | KEEP (normalize name) |

### `data/breed_analysis/5_scientific_nutrition/CLINICAL_EVIDENCE_BASE.csv`

Rows: **7** · Columns: **10**

| Column | Type | Example | Ownership | Nullable | Intern edit? | Disposition |
|--------|------|---------|-----------|----------|--------------|-------------|
| `evidence_id` | str | EVD-ORTHO-001 | Reference | Often | Yes | KEEP (normalize name) |
| `domain` | str | orthopedic | Clinical | Often | Yes | KEEP (normalize name) |
| `condition` | str | Hip Dysplasia | Clinical | Often | Yes | KEEP (normalize name) |
| `nutrient_or_activity` | str | Glucosamine | Clinical | Often | Yes | KEEP (normalize name) |
| `mechanism` | str | Chondroprotective support in loaded joints | Scientific | Often | Yes | KEEP (normalize name) |
| `evidence_level` | str | high | Reference | Often | Yes | KEEP (normalize name) |
| `source_name` | str | OFA Breed Registry | Reference | Often | Yes | KEEP (normalize name) |
| `source_quote` | str | Large and sporting breeds show elevated hip dysplasia p | Reference | Often | Yes | KEEP (normalize name) |
| `source_url` | str | https://pubmed.ncbi.nlm.nih.gov/30123501 | Reference | Yes | Yes | KEEP (normalize name) |
| `year` | str | 2022 | Reference | Yes | Yes | KEEP (normalize name) |

### `data/breed_analysis/5_scientific_nutrition/CONDITION_INGREDIENTS.csv`

Rows: **12** · Columns: **9**

| Column | Type | Example | Ownership | Nullable | Intern edit? | Disposition |
|--------|------|---------|-----------|----------|--------------|-------------|
| `condition` | str | Hip Dysplasia | Clinical | Often | Yes | KEEP (normalize name) |
| `ingredient_name` | str | Glucosamine | Scientific | Often | Yes | KEEP (normalize name) |
| `recommended_daily_dose` | number|str | 500 | Scientific | Often | Yes | KEEP (normalize name) |
| `dose_unit` | number|str | mg | Scientific | Often | Yes | KEEP (normalize name) |
| `source_name` | str | Frontiers in Veterinary Science | Reference | Often | Yes | KEEP (normalize name) |
| `source_quote` | str | Glucosamine-based nutraceuticals showed variable effica | Reference | Often | Yes | KEEP (normalize name) |
| `source_url` | str | https://pmc.ncbi.nlm.nih.gov/articles/PMC9499673/ | Reference | Often | Yes | KEEP (normalize name) |
| `priority_rank` | number|str | 1 | Algorithm | Often | Careful | REVIEW (algo/display) |
| `evidence_type` | str | — | Reference | Yes | Yes | KEEP (normalize name) |

### `data/breed_analysis/5_scientific_nutrition/INGREDIENT_ALIASES.csv`

Rows: **6** · Columns: **4**

| Column | Type | Example | Ownership | Nullable | Intern edit? | Disposition |
|--------|------|---------|-----------|----------|--------------|-------------|
| `canonical_key` | str | omega_3 | Parser | Often | No | MOVE→Python / DELETE |
| `alias_key` | str | omega_3 | Parser | Often | No | MOVE→Python / DELETE |
| `category` | str | nutrient | Product | Often | Yes | KEEP (normalize name) |
| `parent_key` | str | — | Scientific | Yes | Yes | KEEP (normalize name) |

### `data/breed_analysis/5_scientific_nutrition/INGREDIENT_EVIDENCE.csv`

Rows: **10** · Columns: **9**

| Column | Type | Example | Ownership | Nullable | Intern edit? | Disposition |
|--------|------|---------|-----------|----------|--------------|-------------|
| `ingredient_name` | str | Glucosamine | Scientific | Often | Yes | KEEP (normalize name) |
| `source_name` | str | Frontiers in Veterinary Science | Reference | Often | Yes | KEEP (normalize name) |
| `source_quote` | str | Glucosamine-based nutraceuticals showed variable analge | Reference | Often | Yes | KEEP (normalize name) |
| `source_url` | str | https://pmc.ncbi.nlm.nih.gov/articles/PMC9499673/ | Reference | Often | Yes | KEEP (normalize name) |
| `year` | str | 2022 | Reference | Often | Yes | KEEP (normalize name) |
| `supports_joint` | bool|flag | true | Scientific | Often | Yes | KEEP (normalize name) |
| `supports_skin` | bool|flag | false | Scientific | Often | Yes | KEEP (normalize name) |
| `supports_gut` | bool|flag | false | Scientific | Often | Yes | KEEP (normalize name) |
| `anti_inflammatory` | str | false | Scientific | Often | Yes | KEEP (normalize name) |

### `data/breed_analysis/5_scientific_nutrition/INGREDIENT_MECHANISMS.csv`

Rows: **8** · Columns: **7**

| Column | Type | Example | Ownership | Nullable | Intern edit? | Disposition |
|--------|------|---------|-----------|----------|--------------|-------------|
| `nutrient_name` | str | Omega-3 | Scientific | Often | Yes | KEEP (normalize name) |
| `ingredient_name` | str | EPA+DHA | Scientific | Often | Yes | KEEP (normalize name) |
| `source_product_id` | str | FF002_BEEF | Product | Often | Yes | KEEP (normalize name) |
| `amount_per_serving` | number|str | 0.2 | Product | Often | Yes | KEEP (normalize name) |
| `unit` | str | % | Scientific | Often | Yes | KEEP (normalize name) |
| `mechanism_summary` | str | Declared label guaranteed analysis for combo fresh food | Scientific | Often | Yes | KEEP (normalize name) |
| `evidence_level` | str | — | Reference | Yes | Yes | KEEP (normalize name) |

### `data/breed_analysis/5_scientific_nutrition/INGREDIENT_NUTRIENT_ESTIMATES.csv`

Rows: **8** · Columns: **12**

| Column | Type | Example | Ownership | Nullable | Intern edit? | Disposition |
|--------|------|---------|-----------|----------|--------------|-------------|
| `ingredient` | str | Chicken Heart | Scientific | Often | Yes | KEEP (normalize name) |
| `canonical_ingredient` | str | Chicken Heart | Scientific | Often | Yes | KEEP (normalize name) |
| `nutrient` | str | Taurine | Review | Often | Review | KEEP (normalize name) |
| `amount_per_100g` | number|str | 160 | Scientific | Often | Yes | KEEP (normalize name) |
| `unit` | str | mg | Scientific | Often | Yes | KEEP (normalize name) |
| `confidence` | str | 0.70 | Algorithm | Often | Careful | REVIEW (algo/display) |
| `source` | str | literature_estimate | Reference | Often | Yes | KEEP (normalize name) |
| `is_estimated` | bool|flag | true | Scientific | Often | Yes | KEEP (normalize name) |
| `category` | str | organ_meat | Product | Often | Yes | KEEP (normalize name) |
| `parent` | str | Animal Protein | Scientific | Often | Yes | KEEP (normalize name) |
| `property_tags` | str | high_taurine | Scientific | Often | Yes | KEEP (normalize name) |
| `notes` | str | Estimated typical values; verify against primary litera | Product | Yes | Yes | KEEP (normalize name) |

### `data/breed_analysis/5_scientific_nutrition/NATURAL_FOOD_SOURCES.csv`

Rows: **15** · Columns: **5**

| Column | Type | Example | Ownership | Nullable | Intern edit? | Disposition |
|--------|------|---------|-----------|----------|--------------|-------------|
| `ingredient_name` | str | Glucosamine | Scientific | Often | Yes | KEEP (normalize name) |
| `food_source` | str | Green-Lipped Mussel (Dehydrated) | Scientific | Often | Yes | KEEP (normalize name) |
| `amount_per_100g` | number|str | 1500 | Scientific | Often | Yes | KEEP (normalize name) |
| `unit` | str | mg | Scientific | Often | Yes | KEEP (normalize name) |
| `bioavailability_notes` | str | Highly bioavailable lipid-matrix joint support | Scientific | Often | Yes | KEEP (normalize name) |

### `data/breed_analysis/5_scientific_nutrition/NUTRIENT_PRIORITIES.csv`

Rows: **5** · Columns: **9**

| Column | Type | Example | Ownership | Nullable | Intern edit? | Disposition |
|--------|------|---------|-----------|----------|--------------|-------------|
| `condition` | str | Hip Dysplasia | Clinical | Often | Yes | KEEP (normalize name) |
| `nutrient_name` | str | Glucosamine | Scientific | Often | Yes | KEEP (normalize name) |
| `target_dose` | number|str | 520 | Scientific | Often | Yes | KEEP (normalize name) |
| `target_unit` | str | mg | Scientific | Often | Yes | KEEP (normalize name) |
| `priority_rank` | number|str | 1 | Algorithm | Often | Careful | REVIEW (algo/display) |
| `evidence_level` | str | high | Reference | Often | Yes | KEEP (normalize name) |
| `source_name` | str | Canine Rehabilitation Outcomes Review | Reference | Often | Yes | KEEP (normalize name) |
| `source_quote` | str | Glucosamine supports chondrocyte metabolism in loaded j | Reference | Often | Yes | KEEP (normalize name) |
| `source_url` | str | https://pubmed.ncbi.nlm.nih.gov/30123641 | Reference | Often | Yes | KEEP (normalize name) |

### `data/preventative_ingredients/CONDITION_INGREDIENTS.csv`

Rows: **12** · Columns: **8**

| Column | Type | Example | Ownership | Nullable | Intern edit? | Disposition |
|--------|------|---------|-----------|----------|--------------|-------------|
| `condition` | str | Hip Dysplasia | Clinical | Often | Yes | KEEP (normalize name) |
| `ingredient_name` | str | Glucosamine | Scientific | Often | Yes | KEEP (normalize name) |
| `recommended_daily_dose` | number|str | 500 | Scientific | Often | Yes | KEEP (normalize name) |
| `dose_unit` | number|str | mg | Scientific | Often | Yes | KEEP (normalize name) |
| `source_name` | str | Frontiers in Veterinary Science | Reference | Often | Yes | KEEP (normalize name) |
| `source_quote` | str | Glucosamine-based nutraceuticals showed variable effica | Reference | Often | Yes | KEEP (normalize name) |
| `source_url` | str | https://pmc.ncbi.nlm.nih.gov/articles/PMC9499673/ | Reference | Often | Yes | KEEP (normalize name) |
| `priority_rank` | number|str | 1 | Algorithm | Often | Careful | REVIEW (algo/display) |

### `data/preventative_ingredients/CONDITION_PROTOCOLS.csv`

Rows: **12** · Columns: **10**

| Column | Type | Example | Ownership | Nullable | Intern edit? | Disposition |
|--------|------|---------|-----------|----------|--------------|-------------|
| `condition` | str | Hip Dysplasia | Clinical | Often | Yes | KEEP (normalize name) |
| `ingredient_name` | str | Glucosamine | Scientific | Often | Yes | KEEP (normalize name) |
| `recommended_daily_dose` | number|str | 500 | Scientific | Often | Yes | KEEP (normalize name) |
| `dose_unit` | number|str | mg | Scientific | Often | Yes | KEEP (normalize name) |
| `priority_rank` | number|str | 1 | Algorithm | Often | Careful | REVIEW (algo/display) |
| `source_name` | str | Canine Joint Nutrition Trial | Reference | Often | Yes | KEEP (normalize name) |
| `source_quote` | str | Glucosamine at guideline doses improved mobility index  | Reference | Often | Yes | KEEP (normalize name) |
| `source_url` | str | https://pubmed.ncbi.nlm.nih.gov/30123601 | Reference | Often | Yes | KEEP (normalize name) |
| `year` | str | — | Reference | Yes | Yes | KEEP (normalize name) |
| `evidence_type` | str | condition_specific | Reference | Often | Yes | KEEP (normalize name) |

### `data/preventative_ingredients/INGREDIENT_EVIDENCE.csv`

Rows: **10** · Columns: **5**

| Column | Type | Example | Ownership | Nullable | Intern edit? | Disposition |
|--------|------|---------|-----------|----------|--------------|-------------|
| `ingredient_name` | str | Glucosamine | Scientific | Often | Yes | KEEP (normalize name) |
| `source_name` | str | Frontiers in Veterinary Science | Reference | Often | Yes | KEEP (normalize name) |
| `source_quote` | str | Glucosamine-based nutraceuticals showed variable analge | Reference | Often | Yes | KEEP (normalize name) |
| `source_url` | str | https://pmc.ncbi.nlm.nih.gov/articles/PMC9499673/ | Reference | Often | Yes | KEEP (normalize name) |
| `year` | str | 2022 | Reference | Often | Yes | KEEP (normalize name) |

### `data/product_portfolio/EXT_SUPPLEMENTS.csv`

Rows: **0** · Columns: **6**

| Column | Type | Example | Ownership | Nullable | Intern edit? | Disposition |
|--------|------|---------|-----------|----------|--------------|-------------|
| `product_id` | str | — | Product | Yes | Yes | KEEP (normalize name) |
| `supplement_type` | str | — | Review | Yes | Review | KEEP (normalize name) |
| `serving_size_g` | str | — | Review | Yes | Review | KEEP (normalize name) |
| `servings_per_pack` | str | — | Review | Yes | Review | KEEP (normalize name) |
| `storage_method` | str | — | Review | Yes | Review | KEEP (normalize name) |
| `shelf_life_days` | number|str | — | Review | Yes | Review | KEEP (normalize name) |

### `data/product_portfolio/EXT_TREATS_BAKERY.csv`

Rows: **12** · Columns: **9**

| Column | Type | Example | Ownership | Nullable | Intern edit? | Disposition |
|--------|------|---------|-----------|----------|--------------|-------------|
| `product_id` | str | TR001 | Product | Often | Yes | KEEP (normalize name) |
| `treat_type` | str | biscuit | Review | Often | Review | KEEP (normalize name) |
| `bakery_type` | str | homestyle_bakery | Review | Often | Review | KEEP (normalize name) |
| `protein_source` | str | goat_milk | Review | Often | Review | KEEP (normalize name) |
| `texture` | str | baked | Review | Often | Review | KEEP (normalize name) |
| `weight_g` | number|str | 60 | Review | Yes | Review | KEEP (normalize name) |
| `feeding_recommendation` | str | — | Review | Yes | Review | KEEP (normalize name) |
| `storage_method` | str | cool_dry | Review | Often | Review | KEEP (normalize name) |
| `shelf_life_days` | number|str | 30 | Review | Often | Review | KEEP (normalize name) |

### `data/product_portfolio/PACKAGE_TIERS.csv`

Rows: **3** · Columns: **5**

| Column | Type | Example | Ownership | Nullable | Intern edit? | Disposition |
|--------|------|---------|-----------|----------|--------------|-------------|
| `tier_id` | str | essential | Product | Often | Yes | KEEP (normalize name) |
| `title` | str | Essential Care | Display | Often | Review | KEEP (normalize name) |
| `yearly_discount_factor` | number|str | 0.95 | Algorithm | Often | Careful | REVIEW (algo/display) |
| `staple_product_id` | str | SF001 | Product | Often | Yes | KEEP (normalize name) |
| `sort_order` | number|str | 1 | Display | Often | Careful | REVIEW (algo/display) |

### `data/product_portfolio/PRODUCT_CATALOG.csv`

Rows: **16** · Columns: **16**

| Column | Type | Example | Ownership | Nullable | Intern edit? | Disposition |
|--------|------|---------|-----------|----------|--------------|-------------|
| `product_id` | str | SF001 | Product | Often | Yes | KEEP (normalize name) |
| `brand` | str | Farmina | Product | Often | Yes | KEEP (normalize name) |
| `category` | str | STAPLE_FOOD | Product | Often | Yes | KEEP (normalize name) |
| `subcategory` | str | tropical_selection | Product | Often | Yes | KEEP (normalize name) |
| `product_name` | str | Farmina Small Breed Adult Dog Food (Chicken Flavor) | Product | Often | Yes | KEEP (normalize name) |
| `status` | str | active | Product | Often | Yes | KEEP (normalize name) |
| `image_url` | str | — | Product | Yes | Yes | KEEP (normalize name) |
| `purchase_url` | str | — | Product | Yes | Yes | KEEP (normalize name) |
| `description` | str | — | Display | Yes | Review | KEEP (normalize name) |
| `short_description` | str | Farmina N&D Tropical Selection Chicken | Display | Often | Review | KEEP (normalize name) |
| `featured` | bool|flag | all_life_stages | Display | Often | Careful | REVIEW (algo/display) |
| `tags` | str | chicken_tropical_fruit | Display | Often | Review | KEEP (normalize name) |
| `display_order` | number|str | 10 | Display | Often | Careful | REVIEW (algo/display) |
| `inventory_status` | str | in_stock | Product | Often | Yes | KEEP (normalize name) |
| `rating` | str | — | Product | Yes | Yes | KEEP (normalize name) |
| `review_count` | number|str | — | Product | Yes | Yes | KEEP (normalize name) |

### `data/product_portfolio/PRODUCT_COMPONENTS.csv`

Rows: **59** · Columns: **7**

| Column | Type | Example | Ownership | Nullable | Intern edit? | Disposition |
|--------|------|---------|-----------|----------|--------------|-------------|
| `product_id` | str | SF001 | Product | Often | Yes | KEEP (normalize name) |
| `component_type` | str | macro_nutrient | Product | Often | Yes | KEEP (normalize name) |
| `component_name` | str | Crude Protein | Product | Often | Yes | KEEP (normalize name) |
| `value` | number|str | 30 | Product | Yes | Yes | KEEP (normalize name) |
| `unit` | str | % | Scientific | Yes | Yes | KEEP (normalize name) |
| `evidence_level` | str | DeclaredLabel | Reference | Often | Yes | KEEP (normalize name) |
| `notes` | str | Min value from Farmina guaranteed analysis | Product | Often | Yes | KEEP (normalize name) |

### `data/product_portfolio/PRODUCT_DEFAULTS.csv`

Rows: **5** · Columns: **2**

| Column | Type | Example | Ownership | Nullable | Intern edit? | Disposition |
|--------|------|---------|-----------|----------|--------------|-------------|
| `key` | str | default_treat | Algorithm | Often | No | MOVE→Python / DELETE |
| `product_id` | str | TR001 | Product | Often | Yes | KEEP (normalize name) |

### `data/product_portfolio/PRODUCT_FEEDING_RULES.csv`

Rows: **23** · Columns: **5**

| Column | Type | Example | Ownership | Nullable | Intern edit? | Disposition |
|--------|------|---------|-----------|----------|--------------|-------------|
| `product_id` | str | SF001 | Product | Often | Yes | KEEP (normalize name) |
| `min_weight_kg` | number|str | 1.5 | Product | Often | Yes | KEEP (normalize name) |
| `max_weight_kg` | number|str | 2.0 | Product | Often | Yes | KEEP (normalize name) |
| `daily_amount` | number|str | 30 | Product | Often | Yes | KEEP (normalize name) |
| `daily_unit` | str | g | Product | Often | Yes | KEEP (normalize name) |

### `data/product_portfolio/PRODUCT_FUNCTIONS.csv`

Rows: **10** · Columns: **3**

| Column | Type | Example | Ownership | Nullable | Intern edit? | Disposition |
|--------|------|---------|-----------|----------|--------------|-------------|
| `product_id` | str | SF001 | Product | Often | Yes | KEEP (normalize name) |
| `function` | str | Activity Support | Product | Often | Yes | KEEP (normalize name) |
| `confidence` | str | High | Algorithm | Often | Careful | REVIEW (algo/display) |

### `data/product_portfolio/PRODUCT_PRICING.csv`

Rows: **16** · Columns: **4**

| Column | Type | Example | Ownership | Nullable | Intern edit? | Disposition |
|--------|------|---------|-----------|----------|--------------|-------------|
| `product_id` | str | SF001 | Product | Often | Yes | KEEP (normalize name) |
| `list_price_rmb` | number|str | 149 | Product | Often | Yes | KEEP (normalize name) |
| `package_units` | str | 1.5 | Product | Often | Yes | KEEP (normalize name) |
| `unit_label` | str | kg | Product | Often | Yes | KEEP (normalize name) |

### `data/product_portfolio/STAPLE_FOOD.csv`

Rows: **4** · Columns: **17**

| Column | Type | Example | Ownership | Nullable | Intern edit? | Disposition |
|--------|------|---------|-----------|----------|--------------|-------------|
| `product_id` | str | SF001 | Product | Often | Yes | KEEP (normalize name) |
| `food_type` | str | kibble | Review | Often | Review | KEEP (normalize name) |
| `life_stage` | str | all_life_stages | Review | Often | Review | KEEP (normalize name) |
| `size_support` | str | small_breed | Review | Often | Review | KEEP (normalize name) |
| `protein_source` | str | chicken | Review | Often | Review | KEEP (normalize name) |
| `package_weight_g` | number|str | 1500 | Review | Often | Review | KEEP (normalize name) |
| `daily_feeding_chart` | str | See PRODUCT_FEEDING_RULES by weight bracket | Review | Often | Review | KEEP (normalize name) |
| `energy_kcal_per_kg` | str | 4062 | Review | Yes | Review | KEEP (normalize name) |
| `protein_pct` | number|str | 30 | Product | Yes | Yes | KEEP (normalize name) |
| `fat_pct` | number|str | 20 | Product | Yes | Yes | KEEP (normalize name) |
| `fiber_pct` | number|str | 2.7 | Product | Yes | Yes | KEEP (normalize name) |
| `ash_pct` | number|str | 8.0 | Product | Yes | Yes | KEEP (normalize name) |
| `calcium_pct` | number|str | 1.0 | Product | Yes | Yes | KEEP (normalize name) |
| `phosphorus_pct` | number|str | 0.8 | Product | Often | Yes | KEEP (normalize name) |
| `ingredient_list` | str | Farmina N&D Tropical Selection Chicken — declared label | Review | Often | Review | KEEP (normalize name) |
| `storage_method` | str | cool_dry | Review | Often | Review | KEEP (normalize name) |
| `shelf_life_days` | number|str | 540 | Review | Yes | Review | KEEP (normalize name) |

### `data/product_portfolio/TREATS.csv`

Rows: **12** · Columns: **8**

| Column | Type | Example | Ownership | Nullable | Intern edit? | Disposition |
|--------|------|---------|-----------|----------|--------------|-------------|
| `product_id` | str | TR001 | Product | Often | Yes | KEEP (normalize name) |
| `treat_type` | str | biscuit | Review | Often | Review | KEEP (normalize name) |
| `protein_source` | str | goat_milk | Review | Often | Review | KEEP (normalize name) |
| `texture` | str | baked | Review | Often | Review | KEEP (normalize name) |
| `weight_g` | number|str | 60 | Review | Yes | Review | KEEP (normalize name) |
| `feeding_recommendation` | str | — | Review | Yes | Review | KEEP (normalize name) |
| `storage_method` | str | cool_dry | Review | Often | Review | KEEP (normalize name) |
| `shelf_life_days` | number|str | 30 | Review | Often | Review | KEEP (normalize name) |


---

## Ownership summary

| Ownership | Action |
|-----------|--------|
| Scientific / Clinical / Product / Reference | Remain in CSV (normalize) |
| Parser / Metadata (source_csv, aliases) | Move to Python or delete |
| Display (card_title, label, templates) | Layer B / Python |
| Algorithm (confidence on functions, many ranks) | Python unless literature-ordered |
| Derived (	rait duplicate, related_conditions lists) | Prefer joins |

## Related

- [DATA_CONSUMERS.md](DATA_CONSUMERS.md)
- [DATA_DUPLICATION_REPORT.md](DATA_DUPLICATION_REPORT.md)
- [DATA_MIGRATION_V2.md](DATA_MIGRATION_V2.md)
