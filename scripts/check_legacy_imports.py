"""Check for remaining legacy imports during migration.

Exit code:
- 0: no legacy imports found in tracked source/docs content
- 1: legacy imports still present
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGET_PATTERNS = (
    r"from\s+palasik\.core\.(trust_engine|policy_engine)\b",
    r"import\s+palasik\.core\.(trust_engine|policy_engine)\b",
    r"from\s+palasik\.core\s+import\s+(trust_engine|policy_engine)(\s*,|\s*$)",
)
ALLOWED_FILES = {
    Path("tests/core/test_legacy_shims.py"),
    Path("palasik/core/trust_engine.py"),
    Path("palasik/core/policy_engine.py"),
}


def tracked_files() -> list[Path]:
    """Return tracked files from git (excluding docs/examples style binary noise)."""
    cp = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    files = []
    for rel in cp.stdout.splitlines():
        p = ROOT / rel
        rel_path = Path(rel)
        if rel_path in ALLOWED_FILES:
            continue
        if p.is_file() and p.suffix in {".py", ".md", ".yml", ".yaml", ".toml", ".txt"}:
            files.append(p)
    return files


def check_files(files: list[Path]) -> list[tuple[Path, int, str]]:
    patterns = [re.compile(p) for p in TARGET_PATTERNS]
    hits: list[tuple[Path, int, str]] = []

    for file in files:
        try:
            text = file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # Ignore non-utf8 files silently.
            continue

        for idx, line in enumerate(text.splitlines(), 1):
            if any(p.search(line) for p in patterns):
                hits.append((file, idx, line.strip()))

    return hits


def main() -> int:
    files = tracked_files()
    hits = check_files(files)

    if not hits:
        print("[migration-check] legacy-import-scan: 0 issues")
        return 0

    print(f"[migration-check] legacy-import-scan: {len(hits)} issues")
    for path, line_no, line in hits:
        rel = path.relative_to(ROOT)
        print(f"- {rel}:{line_no}: {line}")

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
