"""Canonical PPIE algorithm version.

Bump when behavior changes intentionally. After a bump:
1. Update docs/CHANGELOG.md (and docs/FORMULAS.md if formula behavior changed)
2. Run `py -3 tools/parity_suite.py --freeze`
3. Commit new tests/golden/*.json fixtures
"""

ALGORITHM_VERSION = "2.1.0"
ENGINE_NAME = "PPIE"
RUNTIME = "python"
