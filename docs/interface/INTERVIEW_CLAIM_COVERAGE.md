# INTERVIEW_CLAIM_COVERAGE

| claim | runtime evidence | UI location | exact source | status |
|---|---|---|---|---|
| AI-enabled recommendation workflow | Existing analyze pipeline output with recommendations | `Wellness Analysis` page | `app/api/main.py:/api/v1/analyze`, `app/agent/engine.py` | VERIFIED |
| product portfolio / dog breed scope | Profile intake + product recommendation payload | `Dog Profile`, `Products` | `app/api/main.py:/api/breeds`, `app/agent/response_assembler.py` | VERIFIED |
| scientific and market research | Evidence payload and science endpoints exist | `Health & Evidence` | `app/agent/response_assembler.py` (`scientificEvidence`), `app/api/main.py:/api/v1/science/*` | PARTIAL |
| synthetic customer/dog profiles | Deterministic UI demo profiles | `Dog Profile` selector | `app/ui/cstc/demo_profiles.py` | VERIFIED |
| structured product/breed/health/pricing inputs | Structured request model + API payload mapping | `Dog Profile`, `Financial Model` | `app/ui/cstc/models.py`, `app/ui/cstc/adapter.py` | VERIFIED |
| personalized care-package recommendations | Runtime package recommendations | `Care Packages` | `app/agent/response_assembler.py` (`wellnessPackages`) | VERIFIED |
| product gaps | Closest runtime surface is research gaps endpoint; not integrated as dedicated gap engine in desktop shell | `About / System` and optional API exploration | `app/api/main.py:/api/v1/research/gaps` | PARTIAL |
| portfolio expansion | Product/store portfolio endpoint exists | `Products` | `app/api/main.py:/api/v1/store` | PARTIAL |
| complete care-package opportunities | Package payload includes tier/price economics fields when available | `Care Packages` | `app/agent/response_assembler.py`, `app/agent/package_optimizer.py` | VERIFIED |
| financial modeling | Monthly/yearly plans and package economics available where runtime provides fields | `Financial Model` | `app/agent/bundle_engine.py`, `app/agent/response_assembler.py` | VERIFIED |
| product costs | Product and plan cost fields in analyze payload | `Products`, `Financial Model` | `app/agent/response_assembler.py` (`price`, `monthly_plan`, `yearly_plan`) | VERIFIED |
| consumption | Some serving/feeding assumptions present in payload; coverage varies by product | `Products`, `Financial Model` | `app/agent/response_assembler.py` (`serving_size`, `monthly`) | PARTIAL |
| package pricing | Package and annual plan pricing fields | `Care Packages`, `Financial Model` | `app/agent/response_assembler.py`, `app/agent/bundle_engine.py` | VERIFIED |
| discounts | Exposed only when runtime includes discount/savings fields | `Financial Model` | `app/agent/response_assembler.py` package dictionaries | PARTIAL |
| recurring economics | Annual/monthly equivalents and savings fields where present | `Financial Model` | `app/agent/bundle_engine.py` (`monthly_equivalent`, `savings`) | VERIFIED |
| experimental products | No dedicated experimental-product runtime contract identified | Not surfaced as active feature | Forensic finding from `REFERENCE_PROJECT_INVENTORY.md`, API scan | NOT_IMPLEMENTED |
| rapid scaling | No quantitative scaling metric in runtime output contract | Not surfaced as computed KPI | Forensic finding from runtime contract scan | NOT_IMPLEMENTED |

## Notes
- PARTIAL means the desktop shell exposes closest real runtime outputs without fabricating missing fields.
- NOT_IMPLEMENTED means no trustworthy runtime contract was found for this claim in the current system.
