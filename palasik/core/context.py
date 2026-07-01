from palasik.policy.allow_deny import AllowDenyPolicy
from palasik.policy.rules import RuleBasedPolicy
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

        # Metadata keputusan terakhir (untuk audit + observability)
        self.latest_decision = None
        self.latest_event_id = None

        # ✅ Trust engine default (IMPLEMENTASI NYATA)
        self.trust = SimpleTrustEvaluator()

        # Policy engine default (configurable)
        policy_cfg = {}
        if config:
            policy_cfg = config.get("palasik", "policy", default={}) or {}

        policy_type = str(policy_cfg.get("type", "allow_deny")).lower()
        if policy_type == "rule":
            self.policy = RuleBasedPolicy(policy_cfg)
        else:
            threshold = 0.5
            if config:
                threshold = config.get("palasik", "policy", "threshold", default=0.5)
            self.policy = AllowDenyPolicy(threshold=threshold)

        # Logging keputusan (opsional)
        self.decision_log = None
        if config:
            self.decision_log = config.get("palasik", "decision_log", default=None)

        # Challenge handler (opsional)
        # Jika diset, function menerima (event, context, decision_record) dan mengembalikan bool.
        self.challenge_handler = None

        # Adapter opsional
        self.http_adapter = None
