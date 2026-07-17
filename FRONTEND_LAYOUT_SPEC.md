# Wagtopia JS Frontend — Layout & Data Contract Specification

**Document purpose:** Preserve the exact mobile UI layout, component hierarchy, styling, and variable bindings so a **100% Python agentic backend** can emit a response that renders identically in the existing JavaScript shell—without changing DOM selectors, CSS class names, or user flows.

**Audit date:** 2026-07-09  
**Audited artifacts:** `index.html`, `app.js`, `styles.css`, `server.js`, `src/api/routes.js`, `src/engine/index.js`, `src/engine/wellnessEngine.js`, `src/engine/packageDetailEngine.js`, `server/logic.js` (legacy adapter)

---

## 0. Repository snapshot vs. canonical UI

| Layer | Committed in git (`main`) | Canonical PPIE UI (preserve this) |
|-------|---------------------------|-----------------------------------|
| `index.html` | Static investor demo (Dolly hardcoded, no login) | Login overlay + dynamic profile + **Wellness feed** (`#wellness-feed`) + optional sub-views (`#wellness-hub`, `#wellness-package`, `#wellness-product`, `#wellness-nutrition`) |
| `app.js` | Static grooming diary + shop mock data only | PPIE client: `fetchRecommendations()` → `renderWellnessPage()` + `updateHomeProfile()` + `updatePlanCards()` + Socket.io groomer refresh |
| `styles.css` | Base luxury mobile theme (~1270 lines) | Base theme **plus** login, plan cards, wellness v2, bottom-sheet / report-page extensions |

> **Important:** The canonical layout described below is the **PPIE-integrated mobile experience** (Wellness v2/v3). The committed files were restored to an earlier static demo; this spec is reconstructed from the implemented controller logic and is the contract the Python API must satisfy when those bindings are re-attached.

---

## SECTION A — Visual viewport & component hierarchy

### A.1 Global shell (all pages)

```
<body>
  #login-overlay                    ← full-screen; hidden after profile submit
  #app-shell.device-frame          ← phone chrome (390px frame)
    .device-notch
    .phone-app                      ← 844px scroll viewport
      section.page                  ← one visible at a time (.active)
        #page-home
        #page-diary
        #page-ai                    ← Wellness / PPIE (bottom nav label: "AI Care")
        #page-shop
      nav.bottom-nav                ← fixed; height 72px (--nav-height)
```

**Navigation controller (`app.js`):**

| Trigger | Handler | Effect |
|---------|---------|--------|
| `.nav-item[data-page]` click | `showPage(name, scrollTarget?)` | Toggles `.page.active`, scrolls to top; if `name === 'ai'` can deep-link wellness sub-view |
| `.quick-card[data-nav]` click | `showPage(card.dataset.nav)` | Home shortcuts → diary / ai / shop |
| `.plan-card[data-nav]` click | `showPage('ai', data-intel-tab)` | Home plan teasers → Wellness tab |

**Page visibility:** `.page { display: none }` → `.page.active { display: block }`

---

### A.2 Login overlay (pet profile gate)

**DOM (required IDs):**

| Element ID | Role |
|------------|------|
| `#login-overlay` | Full-screen gate; `.hidden` when authenticated |
| `#login-form` | Submit → `saveProfile()` + `showApp()` + `refreshIntelligence()` |
| `#dog-name` | Text input, max 40 chars |
| `#dog-birthday` | Date input (`YYYY-MM-DD`) |
| `#breed-search` | Typeahead query |
| `#breed-dropdown` | `.open` when results visible |
| `#breed-chips` | Selected breeds (max 5) rendered as `.breed-chip` |

**localStorage key:** `wagtopiaPetProfile` → JSON:

```json
{
  "dogName": "Dolly",
  "breeds": ["Golden Retriever", "Labrador"],
  "birthday": "2022-03-15",
  "weight": 30
}
```

`weight` is optional; added when groomer socket pushes updates.

**Breed search API:** `GET /api/breeds?search={q}` → `string[]` breed names (max 15).

---

### A.3 Home page (`#page-home`) — top-to-bottom flow

```
.home-header
  .brand-mark                         "Wagtopia"
  .header-badge                       "Premium Care"
  #home-greeting                       "Hello, {dogName}'s Parent 👋"     ← dynamic
  #home-greeting-sub                   "{dogName}'s latest wellness…"      ← dynamic

.hero-dog > img                       Static Unsplash hero (not API-driven)

.profile-card
  .profile-avatar                     Static image URL (not API-driven today)
  .profile-meta
    #profile-name                      {dogName}                           ← dynamic
    #profile-breed                     breeds.join(' × ')                   ← dynamic
    #profile-stats > span×3            "{ageYears} yrs" | "{weightKg} kg" | sizeBracket ← dynamic

  .tag-row > .tag×N                    STATIC demo tags (Energetic, Friendly, …)
  .detail-sections
    .detail-block×4                    STATIC CRM copy:
      h3: Personality | Behavior Notes | Sensitive Areas | Favorite Treats
      p:  long-form groomer CRM text (not from PPIE API today)

.section-header "Upcoming Events"
.banner-carousel > .event-banner×4     STATIC marketing banners

.section-header "Quick Access"
.quick-grid > .quick-card×5            Navigation only

#home-plan-cards.plan-cards            PPIE teaser cards (dynamic)
  .plan-card.plan-monthly[data-nav=ai][data-intel-tab=packages]
    #monthly-plan-preview              "{coverage}% coverage · {n} products"
    #monthly-plan-price                "${monthly_cost}/mo"
  .plan-card.plan-yearly[data-nav=ai][data-intel-tab=packages]
    #yearly-plan-preview               "{coverage}% coverage · save with annual billing"
    #yearly-plan-price                 "${yearly_cost}/yr"
```

