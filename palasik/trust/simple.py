# palasik/trust/simple.py

from palasik.trust.base import TrustEvaluator

class SimpleTrustEvaluator(TrustEvaluator):
    def name(self):
        return "simple_trust"

    def evaluate(self, event: dict, context) -> float:
        """
        Contoh sederhana:
        - sensor value <= 100 → trusted
        - sisanya → low trust
        """
        value = event.get("value", 0)

        if value <= 100:
            return 0.9
        return 0.2
