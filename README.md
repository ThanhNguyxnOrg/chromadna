# ChromaDNA

**Adobe Lightroom / Camera Raw Color DNA Miner, Mathematical Preset Blender & AI Agent Skill.**

ChromaDNA extracts the mathematical "Color DNA" (Tone Curves, HSL matrices, 3-Way Color Grading wheels, Camera Calibration) from `.xmp`, `.dng`, and `.lrtemplate` libraries, strips proprietary metadata/local adjustments, and empowers both CLI users and AI Agents (Claude Code, Cursor, Gemini CLI, OpenCode) to **match, blend, preview, and compile** production-ready `.xmp` presets without opening Lightroom.

## Features
- **Universal Preset Miner (`miner.py`):** Recursively parses `.xmp`, embedded XMP packets inside `.dng` RAW files, and legacy `.lrtemplate` Lua tables. Deduplicates identical looks using cosine similarity on normalized parameter vectors.
- **Mathematical Curve & Slider Blender (`blender.py`):** Resamples non-uniform Tone Curves onto a uniform 32-point spline grid to smoothly interpolate between any number of presets (e.g., `70% Kodak Portra + 30% Moody Matte`).
- **Auto Exposure & White Balance Matcher (`matcher.py`):** Separates *Technical Correction* from *Creative Look* by analyzing target image luminance and color cast before applying a Color DNA.
- **Fast Offline Previewer (`previewer.py`):** Generates side-by-side Before/After JPEG previews using NumPy vectorized LUTs and RGB/HSL transforms.
- **Atomic XMP Compiler (`compiler.py`):** Validates every Adobe Camera Raw parameter against strict schema bounds and writes valid RDF/XML `.xmp` files atomically.

## Installation
```bash
pip install -e .
```

## Quick Start
```bash
# 1. Extract & deduplicate your local preset folder into Color DNA catalog
chromadna mine ./raw_vault --out data/color_dna_catalog.json

# 2. List available Color DNA profiles
chromadna list

# 3. Blend two styles (70% Warm Film + 30% Moody Teal) and compile to .xmp
chromadna blend --mix warm_film_01:0.7 moody_teal_02:0.3 --name "Hybrid Film" --out ./output_xmp/hybrid_film.xmp

# 4. Auto-match a photo and render a Before/After preview
chromadna match sample.jpg --dna warm_film_01 --preview preview.jpg --out ./output_xmp/matched.xmp
```
