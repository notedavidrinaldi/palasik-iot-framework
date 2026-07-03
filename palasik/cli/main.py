import argparse
import hashlib
import json
import os
import shutil
import socket
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from uuid import uuid4
import threading

import yaml

from palasik.api.server import create_server
from palasik.core.agent import PalasikAgent
from palasik.core.decision import Decision
from palasik.core.service_helpers import build_status_payload, normalize_event_payload

ALLOWED_ACTIONS = {"ALLOW", "MONITOR", "RESTRICT", "CHALLENGE", "QUARANTINE", "DENY", "BLOCK_ALARM"}
ALLOWED_ACTIONS_TEXT = ", ".join(sorted(ALLOWED_ACTIONS))
DEFAULT_SNAPSHOT_DIR = "runs/policy_snapshots"
DEFAULT_DEPLOY_SMOKE_EVENTS = Path("docs/samples/policy-smoke-events.json")
DEFAULT_MAX_DENY_RATIO = 0.95
DEFAULT_SYSTEMD_SERVICE_NAME = "palasik"
DEFAULT_EDGE_INSTALL_ROOT = "/opt/palasik"
DEFAULT_EDGE_ETC_DIR = "/etc/palasik"
DEFAULT_EDGE_STATE_DIR = "/var/lib/palasik/runs"
DEFAULT_EDGE_LOG_DIR = "/var/log/palasik"
DEFAULT_SYSTEMD_OUTPUT_DIR = "deploy/systemd/rendered"
DEFAULT_ENV_TEMPLATE = Path("deploy/systemd/palasik.env.example")
ALLOWED_CONDITION_OPS = {
    "eq",
    "ne",
    "gt",
    "gte",
    "lt",
    "lte",
    "in",
    "nin",
    "contains",
    "exists",
}


def _render_systemd_service(
    *,
    service_name: str,
    install_root: str,
    etc_dir: str,
    log_dir: str,
    user: str,
    group: str,
    host: str,
    port: int,
) -> str:
    return f"""[Unit]
Description=PALASIK Edge Runtime
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User={user}
Group={group}
WorkingDirectory={install_root}
EnvironmentFile={etc_dir}/{service_name}.env
ExecStartPre={install_root}/.venv/bin/python -m palasik.cli.main check-startup --config {etc_dir}/config.yaml --host {host} --port {port}
ExecStart={install_root}/.venv/bin/python -m palasik.cli.main serve-api --config {etc_dir}/config.yaml --host {host} --port {port}
Restart=always
RestartSec=5
TimeoutStartSec=30
TimeoutStopSec=20
StandardOutput=append:{log_dir}/{service_name}.log
StandardError=append:{log_dir}/{service_name}.log

[Install]
WantedBy=multi-user.target
"""


def _render_install_script(
    *,
    service_name: str,
    install_root: str,
    etc_dir: str,
    state_dir: str,
    log_dir: str,
    user: str,
    group: str,
    config_source: str,
    env_source: str,
    service_source: str,
) -> str:
    return f"""#!/usr/bin/env bash
set -euo pipefail

SERVICE_NAME="{service_name}"
INSTALL_ROOT="{install_root}"
ETC_DIR="{etc_dir}"
STATE_DIR="{state_dir}"
LOG_DIR="{log_dir}"
SERVICE_USER="{user}"
SERVICE_GROUP="{group}"
CONFIG_SOURCE="{config_source}"
ENV_SOURCE="{env_source}"
SERVICE_SOURCE="{service_source}"

if [[ "$(id -u)" -ne 0 ]]; then
  echo "Script ini harus dijalankan sebagai root (sudo)." >&2
  exit 1
fi

if ! id -u "$SERVICE_USER" >/dev/null 2>&1; then
  useradd --system --home "$INSTALL_ROOT" --shell /usr/sbin/nologin "$SERVICE_USER"
fi

mkdir -p "$INSTALL_ROOT" "$ETC_DIR" "$STATE_DIR" "$LOG_DIR"
chown -R "$SERVICE_USER:$SERVICE_GROUP" "$INSTALL_ROOT" "$STATE_DIR" "$LOG_DIR"

cp "$CONFIG_SOURCE" "$ETC_DIR/config.yaml"
cp "$ENV_SOURCE" "$ETC_DIR/$SERVICE_NAME.env"
cp "$SERVICE_SOURCE" "/etc/systemd/system/$SERVICE_NAME.service"

chmod 640 "$ETC_DIR/config.yaml" "$ETC_DIR/$SERVICE_NAME.env"
systemctl daemon-reload
systemctl enable "$SERVICE_NAME.service"

echo "Bundle systemd terpasang."
echo "Lanjutkan dengan:"
echo "  python3 -m palasik.cli.main check-startup --config $ETC_DIR/config.yaml --host 0.0.0.0 --port 8080"
echo "  systemctl start $SERVICE_NAME.service"
echo "  systemctl status $SERVICE_NAME.service"
"""


