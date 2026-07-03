# Changelog

## Unreleased

### Improved
- Align release metadata for v0.2.0 across package modules (`palasik`, `demit`) and packaging config.
- Add explicit development dependency lock file (`requirements-dev.txt`) and testing instructions.
- Standardize local test command using `python -m pytest`.

### Refactor
- Convert legacy core trust/policy engines (`palasik.core.trust_engine`,
  `palasik.core.policy_engine`) into compatibility shims that delegate to the
  active architecture in `palasik.trust` and `palasik.policy`.
- Add optional migration guard via `PALASIK_STRICT_DEPRECATION` so these shims can
  be escalated to deprecation failures during the next migration phase.
- Update `palasik/main.py` demo pipeline to use the canonical trust/policy API
  directly, avoiding legacy module paths in sample runtime flow.
- Enable strict deprecation mode automatically on CI `staging` branch by setting
  `PALASIK_STRICT_DEPRECATION=1` in GitHub Actions, making legacy imports fail
  fast during migration rehearsals.
- Split workflows into `ci.yml` (normal) and `ci-staging.yml` (strict).
  The staging workflow runs with `-W error::DeprecationWarning`, so legacy
  shims become hard failures before deployment.
- Add automatic legacy-import scan script and staging CI step for quick-check
  (`scripts/check_legacy_imports.py` + `ci-staging` scan step) to verify
  migration readiness.
- Add staging migration gate job (`migration-gate`) and helper script
  (`scripts/apply_staging_branch_protection.sh`) so repository can enforce
  migration readiness as a single required branch-protection check.
- Add explicit contributor and docs workflow for migration readiness:
  `CONTRIBUTING.md` references `make migration-check`; `docs/MIGRATION_GATE.md`
  documents the required criteria and decommission plan for `ci-staging.yml`.
- Add PR checklist template in
  `.github/PULL_REQUEST_TEMPLATE/pull_request_template.md` to enforce
  `make migration-check` and strict deprecation validation in PR process.
- Add branch protection audit helper script
  (`scripts/check_staging_gate.sh`) to verify `migration-gate` is set as a
  required status check on `staging`.

## v0.2.0

### Added
- Introduce DEMIT super-app foundation with runtime, app contract, CLI, and sample config
- Add PALASIK as the first DEMIT application
- Add adaptive zero-trust decisions: `MONITOR`, `RESTRICT`, `CHALLENGE`, `DENY`, `ALLOW`
- Add rule-based policy engine
- Add decision ledger output in JSONL format for audit and research
- Add decision ledger analyzer for experiment summaries
- Add runtime and policy test coverage for DEMIT and PALASIK decision flow

### Improved
- Improve plugin loading reliability and compatibility
- Improve MQTT adapter event dispatch
- Improve CLI runtime stability
- Improve project documentation to reflect DEMIT + PALASIK direction

### Notes
- This release marks the transition from PALASIK as a standalone framework toward PALASIK as App 1 inside the DEMIT ecosystem.

## v0.1.0 — Initial Product Release

### Added
- Core PALASIK engine with Zero Trust enforcement
- Trust evaluation using SimpleTrustEvaluator
- Allow/Deny policy engine
- Plugin system with registry & loader
- HTTP adapter (optional forwarding)
- CLI: `palasik init`, `palasik run`
- YAML-based configuration
- Pytest-based test suite
- PEP 621 packaging with console entrypoint

### Notes
- This release establishes PALASIK as a production-ready framework,
  not an experimental prototype.


## v0.1.1
### Fixed
- Fix YAML config with null values causing runtime crash
- Ensure config normalization before ENV override
- Fix MQTT example to use absolute config path

### Improved
- CLI reliability for real-world usage

## v0.1.2
### Fixed
- Fix circular import when accessing palasik.__version__
- Properly expose package version at top-level namespace

## v0.1.3
### Fixed
- Fix circular import when accessing palasik.__version__
- Stabilize version export for PyPI installation
