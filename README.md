# ChromaDNA

**Adobe Lightroom / Camera Raw Color DNA Miner, Mathematical Preset Blender, XMP Compiler, 3D LUT Exporter, Agent Skill & MCP Server.**

ChromaDNA extracts reusable mathematical color profiles from supported Lightroom / Camera Raw preset sources, blends profiles, estimates photo-specific exposure and white-balance adjustments, renders approximate previews, and exports XMP presets and 3D LUTs.

> **Rendering scope:** the preview renderer and .cube exporter are approximations. They do not reproduce every proprietary Adobe Camera Raw operation, camera profile, local adjustment, or RAW rendering stage. Validate generated presets and LUTs in the target application before production use.

## Features

- Preset mining: parse supported .xmp, embedded XMP in .dng, and legacy .lrtemplate sources.
- Color DNA blending: interpolate supported sliders and tone curves across weighted profiles.
- Photo matching: estimate image-specific exposure and white-balance offsets.
- Preview rendering: generate side-by-side Before/After JPEG previews.
- XMP compilation and 3D LUT export.
- Portable Agent Skill and FastMCP server with eight tools.

## Installation

Requires Python 3.10+. From the repository root:

~~~bash
python -m pip install -e .
~~~

This installs the chromadna and chromadna-mcp commands and dependencies declared in pyproject.toml.

## Quick start

~~~bash
# Mine your own preset library into the local catalog
chromadna mine ./raw_vault --out data/color_dna_catalog.json

# Inspect available profile IDs before selecting one
chromadna list

# Blend two profiles and compile an XMP preset
chromadna blend --mix warm_film_01:0.7 moody_teal_02:0.3 --name "Hybrid Film" --out ./output_xmp/hybrid_film.xmp

# Render a preview and export a LUT from the same blend
chromadna blend --mix warm_film_01:0.7 moody_teal_02:0.3 --name "Hybrid Film" --out ./output_xmp/hybrid_film.xmp --preview-img ./sample.jpg --preview-out ./output_xmp/preview.jpg --lut ./output_lut/hybrid_film.cube

# Match a profile to a photo
chromadna match ./sample.jpg --dna warm_film_01 --name "Matched Film" --preview ./output_xmp/matched_preview.jpg --out ./output_xmp/matched.xmp

# Export a standalone 33-cubed LUT
chromadna lut --dna warm_film_01 --name "Warm Film" --size 33 --out ./output_lut/warm_film.cube
~~~

If the package is not installed, repository-local launchers are available:

~~~bash
./scripts/chromadna.sh list
~~~

PowerShell:

~~~powershell
.\scripts\chromadna.ps1 list
~~~

The launchers set PYTHONPATH=src; Python dependencies still need to be installed.

## Agent Skill installation

The root SKILL.md follows the Agent Skills format. With the Vercel Skills CLI:

~~~bash
npx skills add ThanhNguyxnOrg/chromadna --skill chromadna
~~~

The repository is currently private. Installers need GitHub access through Git credentials, GitHub CLI authentication, or SSH.

## Claude Code plugin

The repository includes .claude-plugin/plugin.json, .claude-plugin/marketplace.json, and a plugin-root .mcp.json.

In Claude Code, add the repository as a marketplace and install the plugin:

~~~text
/plugin marketplace add ThanhNguyxnOrg/chromadna
/plugin install chromadna@chromadna-marketplace
~~~

The MCP configuration uses uv to run the project from the installed plugin directory. Install uv on the host machine before enabling the plugin. The catalog path defaults to data/color_dna_catalog.json within the plugin; override CHROMADNA_CATALOG if your catalog is stored elsewhere.

## MCP server

Run the stdio server after installing the project:

~~~bash
chromadna-mcp
~~~

Available tools:
- list_color_dna
- inspect_color_dna
- analyze_photo
- blend_color_dna
- match_photo_to_dna
- render_preview
- compile_xmp_preset
- export_cube_lut

For standalone MCP clients, configure command chromadna-mcp and set CHROMADNA_CATALOG to the catalog's absolute path. The MCP process can only read files accessible to the machine and user account running it; attaching an image in chat does not automatically expose its local path.

## Safety and privacy

- Keep source photos, RAW files, and third-party preset binaries out of Git.
- Keep raw_vault/ and generated output files local.
- Do not write generated presets beside RAW files using the same filename stem.
- Do not claim compatibility until the preset or LUT has been tested in the target editor.

## License

MIT. See LICENSE.
