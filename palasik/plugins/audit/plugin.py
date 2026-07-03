import json
from pathlib import Path

from palasik.core.plugin import PalasikPlugin


class AuditPlugin(PalasikPlugin):
    def name(self):
        return "audit"

    def version(self):
        return "0.1.0"

    def on_start(self, context):
        pass

    def on_event(self, event, context):
        decision = getattr(context, "latest_decision", None)
        if decision is None:
            return

        path = getattr(context, "audit_log", None)
        if path is None:
            path = context.config.get("palasik", "audit_log", default=None)
        if path is None:
            return

        try:
            payload_path = Path(path)
            payload_path.parent.mkdir(parents=True, exist_ok=True)
            with payload_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(decision.to_dict()) + "\n")
        except Exception:
            # Non-blocking: observability harus tidak mengganggu enforcement.
            return

    def on_stop(self, context):
        pass
