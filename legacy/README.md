# Legacy

Compatibility UI and archived pre-cutover trees.

**Current production demo UI:** `workbench.html` / `workbench.js` / `workbench.css` at `GET /`.

Classic customer (`app.js`), business, and developer pages remain routed for compatibility. They render backend payloads; they must not compose packages.

`archive/` holds historical `repository/api` and `repository/frontend` snapshots. Those are not the running path.

See [docs/WAGGY_SYSTEM.md](../docs/WAGGY_SYSTEM.md).
