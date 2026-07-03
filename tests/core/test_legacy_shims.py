import warnings

import pytest

from palasik.core import trust_engine as trust_compat
from palasik.core import policy_engine as policy_compat


def test_legacy_trust_engine_warns_by_default(monkeypatch):
    monkeypatch.setenv("PALASIK_STRICT_DEPRECATION", "0")

    trust_compat.TrustEngine._warned = False

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        trust = trust_compat.TrustEngine()

    result = trust.evaluate({"ip": "10.0.0.1", "value": 90, "protocol": "MQTT"})
    assert result["ip"] == "10.0.0.1"
    assert result["protocol"] == "MQTT"


def test_legacy_policy_engine_warns_by_default(monkeypatch):
    monkeypatch.setenv("PALASIK_STRICT_DEPRECATION", "0")

    policy_compat.PolicyEngine._warned = False

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        policy = policy_compat.PolicyEngine()

    assert policy.decide(0.9) == "ALLOW"
    assert policy.decide(0.2) == "DENY"


def test_strict_deprecation_mode_raises_from_trust_engine(monkeypatch):
    monkeypatch.setenv("PALASIK_STRICT_DEPRECATION", "1")

    with pytest.raises(trust_compat.TrustEngine.DeprecationError):
        trust_compat.TrustEngine._handle_deprecated_import()


def test_strict_deprecation_mode_raises_from_policy_engine(monkeypatch):
    monkeypatch.setenv("PALASIK_STRICT_DEPRECATION", "1")

    with pytest.raises(policy_compat.PolicyEngine.DeprecationError):
        policy_compat.PolicyEngine._handle_deprecated_import()


# Optional helper untuk debugging lokal saat migrate.
def test_env_helpers_work(monkeypatch):
    monkeypatch.setenv("PALASIK_STRICT_DEPRECATION", "true")
    assert trust_compat.TrustEngine._is_strict_mode()
    assert policy_compat.PolicyEngine._is_strict_mode()

    monkeypatch.setenv("PALASIK_STRICT_DEPRECATION", "0")
    assert not trust_compat.TrustEngine._is_strict_mode()
    assert not policy_compat.PolicyEngine._is_strict_mode()
