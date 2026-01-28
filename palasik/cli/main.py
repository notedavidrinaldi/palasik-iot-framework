# palasik/cli/main.py

import argparse
import sys
from pathlib import Path

from palasik.core.agent import PalasikAgent


def cmd_run(args):
    config_path = args.config

    if not Path(config_path).exists():
        print(f"[ERROR] Config file not found: {config_path}")
        sys.exit(1)

    print("[PALASIK] Starting agent...")
    agent = PalasikAgent(config_file=config_path)
    agent.load_plugins()
    agent.start()

    try:
        print("[PALASIK] Agent running. Press Ctrl+C to stop.")
        while True:
            pass
    except KeyboardInterrupt:
        print("\n[PALASIK] Stopping agent...")
        agent.stop()


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
    threshold: 0.7

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

    # palasik run
    run_parser = subparsers.add_parser("run", help="Run PALASIK agent")
    run_parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to config.yaml",
    )
    run_parser.set_defaults(func=cmd_run)

    # palasik init
    init_parser = subparsers.add_parser("init", help="Create config.yaml template")
    init_parser.set_defaults(func=cmd_init)

    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
