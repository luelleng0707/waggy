# Archive

Historical and superseded material. **Not required** to run or integrate PPIE.

Living documentation lives in [`docs/`](../docs/README.md). This tree keeps old phase diaries and retired assets; git history also preserves deleted notes.

## Layout

| Folder | Contents |
|--------|----------|
| `docs/` | Phase diaries, migration notes, frontend/shop audits, old formula copies |
| `javascript/` | Retired browser scripts |
| `html/` | Unused Jinja orphans |
| `css/` | Reserved for extracted dead CSS |
| `python/` | One-off tools |
| `tests/` | Reserved for obsolete tests |
| `data/` | Legacy/duplicate CSV scratch |
| `legacy-parity/` | Node fixtures + sketches |

## Rules

- Do not import archive code into production paths.
- Prefer deleting obsolete *living* docs after merging into the eight files under `docs/`.
- Permanent deletion of archive assets needs human approval.
