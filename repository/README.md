# Waggy v2 Repository Foundation

This directory is the new Waggy v2 architecture foundation.

Layering direction:

1. `repository/warehouse/` (facts only)
2. `repository/engine/` (reasoning services, no persistence)
3. `repository/api/` (transport + orchestration)
4. `repository/frontend/` (presentation)

Legacy code outside this tree is transitional and should be migrated into these layers incrementally.
