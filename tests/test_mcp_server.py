import asyncio
import os
from pathlib import Path
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def test_stdio_server_initializes_and_exposes_all_tools():
    project_root = Path(__file__).resolve().parents[1]
    catalog = project_root / "data" / "color_dna_catalog.json"

    async def exercise_server():
        params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "chromadna.mcp_server"],
            env={**os.environ, "CHROMADNA_CATALOG": str(catalog)},
        )
        async with stdio_client(params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                response = await session.list_tools()
                names = {tool.name for tool in response.tools}
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
                assert expected <= names

    asyncio.run(exercise_server())
