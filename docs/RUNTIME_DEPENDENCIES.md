# RUNTIME_DEPENDENCIES.md

Static import closure from `app.main` (clinical runtime).

## Entry

`app.main` → `app.api.main` → AssessmentAgent / FormulaGraph / Repository / warehouse

## Reachable packages (~91 modules)

- `app.agent.*` — FormulaGraph, nodes, assemblers  
- `app.formulas.stages.*` — clinical calculations  
- `app.data.*` — DataPlatform, native_loader, reports, validation console  
- `app.inference.*` — formula registry / resolvers  
- `app.science.*` — knowledge graph (API science routes)  
- `app.core.paths`  
- `warehouse.repository.*` — entities + ScientificRepository  

## Optional (lazy) imports from API

Still used for authoring routes (not clinical math):

- `authoring.*`
- `curation.*`
- `ontology`

## Not on runtime path (deleted in Phase Φ)

`ppie_platform`, `developer_tools`, `analytics`, `simulation`, `operations`, `quality`, `governance`, `tools`, `debug`
