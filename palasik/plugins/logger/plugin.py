# plugins/logger/plugin.py

from palasik.core.plugin import PalasikPlugin


class LoggerPlugin(PalasikPlugin):

    def name(self):
        return "logger"

    def version(self):
        return "1.2.0"

    def on_start(self, context):
        print("[Logger] PALASIK Agent started")

    def on_event(self, event, context):
        decision = getattr(context, "latest_decision", None)
        if decision is None:
            print(f"[Logger] Event={event}")
            return

        print(
            f"[Logger] Event={event} | "
            f"Decision={decision.decision.value} | "
            f"Policy={decision.policy_name} | "
            f"Trust={decision.trust_score}"
        )

    def on_stop(self, context):
        print("[Logger] PALASIK Agent stopped")
