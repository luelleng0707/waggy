# FRONTEND_BOUNDARY

Target boundary:

FRONTEND
  -> API
  -> PIPELINE
  -> DOMAIN ENGINES
  -> WAREHOUSE

Rules:
- Frontend must not read warehouse CSV files directly.
- Frontend must not import formula runtime modules.
- Frontend must not import optimization internals or evidence-graph internals.
- API responses are the canonical contract between frontend and backend runtime.
