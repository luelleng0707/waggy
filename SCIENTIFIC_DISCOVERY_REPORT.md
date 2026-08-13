# Phase Omega-0: Scientific discovery report

## Scope and method

This is a reconstruction of the veterinary knowledge model represented by the repository, not an endorsement of its scientific validity.  All repository-owned source material was treated as evidence: warehouse CSVs and manifests; runtime formulas and inference constants; the ontology; authoring and curation artifacts; API/report contracts; tests and frozen outputs.  `node_modules`, editor caches, and generated dependency files are implementation dependencies rather than project knowledge.

## Executive finding: what this system is trying to represent

PPIE is a **canine preventative-wellness decision system with a product-matching layer**.  Its central claim is that a dog's breed(s) and their phenotypic traits can identify elevated condition priorities.  Those priorities can be adjusted by trait combinations and owner/groomer observations, mapped to nutritional and lifestyle support, then used to rank an in-house food/supplement/treat catalogue and commercial care packages.

It is not a diagnostic system in the strict clinical sense.  It contains condition labels, surveillance schedules, and intervention claims, but does not represent diagnosis, differential diagnosis, contraindications, medication, laboratory/physical-exam findings, disease severity, or veterinary oversight.

## A. Model A — veterinary knowledge

### Domain model and entity inventory

| Concept | Scientific meaning and purpose | State | Principal evidence locations |
|---|---|---|---|
| Dog profile | Individual animal context: identity, breed composition, age, mass, sex, body condition, activity, environment, observed signs. | Input; only selected fields influence inference. | `app/agent/state.py`, `app/api/payload_adapter.py` |
| Breed | A named population with morphology, climate adaptation, energy and functional lineage; source of population-condition prevalence. 48 records. | Stored entity; inferred/resolved from user label. | `breed/breeds.csv`, `breed/breed_conditions.csv` |
| Mixed-breed composition | Two named breeds, an optional split percentage, and cross-specific condition multipliers. | Input and inferred relationship. | profile model; `mixed_breed_matrix.csv` |
| Trait / phenotype | Size, body type, coat, energy, weakness group, skull type, climate, lifespan, and function group. Traits bridge breed identity to condition risk. | Stored via breed columns and 44 trait records; inferred from breed. | `breeds.csv`, `traits.csv`, `trait_conditions.csv`, `trait_science.csv` |
| Condition | A named health priority. The registry has 34 labels spanning orthopedic, dermatologic, respiratory, eye, dental, GI, cardiac, neurologic, metabolic, infectious/exposure and other concerns. | Stored entity; inferred as a priority or supplied as observed condition. | `conditions.csv`, breed/trait condition relations |
| Condition mechanism/facet | Anatomy, body system, class and facets such as inflammation, pain, barrier, cognition and heat. | Stored only for six conditions; not a complete condition model. | `ontology/condition_graph/conditions.json`, anatomy/physiology indices |
| Epidemiological association | Population prevalence for a breed or trait-condition association, plus evidence metadata. | Stored relationship; aggregated into risk. | `breed_conditions.csv` (16), `trait_conditions.csv` (90) |
| Trait interaction / resilience | A paired phenotype can increase/decrease/neutralize expression of a condition. | Stored relationship; applied as bounded multiplier or benefit reduction. | `mixed_breed_interactions.csv` (10), `trait_benefits.csv` (10) |
| Environment compatibility | Trait/environment compatibility and management note; currently limited to Shanghai Summer/humidity/urban context. | Stored relationship; presented, not materially used in risk. | `breed_environment.csv` (6) |
| Activity prescription | Condition-specific low-impact/management activity, plus generic phenotype/life-stage exercise schedules. | Stored relationship/evidence; condition activities are consumed for top priorities. | `breed_activity.csv` (10), `activity_science.csv` (14) |
| Life stage and clinical timeline | Puppy/adult/senior risk surveillance and prevention. | Stored lookup/relationship; largely presentation/research material. | `life_stages.csv`, `clinical_timelines.csv` |
| Ingredient/nutrient | Nine canonical intervention ingredients, with aliases, evidence statements, mechanisms, doses and food sources. | Stored entity/relationship; inferred as intervention target. | ingredient and nutrition CSVs |
| Nutrition protocol | A condition-to-ingredient daily dose, ranked by priority. | Stored relationship; becomes a daily target. | `condition_ingredients.csv` |
| Food source/nutrient content | Natural food alternatives and estimated nutrient amounts. | Stored relationship; used in richer report/details, not core risk. | `foods.csv`, `food_sources.csv`, `food_nutrients.csv` |
| Evidence item/paper | Citation-like metadata and evidence level attached to relationships. | Stored evidence; retrieved for explanatory output. | `papers.csv` (106), `clinical_evidence.csv` (7), relation CSV source fields |
| Grooming observation | Observable coat/skin/eye/oral cues with normal/monitor/attention criteria. | Stored reference; definitions are loaded rather than profile-tailored. | `grooming_observations.csv` |
| Product | A commercial offering with composition, clinical functions, dose-by-weight rule, price, status and merchandising metadata. | Stored business entity; matched/ranked. | `PRODUCT_*.csv`, `TREAT_BAKERY.csv` |
| Care package/tier | Essential/Balanced/Optimal-style product bundles and commercial discount/default rules. | Stored tier metadata plus code-owned policy. | `package_tiers.csv`, `product_defaults.csv`, package optimizer |
| Wellness goal | Plain-language grouping: joint, skin, dental, digestive, weight, immune, respiratory, eye, cardiac, activity, or general wellness. | Inferred/display label; hard-coded mapping. | `app/agent/wellness_map.py` |