**Profile stat bindings (`updateHomeProfile`):**

| DOM node | API path | Format |
|----------|----------|--------|
| `#profile-stats` span 1 | `data.profile.age_years` or `data.pet.ageYears` | `"{n} yrs"` (1 decimal ok, e.g. `4.3 yrs`) |
| `#profile-stats` span 2 | `data.profile.weight_kg` or `data.pet.estimatedWeightKg` | `"{n} kg"` |
| `#profile-stats` span 3 | derived `sizeBracket` | `"small"` \| `"medium"` \| `"large"` \| `"giant"` |

**Static profile blocks:** Personality, Behavior Notes, Sensitive Areas, Favorite Treats are **not** wired to PPIE. For Python parity, expose optional `profile.crm` object (see Section B).

---

### A.4 Wellness page (`#page-ai`) — canonical mobile-first feed

**Header:**

```
.page-header.ai-header.compact-header
  .ai-badge                          "Wagtopia Wellness"
  #intel-page-title                  "Wellness" | "{name}'s Wellness Report"
```

**Primary scroll container:** `#wellness-feed.wellness-feed` — entire page is one vertical feed (no horizontal intel tabs in v2).

#### A.4.1 Summary card (`.wz-summary-card`)

Rendered by `renderWellnessPage()` into `#wellness-feed`:

| UI block | Class / element | Data binding |
|----------|-----------------|--------------|
| Time greeting | `.wz-greeting` | `wellness_summary.greeting` + `"!"` (e.g. `"Good afternoon!"`) |
| Intro paragraph | `.wz-intro` | `wellness_summary.intro` |
| Closing line | `.wz-intro.subtle` | `wellness_summary.closing` |
| Score label | `.wz-score-label` | `wellness_summary.score_label` (default: `"Estimated Wellness Score"`) |
| Score value | `.wz-score-value` | `wellness_summary.wellness_score` + `<small>/100</small>` |
| Priority list title | `.wz-priorities-label` | Static: `"Primary Health Priorities"` |
| Priority bullets | `.wz-priorities > li` | `wellness_summary.primary_priorities[]` strings (e.g. `"Joint Support"`, `"Dental Care"`) |

**Collapsible “View Analysis” (▼ chevron):**

- Component: `renderCollapsible('analysis', 'View Analysis', body, false)`
- Button: `.wz-collapse-btn` toggles `.wz-collapse.open` on parent
- Chevron: `.wz-chevron` rotates 180° when open (CSS); button label does **not** include `▼` in final version (chevron is separate span)
- Body rows: `wellness_summary.analysis_detail[]` each → `.analysis-row`:
  - `h4` ← `title` (e.g. `"Joint Health"`)
  - `.analysis-metrics` spans:
    - `"Biological estimate: {biological_estimate_percent}%"`
    - `"Observed prevalence: {observed_prevalence_percent}%"` (if not null)
  - `.analysis-traits` ← `supporting_traits.slice(0,4).join(' · ')`

This is the UI location for strings like **`12.7% prevalence`** — they appear inside the collapsed analysis body, not in the summary headline list.

#### A.4.2 Recommended Care Plans (`.wz-section`)

```
h2.wz-section-title                   "Recommended Care Plans"
p.wz-section-sub                      "Complete veterinary-backed wellness programs for {dogName}"
.care-plan-stack
  article.care-plan-card×3            renderCarePlanCard(pkg) per wellnessPackages[]
```

**Per care plan card (`renderCarePlanCard`):**

| Element | Binding |
|---------|---------|
| `.care-plan-badge` | Shown when `pkg.recommended === true` → text `"Recommended"` |
| `.care-plan-name` | `pkg.title` → `"Essential Care"` \| `"Balanced Care"` \| `"Optimal Care"` |
| `.care-plan-best` | `pkg.best_for` (optional, Essential only: `"Budget-conscious owners."`) |
| `.care-plan-score-num` | `pkg.coverage_score` (integer 0–100) |
| `.care-plan-score-label` | Static `"/100 coverage"` |
| `.care-plan-price-num` | `pkg.monthly_cost` (number, **no currency symbol in data**) |
| `.care-plan-price-unit` | Static `"/month"` |
| `.care-plan-desc` | `pkg.description` |
| `.care-plan-includes > li` | `pkg.includes_summary[]` each string |
| `button[data-open-plan]` | `data-open-plan="{pkg.tier}"` → `essential` \| `balanced` \| `optimal` |

**Recommended tier:** `tier === 'balanced'` gets `.care-plan-recommended` + gold border.

