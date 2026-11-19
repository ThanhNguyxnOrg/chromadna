import json
import re
import subprocess
import sys
from pathlib import Path

from chromadna import __version__, mcp_server
from chromadna.cli import resolve_default_catalog_path as cli_default_catalog


def test_cli_uses_installed_catalog_outside_checkout(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    prefix = tmp_path / "venv"
    expected = prefix / "share" / "chromadna" / "color_dna_catalog.json"
    expected.parent.mkdir(parents=True)
    expected.write_text('{"profiles": []}', encoding="utf-8")
    monkeypatch.setattr("chromadna.cli.sysconfig.get_path", lambda key: str(prefix))

    assert cli_default_catalog() == expected


def test_mcp_uses_installed_catalog_outside_checkout(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("CHROMADNA_CATALOG", raising=False)
    monkeypatch.setattr(mcp_server, "REPO_ROOT", tmp_path / "not-a-checkout")
    prefix = tmp_path / "venv"
    expected = prefix / "share" / "chromadna" / "color_dna_catalog.json"
    expected.parent.mkdir(parents=True)
    expected.write_text('{"profiles": []}', encoding="utf-8")
    monkeypatch.setattr(mcp_server.sysconfig, "get_path", lambda key: str(prefix))

    assert mcp_server.resolve_default_catalog_path() == expected


def test_mcp_explicit_catalog_environment_override_wins(tmp_path, monkeypatch):
    expected = tmp_path / "custom-catalog.json"
    monkeypatch.setenv("CHROMADNA_CATALOG", str(expected))

    assert mcp_server.resolve_default_catalog_path() == expected


def test_version_manifests_and_skills_are_synchronized():
    root = Path(__file__).resolve().parents[1]
    pyproject_text = (root / "pyproject.toml").read_text(encoding="utf-8")
    version_match = re.search(r'^version\s*=\s*"([^"]+)"', pyproject_text, flags=re.MULTILINE)
    assert version_match is not None
    version = version_match.group(1)
    assert __version__ == version

    for manifest_rel in ("plugin.json", ".claude-plugin/plugin.json", ".codex-plugin/plugin.json"):
        manifest = json.loads((root / manifest_rel).read_text(encoding="utf-8"))
        assert manifest["version"] == version, f"{manifest_rel} version mismatch"

    root_skill = (root / "SKILL.md").read_text(encoding="utf-8")
    canonical_skill = (root / "skills" / "chromadna" / "SKILL.md").read_text(encoding="utf-8")
    assert root_skill == canonical_skill
    match = re.search(r'^\s*version:\s*"([^"]+)"', canonical_skill, flags=re.MULTILINE)
    assert match is not None and match.group(1) == version


def test_cli_malformed_mix_exits_with_code_2(tmp_path):
    catalog = tmp_path / "catalog.json"
    catalog.write_text('{"profiles": []}', encoding="utf-8")
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "chromadna.cli",
            "blend",
            "--mix",
            "missing_colon",
            "--name",
            "Bad",
            "--out",
            str(tmp_path / "out.xmp"),
            "--catalog",
            str(catalog),
        ],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 2
    assert "Invalid --mix specification" in proc.stderr
