# palasik/policy/base.py

from abc import ABC, abstractmethod

class PolicyEngine(ABC):
    """
    Kontrak policy engine PALASIK.
    """

    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def decide(self, trust_score: float, event: dict, context) -> str:
        """
        Return decision:
        - 'ALLOW'
        - 'DENY'
        """
        pass
