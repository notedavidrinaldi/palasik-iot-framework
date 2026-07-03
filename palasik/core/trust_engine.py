"""Legacy trust engine shim.

The active trust contract in PALASIK now lives in :mod:`palasik.trust`.
This module keeps backward-compatible imports from older demos/scripts by
adapting the old device-based ``evaluate(device)`` call into the new
:class:`palasik.trust.base.TrustEvaluator`-style behavior.
"""

from __future__ import annotations

import os
import warnings

from palasik.trust.simple import SimpleTrustEvaluator


class TrustEngine:
    """Compatibility shim for legacy imports ``palasik.core.trust_engine``."""

    _warned = False

    class DeprecationError(DeprecationWarning):
        """Raised in strict migration mode when legacy imports are not allowed."""

    @staticmethod
    def _is_strict_mode() -> bool:
        strict = os.getenv("PALASIK_STRICT_DEPRECATION", "0").strip().lower()
        return strict in {"1", "true", "yes", "on"}

    @staticmethod
    def _handle_deprecated_import() -> None:
        message = (
            "palasik.core.trust_engine is deprecated. "
            "Use palasik.trust.SimpleTrustEvaluator or another implementation of "
            "palasik.trust.base.TrustEvaluator instead."
        )
        if TrustEngine._is_strict_mode():
            raise TrustEngine.DeprecationError(message)

        warnings.warn(message, DeprecationWarning, stacklevel=2)

    def __init__(self):
        if not self.__class__._warned:
            self.__class__._handle_deprecated_import()
            self.__class__._warned = True

        self._evaluator = SimpleTrustEvaluator()

    def evaluate(self, device: dict):
        """Evaluate trust from a legacy device dictionary.

        Legacy callers usually pass a dict with keys like ``ip``, ``value``,
        ``protocol``, etc. The new evaluator expects an event-like payload,
        so we adapt the shape here.
        """

        if not isinstance(device, dict):
            return {
                "ip": None,
                "trust_score": self._evaluator.evaluate({}, None),
                "protocol": "UNKNOWN",
            }

        event = {
            "ip": device.get("ip"),
            "source": device.get("ip") or device.get("source"),
            "value": device.get("value", 0),
            "protocol": device.get("protocol", "UNKNOWN"),
        }

        return {
            "ip": device.get("ip"),
            "protocol": device.get("protocol", "UNKNOWN"),
            "trust_score": round(float(self._evaluator.evaluate(event, None)), 2),
        }
