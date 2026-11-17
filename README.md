# ChromaDNA

**Adobe Lightroom / Camera Raw Color DNA Miner, Mathematical Preset Blender, XMP Compiler, 3D LUT Exporter, Agent Skill, and MCP Server.**

ChromaDNA extracts reusable color settings from supported Lightroom / Camera Raw preset sources, blends compatible profiles, estimates photo-specific exposure and white-balance adjustments, renders approximate previews, and exports XMP presets and 3D LUTs.

> **Rendering scope:** the preview renderer and .cube exporter are approximations. They do not reproduce every proprietary Adobe Camera Raw operation, camera profile, local adjustment, or RAW rendering stage. Validate generated presets and LUTs in the target application before production use.

## Features

- Preset mining from supported .xmp, embedded XMP in .dng, and legacy .lrtemplate sources.
- Color DNA blending across supported sliders and tone curves.
- Heuristic photo analysis and image-specific exposure / white-balance estimates.
- Approximate Before / After preview rendering.
- XMP preset compilation and 3D .cube LUT export.
- Agent Skill and local FastMCP server.
- Project-local setup for Claude Code, Cursor, Antigravity, and VS Code / GitHub Copilot.

## Requirements

- Python 3.10+
- Node.js 22.20+ and npm for the optional multi-agent setup command
- uv for MCP server execution
- Git (the public repository can be cloned without a GitHub account)

## Install the Python project

From the repository root:

```bash
python -m pip install -e .
```

This installs the chromadna and chromadna-mcp commands with dependencies declared in pyproject.toml. The built wheel also bundles the default community catalog, so installed CLI/MCP commands can run outside the source checkout.

## Quick start

```bash
# Mine your own local preset library into the catalog
chromadna mine ./raw_vault --out data/color_dna_catalog.json

# Inspect exact profile IDs before selecting one
chromadna list

# Blend two profiles and compile an XMP preset
chromadna blend --mix emulsion_kodak_portra_400:0.7 emulsion_cinestill_400d:0.3 --name "Hybrid Film" --out ./output_xmp/hybrid_film.xmp

# Render a preview and export a LUT from the same blend
chromadna blend --mix emulsion_kodak_portra_400:0.7 emulsion_cinestill_400d:0.3 --name "Hybrid Film" --out ./output_xmp/hybrid_film.xmp --preview-img ./sample.jpg --preview-out ./output_xmp/preview.jpg --lut ./output_lut/hybrid_film.cube

# Match a profile to a photo
chromadna match ./sample.jpg --dna emulsion_kodak_portra_400 --name "Matched Film" --preview ./output_xmp/matched_preview.jpg --out ./output_xmp/matched.xmp

# Export a standalone 33-cubed LUT
chromadna lut --dna emulsion_kodak_portra_400 --name "Warm Film" --size 33 --out ./output_lut/warm_film.cube
```

If the package is not installed, use the repository launcher:

```bash
bash scripts/chromadna.sh list
```

PowerShell:

```powershell
.\scripts\chromadna.ps1 list
```

## Multi-agent setup

The GitHub repository is public and can be cloned without authentication. ChromaDNA is not currently published to npm or PyPI. Clone it, then run:

```bash
node scripts/setup.mjs --all
```

The setup command installs the Agent Skill through the Vercel Skills CLI and configures native MCP entries for a wider set of coding agents, including OpenCode, Pi, Cline, Roo Code, Gemini CLI, Kimi Code CLI, Claude Desktop, and Windsurf. A few clients use global configuration files; existing entries are backed up and preserved. It does not publish packages or make the repository public.

Useful variants:

```bash
node scripts/setup.mjs --all --dry-run
node scripts/setup.mjs --skills
node scripts/setup.mjs --mcp --agent=cursor
```

Prefer an AI to perform setup? Copy the single prompt in [Install ChromaDNA with an AI Agent](docs/INSTALL_WITH_AI.md) into any coding agent with terminal access. See [Agent and Client Compatibility](docs/COMPATIBILITY.md) for the full matrix, DeepSeek Harness and Groq API adapters, and cloud-client limitations.

## Community preset catalog

The default catalog contains 451 profiles imported from the pinned [EmulsionPresets](https://github.com/peva3/EmulsionPresets) source revision. The imported records retain their source paths, revision, file hashes, and license information. ChromaDNA does not claim authorship of those preset recipes.

The catalog is **not refreshed automatically**. Maintainers can review and run the pinned importer manually; see [Community Catalog Maintenance](docs/COMMUNITY_CATALOG.md). Third-party notices and the import report live in `data/sources/`.

## Releases

The project version is `0.2.1`. Use **Actions → Release ChromaDNA → Run workflow** to generate/commit `uv.lock`, run the test and build checks, create the matching `v0.2.1` Git tag, and publish a GitHub Release with wheel and source archives. The workflow does not publish to PyPI or npm.

## Agent Skill

The canonical Agent Skill is in skills/chromadna/SKILL.md. The root SKILL.md remains as a compatibility copy for tools that discover a skill from the repository root.

## MCP server

Run the local stdio server after installing the project:

```bash
chromadna-mcp
```

Available tools:

- list_color_dna
- inspect_color_dna
- analyze_photo
- blend_color_dna
- match_photo_to_dna
- render_preview
- compile_xmp_preset
- export_cube_lut

The MCP process can only read files accessible to the machine and user account running it. Attaching an image in a cloud chat does not automatically expose its local filesystem path. The current server is not a hosted remote MCP endpoint.

## Privacy and safety

- Keep source photos, RAW files, and third-party preset binaries out of Git.
- Keep raw_vault/ and generated output files local.
- Do not write generated presets beside RAW files using the same filename stem.
- Do not claim compatibility until the preset or LUT has been tested in the target editor.
- Do not expose the local stdio server to the public internet.

## Contributing

Contributions are welcome. Start with [CONTRIBUTING.md](CONTRIBUTING.md), read the [Code of Conduct](CODE_OF_CONDUCT.md), and review [Security](SECURITY.md) before reporting a vulnerability.

## License

MIT. See [LICENSE](LICENSE).
