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

    def reason_code(self, trust_score: float, event: dict, context) -> str | None:
        """Opsional: kode alasan keputusan untuk audit."""
        return None

    def matched_rules(self):
        """Opsional: daftar rule id/rule name yang match."""
        return []

    def matched_actions(self):
        """Opsional: daftar action spesifik rule yang match."""
        return []
