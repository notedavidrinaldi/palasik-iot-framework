import json

from palasik.core.plugin import PalasikPlugin


class LoggerPlugin(PalasikPlugin):

    def name(self):
        return "logger"

    def version(self):
        return "1.2.0"

    def on_start(self, context):
        print(
            json.dumps(
                {
                    "source": "palasik.logger",
                    "message": "agent_started",
                },
                sort_keys=True,
            )
        )

    def on_event(self, event, context):
        decision = getattr(context, "latest_decision", None)
        if decision is None:
            print(
                json.dumps(
                    {
                        "source": "palasik.logger",
                        "event": event,
                        "message": "decision-unavailable",
                    },
                    default=str,
                    sort_keys=True,
                )
            )
            return

        print(
            json.dumps(
                {
                    "source": "palasik.logger",
                    "event_id": decision.event_id,
                    "decision": decision.decision.value,
                    "policy_name": decision.policy_name,
                    "trust_score": decision.trust_score,
                    "reason_code": decision.reason_code,
                    "event": event,
                    "message": "event_decision",
                },
                sort_keys=True,
                default=str,
            )
        )

    def on_stop(self, context):
        print(
            json.dumps(
                {
                    "source": "palasik.logger",
                    "message": "agent_stopped",
                },
                sort_keys=True,
            )
        )
