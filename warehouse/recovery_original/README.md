# recovery_original — read-only intern preservation

Do not edit files in this directory. They are forensic copies.

- intern_a122a83/ — intern CSVs extracted from git commit a122a83
- snapshot_d6384a0/ — warehouse snapshot extracted from git commit d6384a0
- canonical_before_recovery/ — canonical warehouse folders copied before append-only recovery
- *.zip — git archive blobs used for the extract
- RECOVERY_MAPPING.csv — source_legacy_file / source_legacy_row for every recovered row

Originals in git were not modified. Canonical warehouse files outside this folder
were only appended when empty or when intern rows were absent.
