"""Entry untuk menjalankan DEMIT Super App."""

import argparse
import signal

from demit.core.runtime import DemitRuntime


def run(config_path: str | None = None):
    runtime = DemitRuntime(config_path=config_path)
    runtime.start()

    stop = False

    def _graceful(_signo, _frame):
        nonlocal stop
        stop = True

    signal.signal(signal.SIGINT, _graceful)
    signal.signal(signal.SIGTERM, _graceful)

    print(f"[DEMIT] Super App started with {len(runtime.apps)} app(s). Ctrl+C to stop.")
    while not stop:
        signal.pause()

    runtime.stop()


def main():
    parser = argparse.ArgumentParser(description="DEMIT super-app runtime")
    parser.add_argument(
        "--config",
        default="demit.yaml",
        help="Path ke config DEMIT",
    )
    args = parser.parse_args()
    run(args.config)


if __name__ == "__main__":
    main()
