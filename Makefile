.PHONY: test test-strict migration-check

# Fast local check for core behavior
test:
	python3 -m pytest -q

# Strict migration checks used by CI staging
test-strict:
	PALASIK_STRICT_DEPRECATION=1 python3 -m pytest -q -W error::DeprecationWarning

# Migration readiness check: scan legacy imports + strict deprecation test
migration-check:
	python3 scripts/check_legacy_imports.py
	$(MAKE) test-strict
