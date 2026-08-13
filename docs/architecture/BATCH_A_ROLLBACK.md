# BATCH_A_ROLLBACK

## Purpose
Restore Omega9.6B Batch A archived scaffolding directories without reconstruction.

## Source archive (authoritative)
- `legacy/archive/omega9.6b/repository/api/`
- `legacy/archive/omega9.6b/repository/frontend/`
- `legacy/archive/omega9.6b/repository/docs/`

## Restore targets
- `repository/api/`
- `repository/frontend/`
- `repository/docs/`

## Procedure
1. Verify target path does not contain newer conflicting files.
2. Move archived directory back to its original target path (same relative structure).
3. Re-run regression suites and `py -3 scripts/validate_warehouse.py`.
4. Confirm restored file hashes against `BATCH_A_ARCHIVE_MANIFEST.csv`.

## No-reconstruction rule
- Do not recreate files from memory.
- Do not regenerate file contents.
- Rollback uses archived bytes only.
