from chromadna import mcp_server
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