def _load_file(path: str):
    target = Path(path)
    if not target.exists():
        raise FileNotFoundError(f"File not found: {path}")

    with target.open("r", encoding="utf-8") as f:
        payload = yaml.safe_load(f)

    if payload is None:
        return {}

    return payload


def _load_config_file(path: str):
    target = Path(path)
    if not target.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    return target


def _validate_runtime_path(
    *,
    label: str,
    raw_path: str | None,
    issues: list[str],
    require_absolute: bool = True,
    require_writable: bool = True,
):
    if not raw_path:
        issues.append(f"{label} belum dikonfigurasi")
        return

    target = Path(raw_path)
    if require_absolute and not target.is_absolute():
        issues.append(f"{label} harus absolute path untuk mode service: {target}")
        return

    probe = target if target.exists() else target.parent
    probe = probe.resolve(strict=False)
    while not probe.exists() and probe != probe.parent:
        probe = probe.parent

    if require_writable and not os.access(probe, os.W_OK):
        issues.append(f"{label} tidak writable: {target}")


def _validate_bind_target(*, host: str, port: int, issues: list[str]):
    normalized_host = str(host).strip()
    if not normalized_host:
        issues.append("host tidak boleh kosong")
        return

    try:
        candidates = socket.getaddrinfo(
            normalized_host,
            int(port),
            type=socket.SOCK_STREAM,
            flags=socket.AI_PASSIVE,
        )
    except socket.gaierror as exc:
        issues.append(f"host tidak valid atau tidak bisa di-resolve: {normalized_host} ({exc})")
        return

    bind_errors = []
    for family, socktype, proto, _, sockaddr in candidates:
        probe = socket.socket(family, socktype, proto)
        try:
            probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            probe.bind(sockaddr)
            return
        except OSError as exc:
            bind_errors.append(str(exc))
        finally:
            probe.close()

    if bind_errors:
        issues.append(
            f"bind host/port tidak tersedia: {normalized_host}:{port} ({'; '.join(sorted(set(bind_errors)))})"
        )


def _validate_adapter_endpoint(*, label: str, endpoint: str | None, issues: list[str]):
    if not endpoint or not str(endpoint).strip():
        issues.append(f"{label}.endpoint wajib diisi")
        return

    parsed = urlparse(str(endpoint))
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        issues.append(f"{label}.endpoint tidak valid: {endpoint}")


def _validate_active_adapter_config(*, agent: PalasikAgent, issues: list[str]):
    actions_cfg = agent.config.get("palasik", "actions", default={}) or {}

    webhook_cfg = actions_cfg.get("webhook", {}) or {}
    if "webhook" in agent.context.action_dispatcher.adapters:
        _validate_adapter_endpoint(label="palasik.actions.webhook", endpoint=webhook_cfg.get("endpoint"), issues=issues)

    whatsapp_cfg = actions_cfg.get("whatsapp", {}) or {}
    if "whatsapp" in agent.context.action_dispatcher.adapters:
        _validate_adapter_endpoint(label="palasik.actions.whatsapp", endpoint=whatsapp_cfg.get("endpoint"), issues=issues)

    relay_cfg = actions_cfg.get("relay", {}) or {}
    if "relay" in agent.context.action_dispatcher.adapters:
        _validate_adapter_endpoint(label="palasik.actions.relay", endpoint=relay_cfg.get("endpoint"), issues=issues)

    if "telegram" in agent.context.action_dispatcher.adapters:
        telegram_cfg = actions_cfg.get("telegram", {}) or {}
        if not telegram_cfg.get("bot_token"):
            issues.append("palasik.actions.telegram.bot_token wajib diisi")
        if not telegram_cfg.get("chat_id"):
            issues.append("palasik.actions.telegram.chat_id wajib diisi")

    http_cfg = agent.config.get("palasik", "http", default={}) or {}
    if http_cfg.get("enabled"):
        _validate_adapter_endpoint(label="palasik.http", endpoint=http_cfg.get("endpoint"), issues=issues)