**Grid behavior:** `.care-plan-stack { flex-direction: column; gap: 14px }` — cards stack vertically (mobile-first). No desktop multi-column grid.

#### A.4.3 Lifestyle block

| Element | Binding |
|---------|---------|
| `.lifestyle-big` | `activityRecommendations.recommended_daily_exercise` (e.g. `"75–90 minutes"`) |
| `.activity-pill` | union of `suggested_physical[]` + `suggested_mental[]` |
| `.lifestyle-tip` | `activityRecommendations.lifestyle_tip` (prefix `💡 ` added in JS) |

#### A.4.4 Collapsible research (“Why did we recommend these plans?”)

- `renderCollapsible('why', 'Why did we recommend these plans?', researchBody, false)`
- `researchSection.biological_traits[]` → `.bio-chip`
- `researchSection.health_priorities[]` → compact `.analysis-row` with `title` + `biological_estimate_percent`
- `researchSection.ingredient_evidence[]` → `.research-quote` with `quote` + `cite` = `source_name`
- `researchSection.literature[]` → `.research-lit` with `quote`/`source_quote` + `source_name`

---

### A.5 Wellness sub-views (v3 — full-page drill-down)

When bottom sheets were replaced by dedicated pages, structure becomes:

```
#page-ai
  #wellness-hub.wellness-view          ← contains #wellness-feed
  #wellness-package.wellness-view.hidden
    #package-back                      "← Wellness"
    #package-page-content.report-page  ← renderPackagePage(pkg) HTML
  #wellness-product.wellness-view.hidden
    #product-back                      "← Care Package"
    #product-page-content
  #wellness-nutrition.wellness-view.hidden
    #nutrition-back
    #nutrition-page-content
```

**View state:** `wellnessNav = { view: 'hub'|'package'|'product'|'nutrition', tier, productKey }`  
**`showWellnessView(view)`** toggles `.hidden` on the four `.wellness-view` containers and updates `#intel-page-title`.

**Package page sections (`renderPackagePage`):** Package Summary → Products (`.pkg-product-card`) → Daily Nutrition Intake (nutrient rings) → Feeding Guide → Research → Cost table → Subscribe CTA.

**Product drill-down:** `[data-open-product="{product_id|product_name}"]` → `showProductPage(key)` using `productAnalyses[key]`.

---

### A.6 Bottom sheets (v2 alternate — still in CSS/DOM spec)

If sheets are used instead of full pages:

| Overlay ID | Tabs | Body ID | Footer CTA |
|------------|------|---------|------------|
| `#plan-sheet-overlay` | overview, products, nutrition, cost | `#plan-sheet-body` | `#plan-subscribe-btn` |
| `#product-sheet-overlay` | — | `#product-sheet-body` | `#product-add-btn` |

`openPlanSheet(tier)` sets `#plan-sheet-title`, renders tab content from `wellnessPackages.find(tier)`.

---

### A.7 Diary page (`#page-diary`) — static session renderer

Not PPIE-driven. `renderReport(sessionId)` fills `#grooming-report` from local `sessions` object in `app.js`.

**Calendar:** `.cal-day.has-session[data-session]` click → `renderReport(id)`.

Only dynamic home binding: `#page-diary .page-header h1` → `"{dogName}'s Diary"`.

---

### A.8 Shop page (`#page-shop`) — static catalog

`renderShop(category)` fills `#product-grid` from hardcoded `shopProducts[]`. Category filter via `.cat-btn[data-cat]`.

Product card pattern:

```html
<div class="shop-product">
  <img src="{img}">
  <div class="shop-product-info">
    <span class="cat-tag">{cat}</span>
    <h4>{name}</h4>
    <div class="price">{price}</div>   <!-- pre-formatted string e.g. "$12.99" -->
  </div>
</div>
```

---

### A.9 State-driven rendering summary

| User action | State change | Re-render |
|-------------|--------------|-----------|
| Login submit | `petProfile` saved | `refreshIntelligence()` |
| Nav → AI Care | `showPage('ai')` | Feed already populated |
| Tap care plan “View Details” | `openPlanSheet(tier)` or `showPackagePage(tier)` | Package detail from `packageDetails[tier]` or `wellnessPackages` |
| Collapsible header click | `.wz-collapse.open` toggle | CSS only |
| Groomer socket event | `petProfile.weight` update | `refreshIntelligence()` + toast banner |
| Calendar day tap | `.cal-day.active` | `renderReport(sessionId)` |

---

## SECTION B — Full data layout matrix (Python API contract)

### B.1 Primary endpoint

**Canonical:** `POST /api/v1/analyze`  
**Headers:** `x-api-key: wagtopia-demo-key`, `Content-Type: application/json`  
**Legacy adapter:** `POST /api/recommendations` (maps v2 response → v1 shape via `mapLegacyResponse`)

**Request body (Python must accept):**

```json
{
  "pet_name": "Dolly",
  "breeds": ["Golden Retriever", "Labrador"],
  "birthday": "2022-03-15",
  "weight": 30,
  "weight_kg": 30,
  "sex": "female",
  "activity_level": "high",
  "current_environment": "Shanghai Summer",
  "observed_conditions": []
}
```

