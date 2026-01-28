from palasik.policy.allow_deny import AllowDenyPolicy
from palasik.trust.simple import SimpleTrustEvaluator
from palasik.core.logger import Logger


class PalasikContext:
    """
    Context global PALASIK.
    Menyimpan state bersama: config, trust, policy, logger, adapter.
    """

    def __init__(self, config=None):
        self.config = config

        # Logger default
        self.logger = Logger()

        # ✅ Trust engine default (IMPLEMENTASI NYATA)
        self.trust = SimpleTrustEvaluator()

        # Policy engine default (configurable)
        threshold = 0.5
        if config:
            threshold = config.get("palasik", "policy", "threshold", default=0.5)

        self.policy = AllowDenyPolicy(threshold=threshold)

        # Adapter opsional
        self.http_adapter = None
