# API Layer

API layer should orchestrate engine services and expose transport contracts.

Rules:
- No direct CSV reads.
- Access warehouse only through engine/service boundaries.
- Keep request/response schemas explicit and versioned.