| Field | Required | UI consumer |
|-------|----------|-------------|
| `pet_name` / `dogName` | Yes | All greetings, copy interpolation |
| `breeds` | Yes (1–5) | `#profile-breed`, risk engine |
| `birthday` | Yes | Age → `#profile-stats`, `biology.age_years` |
| `weight` / `weight_kg` | Recommended | `#profile-stats`, feeding math |
| `observed_conditions` | No | Groomer boost, `groomer[]` live grid |

---

### B.2 Profile & CRM fields

| UI location | Field | Type | Example | Notes |
|-------------|-------|------|---------|-------|
| `#profile-name` | `profile.pet_name` | string | `"Dolly"` | |
| `#profile-breed` | `profile.breeds[]` | string[] | `["Golden Retriever","Labrador"]` | Join with ` × ` |
| `#profile-stats` [0] | `profile.age_years` | number | `4.3` | Display `"{n} yrs"` |
| `#profile-stats` [1] | `profile.weight_kg` | number | `30` | Display `"{n} kg"` |
| `#profile-stats` [2] | `sizeBracket` | string | `"large"` | Derived: &lt;8 small, &lt;18 medium, &lt;35 large, else giant |
| `.tag-row` | *not wired* | string[] | `["Energetic","Friendly"]` | **Proposed:** `profile.personality_tags[]` |
| Personality `p` | *static* | string | long text | **Proposed:** `profile.personality` |
| Behavior Notes `p` | *static* | string | | **Proposed:** `profile.behavior_notes` |
| Sensitive Areas `p` | *static* | string | | **Proposed:** `profile.sensitive_areas` |
| Favorite Treats `p` | *static* | string | | **Proposed:** `profile.favorite_treats` |
| `.profile-avatar` `src` | *static URL* | string | | **Proposed:** `profile.avatar_url` |

---

### B.3 `wellness_summary` (summary card)

| Key | Type | UI binding |
|-----|------|------------|
| `greeting` | string | `.wz-greeting` — time-based: `"Good morning"` \| `"Good afternoon"` \| `"Good evening"` |
| `intro` | string | `.wz-intro` — mentions top 3 priority labels |
| `closing` | string | `.wz-intro.subtle` |
| `wellness_score` | number 0–100 | `.wz-score-value` |
| `score_label` | string | `.wz-score-label` |
| `primary_priorities` | string[] | `.wz-priorities li` — display labels like `"Joint Support"` |
| `traits_analysed` | string[] | Available for research chips (not always shown in summary) |
| `analysis_detail[]` | object[] | Collapsible analysis body |
| `analysis_detail[].title` | string | `h4` — goal title e.g. `"Joint Health"` |
| `analysis_detail[].biological_estimate_percent` | number | `"Biological estimate: X%"` |
| `analysis_detail[].observed_prevalence_percent` | number \| null | `"Observed prevalence: X%"` |
| `analysis_detail[].difference_percent` | number \| null | Optional delta row |
| `analysis_detail[].supporting_traits` | string[] | `.analysis-traits` |
| `analysis_detail[].explanation` | string | Available in expanded insight cards (v1 panels) |

---

### B.4 `healthInsights[]` (priority metrics — alternate/tabbed UI)

Used when `renderIntelPanels` / insight cards are active. Maps 1:1 to wellness goals.

| Key | Type | Display |
|-----|------|---------|
| `goal_id` | string | `joint_health`, `dental_health`, … |
| `title` | string | `"Joint Health"` |
| `estimated_biological_risk_percent` | number | `"14.0%"` style biological estimate |
| `observed_breed_prevalence_percent` | number \| null | `"14.9%"` prevalence |
| `estimate_vs_observed_difference` | number \| null | Signed delta |
| `confidence_percent` | number | Confidence meter |
| `explanation` | string | Paragraph after “Why this matters” |
| `supporting_traits` | string[] | Bullet list |
| `peer_reviewed_study_count` | number | Footer count |
| `groomer_priority` | boolean | Badge “Groomer priority” |
| `evidence_sources[]` | `{source_name, source_quote, source_url}` | Literature / citation blocks |

**Legacy `priorities[]` shape (insight-first cards with products nested):**

| Key | Type | Notes |
|-----|------|-------|
| `id` | string | Category key e.g. `joint` |
| `title` | string | `"Joint Health"` |
| `priorityLevel` | string | `"High Priority"` \| `"Moderate Priority"` \| `"Watch"` |
| `priorityScore` | number | Large score top-right |
| `riskReasoning` | string | Quoted in `.risk-reasoning` |
| `whyProfile.breeds` | string[] | Why block |
| `whyProfile.ageYears` | number | `"4.3 years"` in copy |
| `whyProfile.weightKg` | number | `"30kg"` |
| `breedEvidence` | `{sourceName, quote, url}` | Citation block |
| `ingredients[]` | `{name, targetMgPerDay, evidenceQuote, sourceName, sourceUrl}` | |
| `products[]` | see B.6 legacy product row | Nested product cards |

---

### B.5 `wellnessPackages[]` (care plan cards — **primary**)

