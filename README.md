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
- Node.js and npm for the optional multi-agent setup command
- uv for MCP server execution
- Git access to this private repository

## Install the Python project

From the repository root:

```bash
python -m pip install -e .
```

This installs the chromadna and chromadna-mcp commands with dependencies declared in pyproject.toml.

## Quick start

```bash
# Mine your own local preset library into the catalog
chromadna mine ./raw_vault --out data/color_dna_catalog.json

# Inspect exact profile IDs before selecting one
chromadna list

# Blend two profiles and compile an XMP preset
chromadna blend --mix warm_film_01:0.7 moody_teal_02:0.3 --name "Hybrid Film" --out ./output_xmp/hybrid_film.xmp

# Render a preview and export a LUT from the same blend
chromadna blend --mix warm_film_01:0.7 moody_teal_02:0.3 --name "Hybrid Film" --out ./output_xmp/hybrid_film.xmp --preview-img ./sample.jpg --preview-out ./output_xmp/preview.jpg --lut ./output_lut/hybrid_film.cube

# Match a profile to a photo
chromadna match ./sample.jpg --dna warm_film_01 --name "Matched Film" --preview ./output_xmp/matched_preview.jpg --out ./output_xmp/matched.xmp

# Export a standalone 33-cubed LUT
chromadna lut --dna warm_film_01 --name "Warm Film" --size 33 --out ./output_lut/warm_film.cube
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

The repository is private and is not published to npm or PyPI. Clone it with an authenticated GitHub account, then run:

```bash
node scripts/setup.mjs --all
```

The setup command installs the Agent Skill through the Vercel Skills CLI and configures project-local MCP entries for supported clients. It does not publish packages, make the repository public, or modify global configuration.

Useful variants:

```bash
node scripts/setup.mjs --all --dry-run
node scripts/setup.mjs --skills
node scripts/setup.mjs --mcp --agent=cursor
```

See [Agent and Client Compatibility](docs/COMPATIBILITY.md) for the integration matrix, cloud-client limitations, and manual adapters.

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

## License

MIT. See [LICENSE](LICENSE).
