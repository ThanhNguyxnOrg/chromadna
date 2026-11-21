import json
import sys

import pytest

from chromadna.cli import main


@pytest.mark.parametrize("source", ["missing", "file", "empty", "malformed"])
def test_mine_preserves_catalog_when_no_profiles_can_be_mined(tmp_path, monkeypatch, capsys, source):
    vault = tmp_path / "raw_vault"
    if source == "file":
        vault.write_text("not a directory")
    elif source != "missing":
        vault.mkdir()
        if source == "malformed":
            (vault / "broken.xmp").write_text("<broken")

    catalog = tmp_path / "catalog.json"
    original = b'{"profiles": [{"id": "keep-me"}]}\n'
    catalog.write_bytes(original)
    monkeypatch.setattr(sys, "argv", ["chromadna", "mine", str(vault), "--out", str(catalog)])

    with pytest.raises(SystemExit) as error:
        main()
    assert error.value.code == 2
    assert str(vault) in capsys.readouterr().err
    assert catalog.read_bytes() == original


def test_mine_writes_catalog_when_a_preset_is_usable(tmp_path, monkeypatch):
    (tmp_path / "broken.xmp").write_text("<broken")
    (tmp_path / "warm.lrtemplate").write_text("s = { settings = { Vibrance = 20 } }")
    catalog = tmp_path / "output" / "catalog.json"
    monkeypatch.setattr(sys, "argv", ["chromadna", "mine", str(tmp_path), "--out", str(catalog)])

    main()
    result = json.loads(catalog.read_text())
    assert result["total_profiles"] == 1
    assert result["profiles"][0]["sliders"]["Vibrance"] == 20