def _collect_startup_issues(
    *,
    agent: PalasikAgent,
    config_path: str,
    host: str,
    port: int,
    require_absolute_paths: bool = True,
):
    issues = []
    if not (1 <= int(port) <= 65535):
        issues.append("port harus di antara 1 dan 65535")
    else:
        _validate_bind_target(host=host, port=port, issues=issues)

    policy_issues = _validate_policy_or_exit(config_path=config_path)
    issues.extend(policy_issues)

    decision_log = agent.config.get("palasik", "decision_log", default=None)
    _validate_runtime_path(
        label="palasik.audit_log",
        raw_path=agent.context.audit_log,
        issues=issues,
        require_absolute=require_absolute_paths,
    )
    _validate_runtime_path(
        label="palasik.observability.metrics_file",
        raw_path=agent.context.metrics_file,
        issues=issues,
        require_absolute=require_absolute_paths,
    )
    if decision_log:
        _validate_runtime_path(
            label="palasik.decision_log",
            raw_path=decision_log,
            issues=issues,
            require_absolute=require_absolute_paths,
            require_writable=True,
        )

    dispatcher = agent.context.action_dispatcher
    _validate_active_adapter_config(agent=agent, issues=issues)
    routes = dict(getattr(dispatcher, "action_map", {}) or {})
    adapters = dict(getattr(dispatcher, "adapters", {}) or {})
    known_adapters = {"logger", "webhook", "telegram", "whatsapp", "relay", "http_forward"}
    for action_name, adapter_name in routes.items():
        if not isinstance(action_name, str) or not action_name.strip():
            issues.append("actions.routes memiliki action name kosong")
            continue
        if not isinstance(adapter_name, str) or not adapter_name.strip():
            issues.append(f"actions.routes.{action_name} harus menunjuk adapter string")
            continue
        if adapter_name not in known_adapters:
            issues.append(f"actions.routes.{action_name} menunjuk adapter tidak dikenal: {adapter_name}")
            continue
        if adapter_name != "logger" and adapter_name not in adapters:
            issues.append(
                f"actions.routes.{action_name} menunjuk adapter '{adapter_name}' tapi adapter tidak aktif"
            )

    return issues


def _build_startup_payload(
    *,
    agent: PalasikAgent,
    config_path: str,
    host: str,
    port: int,
    issues: list[str],
):
    return {
        "command": "check-startup",
        "status": "PASS" if not issues else "FAIL",
        "config": config_path,
        "bind": {
            "host": host,
            "port": port,
        },
        "paths": {
            "audit_log": agent.context.audit_log,
            "metrics_file": agent.context.metrics_file,
            "decision_log": agent.config.get("palasik", "decision_log", default=None),
        },
        "actions": {
            "active_adapters": sorted(agent.context.action_dispatcher.adapters.keys()),
            "routes": dict(agent.context.action_dispatcher.action_map),
        },
        "issues": issues,
    }


def _load_policy_from_config(config_path: str):
    config_payload = _load_file(config_path)
    if not isinstance(config_payload, dict):
        raise ValueError("Config harus berupa YAML object")

    palasik_cfg = config_payload.get("palasik", {})
    if not isinstance(palasik_cfg, dict):
        raise ValueError("Bagian `palasik` harus berupa object")

    policy = palasik_cfg.get("policy")
    if policy is None:
        raise ValueError("Config tidak memiliki `palasik.policy`")

    if not isinstance(policy, dict):
        raise ValueError("`palasik.policy` harus berupa object")

    return policy


def _load_policy_from_policy_file(path: str):
    payload = _load_file(path)
    if payload is None:
        raise ValueError("Policy file kosong")

    if isinstance(payload, dict) and "policy" in payload:
        payload = payload["policy"]

    if not isinstance(payload, dict):
        raise ValueError("Policy file harus berupa YAML object")

    return payload


def _validate_policy(policy: dict) -> list[str]:
    issues = []

    if not isinstance(policy, dict):
        return ["policy harus berupa object"]

    policy_type = str(policy.get("type", "allow_deny")).lower()

    # default_deny default behavior (fase 2): wajib aktif.
    if policy.get("default_deny") is not True:
        issues.append("policy.default_deny harus bernilai true")

    default_action = str(policy.get("default_action", "DENY")).upper()
    if default_action not in ALLOWED_ACTIONS:
        issues.append(
            f"policy.default_action tidak valid: {default_action!r}. "
            f"Gunakan salah satu: {ALLOWED_ACTIONS_TEXT}"
        )

    if default_action != "DENY":
        issues.append("policy.default_action harus DENY agar default deny berlaku")

    # For allow_deny policy, enforce threshold sederhana
    if policy_type == "allow_deny":
        threshold = policy.get("threshold", 0.5)
        try:
            value = float(threshold)
            if not (0.0 <= value <= 1.0):
                issues.append("policy.threshold harus di antara 0.0 dan 1.0")
        except (TypeError, ValueError):
            issues.append("policy.threshold harus numerik")
        return issues

    # For rule policy, require rule schema yang eksplisit.
    if policy_type == "rule":
        rules = policy.get("rules")
        if not isinstance(rules, list) or len(rules) == 0:
            issues.append("policy.rules wajib ada dan harus berupa list non-empty")
            return issues

        for i, rule in enumerate(rules):
            if not isinstance(rule, dict):
                issues.append(f"rules[{i}] harus berupa object")
                continue

            rule_id = rule.get("id")
            action = str(rule.get("action", "")).upper()
            reason_code = rule.get("reason_code")
            condition = rule.get("condition")
            when = rule.get("when")

            if not isinstance(rule_id, str) or not rule_id.strip():
                issues.append(f"rules[{i}].id wajib string tidak kosong")

            if action not in ALLOWED_ACTIONS:
                issues.append(
                    f"rules[{i}].action tidak valid: {action!r}. "
                    f"Gunakan salah satu: {ALLOWED_ACTIONS_TEXT}"
                )

            if action == "DENY":
                if not isinstance(reason_code, str) or not reason_code.strip():
                    issues.append(f"rules[{i}] action DENY wajib memiliki reason_code")

            if condition is None:
                if when is not None:
                    issues.append(
                        f"rules[{i}] menggunaan field `when` (legacy). "
                        "Untuk fase 2, gunakan field `condition`"
                    )
                else:
                    issues.append(f"rules[{i}] wajib memiliki condition")
                continue

            if not isinstance(condition, dict):
                issues.append(f"rules[{i}].condition harus object")
                continue

            op = str(condition.get("op", "")).lower()
            key = condition.get("key")
            if op not in ALLOWED_CONDITION_OPS:
                issues.append(f"rules[{i}].condition.op tidak valid: {op!r}")

            if not isinstance(key, str) or not key.strip():
                issues.append(f"rules[{i}].condition.key wajib string tidak kosong")

            if op != "exists":
                if "value" not in condition:
                    issues.append(f"rules[{i}].condition.value wajib ada untuk op={op}")
        return issues

    issues.append(f"policy.type tidak dikenali: {policy_type!r}")
    return issues


