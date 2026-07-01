"""Legacy policy engine shim.

The active policy contract lives in :mod:`palasik.policy`.
This module keeps backward-compatible imports from older demos/scripts by
adapting the old ``decide(trust_score)`` API.
"""

from __future__ import annotations

import os
import warnings

from palasik.policy.allow_deny import AllowDenyPolicy


class PolicyEngine:
    """Compatibility shim for legacy imports ``palasik.core.policy_engine``."""

    class DeprecationError(DeprecationWarning):
        """Raised in strict migration mode when legacy imports are not allowed."""

    @staticmethod
    def _is_strict_mode() -> bool:
        strict = os.getenv("PALASIK_STRICT_DEPRECATION", "0").strip().lower()
        return strict in {"1", "true", "yes", "on"}

    @staticmethod
    def _handle_deprecated_import() -> None:
        message = (
            "palasik.core.policy_engine is deprecated. "
            "Use a policy engine from palasik.policy (for example, "
            "AllowDenyPolicy or RuleBasedPolicy) instead."
        )
        if PolicyEngine._is_strict_mode():
            raise PolicyEngine.DeprecationError(message)

        warnings.warn(message, DeprecationWarning, stacklevel=2)

    _warned = False

    def __init__(self):
        if not self.__class__._warned:
            self.__class__._handle_deprecated_import()
            self.__class__._warned = True

        self._policy = AllowDenyPolicy()

    def decide(self, trust_score):
        # Keep signature compatible with legacy calls that only pass trust_score.
        return self._policy.decide(trust_score, {}, None)
