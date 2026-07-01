# palasik/core/engine.py

from pathlib import Path
from uuid import uuid4
import json

from palasik.core.decision import Decision, DecisionRecord
from palasik.core.registry import PluginRegistry


class PalasikEngine:
    """
    Engine utama PALASIK.
    Enforcement point Zero Trust.
    """

    def __init__(self, context):
        self.context = context
        self.registry = PluginRegistry()
        self.running = False

    def register_plugin(self, plugin):
        self.registry.register(plugin)

    def start(self):
        self.running = True
        for plugin in self.registry.all():
            try:
                plugin.on_start(self.context)
            except Exception as e:
                self.context.logger.error(
                    f"Plugin '{plugin.name()}' failed on_start: {e}"
                )
                continue

    def emit(self, event: dict):
        """
        Enforcement point utama.
        """

        event_id = event.get("event_id", str(uuid4()))
        decision_record: DecisionRecord | None = None

        try:
            trust_score = self.context.trust.evaluate(event, self.context)
            decision_value = self.context.policy.decide(trust_score, event, self.context)
            decision = Decision.from_value(decision_value)

            rationale = self.context.policy.explain(
                trust_score,
                event,
                self.context,
            )
            if not rationale:
                rationale = [f"trust_score={trust_score}"]

            decision_record = DecisionRecord(
                event_id=event_id,
                trust_score=trust_score,
                decision=decision,
                policy_name=getattr(self.context.policy, "name", lambda: "policy")(),
                rationale=list(rationale),
                event_snapshot=self._snapshot_event(event),
            )
            self.context.latest_decision = decision_record
            self.context.latest_event_id = event_id
        except Exception as e:
            # Fail-safe: jika trust/policy error, tolak event
            self.context.logger.error(f"Decision pipeline error: {e} | event={event}")
            return

        decision = self._resolve_decision(event, decision_record)
        if decision_record is not None:
            decision_record.decision = decision

        decision_payload = decision_record.to_dict() if decision_record else {}

        should_forward = decision == Decision.ALLOW

        # 🔐 ENFORCEMENT
        if decision == Decision.ALLOW:
            pass
        elif decision == Decision.MONITOR:
            self.context.logger.info(
                f"Event monitored | decision={decision.value} | event_id={event_id} | trust={trust_score}"
            )
            should_forward = True
        elif decision == Decision.RESTRICT:
            self.context.logger.warning(
                f"Event restricted | decision={decision.value} | event_id={event_id} | trust={trust_score} rationale={rationale}"
            )
        elif decision == Decision.CHALLENGE:
            self.context.logger.warning(
                f"Event challenged | event_id={event_id} | trust={trust_score} rationale={rationale}"
            )
            self.context.logger.info(f"PALASIK_DECISION {decision_payload}")
            self._write_decision_log(decision_record)
            return
        else:
            self.context.logger.info(
                f"Event blocked by policy | "
                f"decision={decision.value} | event_id={event_id} | trust={trust_score} | rationale={rationale}"
            )
            self.context.logger.info(f"PALASIK_DECISION {decision_payload}")
            self._write_decision_log(decision_record)
            return

        # ✅ EVENT LULUS ENFORCEMENT → plugin
        for plugin in self.registry.all():
            try:
                plugin.on_event(event, self.context)
            except Exception as e:
                self.context.logger.error(
                    f"Plugin '{plugin.name()}' failed on event: {e} | event={event}"
                )

        # ✅ EVENT LULUS → HTTP (opsional)
        if should_forward:
            http_adapter = getattr(self.context, "http_adapter", None)
            if http_adapter:
                try:
                    http_adapter.forward(event)
                except Exception as e:
                    self.context.logger.error(f"HTTP adapter forward failed: {e}")

        # Audit trail ringkas
        self.context.logger.info(f"PALASIK_DECISION {decision_payload}")
        self._write_decision_log(decision_record)

    def stop(self):
        for plugin in self.registry.all():
            try:
                plugin.on_stop(self.context)
            except Exception as e:
                self.context.logger.error(
                    f"Plugin '{plugin.name()}' failed on_stop: {e}"
                )
        self.running = False

    def _snapshot_event(self, event):
        """Ringkas event untuk log keputusan riset agar ringan."""
        if not isinstance(event, dict):
            return None

        return {
            "type": event.get("type"),
            "topic": event.get("topic"),
            "value": event.get("value"),
            "source": event.get("source"),
        }

    def _resolve_decision(self, event, decision_record):
        """Resolve challenge decision menjadi final decision."""
        assert decision_record is not None

        decision = decision_record.decision
        if decision != Decision.CHALLENGE:
            return decision

        # Jika ada indikasi challenge terjawab langsung pada event, izinkan/ditolak.
        if event.get("challenge_passed") in (True, "true", "1", 1):
            decision_record.rationale.append("challenge_passed_by_event")
            decision_record.challenge = "passed"
            decision_record.decision = Decision.ALLOW
            return Decision.ALLOW

        handler = getattr(self.context, "challenge_handler", None)
        if callable(handler):
            try:
                allowed = bool(handler(event, self.context, decision_record))
            except Exception as e:
                self.context.logger.error(
                    f"Challenge handler failed for event_id={decision_record.event_id}: {e}"
                )
                allowed = False

            if allowed:
                decision_record.rationale.append("challenge_handler_allowed")
                decision_record.challenge = "passed"
                return Decision.ALLOW

            decision_record.rationale.append("challenge_handler_denied")
            decision_record.challenge = "failed"
            return Decision.DENY

        decision_record.challenge = "pending"
        return Decision.CHALLENGE

    def _write_decision_log(self, decision_record: DecisionRecord | None):
        if decision_record is None:
            return

        path = getattr(self.context, "decision_log", None)
        if not path:
            return

        try:
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            with p.open("a", encoding="utf-8") as f:
                f.write(json.dumps(decision_record.to_dict()) + "\n")
        except Exception as e:
            self.context.logger.error(f"Failed to write decision log: {e}")