| Key | Type | UI element |
|-----|------|------------|
| `tier` | `"essential"` \| `"balanced"` \| `"optimal"` | `data-open-plan`, `data-plan-tier` |
| `title` | string | `.care-plan-name` |
| `recommended` | boolean | `.care-plan-recommended`, badge |
| `best_for` | string \| null | `.care-plan-best` |
| `coverage_score` | number | `.care-plan-score-num` |
| `monthly_cost` | number | `.care-plan-price-num` (JS prefixes `$`) |
| `yearly_cost` | number | Home yearly card, sheets |
| `description` | string | `.care-plan-desc` |
| `tagline` | string | First sentence variant |
| `includes_summary` | string[] | `.care-plan-includes li` |
| `why_fits` | string | Meta under package stats (tabbed UI) |
| `overview` | string | Plan sheet “overview” tab |
| `subscribe_cta` | string | `"Subscribe to Balanced Care"` |
| `products_included[]` | object[] | Sheet + package rows |
| `nutrition_coverage[]` | `{goal_id, title, coverage_percent}` | Nutrition tab bars |
| `activities_included` | string[] | Optional footer line |

**`products_included[]` item:**

| Key | Type | Display pattern |
|-----|------|-----------------|
| `type` | string | `"fresh_food"` \| `"supplement"` \| `"treat"` \| `"dental"` |
| `name` | string | Product display name |
| `product_id` | string | e.g. `"FF003"`, `"SP013"` — for analysis lookup |
| `brand` | string | `"Wagtopia"` |
| `monthly_cost` | number | `"$X/mo"` in rows |
| `serving_size` / `daily_amount` | string | `"1 serving/day"` |
| `monthly_quantity` | string | `"30 units/month"` |
| `why_selected` | string | Product sheet |
| `active_ingredients[]` | `{name, amount, unit}` | Ingredient pills |
| `advantages[]` | string[] | Bullet list |
| `coverage_percent` | number | Coverage badge |

**Enriched package fields (`packageDetailEngine` — package page):**

| Key | Purpose |
|-----|---------|
| `package_summary` | Hero prose |
| `product_cards[]` | `{product_id, product_name, brand, category, image_url, daily_serving, monthly_amount, monthly_cost}` |
| `daily_nutrition_intake[]` | Nutrient rings: `{nutrient, provided, target_daily, unit, coverage_percent}` |
| `full_nutrition_report[]` | Full nutrition page |
| `feeding_strategies[]` | Options A–D with `items[]`, `calories_estimate`, `highlights[]` |
| `cost_breakdown` | `{rows[], monthly_total, yearly_total, annual_discount_percent, savings_vs_monthly}` |
| `research_notes[]` | `{nutrient, quote, source_name, source_url}` |

---

### B.6 Product display strings

**Wellness recommendation row (`productRecommendations[]`):**

```
{product_name}
{brand} · {product_type} · ${price}/unit
Serving: {serving_size} | Coverage: {coverage_percent}% | Est. monthly: ${monthly_cost_estimate}/mo
Active: {name} {amount}{unit}, …
Why we selected this — {why_selected}
{combined_coverage_note}
```

**Legacy nested product (`renderPriorityCard`):**

```
{productName}
{brand} · ${price}
Active: {name} {amountMg}mg
Dosage: {dosagePerServing}/serving
Suggested: {suggestedUsage}
Coverage: {coveragePercent}%
```

**Package product row:**

```
<span class="pkg-type">{type}</span>
<span>{name}</span>
<span class="pkg-cost">${monthly_cost}/mo</span>
```

**Staple food label pattern (engine internal):**  
`"{product_name}"` with `product_id` like `FF002_BEEF` — UI shows **name only**, not `(SF005)` suffix. Legacy mock IDs `SF001`–`SF005`, `SP001`–`SP008`, `TR001`–`TR002` must not appear in production data.

**Real catalog IDs (18 products):** `TR003`–`TR007`, `FF001`, `FF002_*`, `FF003`, `SP009`–`SP015`.

---

### B.7 `wellness_coverage` (score ring — when shown on AI tab)

| Key | Type | UI |
|-----|------|-----|
| `overall_score` | number | Ring + `#wellness-score-num` |
| `label` | string | Score card title |
| `subtitle` | string | Descriptor line |
| `dimensions[]` | `{goal_id, title, coverage_percent}` | `.dimension-bar` width = percent |

Ring math: `stroke-dashoffset = 327 - (327 * score / 100)` on `#score-ring-fill` (circumference 327).

---

### B.8 `nutritionalTargets[]` / ingredients

| Key | Type | UI |
|-----|------|-----|
| `ingredient` | string | `h4` |
| `daily_target` | string | `"500mg"` combined value+unit |
| `monthly_target` | string | `"15000mg"` |
| `supports_goals` | string[] | Joined goals |
| `evidence_quote` | string | Blockquote |
| `source_name`, `source_url` | strings | Citation row |

---

### B.9 `activityRecommendations`

| Key | Type |
|-----|------|
| `recommended_daily_exercise` | string e.g. `"75–90 minutes"` |
| `suggested_physical` | string[] |
| `suggested_mental` | string[] |
| `lifestyle_tip` | string |
| `condition_specific[]` | `{activity, frequency, duration_minutes, supports}` |
| `future_personalization_note` | string |

---

### B.10 `researchSection`

