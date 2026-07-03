.PHONY: test test-strict migration-check policy-lint policy-deploy-check edge-smoke edge-health edge-health-wait edge-health-strict edge-post-restart-check edge-post-restart-check-strict systemd-bundle

POLICY_CONFIG ?= examples/mqtt_zero_trust_gateway/config.yaml
PALASIK_HOST ?= 127.0.0.1
PALASIK_PORT ?= 8080

POLICY_SMOKE_EVENTS ?= docs/samples/policy-smoke-events.json

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
	$(MAKE) policy-lint
	$(MAKE) policy-deploy-check

policy-lint:
	python3 -m palasik.cli.main validate-policy --config examples/mqtt_zero_trust_gateway/config.yaml
	python3 -m palasik.cli.main validate-policy --policy docs/samples/policy-baseline.yaml

policy-deploy-check:
	python3 -m palasik.cli.main policy-deploy-check \
		--config $(POLICY_CONFIG) \
		--smoke-events $(POLICY_SMOKE_EVENTS) \
		--max-deny-ratio 0.95 \
		--require-allow

edge-smoke:
	bash scripts/smoke_serve_api.sh $(POLICY_CONFIG)

edge-health:
	bash scripts/check_health_alerts.sh

edge-health-wait:
	PALASIK_HEALTH_RETRIES=30 PALASIK_HEALTH_RETRY_SLEEP=1 bash scripts/check_health_alerts.sh

edge-health-strict:
	PALASIK_HEALTH_STRICT_UP_ONLY=1 bash scripts/check_health_alerts.sh

edge-post-restart-check:
	python3 -m palasik.cli.main check-startup --config $(POLICY_CONFIG) --host $(PALASIK_HOST) --port $(PALASIK_PORT) --allow-relative-paths
	PALASIK_HOST=$(PALASIK_HOST) PALASIK_PORT=$(PALASIK_PORT) $(MAKE) edge-health-wait

edge-post-restart-check-strict:
	python3 -m palasik.cli.main check-startup --config $(POLICY_CONFIG) --host $(PALASIK_HOST) --port $(PALASIK_PORT) --allow-relative-paths
	PALASIK_HOST=$(PALASIK_HOST) PALASIK_PORT=$(PALASIK_PORT) $(MAKE) edge-health-strict

systemd-bundle:
	python3 -m palasik.cli.main install-systemd \
		--config-source $(POLICY_CONFIG)
