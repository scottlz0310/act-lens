#!/usr/bin/env python3
"""Helper: run `detect-secrets scan --all-files` and compare with baseline.

This is intended as a manual developer helper (not a pre-commit hook).
It ignores the `generated_at` timestamp when comparing JSON results.
"""

from __future__ import annotations

import json
import shutil
import subprocess  # nosec - intended to call the `uv` wrapper
from pathlib import Path
from typing import Any, cast

BASELINE = Path(".secrets.baseline")


def _load_json(fp: Path) -> dict[str, Any]:
    with fp.open("r", encoding="utf-8") as f:
        return json.load(f)


def _remove_generated_at(obj: Any) -> Any:
    if isinstance(obj, dict):
        new_obj: dict[str, Any] = {}
        for k, v in cast(dict[str, Any], obj).items():
            if k == "generated_at":
                continue
            new_obj[k] = _remove_generated_at(v)
        return new_obj
    if isinstance(obj, list):
        return [_remove_generated_at(v) for v in cast(list[Any], obj)]
    return obj


def main() -> int:
    if not BASELINE.exists():
        print(
            "No .secrets.baseline found. Create one with:\n  uv run detect-secrets scan > .secrets.baseline"
        )
        return 1

    uv_path = shutil.which("uv")
    if not uv_path:
        print("`uv` not found in PATH. Run `uv sync` to install dev dependencies.")
        return 1

    proc = subprocess.run(  # nosec
        [uv_path, "run", "detect-secrets", "scan", "--all-files"],
        check=False,
        capture_output=True,
        text=True,
    )

    if proc.returncode not in (0, 1):
        print("detect-secrets failed to run:")
        print(proc.stderr or "")
        return 2

    try:
        new = json.loads(proc.stdout)
    except Exception:
        print(
            "failed to parse detect-secrets output as JSON. Are you running the expected version?"
        )
        print(proc.stdout or "")
        return 2

    old = _load_json(BASELINE)
    new_clean = _remove_generated_at(new)
    old_clean = _remove_generated_at(old)

    if old_clean != new_clean:
        old_results = old_clean.get("results", {})
        new_results = new_clean.get("results", {})
        added_files = sorted(set(new_results.keys()) - set(old_results.keys()))
        changed = [
            k for k in set(new_results) & set(old_results) if new_results[k] != old_results[k]
        ]

        print(
            "detect-secrets: repository snapshot differs from .secrets.baseline. New potential secrets detected."
        )
        if added_files:
            print("New files with secrets detected:")
            for f in added_files[:20]:
                print("  ", f)
            if len(added_files) > 20:
                print("  ... (", len(added_files) - 20, "more)")

        if changed:
            print("Files with changed findings:")
            for f in changed[:20]:
                print("  ", f)
            if len(changed) > 20:
                print("  ... (", len(changed) - 20, "more)")

        print("\nIf these are expected, update the baseline:")
        print("  uv run detect-secrets scan > .secrets.baseline")
        print("Then review and commit .secrets.baseline. See README for guidance.")
        return 3

    print("detect-secrets: no new secrets detected (baseline validated)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
