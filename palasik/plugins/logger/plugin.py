# plugins/logger/plugin.py

from palasik.core.plugin import PalasikPlugin
from palasik.trust.simple import SimpleTrustEvaluator

class LoggerPlugin(PalasikPlugin):

    def __init__(self):
        self.trust = SimpleTrustEvaluator()

    def name(self):
        return "logger"

    def version(self):
        return "1.0.0"

    def on_start(self, context):
        print("[Logger] PALASIK Agent started")

    def on_event(self, event, context):
        trust_score = self.trust.evaluate(event, context)
        print(f"[Logger] Event={event} | Trust={trust_score}")

    def on_stop(self, context):
        print("[Logger] PALASIK Agent stopped")
