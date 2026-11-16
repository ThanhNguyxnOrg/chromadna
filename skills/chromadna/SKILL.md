---
name: chromadna
description: Extract and blend Lightroom and Adobe Camera Raw preset color profiles, analyze and match photo color, compile XMP presets, render approximate previews, and export 3D .cube LUTs. Use for Lightroom presets, Camera Raw looks, film emulation, photo color matching, XMP, LUT, and preset-library mining.
license: MIT
compatibility: Requires Python 3.10+, project dependencies, and access to input files on the machine running the CLI or MCP server.
metadata:
  version: "0.2.0"
  repository: "ThanhNguyxnOrg/chromadna"
---

# ChromaDNA

ChromaDNA extracts supported color settings from Lightroom / Camera Raw preset sources, blends compatible profiles, estimates photo-specific adjustments, compiles XMP presets, renders approximate previews, and exports 3D LUTs.

**Important limitation:** the preview renderer and .cube exporter are approximations. They do not reproduce Adobe Camera Raw proprietary rendering, camera profiles, local masks, RAW processing, or every slider operation. Never describe output as pixel-identical to Lightroom.

## Start safely

Run commands from the repository root. Install dependencies with:

```bash
python -m pip install -e .
```

Use the installed CLI or the repository launcher:

```bash
chromadna list
bash scripts/chromadna.sh list
```

On Windows PowerShell:

```powershell
.\scripts\chromadna.ps1 list
```

## Required workflow

1. **Discover profiles before use.** Run chromadna list and use only exact IDs returned by the catalog. Never invent IDs.
2. **Analyze a photo before matching.** Run chromadna analyze ./photo.jpg. Describe computed exposure and white-balance offsets as heuristic estimates, not calibrated measurements.
3. **Blend and compile.** Use chromadna blend --mix <id>:0.7 <id>:0.3 --name "Hybrid Look" --out ./output_xmp/hybrid.xmp.
4. **Export a LUT.** Use chromadna lut --dna <exact-id> --name "Look" --size 33 --out ./output_lut/look.cube.
5. **Inspect generated previews.** If the output image is not accessible for visual inspection, say so. File generation alone is not visual verification.

## Preset mining

Supported source extensions are .xmp, .dng (embedded XMP packet extraction), and .lrtemplate (legacy parser):

```bash
chromadna mine ./raw_vault --out data/color_dna_catalog.json
```

Keep original presets and RAW files outside Git. Do not upload copyrighted preset packs without permission.

## Safety rules

- Write generated XMP files to a dedicated output directory, never beside a RAW file with the same filename stem.
- Do not invent slider keys or claim undocumented Adobe properties are supported.
- Preserve the distinction between creative look selection and image-specific technical compensation.
- Validate generated XMP and LUT files in the target application before production use.
- Treat source photos, RAW files, and user preset libraries as private. Do not commit them.
- Do not claim that a local image attachment is available to an MCP server unless the server can access its filesystem path.

## MCP

When connected, call list_color_dna before selecting a profile. Use analyze_photo, match_photo_to_dna, blend_color_dna, render_preview, compile_xmp_preset, and export_cube_lut as appropriate. The current stdio server accepts filesystem paths visible to the server process; it does not automatically receive images attached to a cloud chat.
