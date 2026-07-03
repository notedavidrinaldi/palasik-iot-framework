# palasik/core/engine.py

from pathlib import Path
from time import perf_counter
from uuid import uuid4
import json
from palasik.core.correlation import CorrelationEngine, CorrelationResult
from palasik.core.decision import Decision, DecisionRecord
from palasik.core.event_contract import normalize_event
from palasik.core.risk import RiskEngine, RiskPolicyConfig
from palasik.core.registry import PluginRegistry


class PalasikEngine:
    """
    Engine utama PALASIK.
    Zero-Trust event processing pipeline:
      ingest -> validate -> trust -> policy -> risk -> correlation -> keputusan -> aksi/audit.
    """

    def __init__(self, context):
        self.context = context
        self.registry = PluginRegistry()
        self.running = False
        self.risk_engine = RiskEngine(self._load_risk_config())
        self.correlation = CorrelationEngine(**self._load_correlation_config())

    def register_plugin(self, plugin):
        self.registry.register(plugin)

    def _plugin_name(self, plugin):
        """Resolve a safe plugin name for logs and registry key lookup."""
        name = getattr(plugin, "name", None)
        if callable(name):
            return name()

        return plugin.__class__.__name__

    def start(self):
        self.running = True
        for plugin in self.registry.all():
            try:
                plugin.on_start(self.context)
            except Exception as e:
                self.context.logger.error(
                    f"Plugin '{self._plugin_name(plugin)}' failed on_start: {e}"
                )
                continue

    def emit(self, event: dict):
        """
        Enforcement point utama.
        """

        if event is None:
            event = {}

        if not isinstance(event, dict):
            event = {"raw": event}

        normalized_event, issues = normalize_event(event, default_version="1", max_age_seconds=self._max_event_age())
        event_id = normalized_event.get("event_id", str(uuid4()))
        normalized_event["event_id"] = event_id
        trace_id = str(uuid4())
        latency_ms = 0.0

        decision = Decision.DENY
        trust_score = 0.0
        rationale = []
        reason_code = None
        matched_rules = []
        actions = []
        correlation_result = CorrelationResult(False)
        risk_label = "UNKNOWN"
        risk_score = None

        self.context.latest_event_id = event_id

        try:
            t0 = perf_counter()

            # Fail fast: event tidak valid -> route deny + audit.
            if issues:
                trust_score = 0.0
                decision = Decision.DENY
                rationale = [f"event_contract={issue}" for issue in issues]
                reason_code = "INVALID_SCHEMA"
            else:
                trust_score = self.context.trust.evaluate(normalized_event, self.context)

                raw_decision = self.context.policy.decide(
                    trust_score,
                    normalized_event,
                    self.context,
                )
                decision = Decision.from_value(raw_decision)

                rationale = self.context.policy.explain(
                    trust_score,
                    normalized_event,
                    self.context,
                )
                if not rationale:
                    rationale = [f"trust_score={trust_score}"]

                reason_fn = getattr(self.context.policy, "reason_code", None)
                if callable(reason_fn):
                    reason_code = reason_fn(trust_score, normalized_event, self.context)

                matched_rules = self._policy_matched_rules(self.context.policy)
                actions = self._policy_matched_actions(self.context.policy)

                risk_score, risk_details = self.risk_engine.score(
                    trust_score,
                    normalized_event,
                    decision,
                )

                risk_label = self.risk_engine.label(risk_score)
                normalized_event["risk_reasoning"] = risk_details

                # Korelasi event (simple burst detector)
                correlation_result = self.correlation.evaluate(normalized_event, risk_score)
                if correlation_result.is_correlated:
                    rationale.append(f"correlation_hit=count={correlation_result.window_count}")
                    risk_score = min(100, risk_score + 10)
                    risk_label = self.risk_engine.label(risk_score)
                    # naikkan keputusan bila korelasi kuat
                    actions.extend(["notify_telegram", "create_ticket"])

                resolved = self.risk_engine.escalate(decision, risk_score)
                rationale.append(f"policy_decision={decision.value}")
                rationale.append(f"risk_score={risk_score}")
                rationale.append(f"risk_label={risk_label}")
                rationale.extend(risk_details)

                decision = Decision.from_value(resolved)

            latency_ms = (perf_counter() - t0) * 1000
        except Exception as e:
            # Fail-safe: jika trust/policy error, tolak event
            self.context.logger.error(f"Decision pipeline error: {e} | event={normalized_event}")
            decision = Decision.DENY
            reason_code = reason_code or "PIPELINE_ERROR"
            rationale = [f"pipeline_error={e}"]

        if decision is Decision.CHALLENGE:
            decision = self._resolve_challenge(event=normalized_event, decision_record=None, rationale=rationale)

        decision_record = DecisionRecord(
            event_id=event_id,
            trust_score=trust_score,
            decision=decision,
            policy_name=getattr(self.context.policy, "name", lambda: "policy")(),
            risk_score=risk_score,
            risk_label=risk_label,
            rationale=list(rationale),
            reason_code=reason_code,
            event_snapshot=self._snapshot_event(normalized_event),
            matched_rules=matched_rules or None,
            actions=actions or None,
            trace_id=trace_id,
            correlation_id=correlation_result.correlation_id if correlation_result else None,
        )

        self.context.latest_decision = decision_record

        if decision_record is not None:
            self.context.metrics.record(
                decision_record.decision.value,
                decision_record.reason_code,
                latency_ms,
                decision_record.trust_score,
                correlated=correlation_result.is_correlated,
            )
            self.context.metrics.dump_to_file(getattr(self.context, "metrics_file", None))
            audit_service = getattr(self.context, "audit_service", None)
            if audit_service is not None:
                audit_service.write_decision(decision_record)

        decision_payload = decision_record.to_dict() if decision_record else {}

        should_forward = decision in {Decision.ALLOW, Decision.MONITOR, Decision.RESTRICT, Decision.WARN}

        # 🔐 ENFORCEMENT
        if decision == Decision.ALLOW:
            pass
        elif decision == Decision.MONITOR:
            self.context.logger.info(
                f"Event monitored | decision={decision.value} | event_id={event_id} | trust={trust_score}"
            )
        elif decision == Decision.RESTRICT:
            self.context.logger.warning(
                f"Event restricted | decision={decision.value} | event_id={event_id} | trust={trust_score} rationale={rationale}"
            )
        elif decision == Decision.WARN:
            self.context.logger.warning(
                f"Event warn | decision={decision.value} | event_id={event_id} | trust={trust_score} rationale={rationale}"
            )
        elif decision in {Decision.QUARANTINE, Decision.BLOCK_ALARM, Decision.DENY}:
            self.context.logger.info(
                f"Event blocked by policy | "
                f"decision={decision.value} | event_id={event_id} | trust={trust_score} | rationale={rationale}"
            )
            if decision == Decision.BLOCK_ALARM:
                self.context.logger.warning(f"Event blocked + alarm | event_id={event_id}")
            self.context.logger.info(f"PALASIK_DECISION {decision_payload}")
            self._dispatch_actions(
                actions or ["create_ticket", "notify_telegram", "notify_whatsapp"],
                normalized_event,
                decision_record,
                trace_id,
            )
            self._write_decision_log(decision_record)
            return
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
                plugin.on_event(normalized_event, self.context)
            except Exception as e:
                self.context.logger.error(
                    f"Plugin '{self._plugin_name(plugin)}' failed on event: {e} | event={normalized_event}"
                )

        # ✅ ACTIONS
        self._dispatch_actions(actions, normalized_event, decision_record, trace_id)

        # ✅ EVENT LULUS → HTTP (opsional)
        if should_forward:
            http_adapter = getattr(self.context, "http_adapter", None)
            if http_adapter:
                try:
                    http_adapter.forward(normalized_event)
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
                    f"Plugin '{self._plugin_name(plugin)}' failed on_stop: {e}"
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

    def _policy_matched_rules(self, policy):
        rule = getattr(policy, "last_match", None)
        if callable(rule):
            matched = rule()
            if matched is None:
                return []

            rid = matched.get("id")
            name = matched.get("name")
            if isinstance(rid, str) and rid:
                return [rid]
            if isinstance(name, str) and name:
                return [name]
        return []

    def _policy_matched_actions(self, policy):
        actions_fn = getattr(policy, "last_matched_actions", None)
        if callable(actions_fn):
            actions = actions_fn()
            if isinstance(actions, list):
                return [str(a) for a in actions if str(a).strip()]

        return []

    def _load_risk_config(self):
        cfg = {}
        if self.context and self.context.config:
            cfg = self.context.config.get("palasik", "risk", default={}) or {}

        if not isinstance(cfg, dict):
            cfg = {}

        return self._risk_config_from_dict(cfg)

    def _risk_config_from_dict(self, cfg: dict):
        from palasik.core.risk import RiskPolicyConfig

        return RiskPolicyConfig(
            warn_threshold=int(cfg.get("warn_threshold", 55)),
            quarantine_threshold=int(cfg.get("quarantine_threshold", 75)),
            critical_threshold=int(cfg.get("critical_threshold", 92)),
            critical_action=str(cfg.get("critical_action", "BLOCK_ALARM")),
        )

    def _load_correlation_config(self):
        cfg = {}
        if self.context and self.context.config:
            cfg = self.context.config.get("palasik", "correlation", default={}) or {}
        if not isinstance(cfg, dict):
            cfg = {}

        return {
            "window_seconds": int(cfg.get("window_seconds", 120)),
            "repeat_threshold": int(cfg.get("repeat_threshold", 3)),
            "risk_threshold": int(cfg.get("risk_threshold", 75)),
        }

    def _max_event_age(self) -> int:
        cfg = self.context.config.get("palasik", "event", default={}) if self.context and self.context.config else {}
        if not isinstance(cfg, dict):
            return 600
        return int(cfg.get("max_age_seconds", 600))

    def _resolve_challenge(self, event, decision_record, rationale):
        """Resolve challenge decision menjadi final decision."""
        if event.get("challenge_passed") in (True, "true", "1", 1):
            rationale.append("challenge_passed_by_event")
            return Decision.ALLOW

        handler = getattr(self.context, "challenge_handler", None)
        if callable(handler):
            try:
                allowed = bool(handler(event, self.context, decision_record))
            except Exception as e:
                self.context.logger.error(
                    f"Challenge handler failed for event_id={event.get('event_id')}: {e}"
                )
                allowed = False

            if allowed:
                rationale.append("challenge_handler_allowed")
                return Decision.ALLOW

            rationale.append("challenge_handler_denied")
            return Decision.DENY

        return Decision.CHALLENGE

    def _dispatch_actions(self, actions: list[str], event: dict, decision_record=None, trace_id: str | None = None):
        if not actions:
            return

        dispatcher = getattr(self.context, "action_dispatcher", None)
        if dispatcher is None:
            return

        dispatcher.dispatch_actions(
            actions,
            event,
            decision_record=decision_record,
            trace_id=trace_id,
        )

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
