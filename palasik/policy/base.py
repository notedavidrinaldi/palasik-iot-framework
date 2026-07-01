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
        - ALLOW
        - MONITOR
        - RESTRICT
        - QUARANTINE
        - DENY
        """
        pass

    def explain(self, trust_score: float, event: dict, context) -> list[str]:
        """Opsional: kembalikan daftar alasan keputusan (untuk audit/rationale)."""
        return [f"trust_score={trust_score}"]