### Relationship graph

```mermaid
flowchart LR
  Dog[Dog profile] -->|has| Breed[Breed(s)]
  Breed -->|has phenotype| Trait[Trait]
  Breed -->|predisposed to; prevalence| Condition[Condition]
  Trait -->|associated with; prevalence| Condition
  Trait -->|modifies expression| Condition
  Trait -->|compatible with| Environment[Environment]
  Condition -->|supports surveillance/prevention| Timeline[Clinical timeline]
  Condition -->|is managed with| Activity[Activity protocol]
  Condition -->|maps to target dose| Ingredient[Ingredient/nutrient]
  Ingredient -->|has evidence/mechanism| Evidence[Evidence/paper]
  Ingredient -->|occurs in| Food[Food source]
  Product -->|contains| Ingredient
  Product -->|has function, price, feeding rule| Package[Care package]
  Package -->|recommended to| Dog
```

| Source → relation → target | Scientific rationale represented | Current implementation |
|---|---|---|
| Breed → predisposed_to → Condition | Breed registry prevalence captures population-level association. | Adds breed-condition prevalence; two-breed union is summed then capped at 1.0. |
| Trait → associated_with → Condition | Conformation/phenotype is used as an additional proxy for condition susceptibility. | Trait-condition prevalences are summed by condition. |
| Trait pair → increases/decreases → Condition | Combinations represent compounded morphology/lifestyle stress or protective phenotype. | Multiplied and clamped to 0.80–1.20; a second benefit table applies reductions. |
| Breed pair → modifies → Condition | A specific cross may have a different condition burden than either parent. | Matrix records are returned as adjustments; risk path also has a mixed-breed nudge. |
| Trait × environment → management advice | Heat, humidity, coat, body mass and activity can affect husbandry. | Compatibility records are attached to biology/report; not an epidemiological modifier. |
| Condition → activity protocol | Low-impact exercise/grooming/activity is framed as preventative or supportive care. | Top ten condition priorities are joined to `breed_activity.csv`. |
| Condition → ingredient/dose → nutrient target | A condition receives one or more suggested nutraceutical targets. | First (highest priority) dose is retained per ingredient in the nutrition stage; ingredient engine instead uses maximum dose across conditions. |
| Ingredient → evidence/mechanism → paper | Nutraceutical claims ought to be traceable to literature. | Source quote/URL is carried to output; links are not normalized to `papers.csv`. |
| Ingredient → food source | Whole-food alternative may provide the nutrient. | Used for report/detail alternatives. |
| Product → contains → ingredient | Product composition is assessed against intervention target. | Active component names are normalized/aliased and compared with required dose. |
| Product → function → wellness goal | Product label/function text is used as clinical-function score. | Token/string scoring in package optimizer. |
| Product → feeding rule/price → package | Individual serving and commercial cost determine selection. | Weight bracket, monthly/yearly cost, coverage and score drive packages. |

### Coherent knowledge inventory

The retained veterinary propositions cluster into six bodies of knowledge:

