# FOLDER_USAGE.md

| Folder | Imported by | Executed how | Keep? |
|--------|-------------|--------------|-------|
| `app/` | uvicorn, tests | Runtime | **yes** |
| `warehouse/` | Repository | Runtime data | **yes** |
| `tests/` | pytest | CI / local | **yes** |
| `docs/` | humans | Read | **yes** |
| `scripts/` | CLI | Bootstrap / Φ tools | **yes** |
| `authoring/` | API authoring routes, tests | `py -3 -m authoring.pipeline` | **yes** (science authoring) |
| `curation/` | authoring, API | helpers | **yes** |
| `ontology/` | authoring, API | helpers | **yes** |
| `science_pipeline/` | CLI | `py -3 -m science_pipeline.release` | **yes** |
| Demo UI root `*.js`/`index.html` | FastAPI static | Browser | **yes** |

Deleted: analytics, simulation, ppie_platform, developer_tools, operations, tools, debug, quality, governance, archive, meta.
