import asyncio
import json
from pathlib import Path
import sys

import pytest

from chromadna.mcp_server import _apply_overrides, blend_color_dna

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def test_unknown_or_invalid_slider_overrides_are_rejected():
    with pytest.raises(ValueError, match="Unsupported or invalid slider override"):
        _apply_overrides(
            {"id": "look", "sliders": {}, "tone_curves": {}},
            {"NotARealSlider": 20},
        )


def test_mcp_blend_rejects_boolean_weights(tmp_path):
    catalog = tmp_path / "catalog.json"
    catalog.write_text(
        json.dumps(
            {
                "profiles": [
                    {
                        "id": "look_a",
                        "category": "Film Emulation",
                        "tags": [],
                        "sliders": {"Contrast2012": 10},
                        "tone_curves": {},
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="weight"):
        blend_color_dna(
            weights={"look_a": True},  # type: ignore[dict-item]
            preset_name="Invalid Bool Weight",
            output_xmp_path=str(tmp_path / "out.xmp"),
            catalog_path=str(catalog),
        )


def test_stdio_server_initializes_and_exposes_all_tools():
    project_root = Path(__file__).resolve().parents[1]
    catalog = project_root / "data" / "color_dna_catalog.json"
    server = StdioServerParameters(
        command=sys.executable,
        args=["-m", "chromadna.mcp_server"],
        env={"PYTHONPATH": str(project_root / "src"), "CHROMADNA_CATALOG": str(catalog)},
    )

    async def _run():
        async with stdio_client(server) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools_result = await session.list_tools()
                names = {t.name for t in tools_result.tools}
                expected = {
                    "list_color_dna",
                    "inspect_color_dna",
                    "analyze_photo",
                    "blend_color_dna",
                    "match_photo_to_dna",
                    "render_preview",
                    "compile_xmp_preset",
                    "export_cube_lut",
                }
                assert expected.issubset(names)

                listed = await session.call_tool("list_color_dna", {"tag": "matte"})
                assert not listed.isError
                payload = json.loads(listed.content[0].text)
                assert payload["total_matched"] > 0

    asyncio.run(_run())