1. **Predisposition and morphology.**  Large/giant, deep-chested, chondrodysplastic, brachycephalic, athletic/high-energy, coat and companion-lineage traits are used to prioritize hip dysplasia, IVDD, BOAS/heat stress, GDV, cruciate injury, obesity, dental disease, dermatitis and other listed conditions.  This is represented redundantly as breed-specific prevalence, trait-specific prevalence, interaction multipliers and benefit reductions.
2. **Preventative condition management.**  The model contains condition-linked activity prescriptions (hydrotherapy, controlled incline walks, core work, cool-hour walks, barrier bathing, dental chews, interval/post-meal walks, visual enrichment, low-impact cardiac conditioning), clinical timelines, grooming checks, and life-stage exercise prescriptions.
3. **Condition-directed nutraceutical support.**  Hip dysplasia → glucosamine/omega-3; IVDD → MSM/glucosamine; BOAS → omega-3; atopic dermatitis → omega-3/zinc; dental disease → seaweed blend; degenerative valve disease → taurine; chronic enteropathy → probiotics; obesity → L-carnitine; cataracts → lutein. These claims are explicitly support/prevention-oriented, but results are rendered with a level of specificity closer to a prescription.
4. **Nutrition and food composition.**  Natural sources and estimated food nutrient values are available for selected intervention nutrients. A separate `nutrient_priorities` set gives partially conflicting targets (e.g., hip glucosamine 520 mg vs 500 mg in condition ingredients).
5. **Evidence provenance.**  Most clinical propositions carry source name, quote, URL, year and/or evidence level. `papers.csv` exists as a bibliographic registry, while clinical/evidence rows embed sources independently.
6. **Commercial fulfillment.**  The product portfolio contains food, supplements and treats, their active components and label-defined functions. It is business knowledge, not veterinary knowledge, but it determines which scientific-looking interventions are surfaced.

## B. CSV inventory

Legend: **E** entity, **R** relationship, **V** evidence, **L** lookup/configuration, **B** business/product, **G** generated/historical. “Consumed” denotes a runtime/research consumer, not scientific validity.