| Key | Type |
|-----|------|
| `title` | string |
| `biological_traits` | string[] |
| `health_priorities[]` | `{title, biological_estimate_percent, observed_prevalence_percent, supporting_traits}` |
| `ingredient_evidence[]` | `{ingredient, supports[], quote, source_name, source_url}` |
| `literature[]` | evidence objects with `quote`/`source_quote`, `source_name` |

---

### B.11 `calculationTrace[]` (epidemiology drill-down)

Per priority goal — powers trace cards when enabled:

| Key | Content |
|-----|---------|
| `condition` | Goal title |
| `observed_inputs` | `{age, weight, body_size, body_type, coat_type, activity, breed_mix[]}` |
| `published_evidence[]` | `{breed, condition, observed_prevalence_percent, sample_size, source_title, source_url, source_year}` |
| `trait_contributions[]` | `{trait, role, explanation}` |
| `nutrient_targets[]` | `{nutrient, target_daily_value, unit, reason, evidence}` |
| `product_contributions[]` | Product-level nutrient gap filling |
| `decision_log[]` | String audit trail |

---

### B.12 `groomer[]` live grid

| Key | Values | UI |
|-----|--------|-----|
| `key` | `eyes`, `ears`, `skin`, `teeth`, `limps`, `shedding`, `anal gland` | Cell id |
| `label` | Human label | `.gl-label` |
| `status` | `flagged` \| `clear` | Cell class + status text |
| `live` | boolean | `.gl-live` badge |

Socket: `update_pet_profile` / `recommendation:update` → `refreshIntelligence()`.

---

### B.13 Complete top-level response envelope

Python `POST /api/v2/wellness/evaluate` (or JS-compatible wrapper) should emit at minimum:

```json
{
  "engine": "PPIE",
  "version": "2.1.0",
  "profile": { },
  "biology": { },
  "wellness_summary": { },
  "wellness_coverage": { },
  "healthInsights": [ ],
  "nutritionalTargets": [ ],
  "productRecommendations": [ ],
  "wellnessPackages": [ ],
  "packageDetails": { "essential": {}, "balanced": {}, "optimal": {} },
  "productAnalyses": { },
  "activityRecommendations": { },
  "researchSection": { },
  "calculationTrace": [ ],
  "groomer": [ ],
  "monthly_plan": { },
  "yearly_plan": { }
}
```

Legacy aliases preserved for older bindings: `risks`, `ingredients`, `products`, `wellness_score`.

---

## SECTION C — Currency, pricing & math rendering

### C.1 The zero-dollar root cause

The UI **does not** read prices from HTML. It formats **numeric** fields at render time:

```javascript
function fmtMoney(n) {
  return `$${Math.round(n)}`;
}
// Examples in templates:
`$${pkg.monthly_cost}/mo`
`$${pkg.yearly_cost}/yr`
`$${p.price}/unit`
```

**Failure modes that produce `$0`:**

| Cause | Mechanism |
|-------|-----------|
| **Missing / zero `price` on product objects** | `productRecommendations[].price` is 0 when `list_price_rmb` failed to load |
| **Deprecated `list_price_usd`** | `csvLoader.js` line: `parseFloat(priceRow.list_price_rmb) \|\| parseFloat(priceRow.list_price_usd) \|\| 0` — if only USD column populated in old data, currency flag may be wrong but price might work; if both empty → **0** |
| **Legacy adapter dropping fields** | `mapLegacyResponse` passes `products` but home cards read `wellnessPackages[].monthly_cost` |
| **Unit mismatch in components** | Product matching returns 0% coverage (not $0) but can exclude products from packages, indirectly yielding empty/minimal plans |
| **Hardcoded demo shop** | `shopProducts[].price` are strings like `"$12.99"` — separate from PPIE (always works in static demo) |
| **Grooming diary products** | `sessions[].productsUsed[].price` are **pre-formatted strings** (`"$28"`) in static mock — not from API |

**Python fix contract:** Always populate numeric fields from `PRODUCT_PRICING.list_price_rmb`:

```
unit_cost_per_bag = list_price_rmb / package_units
monthly_cost = quantity × unit_cost_per_bag   // rounded per engine rules
```

Never send pre-formatted `"$0"` strings for PPIE-driven fields — send numbers; let JS format (until localization patch).

---

### C.2 Currency injection map (all `$` locations to swap for ¥)

| File / function | Pattern | Current | Target (RMB) |
|-----------------|---------|---------|----------------|
| `fmtMoney(n)` | `` `$${Math.round(n)}` `` | `$42` | `¥42` or `¥42.00` |
| `updatePlanCards` | `` `$${balanced.monthly_cost}/mo` `` | `/mo` | `/月` |
| `updatePlanCards` | `` `$${optimal.yearly_cost}/yr` `` | `/yr` | `/年` |
| `renderCarePlanCard` | `.care-plan-price-num` + `.care-plan-price-unit` | `/month` | `/月` |
| `renderPlanSheetContent` cost tab | `$${pkg.monthly_cost}/mo` | | `¥{n}/月` |
| `renderPackagePage` cost table | `$' + r.monthly_cost` | | `¥` prefix |
| `renderIntelPanels` products | `$${p.price}/unit` | | `¥{n}/单位` or keep `/unit` |
| `productCardHTML` (diary) | `p.price` string | Already formatted | Backend should send `¥28` strings **or** change renderer |
| `renderShop` | `p.price` string | Static | Same |
| `buildCostBreakdown` (server) | `unit_price: \`$${p.price}\`` | Server-side `$` in enriched package | Python should emit **numeric** `unit_price_rmb` and let UI format |

