# Changelog

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
