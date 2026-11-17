---
name: chromadna
description: Extract and blend Lightroom and Adobe Camera Raw preset color profiles, analyze and match photo color, compile XMP presets, render approximate previews, and export 3D .cube LUTs. Use for Lightroom presets, Camera Raw looks, film emulation, photo color matching, XMP, LUT, and preset-library mining.
license: MIT
compatibility: Requires Python 3.10+, project dependencies, and access to input files on the machine running the CLI or MCP server.
metadata:
  version: "0.2.1"
  repository: "ThanhNguyxnOrg/chromadna"
---

# ChromaDNA

ChromaDNA extracts supported color settings from Lightroom / Camera Raw preset sources, blends compatible profiles, estimates photo-specific adjustments, compiles XMP presets, renders approximate previews, and exports 3D LUTs.

**Important limitation:** the preview renderer and .cube exporter share an approximate RGB transform. They do not reproduce Adobe Camera Raw's proprietary rendering pipeline, camera profiles, local masks, RAW processing, spatial effects, or every slider operation. Never describe output as pixel-identical to Lightroom.

## Runtime and installation

The GitHub repository is public. Clone it without authentication:

```bash
git clone https://github.com/ThanhNguyxnOrg/chromadna.git
cd chromadna
python -m pip install -e ".[dev]"
```

Run commands from the repository root. On Windows PowerShell:

```powershell
.\scripts\chromadna.ps1 list
```

On macOS/Linux:

```bash
chromadna list
bash scripts/chromadna.sh list
```

## Required workflow

1. **Discover profiles before use.** Run `chromadna list` and use only exact IDs returned by the catalog. Never invent IDs.
2. **Analyze a photo before matching.** Run `chromadna analyze ./photo.jpg`. Describe computed exposure and white-balance offsets as heuristic estimates, not calibrated measurements.
3. **Blend compatible creative profiles only.** Example:
   ```bash
   chromadna blend --mix emulsion_kodak_portra_400:0.7 emulsion_cinestill_400d:0.3 --name "Hybrid Look" --out ./output_xmp/hybrid.xmp
   ```
   Utility/reset profiles and video-reference records are non-blendable. The engine rejects negative, non-finite, malformed, and all-zero weights.
4. **Match a profile to a photo.**
   ```bash
   chromadna match ./photo.jpg --dna emulsion_kodak_portra_400 --name "Matched Look" --out ./output_xmp/matched.xmp
   ```
5. **Export a LUT.**
   ```bash
   chromadna lut --dna emulsion_kodak_portra_400 --name "Look" --size 33 --out ./output_lut/look.cube
   ```
6. **Inspect generated previews.** The preview renderer uses the same approximate transform kernel as the LUT exporter for supported operations. If the output image is not accessible for visual inspection, say so. File generation alone is not visual verification.

## Preset mining

Supported source extensions are .xmp, .dng (embedded XMP packet extraction), and .lrtemplate (legacy parser):

```bash
chromadna mine ./raw_vault --out data/color_dna_catalog.json
```

The default community catalog contains 451 profiles imported from a pinned upstream revision. Release wheels bundle the catalog and can run outside the source checkout. Keep original presets and RAW files outside Git. Do not upload copyrighted preset packs without permission.

## Safety and compatibility

- Write generated XMP files to a dedicated output directory, never beside a RAW file with the same filename stem.
- Do not invent slider keys or claim undocumented Adobe properties are supported.
- Preserve the distinction between creative look selection and image-specific technical compensation.
- Unknown or invalid MCP slider overrides are rejected rather than silently ignored.
- Validate generated XMP and LUT files in their target applications before production use.
- Treat source photos, RAW files, and user preset libraries as private. Do not commit them.
- Do not claim that a local image attachment is available to an MCP server unless the server can access its filesystem path.
- The local MCP server uses stdio and filesystem paths visible to its process; it is not a hosted remote endpoint.

## MCP tools

When connected, call `list_color_dna` before selecting a profile. Use `inspect_color_dna`, `analyze_photo`, `match_photo_to_dna`, `blend_color_dna`, `render_preview`, `compile_xmp_preset`, and `export_cube_lut` as appropriate. Check `blendable` and `profile_kind` before choosing a profile. The server rejects non-blendable profiles in blend, match, preview, and LUT operations.
