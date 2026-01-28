# palasik/trust/base.py

from abc import ABC, abstractmethod

class TrustEvaluator(ABC):
    """
    Kontrak evaluator kepercayaan device / event.
    """

    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def evaluate(self, event: dict, context) -> float:
        """
        Return trust score (0.0 - 1.0)
        """
        pass