**Suffix localization:**

| English (current) | Chinese target |
|-------------------|----------------|
| `/month`, `/mo` | `/月` |
| `/year`, `/yr` | `/年` |
| `per month` | `每月` |
| `Annual (bundled)` | `年付（优惠）` |

**Recommended approach for Python migration:**

1. Add `currency: "RMB"` and numeric `*_rmb` fields to API.
2. Replace `fmtMoney` with `fmtCurrency(n, currency)` in one JS helper.
3. Keep field names `monthly_cost` / `yearly_cost` but document they are **RMB minor units or whole yuan** (engine currently uses whole yuan integers).

---

### C.3 Coverage & prevalence math (display only)

| Metric | Formula (engine) | Display |
|--------|------------------|---------|
| Wellness score | Mean of `wellness_coverage.dimensions[].coverage_percent` | Integer `/100` |
| Package coverage | Weighted mean of nutrition dimension coverages × tier multiplier | `{score}/100 coverage` |
| Biological estimate | Trait + breed epidemiology pipeline | `{n}%` one decimal |
| Observed prevalence | Max breed registry prevalence for goal | `{n}%` e.g. `12.7%` |
| Product coverage | `amount_per_serving / daily_target × 100` capped | `{n}%` |
| Ring stroke | `327 - (327 × score / 100)` | SVG animation |

---

## SECTION D — CSS styling & brand system

### D.1 Design tokens (`:root` in `styles.css`)

| Token | Hex | Usage |
|-------|-----|-------|
| `--cream` | `#FAF6F0` | App background, chips |
| `--cream-dark` | `#F0E8DC` | Borders, tracks |
| `--beige` | `#E8DFD0` | Sheet handle |
| `--brown` | `#8B7355` | Primary brand, buttons |
| `--brown-dark` | `#6B5740` | Headings, CTA |
| `--brown-light` | `#A89078` | Gradients |
| `--gold` | `#C4A574` | Accents, recommended border |
| `--gold-light` | `#D4BC94` | Sparklines |
| `--text` | `#3D3429` | Body text |
| `--text-muted` | `#7A6F63` | Secondary text |
| `--white` | `#FFFCF8` | Cards |
| `--shadow` | `0 4px 24px rgba(107, 87, 64, 0.08)` | Card elevation |
| `--shadow-lg` | `0 8px 32px rgba(107, 87, 64, 0.12)` | Hover / recommended |
| `--radius` | `16px` | Standard corners |
| `--radius-sm` | `12px` | Inputs |
| `--radius-lg` | `24px` | Profile / plan cards |
| `--nav-height` | `72px` | Bottom padding offset |
| `--font` | `'DM Sans', …` | UI sans |
| `--font-serif` | `'Noto Serif', …` | Headlines |

**Page backdrop (outside phone):** `linear-gradient(145deg, #2C2419, #4A3F32, #3D3429)`

**Status / semantic colors:**

| Use | Hex |
|-----|-----|
| Positive / up trend | `#5A7A4A` |
| Resolved pill bg | `#E8F0E4` |
| Flagged groomer / warning | `#C4A574`, `#FFF9F0` |
| Fresh warning text | `#8B5A3C` |
| Live toast / banner | `#5A7A4A` on white text |

**Event banner gradients:** `#8B7355→#C4A574`, `#A67B5B→#D4A574`, `#7A6B5A→#B8956A`, `#6B5740→#A89078`

**Plan card gradients:**

| Class | Gradient |
|-------|----------|
| `.plan-monthly` / `.monthly-mega` | `#6B5740 → #8B7355 → #A89078` |
| `.plan-yearly` / `.yearly-mega` | `#4A3F32 → #6B5740 → #C4A574` |

---

### D.2 Layout patterns

| Pattern | CSS | Where |
|---------|-----|-------|
| Phone frame | `390px` width, `border-radius: 44px`, inner `36px` | `.device-frame` / `.phone-app` |
| Vertical scroll | `overflow-y: auto` on `.page` | Each tab page |
| Bottom nav | `position: absolute; bottom: 0; height: 72px; flex space-around` | `.bottom-nav` |
| Home quick grid | `grid-template-columns: repeat(2, 1fr); gap: 10px` | `.quick-grid` |
| Care plan stack | `flex-direction: column; gap: 14px` | `.care-plan-stack` |
| Groomer live grid | `grid-template-columns: repeat(2, 1fr)` | `.groomer-live-grid` |
| Shop layout | Sidebar `90px` + flexible main | `.shop-sidebar` + `.shop-main` |
| Product grid | `repeat(2, 1fr)` | `.product-grid` |
| Banner carousel | horizontal scroll, `scroll-snap-type: x mandatory` | `.banner-carousel` |
| Bottom sheet | `max-height: 88vh`, slide-up animation | `.bottom-sheet` |
| Collapsible | `.wz-collapse-body { display: none }` → `.open { display: block }` | Analysis / Why sections |

