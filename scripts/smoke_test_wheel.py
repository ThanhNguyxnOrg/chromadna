#!/usr/bin/env python3
"""Smoke-test the built wheel from an isolated environment outside the checkout."""

from __future__ import annotations

import os
import subprocess
import tempfile
import venv
from pathlib import Path


def main() -> int:
    dist_dir = Path("dist")
    wheels = sorted(dist_dir.glob("chromadna-*.whl"))
    if len(wheels) != 1:
        raise SystemExit(f"Expected exactly one ChromaDNA wheel in {dist_dir}, found {len(wheels)}.")

    wheel = wheels[0].resolve()
    with tempfile.TemporaryDirectory(prefix="chromadna-wheel-smoke-") as temp_dir:
        root = Path(temp_dir)
        environment_dir = root / "venv"
        venv.EnvBuilder(with_pip=True).create(environment_dir)

        scripts_dir = environment_dir / ("Scripts" if os.name == "nt" else "bin")
        python = scripts_dir / ("python.exe" if os.name == "nt" else "python")
        cli = scripts_dir / ("chromadna.exe" if os.name == "nt" else "chromadna")

        env = os.environ.copy()
        env.pop("CHROMADNA_CATALOG", None)
        subprocess.run(
            [str(python), "-m", "pip", "install", "--disable-pip-version-check", str(wheel)],
            check=True,
            env=env,
        )
        result = subprocess.run(
            [str(cli), "list"],
            cwd=root,
            env=env,
            check=True,
            capture_output=True,
            text=True,
        )
        if "emulsion_kodak_portra_400" not in result.stdout:
            raise SystemExit("Installed wheel could not resolve and list the bundled catalog.")
        profile_lines = [line for line in result.stdout.splitlines() if " | tags=" in line]
        print(f"Wheel smoke test passed: installed package listed {len(profile_lines)} bundled profiles.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
