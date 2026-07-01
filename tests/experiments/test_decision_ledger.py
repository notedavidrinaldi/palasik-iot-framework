import json
from pathlib import Path
import importlib.util

REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER_PATH = REPO_ROOT / "experiments" / "decision_ledger.py"

spec = importlib.util.spec_from_file_location("palasik_decision_ledger", LEDGER_PATH)
assert spec and spec.loader
decision_ledger = importlib.util.module_from_spec(spec)
spec.loader.exec_module(decision_ledger)


def test_summarize_records_accepts_jsonl_records(tmp_path: Path):
    ledger = tmp_path / "ledger.jsonl"
    records = [
        {
            "event_id": "1",
            "trust_score": 0.1,
            "decision": "DENY",
            "policy_name": "allow_deny_policy",
            "rationale": ["low trust"],
            "challenge": None,
            "created_at_utc": "2026-01-01T00:00:00+00:00",
        },
        {
            "event_id": "2",
            "trust_score": 0.9,
            "decision": "ALLOW",
            "policy_name": "rule_policy",
            "rationale": ["ok"],
            "challenge": None,
            "created_at_utc": "2026-01-01T00:00:01+00:00",
        },
        {
            "event_id": "3",
            "trust_score": 0.4,
            "decision": "CHALLENGE",
            "policy_name": "rule_policy",
            "rationale": ["needs challenge"],
            "challenge": "pending",
            "created_at_utc": "2026-01-01T00:00:02+00:00",
        },
    ]
    ledger.write_text(
        "\n".join(json.dumps(r) for r in records),
        encoding="utf-8",
    )

    result = decision_ledger.summarize_records(decision_ledger.iter_records(ledger))

    assert result["total_events"] == 3
    assert result["decision_counts"]["ALLOW"] == 1
    assert result["challenge_counts"]["pending"] == 1
    assert result["decision_counts"]["DENY"] == 1