def _normalize_event_payload(payload: dict | None):
    return normalize_event_payload(payload)


def _policy_signature(policy: dict) -> str:
    payload = json.dumps(policy, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _snapshot_filename(policy: dict, when: datetime | None = None) -> str:
    policy_id = str(policy.get("policy_id", "policy")).strip() or "policy"
    slug = [c for c in policy_id.lower() if c.isalnum() or c in {"-", "_"}]
    if not slug:
        slug = ["policy"]

    stamp = (when or datetime.now(timezone.utc)).strftime("%Y%m%dT%H%M%SZ")
    safe_policy_id = "".join(slug)
    return f"{safe_policy_id}-{stamp}.snapshot.yaml"


def _extract_policy_payload(payload: Any) -> dict:
    if payload is None:
        raise ValueError("Policy snapshot kosong")

    if isinstance(payload, dict) and "policy" in payload:
        payload = payload["policy"]

    if not isinstance(payload, dict):
        raise ValueError("Format snapshot policy tidak valid")

    return payload


def _run_smoke_decision_checks(
    agent: PalasikAgent,
    events: list[dict],
    max_deny_ratio: float,
    require_allow: bool = True,
):
    allow_count = 0
    deny_count = 0
    deny_missing_reason = 0
    decisions = []

    for raw_event in events:
        event = _normalize_event_payload(dict(raw_event))
        payload = _resolve_decision_payload(agent, event)
        decisions.append(payload)

        if payload["decision"] == "ALLOW":
            allow_count += 1
        elif payload["decision"] == "DENY":
            deny_count += 1
            if not payload.get("reason_code"):
                deny_missing_reason += 1

    total = len(decisions)
    deny_ratio = deny_count / total if total else 0.0

    issues = []
    if total == 0:
        issues.append("Smoke events tidak tersedia")
    if total and deny_ratio >= max_deny_ratio:
        issues.append(
            f"Terlalu banyak DENY saat smoke test: deny_ratio={round(deny_ratio, 3)} "
            f">= threshold={max_deny_ratio}"
        )
    if require_allow and total and allow_count == 0:
        issues.append("Tidak ada keputusan ALLOW pada smoke test")
    if deny_missing_reason > 0:
        issues.append(
            f"{deny_missing_reason} keputusan DENY pada smoke test tanpa reason_code"
        )

    summary = {
        "events": total,
        "allow_count": allow_count,
        "deny_count": deny_count,
        "deny_ratio": round(deny_ratio, 3),
        "issues": issues,
        "decisions": decisions,
    }

    return summary, issues


def _load_smoke_events(path: str | None):
    if path is None:
        if not DEFAULT_DEPLOY_SMOKE_EVENTS.exists():
            raise FileNotFoundError(
                f"Smoke events default tidak ditemukan: {DEFAULT_DEPLOY_SMOKE_EVENTS}"
            )
        path = str(DEFAULT_DEPLOY_SMOKE_EVENTS)

    payload = _load_file(path)
    if isinstance(payload, dict) and "events" in payload:
        payload = payload["events"]

    if not isinstance(payload, list):
        raise ValueError("Smoke events harus berupa list")

    if len(payload) == 0:
        raise ValueError("Smoke events kosong")

    normalized = []
    for idx, item in enumerate(payload):
        if not isinstance(item, dict):
            raise ValueError(f"events[{idx}] harus object")
        normalized.append(item)

    return normalized


def _resolve_decision_payload(agent: PalasikAgent, event: dict):
    trust_score = agent.context.trust.evaluate(event, agent.context)
    policy = agent.context.policy

    decision_value = policy.decide(trust_score, event, agent.context)
    decision = Decision.from_value(decision_value)

    rationale = policy.explain(trust_score, event, agent.context)
    if not rationale:
        rationale = [f"trust_score={trust_score}"]

    reason_code = None
    reason_fn = getattr(policy, "reason_code", None)
    if callable(reason_fn):
        reason_code = reason_fn(trust_score, event, agent.context)

    return {
        "event_id": event.get("event_id"),
        "event_version": event.get("version"),
        "trust_score": trust_score,
        "decision": decision.value,
        "policy_name": getattr(policy, "name", lambda: "policy")(),
        "reason_code": reason_code,
        "rationale": rationale,
    }


def _validate_policy_or_exit(policy_source: dict | None = None, config_path: str | None = None, policy_path: str | None = None):
    issues = []
    if policy_path:
        source = _load_policy_from_policy_file(policy_path)
        issues = _validate_policy(source)
    elif config_path:
        source = _load_policy_from_config(config_path)
        issues = _validate_policy(source)
    elif policy_source is not None:
        issues = _validate_policy(policy_source)
    else:
        raise ValueError("Sumber policy tidak tersedia")

    return issues


def cmd_validate_policy(args):
    try:
        issues = _validate_policy_or_exit(config_path=args.config, policy_path=args.policy)
        if issues:
            print("[PALASIK] policy validate: FAIL")
            for item in issues:
                print(f" - {item}")
            raise SystemExit(1)

        print("[PALASIK] policy validate: PASS")
    except Exception as e:
        print(f"[PALASIK] policy validate: ERROR - {e}")
        raise SystemExit(1)


def cmd_policy_snapshot(args):
    config_path = args.config
    snapshot_dir = Path(args.snapshot_dir)
    _load_config_file(config_path)

    try:
        issues = _validate_policy_or_exit(config_path=config_path)
        if issues:
            raise ValueError("Policy config tidak valid: " + "; ".join(issues))

        policy = _load_policy_from_config(config_path)

        snapshot_dir.mkdir(parents=True, exist_ok=True)
        snapshot_path = snapshot_dir / _snapshot_filename(policy)
        snapshot_payload = {
            "metadata": {
                "created_at_utc": datetime.now(timezone.utc).isoformat(),
                "source_config": str(config_path),
                "policy_signature": _policy_signature(policy),
                "policy_version": policy.get("version", "1"),
            },
            "policy": policy,
        }

        with snapshot_path.open("w", encoding="utf-8") as f:
            yaml.safe_dump(snapshot_payload, f, sort_keys=False)

        print("[PALASIK] policy snapshot: PASS")
        print(f"path={snapshot_path}")
    except Exception as e:
        print(f"[PALASIK] policy snapshot: ERROR - {e}")
        raise SystemExit(1)


def cmd_policy_rollback(args):
    _load_config_file(args.config)
    _load_config_file(args.snapshot)

    try:
        snapshot = _load_file(args.snapshot)
        policy = _extract_policy_payload(snapshot)
        issues = _validate_policy(policy)
        if issues:
            raise ValueError("Policy snapshot tidak valid: " + "; ".join(issues))

        config_path = Path(args.config)
        config_payload = _load_file(args.config)
        if not isinstance(config_payload, dict):
            raise ValueError("Config harus berupa YAML object")

        palasik_cfg = config_payload.get("palasik")
        if palasik_cfg is None:
            palasik_cfg = {}
            config_payload["palasik"] = palasik_cfg
        elif not isinstance(palasik_cfg, dict):
            raise ValueError("Bagian `palasik` harus berupa object")

        backup_dir = Path(args.backup_dir)
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup_path = backup_dir / f"{config_path.name}.rollback-backup-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
        shutil.copyfile(config_path, backup_path)

        palasik_cfg["policy"] = policy
        with config_path.open("w", encoding="utf-8") as f:
            yaml.safe_dump(config_payload, f, sort_keys=False)

        print("[PALASIK] policy rollback: PASS")
        print(f"config={config_path}")
        print(f"backup={backup_path}")
    except Exception as e:
        print(f"[PALASIK] policy rollback: ERROR - {e}")
        raise SystemExit(1)


def cmd_policy_deploy_check(args):
    config_path = args.config
    _load_config_file(config_path)

    try:
        issues = _validate_policy_or_exit(config_path=config_path)
        if issues:
            raise ValueError("Policy config tidak valid: " + "; ".join(issues))

        events = _load_smoke_events(args.smoke_events)
        if len(events) > args.limit:
            events = events[: args.limit]

        max_deny_ratio = args.max_deny_ratio
        if not (0 <= max_deny_ratio <= 1):
            raise ValueError("--max-deny-ratio harus di antara 0.0 dan 1.0")

        agent = PalasikAgent(config_file=config_path)
        summary, check_issues = _run_smoke_decision_checks(
            agent,
            events,
            max_deny_ratio=max_deny_ratio,
            require_allow=args.require_allow,
        )

        if check_issues:
            print("[PALASIK] policy deploy-check: FAIL")
            for item in check_issues:
                print(f" - {item}")
            print(json.dumps(
                {
                    "command": "policy-deploy-check",
                    "status": "FAIL",
                    "summary": summary,
                },
                indent=2,
                sort_keys=True,
            ))
            raise SystemExit(1)

        print("[PALASIK] policy deploy-check: PASS")
        print(
            json.dumps(
                {
                    "command": "policy-deploy-check",
                    "status": "PASS",
                    "summary": summary,
                },
                indent=2,
                sort_keys=True,
            )
        )
    except Exception as e:
        print(f"[PALASIK] policy deploy-check: ERROR - {e}")
        raise SystemExit(1)


def _build_status_payload(agent: PalasikAgent, command: str = "status"):
    return build_status_payload(agent, command=command)


def cmd_run(args):
    config_path = args.config
    _load_config_file(config_path)

    print("[PALASIK] Starting agent...")
    agent = None
    try:
        issues = _validate_policy_or_exit(config_path=config_path)
        if issues:
            raise ValueError("Policy config tidak valid: " + "; ".join(issues))

        agent = PalasikAgent(config_file=config_path)
        agent.load_plugins()
        agent.start()

        print("[PALASIK] Agent running. Press Ctrl+C to stop.")
        stop_event = threading.Event()
        while not stop_event.is_set():
            stop_event.wait(1.0)
    except Exception as e:
        print(f"[PALASIK] run: FAIL - {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[PALASIK] Stopping agent...")
    finally:
        if agent is not None:
            agent.stop()


def cmd_serve(args):
    config_path = args.config
    _load_config_file(config_path)

    agent = None
    server = None
    try:
        issues = _validate_policy_or_exit(config_path=config_path)
        if issues:
            raise ValueError("Policy config tidak valid: " + "; ".join(issues))

        agent = PalasikAgent(config_file=config_path)
        agent.load_plugins()
        agent.start()

        server = create_server(agent, host=args.host, port=args.port)
        print(f"[PALASIK] API serving on http://{args.host}:{args.port}")
        server.serve_forever()
    except Exception as e:
        print(f"[PALASIK] serve: FAIL - {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[PALASIK] Stopping API server...")
    finally:
        if server is not None:
            try:
                server.shutdown()
                server.server_close()
            except Exception:
                pass
        if agent is not None:
            try:
                agent.stop()
            except Exception:
                pass


def cmd_check(args):
    config_path = args.config
    _load_config_file(config_path)

    agent = None
    try:
        issues = _validate_policy_or_exit(config_path=config_path)
        if issues:
            raise ValueError("Policy config tidak valid: " + "; ".join(issues))

        agent = PalasikAgent(config_file=config_path)
        agent.load_plugins()
        agent.start()

        event = _normalize_event_payload({
            "type": "health-check",
            "source": {
                "device_id": "health-check",
                "ip": "127.0.0.1",
            },
            "value": 10,
        })

        agent.emit(event)

        if agent.context.latest_decision is None:
            raise RuntimeError("Decision pipeline did not return a decision")

        latest = agent.context.latest_decision
        print("[PALASIK] check: PASS")
        print(
            f"decision={latest.decision.value} "
            f"policy={latest.policy_name} "
            f"trust_score={latest.trust_score} "
            f"reason_code={latest.reason_code}"
        )
        print("[PALASIK] check completed")
    except Exception as e:
        print(f"[PALASIK] check: FAIL - {e}")
        sys.exit(1)
    finally:
        if agent is not None:
            try:
                agent.stop()
            except Exception:
                pass


def cmd_check_startup(args):
    config_path = args.config
    _load_config_file(config_path)

    agent = None
    try:
        agent = PalasikAgent(config_file=config_path)
        issues = _collect_startup_issues(
            agent=agent,
            config_path=config_path,
            host=args.host,
            port=args.port,
            require_absolute_paths=not args.allow_relative_paths,
        )
        payload = _build_startup_payload(
            agent=agent,
            config_path=config_path,
            host=args.host,
            port=args.port,
            issues=issues,
        )
        if issues:
            print("[PALASIK] check-startup: FAIL")
            print(json.dumps(payload, indent=2, sort_keys=True))
            raise SystemExit(1)

        print("[PALASIK] check-startup: PASS")
        print(json.dumps(payload, indent=2, sort_keys=True))
    except Exception as e:
        print(f"[PALASIK] check-startup: FAIL - {e}")
        sys.exit(1)
    finally:
        if agent is not None:
            try:
                agent.stop()
            except Exception:
                pass


def cmd_install_systemd(args):
    config_source = Path(args.config_source).resolve()
    env_template = Path(args.env_template).resolve()
    output_dir = Path(args.output_dir).resolve()

    if not config_source.exists():
        raise SystemExit(f"Config source tidak ditemukan: {config_source}")
    if not env_template.exists():
        raise SystemExit(f"Env template tidak ditemukan: {env_template}")

    output_dir.mkdir(parents=True, exist_ok=True)

    service_path = output_dir / f"{args.service_name}.service"
    env_path = output_dir / f"{args.service_name}.env"
    install_path = output_dir / f"install_{args.service_name}_systemd.sh"

    service_path.write_text(
        _render_systemd_service(
            service_name=args.service_name,
            install_root=args.install_root,
            etc_dir=args.etc_dir,
            log_dir=args.log_dir,
            user=args.user,
            group=args.group,
            host=args.host,
            port=args.port,
        ),
        encoding="utf-8",
    )
    env_path.write_text(env_template.read_text(encoding="utf-8"), encoding="utf-8")
    install_path.write_text(
        _render_install_script(
            service_name=args.service_name,
            install_root=args.install_root,
            etc_dir=args.etc_dir,
            state_dir=args.state_dir,
            log_dir=args.log_dir,
            user=args.user,
            group=args.group,
            config_source=str(config_source),
            env_source=str(env_path),
            service_source=str(service_path),
        ),
        encoding="utf-8",
    )
    install_path.chmod(0o755)

    payload = {
        "command": "install-systemd",
        "status": "PASS",
        "output_dir": str(output_dir),
        "service_file": str(service_path),
        "env_file": str(env_path),
        "install_script": str(install_path),
    }
    print("[PALASIK] install-systemd: PASS")
    print(json.dumps(payload, indent=2, sort_keys=True))


def cmd_status(args):
    config_path = args.config
    _load_config_file(config_path)

    agent = None
    try:
        issues = _validate_policy_or_exit(config_path=config_path)
        if issues:
            raise ValueError("Policy config tidak valid: " + "; ".join(issues))

        agent = PalasikAgent(config_file=config_path)
        agent.load_plugins()
        agent.start()

        event = _normalize_event_payload({
            "type": "status-check",
            "source": {
                "device_id": "status-check",
                "ip": "127.0.0.1",
            },
            "value": 10,
        })
        agent.emit(event)

        print(json.dumps(_build_status_payload(agent), indent=2, sort_keys=True))
    except Exception as e:
        print(f"[PALASIK] status: FAIL - {e}")
        sys.exit(1)
    finally:
        if agent is not None:
            try:
                agent.stop()
            except Exception:
                pass


def cmd_simulate(args):
    config_path = args.config
    event_path = args.event

    _load_config_file(config_path)

    try:
        issues = _validate_policy_or_exit(config_path=config_path)
        if issues:
            raise ValueError("Policy config tidak valid: " + "; ".join(issues))

        raw_event_path = Path(event_path)
        if not raw_event_path.exists():
            raise FileNotFoundError(f"Event file tidak ditemukan: {event_path}")

        with raw_event_path.open("r", encoding="utf-8") as f:
            payload = json.load(f)

        event = _normalize_event_payload(payload)

        agent = PalasikAgent(config_file=config_path)
        decision = _resolve_decision_payload(agent, event)

        print(json.dumps(decision, indent=2, sort_keys=True))
    except Exception as e:
        print(f"[PALASIK] simulate: FAIL - {e}")
        sys.exit(1)


def cmd_init(args):
    target = Path("config.yaml")
    if target.exists():
        print("[ERROR] config.yaml already exists")
        sys.exit(1)

    template = """palasik:
  broker:
    host: localhost
    port: 1883
    topic: palasik/sensor/#

  policy:
    version: "1"
    default_deny: true
    default_action: DENY
    policy_id: palasik-baseline
    type: rule
    rules:
      - id: deny_unknown_device
        action: DENY
        reason_code: UNKNOWN_DEVICE
        condition:
          op: eq
          key: source.device_id
          value: unknown
      - id: allow_trusted_device
        action: ALLOW
        reason_code: TRUSTED_DEVICE
        condition:
          op: gte
          key: trust_score
          value: 0.75

  plugins:
    enabled:
      - logger
      - audit

  observability:
    metrics_file: runs/metrics.json
    alert:
      deny_spike_threshold: 0.45
      trust_score_drop_threshold: 0.25

  audit_log: runs/audit.jsonl

  http:
    enabled: false
    endpoint: "https://example.com/webhook"
    timeout: 5
"""

    target.write_text(template)
    print("[PALASIK] config.yaml created")


def main():
    parser = argparse.ArgumentParser(
        prog="palasik",
        description="PALASIK IoT Zero Trust Gateway",
    )

    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="Run PALASIK agent")
    run_parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to config.yaml",
    )
    run_parser.set_defaults(func=cmd_run)

    serve_parser = subparsers.add_parser("serve", aliases=["serve-api"], help="Run PALASIK HTTP API")
    serve_parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to config.yaml",
    )
    serve_parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Bind host HTTP API",
    )
    serve_parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Bind port HTTP API",
    )
    serve_parser.set_defaults(func=cmd_serve)

    check_parser = subparsers.add_parser("check", help="Run PALASIK startup self-check")
    check_parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to config.yaml",
    )
    check_parser.set_defaults(func=cmd_check)

    startup_parser = subparsers.add_parser(
        "check-startup",
        help="Validasi config/path/action route sebelum mode service start",
    )
    startup_parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to config.yaml",
    )
    startup_parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Bind host yang akan dipakai service",
    )
    startup_parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Bind port yang akan dipakai service",
    )
    startup_parser.add_argument(
        "--allow-relative-paths",
        action="store_true",
        help="Izinkan storage path relatif (default: fail-fast untuk mode service)",
    )
    startup_parser.set_defaults(func=cmd_check_startup)

    validate_parser = subparsers.add_parser("validate-policy", help="Lint policy config")
    validate_parser.add_argument(
        "--config",
        help="Path to config.yaml (dengan field palasik.policy)",
    )
    validate_parser.add_argument(
        "--policy",
        help="Path file policy YAML murni",
    )
    validate_parser.set_defaults(func=cmd_validate_policy)

    snapshot_parser = subparsers.add_parser(
        "policy-snapshot",
        help="Simpan snapshot kebijakan aktif untuk rollback cepat",
    )
    snapshot_parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path config yang memuat palasik.policy",
    )
    snapshot_parser.add_argument(
        "--snapshot-dir",
        default=DEFAULT_SNAPSHOT_DIR,
        help="Direktori output snapshot",
    )
    snapshot_parser.set_defaults(func=cmd_policy_snapshot)

    rollback_parser = subparsers.add_parser(
        "policy-rollback",
        help="Rollback policy dari snapshot policy ke config aktif",
    )
    rollback_parser.add_argument("--config", default="config.yaml", help="Path config yang akan di-rollback")
    rollback_parser.add_argument("--snapshot", required=True, help="Path file policy snapshot")
    rollback_parser.add_argument(
        "--backup-dir",
        default="runs/policy_backups",
        help="Direktori backup config sebelum rollback",
    )
    rollback_parser.set_defaults(func=cmd_policy_rollback)

    deploy_check_parser = subparsers.add_parser(
        "policy-deploy-check",
        help="Validasi akhir deployment policy agar tidak outage",
    )
    deploy_check_parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path config kandidat untuk deploy",
    )
    deploy_check_parser.add_argument(
        "--smoke-events",
        help="Path file event smoke (list), default: docs/samples/policy-smoke-events.json",
    )
    deploy_check_parser.add_argument(
        "--max-deny-ratio",
        type=float,
        default=DEFAULT_MAX_DENY_RATIO,
        help="Batas maksimal deny ratio (0-1) untuk smoke test",
    )
    deploy_check_parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Jumlah maksimum event untuk smoke test",
    )
    deploy_check_parser.add_argument(
        "--require-allow",
        action="store_true",
        help="Wajib ada minimal 1 keputusan ALLOW",
    )
    deploy_check_parser.set_defaults(func=cmd_policy_deploy_check)

    simulate_parser = subparsers.add_parser("simulate", help="Preview keputusan dari satu event JSON")
    simulate_parser.add_argument("event", help="Path file event JSON")
    simulate_parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to config.yaml",
    )
    simulate_parser.set_defaults(func=cmd_simulate)

    status_parser = subparsers.add_parser("status", help="Lihat status gateway + metrics terbaru")
    status_parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to config.yaml",
    )
    status_parser.set_defaults(func=cmd_status)

    install_parser = subparsers.add_parser(
        "install-systemd",
        help="Render bundle service systemd + script install edge",
    )
    install_parser.add_argument("--config-source", default="config.yaml", help="Config sumber yang akan disalin")
    install_parser.add_argument("--env-template", default=str(DEFAULT_ENV_TEMPLATE), help="Template env sumber")
    install_parser.add_argument("--output-dir", default=DEFAULT_SYSTEMD_OUTPUT_DIR, help="Direktori output bundle")
    install_parser.add_argument("--service-name", default=DEFAULT_SYSTEMD_SERVICE_NAME, help="Nama service systemd")
    install_parser.add_argument("--install-root", default=DEFAULT_EDGE_INSTALL_ROOT, help="Root source runtime di host")
    install_parser.add_argument("--etc-dir", default=DEFAULT_EDGE_ETC_DIR, help="Direktori config di host")
    install_parser.add_argument("--state-dir", default=DEFAULT_EDGE_STATE_DIR, help="Direktori state persistent")
    install_parser.add_argument("--log-dir", default=DEFAULT_EDGE_LOG_DIR, help="Direktori log runtime")
    install_parser.add_argument("--user", default="palasik", help="User service systemd")
    install_parser.add_argument("--group", default="palasik", help="Group service systemd")
    install_parser.add_argument("--host", default="0.0.0.0", help="Bind host service HTTP API")
    install_parser.add_argument("--port", type=int, default=8080, help="Bind port service HTTP API")
    install_parser.set_defaults(func=cmd_install_systemd)

    init_parser = subparsers.add_parser("init", help="Create config.yaml template")
    init_parser.set_defaults(func=cmd_init)

    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
