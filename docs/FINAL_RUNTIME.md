# FINAL_RUNTIME.md

```
uvicorn app.main:app
        ↓
app.api.main
        ↓
PPIEWellnessAgent / AssessmentAgent
        ↓
DataRepository ← warehouse/{reference,science,runtime}
        ↓
FormulaGraph → AssessmentResult → JSON
```

Boot check: `GET /health`  
Assess: `POST /api/v1/ppie/assess` with `x-api-key`
