---
name: chromadna
description: Extract and blend Lightroom and Adobe Camera Raw preset color profiles, analyze and match photo color, compile XMP presets, render approximate previews, and export 3D .cube LUTs. Use for Lightroom presets, Camera Raw looks, film emulation, photo color matching, XMP, LUT, and preset-library mining.
license: MIT
compatibility: Requires Python 3.10+, the ChromaDNA repository, and its Python dependencies. Photo paths must be accessible to the process running the CLI or MCP server.
metadata:
  version: "0.2.0"
  repository: "ThanhNguyxnOrg/chromadna"
---

# ChromaDNA — Color DNA, XMP and 3D LUT

Use ChromaDNA to inspect, extract, blend, match, preview, and export reusable color looks. The Python preview renderer and generated 3D LUT are approximations of Adobe Camera Raw; neither reproduces every proprietary ACR operation, local mask, camera profile, or RAW rendering behavior.

## Runtime

Run commands from the repository root. Prefer the installed chromadna executable. If it is unavailable, use the repository launcher:

```bash
bash scripts/chromadna.sh list
```

Or invoke the module directly (dependencies must already be installed):

```bash
PYTHONPATH=src python3 -m chromadna.cli list
```

On Windows PowerShell:

```powershell
.\scripts\chromadna.ps1 list
```

Install the project and dependencies with python -m pip install -e . The MCP server additionally requires the mcp dependency declared in pyproject.toml.

## Required workflow

### 1. Discover IDs — never guess

Always inspect the catalog before selecting a profile:

```bash
chromadna list
chromadna list --tag matte
```

Use only exact IDs returned by chromadna list or present in data/color_dna_catalog.json. Never invent, infer, or silently rename a dna_id. If the catalog is missing, explain that the user must mine source presets first:

```bash
chromadna mine ./raw_vault --out data/color_dna_catalog.json
```

Do not commit original third-party preset files; keep raw_vault/ private and gitignored.

### 2. Analyze or match a supplied photo

For a supplied image, analyze it before recommending a look:

```bash
chromadna analyze ./photo.jpg
```

Then use the chosen profile ID to compute image-specific technical compensation:

```bash
chromadna match ./photo.jpg --dna <exact-id> --name "Matched Look" --out ./output_xmp/matched.xmp --preview ./output_xmp/preview.jpg
```

Do not guess exposure or white-balance offsets. Keep creative look selection separate from image-specific technical correction. The matcher is heuristic; describe its offsets as computed estimates, not calibrated measurements.

### 3. Blend, compile, or export

Blend two or more profiles:

```bash
chromadna blend --mix <id-1>:0.7 <id-2>:0.3 --name "Hybrid Look" --out ./output_xmp/hybrid.xmp
```

Optionally render a preview and export a LUT from the same blended DNA:

```bash
chromadna blend --mix <id-1>:0.7 <id-2>:0.3 --name "Hybrid Look" --out ./output_xmp/hybrid.xmp --preview-img ./photo.jpg --preview-out ./output_xmp/preview.jpg --lut ./output_lut/hybrid.cube
```

Compile a standalone XMP preset:

```bash
chromadna compile --dna <exact-id> --name "Preset Name" --out ./output_xmp/preset.xmp
```

Export a single-profile or blended 3D LUT (default grid size 33):

```bash
chromadna lut --dna <exact-id> --name "LUT Title" --out ./output_lut/look.cube
chromadna lut --mix <id-1>:0.65 <id-2>:0.35 --name "Hybrid LUT" --size 33 --out ./output_lut/hybrid.cube
```

The match command also accepts --lut <path> to export a LUT from the adapted profile.

### 4. Inspect previews honestly

When a preview is generated, inspect the actual output image if the runtime provides image viewing. Check highlight clipping, crushed shadows, color casts, and skin-tone shifts. If you cannot access the output image, say so; do not claim visual verification.

Consult references/acr_pipeline_rules.md before changing interacting Camera Raw sliders. Use only parameter names and bounds defined by the project schema. Never fabricate crs:* XMP properties or claim an undocumented tag is supported.

## Mandatory guardrails

- **Protect RAW sidecars:** never write an XMP preset beside a RAW file using the same stem (for example, IMG_001.xmp beside IMG_001.CR3). Use a dedicated output directory such as ./output_xmp/.
- **Grain and sharpening:** when GrainAmount > 0, keep Sharpness <= 10.
- **Avoid double saturation:** steep tone curves can increase perceived chroma; do not stack aggressive global saturation without inspecting the result.
- **No invented IDs or schema keys:** list profiles first; inspect references/slider_schema.json and the implementation schema before using parameter names. Never invent crs:* tags.
- **No false validation claims:** successful file generation does not prove Lightroom/ACR import compatibility or visual equivalence. State what was and was not tested.
- **Privacy and copyright:** do not commit source photos, RAW files, or third-party preset binaries. Keep private source material outside Git.

## MCP tools

When the ChromaDNA MCP server is connected, use its tools for the same workflow: call list_color_dna before choosing IDs; then use analyze_photo, match_photo_to_dna, blend_color_dna, render_preview, compile_xmp_preset, or export_cube_lut as appropriate. MCP image paths refer to files accessible to the server process; attaching an image in a chat does not automatically make its local path available to the server.
