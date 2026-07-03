from palasik.policy.allow_deny import AllowDenyPolicy
from palasik.policy.rules import RuleBasedPolicy
from palasik.trust.simple import SimpleTrustEvaluator
from palasik.core.audit import AuditService
from palasik.core.logger import Logger
from palasik.core.metrics import RuntimeMetrics


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

        # Audit trail (opsional, plugin-level)
        self.audit_log = None
        if config:
            self.audit_log = config.get("palasik", "audit_log", default=None)

        # Observability defaults
        self.metrics = RuntimeMetrics()
        self.metrics_file = None
        self.metrics_alerts = None
        if config:
            observability = config.get("palasik", "observability", default={}) or {}
            if isinstance(observability, dict):
                self.metrics_file = observability.get("metrics_file")
                self.metrics_alerts = observability.get("alert")

            try:
                self.metrics, persisted_path = RuntimeMetrics.from_file(self.metrics_file)
                if persisted_path:
                    self.metrics_file = persisted_path
            except Exception:
                self.metrics = RuntimeMetrics()

        # Challenge handler (opsional)
        # Jika diset, function menerima (event, context, decision_record) dan mengembalikan bool.
        self.challenge_handler = None

        # Adapter opsional
        self.http_adapter = None
        self.action_dispatcher = None
        self.audit_service = AuditService(self.audit_log)
