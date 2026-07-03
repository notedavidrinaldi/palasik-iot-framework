#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "docs" / "images"
FONT_CANDIDATES = [
    "/System/Library/Fonts/Menlo.ttc",
    "/System/Library/Fonts/SFNSMono.ttf",
]


PANELS = {
    "readme-init-check.png": [
        "$ pip install palasik",
        "Collecting palasik",
        "Successfully installed palasik-0.2.0",
        "",
        "$ palasik init",
        "[PALASIK] config.yaml created",
        "",
        "$ palasik check --config config.yaml",
        "[INFO] PALASIK_DECISION {'decision': 'ALLOW', 'reason_code': 'TRUSTED_DEVICE'}",
        "[PALASIK] check: PASS",
        "decision=ALLOW policy=rule_policy trust_score=0.9 reason_code=TRUSTED_DEVICE",
        "[PALASIK] check completed",
    ],
    "readme-simulate.png": [
        "$ cat sample-event.json",
        "{",
        '  "version": "1",',
        '  "event_id": "evt-demo-01",',
        '  "type": "sensor.temperature",',
        '  "source": {"device_id": "edge-sensor-01", "ip": "192.168.1.10"},',
        '  "value": 42',
        "}",
        "",
        "$ palasik simulate sample-event.json --config config.yaml",
        "{",
        '  "decision": "ALLOW",',
        '  "policy_name": "rule_policy",',
        '  "reason_code": "TRUSTED_DEVICE",',
        '  "trust_score": 0.9',
        "}",
    ],
    "readme-status.png": [
        "$ palasik status --config config.yaml",
        "{",
        '  "command": "status",',
        '  "status": "UP",',
        '  "policy_name": "rule_policy",',
        '  "metrics": {',
        '    "events_total": 1,',
        '    "events_allowed": 1,',
        '    "events_denied": 0,',
        '    "pipeline_avg_latency_ms": 0.034,',
        '    "reason_code_breakdown": {"TRUSTED_DEVICE": 1}',
        "  },",
        '  "storage": {"audit_log": {"exists": true}, "metrics_file": {"exists": true}}',
        "}",
    ],
    "readme-policy-ops.png": [
        "$ palasik policy-snapshot --config config.yaml",
        "[PALASIK] policy snapshot: PASS",
        "path=runs/policy_snapshots/palasik-baseline-20260703T091720Z.snapshot.yaml",
        "",
        "$ palasik policy-deploy-check --config config.yaml --smoke-events docs/samples/policy-smoke-events.json --require-allow",
        "[PALASIK] policy deploy-check: PASS",
        "events=3 allow_count=2 deny_count=1 deny_ratio=0.333",
        "",
        "$ palasik policy-rollback --config config.yaml --snapshot runs/policy_snapshots/<snapshot>",
        "[PALASIK] policy rollback: PASS",
        "backup=runs/policy_backups/config.yaml.rollback-backup-20260703T091733Z",
    ],
}


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in FONT_CANDIDATES:
        path = Path(candidate)
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def render_panel(filename: str, lines: list[str]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    title_font = load_font(24)
    body_font = load_font(18)

    line_height = 28
    text_width = max(int(body_font.getlength(line)) for line in lines) if lines else 400
    width = max(920, text_width + 80)
    height = 96 + len(lines) * line_height + 40

    image = Image.new("RGB", (width, height), "#0b1020")
    draw = ImageDraw.Draw(image)

    draw.rounded_rectangle((18, 18, width - 18, height - 18), radius=22, fill="#0f172a", outline="#294164", width=2)
    draw.rounded_rectangle((34, 34, width - 34, 84), radius=16, fill="#111c33")
    draw.ellipse((54, 50, 68, 64), fill="#ff5f57")
    draw.ellipse((78, 50, 92, 64), fill="#febc2e")
    draw.ellipse((102, 50, 116, 64), fill="#28c840")
    draw.text((140, 45), "PALASIK CLI walkthrough", fill="#dbeafe", font=title_font)

    y = 108
    for line in lines:
        color = "#7dd3fc" if line.startswith("$ ") else "#e5eefc"
        draw.text((54, y), line, fill=color, font=body_font)
        y += line_height

    image.save(OUTPUT_DIR / filename)


def main() -> None:
    for filename, lines in PANELS.items():
        render_panel(filename, lines)


if __name__ == "__main__":
    main()
