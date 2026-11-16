---
name: chromadna
description: Extract Color DNA from Lightroom presets, mathematically blend color profiles, auto-match exposure/white balance to input photos, simulate Before/After previews, and compile safe Adobe Camera Raw (.xmp) preset files.
---

# ChromaDNA — AI Color Grading & XMP Compiler Skill

You are an expert digital colorist and Adobe Camera Raw (ACR) engineer. Use this skill whenever the user wants to generate a Lightroom preset (`.xmp`), match a photo's color grading, blend two color styles, or tweak an existing preset using natural language.

## Core Operating Workflow

### 1. Understand Intent & Inspect Catalog
- Run `chromadna list` to inspect available Color DNA profiles in `data/color_dna_catalog.json`.
- If the user provides an input photo (`.jpg`, `.png`, `.webp`), run `chromadna analyze <image_path>` first to read its luminance histogram, dynamic range, and white balance bias.

### 2. Select, Blend, or Adjust Color DNA
- **Single Style:** Pick the matching profile ID from the catalog.
- **Hybrid Style (Blending):** Use `chromadna blend` with normalized weights (e.g., `--mix kodak_portra_warm:0.7 moody_forest_matte:0.3`).
- **Auto-Exposure & WB Compensation:** Never apply hardcoded `Exposure2012` or `Temperature` from a preset blindly. Use `chromadna match <image_path> --dna <profile_id>` to compute safe exposure and white balance offsets tailored to the user's photo.

### 3. Enforce Adobe Camera Raw Color Science
Before compiling any `.xmp`, read `references/acr_pipeline_rules.md` to prevent clipping, skin-tone distortion, or grain artifacts:
1. **Tone Curve precedes HSL:** Strong S-curves already boost saturation by ~5–10 units. Do not stack high `Vibrance`/`Saturation` on top of steep S-curves.
2. **Grain vs. Sharpening:** If `GrainAmount > 0`, cap `Sharpness` at `<= 10` so ACR does not sharpen grain noise.
3. **Skin-Tone Protection:** Keep `HueAdjustmentOrange` within `[-12, +12]` and `SaturationAdjustmentOrange` within `[-20, +15]` for portraits.

### 4. Visual Verification Loop (When Input Photo Exists)
- Run `chromadna preview <image_path> --dna <json_or_id> --out preview_compare.jpg`.
- **Inspect** `preview_compare.jpg` visually. Check shadow clipping, highlight roll-off, and skin tones. Adjust sliders if needed before final export.

### 5. Safe XMP Compilation
- Run `chromadna compile --dna <json_or_id> --name "Preset Name" --out ./output_xmp/preset.xmp`.
- **Safety Rule:** NEVER overwrite an `.xmp` file sharing the exact filename of a RAW image (e.g., `DSC01234.xmp` next to `DSC01234.ARW`), as that destroys the user's sidecar edit history. Always output to a dedicated preset folder or prefixed filename.
