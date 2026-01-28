# plugins/logger/plugin.py

from palasik.core.plugin import PalasikPlugin
from palasik.trust.simple import SimpleTrustEvaluator
from palasik.policy.allow_deny import AllowDenyPolicy

class LoggerPlugin(PalasikPlugin):

    def __init__(self):
        self.trust = SimpleTrustEvaluator()
        self.policy = AllowDenyPolicy(threshold=0.7)

    def name(self):
        return "logger"

    def version(self):
        return "1.1.0"

    def on_start(self, context):
        print("[Logger] PALASIK Agent started")

    def on_event(self, event, context):
        trust_score = self.trust.evaluate(event, context)
        decision = self.policy.decide(trust_score, event, context)

        print(
            f"[Logger] Event={event} | "
            f"Trust={trust_score} | "
            f"Decision={decision}"
        )

    def on_stop(self, context):
        print("[Logger] PALASIK Agent stopped")