| CSV | Type and represented concept | Canonicality / duplication / consumer | If absent |
|---|---|---|---|
| `breed/breeds.csv` (48) | E: breed phenotype. | Canonical live input to biology/risk. | Breed resolution and trait inference fail. |
| `breed/breed_conditions.csv` (16) | R+V: breed prevalence. | Canonical live. | Removes direct breed epidemiology. |
| `breed/trait_conditions.csv` (90) | R+V: phenotype prevalence. | Canonical live; projected into nine legacy-named in-memory tables. | Removes central risk signal. |
| `breed/mixed_breed_matrix.csv` (5) | R+V: named-cross multiplier. | Live/inferred; overlaps interaction model. | Removes explicit cross adjustments. |
| `breed/mixed_breed_interactions.csv` (10) | R+V: trait-pair effects. | Canonical live despite name; semantically duplicates `trait_benefits`. | Removes interaction effects. |
| `breed/breed_environment.csv` (6) | R+V: trait/environment compatibility. | Live biology/report enrichment; sparse context. | Environment advice disappears. |
| `breed/activities.csv` (1) | E/lookup: activity vocabulary. | No clear runtime consumer. | Likely no live impact. |
| `breed/breed_activity.csv` (10) | R+V: condition activity intervention. | Live ActivityNode. | Lifestyle requirements disappear. |
| `breed/activity_science.csv` (14) | V/R: 10 evidence items + 4 prescription rows. | Loader/research/activity recommendations; mixes two types. | Activity evidence/prescriptions weaken. |
| `condition/conditions.csv` (34) | E: condition register. | Canonical vocabulary but body-system field is empty. | Identifier/reference validation loses registry. |
| `condition/condition_protocols.csv` (12) | R+V: condition-to-ingredient protocol. | Duplicates `condition_ingredients` with different citations; not core target mapping. | Protocol/research view loses one duplicate. |
| `condition/clinical_timelines.csv` (6) | R+V: stage/trait surveillance and prevention. | Limited/mostly report research use; includes `Arthritis`, absent from condition registry. | Timeline content lost. |
| `condition/grooming_observations.csv` (10) | E/R: observable care signs/criteria. | Grooming node loads every row, not selectively. | Grooming checklist definitions disappear. |
| `ingredient/ingredients.csv` (9) | E: ingredient vocabulary. | Reference. | Ingredient ID vocabulary lost. |
| `ingredient/condition_ingredients.csv` (24) | R+V: 12 links duplicated as `sci` and `prev` lanes. | Core live target mapping; loader collapses lanes to 12 condition+ingredient links. | Core supplementation recommendations fail. |
| `ingredient/ingredient_aliases.csv` (6) | L/R: aliases/taxonomy. | Live product/ingredient matching. | Some component-target matches fail. |
| `ingredient/ingredient_evidence.csv` (20) | V: 10 evidence records duplicated by lane. | Used in explanation; `prev` loses support flags. | Ingredient evidence disappears. |
| `ingredient/ingredient_mechanisms.csv` (8) | B/V: product-declared payloads labeled mechanisms. | Live details; not a general mechanism table. | Product ingredient detail degrades. |
| `nutrition/life_stages.csv` (3) | L: stages. | Reference; age stages are also hard-coded/runtime-derived. | Little direct impact. |
| `nutrition/nutrient_priorities.csv` (5) | R+V: alternative condition nutrient targets. | Used in report assembly, not core nutrition target stage. Conflicts with condition ingredients. | Preventative/report priority view changes. |
| `nutrition/food_sources.csv` (15) | R: ingredient food sources. | Live report alternatives. | Natural-food alternatives disappear. |
| `nutrition/foods.csv` (15) | E/R: same food-source facts with food IDs. | Duplicates `food_sources` almost exactly. | Likely no core impact if food sources remains. |
| `nutrition/food_nutrients.csv` (8) | R/V: nutrient composition estimates. | Used for food/detail enrichment. | Quantified natural-food support disappears. |
| `physiology/traits.csv` (44) | E: trait vocabulary. | Reference/graph support; breeds also embed values. | Trait identity registry lost. |
| `physiology/trait_science.csv` (22) | V/R: trait purpose/explanation and some condition deltas. | Biology/report enrichment; multiplexed records. | Trait narrative/evidence weakens. |
| `physiology/trait_benefits.csv` (10) | R+V: protective trait pairs. | Live benefit reduction; overlaps trait interactions. | Protective modifiers disappear. |
| `evidence/papers.csv` (106) | V: bibliographic registry. | Used for provenance/authoring; most relationship citations do not FK to it. | Paper lookup/audit weakens, core inference remains. |
| `evidence/clinical_evidence.csv` (7) | V/R: condition intervention/activity evidence. | Evidence node/report. Includes a placeholder general-wellness record. | Clinical evidence display weakens. |
| `product/PRODUCT_CATALOG.csv` (16) | B/E: active/inactive catalogue. | Core product matching/store. | Commercial outputs fail. |
| `product/PRODUCT_COMPONENTS.csv` (59) | B/R: product composition. | Core coverage/product details. | Ingredient-to-product matching fails. |
| `product/PRODUCT_FUNCTIONS.csv` (10) | B/R: product functions/confidence. | Package clinical-function scoring. | Function score/product rationale weakens. |
| `product/PRODUCT_FEEDING_RULES.csv` (23) | B/R: mass-to-serving brackets. | Core feeding/cost. | Feeding calculations fail/default. |
| `product/PRODUCT_PRICING.csv` (16) | B/R: price/package quantity. | Core package cost/ranking. | Cost score/price outputs fail. |
| `product/TREAT_BAKERY.csv` (12) | B metadata: treat specification/storage. | Store/detail enrichment. | Treat detail disappears. |
| `product/package_tiers.csv` (3) | B/L: tier title, discount, staple. | Package outputs. | Tier naming/default selection changes. |
| `product/product_defaults.csv` (5) | B/L: default product keys. | Repository policy/defaults. | Default selections fail. |
| `runtime/aliases.csv` (4) | L: breed aliases. | Live normalization. | Alias inputs may not resolve. |
| `runtime/parameters.csv` (18) | L: weights/clamps. | Loaded into execution context, while central config retains the same hard-coded values. | Current formulas often keep defaults; reveals duplication. |
| `runtime/units.csv` (14) | L: unit conversion. | Unit normalizer/product matching. | Unit compatibility/conversion weakens. |

No runtime writer creates the scientific CSVs. Authoring writes draft/published JSON and staging material, release tools snapshot/promote warehouse content, and tests emit golden/parity JSON. Thus CSVs are authored/imported reference data rather than user-generated clinical records.