**Mobile constraints:**

- Max content width inside frame: **366px** (390 − 12×2 padding)
- Touch targets: plan buttons `padding: 14px`, nav items `padding: 8px 16px`
- Horizontal tab strips: `overflow-x: auto; -webkit-overflow-scrolling: touch`
- `scroll-behavior: smooth` on pages

---

### D.3 Typography scale (key sizes)

| Element | Size | Weight | Family |
|---------|------|--------|--------|
| `.greeting` / `.wz-greeting` | 22–26px | 600 | serif |
| `.care-plan-name` | 20px | 600 | serif |
| `.care-plan-price-num` | 24px | 700 | sans |
| `.wz-score-value` | 32px | 700 | serif |
| `.wz-section-title` | 18px | 600 | serif |
| Body / `.wz-intro` | 14px | 400 | sans |
| Labels / `.wz-priorities-label` | 11–12px | 600 uppercase | sans |
| Bottom nav | 10px | 500 | sans |

---

### D.4 Motion

| Animation | Definition |
|-----------|------------|
| `fadeIn` | Reports: opacity 0→1, translateY 8px→0 |
| `sheetUp` | Bottom sheet: translateY 100%→0 |
| `pulse-live` | Groomer live pill opacity pulse |
| Priority cards | `animation: fadeIn 0.45s ease both` + staggered `animation-delay` |
| Chevron | `transform: rotate(180deg)` when `.wz-collapse.open` |

---

## SECTION E — Controller / server wiring

### E.1 Static file server

`server.js` → `express.static(__dirname)` serves `index.html`, `app.js`, `styles.css` at port **3000**.

### E.2 API routes (`src/api/routes.js`)

| Method | Path | Handler |
|--------|------|---------|
| POST | `/api/v1/analyze` | `analyze(req.body)` → full v2.1 envelope |
| POST | `/api/recommendations` | `analyze` → `mapLegacyResponse` |
| GET | `/api/breeds` | Breed typeahead |
| POST | `/api/v1/groomer/update` | Session observations → Socket emit |
| POST | `/api/groomer/submit` | Legacy groomer form |

### E.3 Client fetch evolution

| Generation | Endpoint | Notes |
|------------|----------|-------|
| v1 | `POST /api/recommendations` | Returns `monthlyPack`, `priorities` |
| v2 | `POST /api/v1/analyze` | Full wellness envelope |
| Python target | `POST /api/v2/wellness/evaluate` (FastAPI) | Must map to same field names |

**Client refresh pipeline:**

```
refreshIntelligence()
  → intelData = await fetchRecommendations()
  → updateHomeProfile(intelData)
  → updatePlanCards(intelData)
  → updateWellnessScore(intelData)   // optional if score on feed
  → renderWellnessPage(intelData)    // primary v2
```

---

## SECTION F — Python backend checklist (preservation contract)

To render the existing layout without JS changes:

- [ ] Emit **numeric** `monthly_cost`, `yearly_cost`, `price` from `list_price_rmb` (never rely on `list_price_usd`)
- [ ] Populate `wellnessPackages[3]` with tiers `essential`, `balanced`, `optimal`
- [ ] Set `recommended: true` only on `balanced`
- [ ] Fill `includes_summary[]` with human-readable bundle lines
- [ ] Provide `wellness_summary.analysis_detail` for collapsible prevalence rows
- [ ] Map goal titles consistently: `Joint Health` ↔ `joint_health` ↔ display `Joint Support` in `primary_priorities`
- [ ] Include `packageDetails` + `productAnalyses` if package/product sub-pages are enabled
- [ ] Keep `groomer[]` grid keys stable for Socket.io updates
- [ ] Optional CRM fields for static profile blocks if marketing copy should become dynamic

---

## Appendix A — File reference map

| Concern | Primary file |
|---------|--------------|
| DOM scaffold | `index.html` |
| Rendering & events | `app.js` |
| Visual system | `styles.css` |
| PPIE orchestration | `src/engine/index.js` |
| Package enrichment | `src/engine/packageDetailEngine.js` |
| Wellness narratives | `src/engine/wellnessEngine.js` |
| Product pricing load | `src/db/csvLoader.js` → `buildProductCatalog()` |
| HTTP surface | `src/api/routes.js` |
| Legacy adapter | `server/logic.js` (deprecated path) |

---

## Appendix B — Evolution timeline (for archaeologists)

1. **Static demo** — Hardcoded Dolly, grooming diary, shop mocks  
2. **PPIE v1** — Login + intel tabs + `renderIntelPanels` + `monthlyPack`  
3. **Insight-first** — `priority-card` stack + `renderPriorityCard` + mega plans  
4. **Wellness v2** — Mobile feed + `care-plan-card` + collapsibles + bottom sheets  
5. **Wellness v3** — Full-page package/product/nutrition reports + `calculationTrace`  
6. **Python agent** — Streamlit mirror (`app/ui/demo_app.py`) uses ¥ but **does not** replace this JS layout

**This specification targets the v2/v3 JS layout** as the customer-facing product surface to preserve.

---

*End of specification.*
