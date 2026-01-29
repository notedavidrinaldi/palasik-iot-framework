# Changelog

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