## C. Algorithm inventory

| Algorithm/group | Classification | True purpose and knowledge status |
|---|---|---|
| Profile validation, alias and unit normalization | Validation / transformation | Makes inbound dog data joinable. It does not add veterinary inference. |
| Breed resolution and trait expansion | Graph traversal / projection | Converts a breed label into its stored phenotype vector. |
| Breed-risk union | Mathematical calculation / aggregation | Adds prevalence across one/two breed records and caps at 100%; this assumes additive compatibility of cited prevalences. |
| Trait-risk aggregation | Scientific reasoning + calculation | Sums condition prevalences across trait categories; is a model assumption embedded in code. |
| Interaction and benefit application | Scientific reasoning + calculation | Applies trait-pair factors and benefit reductions with hard bounds. Encodes veterinary meaning as algorithm/data hybrid. |
| Observed-condition/groomer boost | Scientific reasoning heuristic | Maps free text such as limping/itching to conditions; code-owned heuristic, not literature-backed evidence rows. |
| Significance/confidence | Ranking | Converts trait evidence coverage and risk into rank/confidence. Mostly epistemic/computational, not a clinical probability calibration. |
| Condition-to-ingredient mapping | Graph traversal / filtering | Joins ranked conditions to dose links, de-duplicates by ingredient. |
| Dose calculation | Mathematical calculation | Uses a fixed dose or weight-based `mg_per_kg × mass`; conflicts with CSV records that are mostly fixed daily dose. |
| Product matching | Filtering / join | Normalizes alias/component names, checks units, calculates component dose coverage. |
| Feeding/cost | Calculation | Selects an applicable weight bracket, derives monthly/yearly consumption and price. |
| Package optimizer | Ranking / constrained optimization | Produces tiers using coverage, token-based function relevance, evidence flags, cost efficiency and diversity. It is commercial/business logic built on a clinical-looking score. |
| Clinical report/assessment assemblers | Projection / formatting / serialization | Re-express the same result into modular assessment, report, legacy JSON and UI formats. |
| Evidence ranking/duplicate/conflict curation | Validation / metadata analysis | Helps authoring audit evidence; does not alter live clinical inference. |

Algorithms that should be recognized as **model assumptions rather than facts**: additive prevalence union; trait category weights; 0.80–1.20 interaction cap; mixed-breed nudge; free-text groomer mapping; hard-coded wellness-goal taxonomy; package score weights (0.35 coverage, 0.25 function, 0.20 evidence, 0.15 cost, 0.05 diversity); 55% essential coverage floor.

## D. Inputs and outputs

### Input inventory

| Input | Direct effect |
|---|---|
| Name | Presentation/identity only. |
| Primary/secondary breed | Directly determines phenotype, epidemiology, trait risks and cross adjustments. |
| Breed split percentage | Carried in biology; no demonstrated weighted use in risk aggregation. |
| Age / birthday | Birthday can derive age; age is used for report/life-stage/exercise presentation, not clearly a central risk modifier. |
| Weight | Directly determines serving bracket, costs and any weight-based ingredient dose. |
| Environment | Selects/describes compatibility records; not a risk multiplier. |
| Activity level | Presented and may guide activity detail; not a demonstrated risk modifier. |
| Sex/gender, height | Accepted and largely presentation/pass-through. |
| BCS | Accepted but no demonstrated nutrition/risk computation. |
| Observed conditions | Directly boosts/signals matching condition priorities through heuristic mapping. |

Important missing clinical inputs: neuter/reproductive status; verified diagnosis and severity/stage; medication/supplement and dietary history; allergies/adverse events; comorbidities; laboratory results; mobility/pain score; calorie intake and BCS trend; clinician restrictions; pregnancy/lactation; renal/hepatic disease; owner goals/budget; exposure geography; and outcome/follow-up data.

### Output inventory

| Output | Required knowledge / classification |
|---|---|
| Risk priorities and explanations | Breed/trait relations + modifiers; scientific-model output, not diagnosis. |
| Biology/trait and environment narrative | Breed/trait/environment tables; explanatory presentation. |
| Activity and grooming guidance | Condition activity and observation data; preventative presentation. |
| Ingredient targets and doses | Condition-ingredient links + mass; scientific/support output with protocol-like presentation. |
| Natural-food alternatives | Food/nutrient tables; nutrition presentation. |
| Product recommendations, feeding plan, coverage | Product catalogue/components/feeding/price; commercial matching. |
| Essential/Balanced/Optimal packages | Tier/defaults/optimizer; commercial business logic. |
| Evidence/research section, trace, confidence | Evidence tables and formula ledgers; explainability/metadata. |
| Clinical assessment and clinical report | Projection of all above; report format, not an independently calculated assessment. |

## E. Real knowledge flow

```mermaid
flowchart TD
  I[Dog profile] --> N[Validate, normalize labels/units]
  N --> B[Resolve breed(s) to phenotype]
  B --> R[Breed + trait condition retrieval]
  R --> M[Apply trait interactions, benefits, mixed-breed and observed-sign modifiers]
  M --> P[Rank condition priorities]
  P --> A[Join activity and ingredient interventions]
  A --> D[Choose/de-duplicate nutrient doses]
  D --> X[Match product components and feeding rules]
  X --> O[Rank commercial bundles by coverage, function, evidence, cost]
  O --> S[Assemble clinical/legacy/UI reports]
```

Decision points: unknown breed resolution; trait row selection; prevalence summation/capping; multiplier/bounds; observed-sign mapping; ingredient de-duplication; alias/unit compatibility; active-product filter; feeding-bracket selection; package score/tier selection.

Information discarded or obscured: breed split is not propagated as a numerical risk weight; relation-level uncertainty/sample population is not preserved consistently through score aggregation; competing dose recommendations are collapsed (one path first-row, one path maximum); source-to-paper identity often becomes only text/URL; activity/environment evidence does not become an explicit quantified modifier; condition body-system is blank; and final package score combines scientific support with pricing/portfolio constraints.

## F. Redundancy, conflicting representations, and historical baggage

1. **Two identical lanes in condition ingredients and ingredient evidence.** `sci` and `prev` duplicate 12 and 10 records respectively. The loader reunites/deduplicates condition ingredients, but not ingredient evidence. This is release/parity baggage, not independent knowledge.
2. **Condition protocols duplicate condition ingredients.** Same condition/ingredient/dose relationships, with different source identities/quotes. They cannot both be the canonical clinical protocol without reconciliation.
3. **Nutrient priorities duplicates a subset with altered numbers.** Hip glucosamine/omega-3 values conflict with the live mapping values and adds calories/chondroitin not available through the core condition-ingredient path.
4. **Food sources and foods duplicate the same 15 food facts.** `foods` adds an ID; otherwise this is a projection-level duplicate.
5. **Trait interaction and benefit tables overlap.** Both say trait pairs change condition expression but use separate mechanics and terminology; `Mesocephalic × Athletic → BOAS` appears in both with different factors (0.72 vs 0.74).
6. **Runtime parameters duplicate hard-coded inference configuration.** The 18 CSV values mirror `app/inference/config.py`; nodes read context parameters but legacy logic still obtains code defaults. This is duplicated model policy.
7. **Wellness goals/nutrient catalogue/groomer map are code-held domain knowledge.** They overlap conditions/ingredient aliases and are not maintained in the warehouse.
8. **Ontology JSON duplicates only a partial condition registry.** Six ontology conditions include Anxiety, while `conditions.csv` has no Anxiety; most CSV conditions have no ontology entry. These are a separate, incomplete representation.
9. **Authoring drafts and published drafts.** 27 drafts and 14 published records are evidence-workflow history, not the live canonical warehouse. Several published drafts are historical copies.
10. **Tests/parity/golden output JSON.** These are generated behavior snapshots that preserve older `data/breed_analysis/...` path names. They are historical/validation artifacts, not source knowledge.
11. **Legacy JavaScript UI/API files and demo assets.** They present or mirror output contracts; they do not hold canonical veterinary facts.

The curation conflict report itself identifies unresolved `reduces` versus `supports` relations for glucosamine/omega-3/MSM links. This confirms that relation semantics are not consistently modeled.

## G. Traceability gaps and missing scientific concepts

### Traceability gaps

- No stable primary key joins most relationship rows to `papers.csv`; citation strings/URLs are duplicated across tables.
- Evidence level is inconsistent: high/medium/low labels, confidence, lane, record kind, source quote and raw paper data coexist without a common evidence model.
- Population, sample size and prevalence are present for some risk relations but absent for nearly all intervention claims; no study design, effect size, confidence interval, species/population applicability, conflicts or contraindications propagates to recommendations.
- Dose basis is weak: fixed daily values dominate, even though dog mass is accepted; units such as percent, grams, capsules and billion CFU are not a uniform pharmacological/nutrient dose ontology.
- Products have label components but no validated bioavailability, nutrient conversion, indication, safety, contraindication, manufacturing lot or availability model.
- The condition registry is not a usable clinical ontology: empty body-system column, no synonym/status/severity/stage/diagnostic criteria; names vary (`Arthritis` vs `Osteoarthritis`, BOAS casing, dry skin, general wellness).
- Outputs call themselves clinical reports/assessments although no clinical examination or diagnostic evidence is represented.

### Missing concepts

The absent concepts most material to a veterinary knowledge model are: diagnosis versus risk; symptom/sign; disease severity/stage; contraindication and adverse event; treatment/medicine and interaction; diet formulation and energy requirement; nutrient requirement framework; caloric intake; BCS trend; lab/imaging/exam finding; clinical outcome; owner adherence; veterinarian decision/approval; temporal provenance/last review; evidence synthesis and uncertainty; exposure geography; allergy; reproductive state; and clear distinction among preventative, supportive, therapeutic and marketing claims.

## H. Model B — software implementation observations

This section intentionally describes implementation only; it does not prescribe changes.

- **Canonical runtime source:** `warehouse/science` selected through manifest/registry and loaded into in-memory DataRepository views.
- **Scientific retrieval:** `app/data/native_loader.py`, `app/data/repository.py`, `warehouse/repository/*` project and annotate CSV records, including legacy aliases and lanes.
- **Reasoning:** FormulaGraph runs Profile → Breed → Biology → Risk → Epidemiology → Activity/Grooming/Nutrition/Ingredient → Product → Package marker → Assessment/Report/Evidence/Confidence/Validation/Trace/Export. The graph’s displayed order differs somewhat from the actual legacy report/package construction deferred to export.
- **Presentation:** FastAPI, report builders, Jinja/UI templates, static JavaScript, and legacy adapters reshape outputs. They introduce no canonical scientific facts except some labels/text mappings.
- **Authoring/curation:** Draft JSON is accepted, materialized/staged, audited for duplicates/conflicts and released separately. It is a knowledge-editing workflow adjacent to, not fully integrated with, the live evidence graph.
- **Scientific knowledge leaking into implementation:** trait weights, grooming-sign mappings, wellness-goal condition groups, nutrient display catalogue, package score weights and defaults. These are substantive model policy in Python.
- **Implementation leaking into knowledge:** `lane` (`sci`/`prev`), source CSV labels, product IDs and package tiers enter evidence/clinical explanations; “mechanism” rows can be package-label payload facts.

## I. Questions that remain unanswered

1. Which source is authoritative when condition ingredient, condition protocol and nutrient-priority records disagree?
2. Are the prevalence values actual comparable probabilities, and are they adjusted for population, age, sex, geography and ascertainment? If not, what does their sum mean?
3. Is each nutritional dose a nutrient dose, an ingredient mass, an extract dose, a product serving, or a regimen defined for a specified population?
4. Are product component values per serving, per 100 g, per pack, or label guarantee? `ingredient_mechanisms.csv` mixes these bases.
5. What clinical boundary governs a recommendation versus a diagnosis or treatment claim, and when must a veterinarian take over?
6. Which conditions are truly in scope? Why do ontology, condition registry, timelines, wellness goals and free-text grooming map use different condition universes?
7. Is the observed-condition field a confirmed diagnosis, an owner observation, or a groomer note? Its current handling treats it as a risk signal.
8. What outcomes would validate the risk ranking, activity plan, dose target and package selection independently?
9. Are `papers.csv` records complete/verified and intended to be the evidence authority? Why do many relation sources have no `paper_id`?
10. Which warehouse tables are intentionally retained only for parity/history, versus intended as active veterinary knowledge?

## Bottom line

The scientific system being represented is a **breed- and phenotype-informed canine preventative wellness graph**, with condition prioritization leading to supportive nutrition, activity, grooming and commercial product packages. Its strongest represented concepts are breed/trait-condition associations and condition-to-ingredient mappings. Its central scientific limitations are fragmented evidence provenance, duplicate/conflicting protocol data, code-embedded clinical policy, sparse individual clinical context, and an unresolved boundary between support recommendations and clinical care.
