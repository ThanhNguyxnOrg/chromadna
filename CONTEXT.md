# ChromaDNA — Project Context & Architecture

Living architectural brief for humans and AI coding agents. Treat implementation and tests as the source of truth; this document records intended direction, not proof that every capability is implemented.

## 1. Core vision

ChromaDNA is an AI-native color-grading compiler and preset engine for Adobe Lightroom / Camera Raw.

Intended pipeline:
1. Mine develop settings from user-provided XMP sidecars, DNG-embedded XMP, and legacy Lightroom template files.
2. Normalize settings into reusable mathematical profiles called Color DNA.
3. Analyze input images (histogram, dynamic range, color cast) and optionally compensate exposure / white balance before applying a look.
4. Blend profiles using weights, including tone curves with differing control-point counts.
5. Render an explicitly approximate offline preview for an AI vision feedback loop.
6. Compile safe XMP sidecars and 3D .cube LUTs.

The standalone Python CLI and Agent Skill are first-class interfaces. Lightroom itself should not be required for mining, analysis, blending, preview generation, or compilation.

## 2. Ecosystem map

These repositories are architectural references, not bundled dependencies. Verify current licenses and behavior before copying code or data.

| Reference | Useful idea | ChromaDNA's intended differentiation |
|---|---|---|
| https://github.com/peva3/EmulsionPresets | Curated film-emulation presets and LLM-friendly color workflow documentation | Add mining, adaptive matching, blending, and compilation rather than only a static collection |
| https://github.com/Automaat/lightroom-mcp | Lightroom integration and XMP safety practices | Provide an independent computational engine; optional integration can delegate application control to Lightroom MCP |
| https://github.com/drshy-org/lightroom-py | Python CLI and agent-oriented workflow | Emphasize color-profile mathematics and reusable profile data |
| https://github.com/javierbyte/lightroom-interpolator | Interpolating XMP settings for timelapse workflows | Generalize blending to multiple profiles and tone curves |

The table describes intended differentiation, not a formal benchmark. Do not assert deficiencies without checking the current upstream source.

## 3. Technical pillars

### Color engine
- Normalize slider ranges and validate profile schemas.
- Resample tone curves onto a common grid before blending.
- Distinguish preview approximations from Adobe's proprietary rendering pipeline.
- Explore CIELAB / Oklab analysis, histogram matching, and skin-tone protection.

### AI agent ecosystem
- Keep SKILL.md accurate and document only implemented CLI commands.
- Consider an optional FastMCP server for mining, analysis, blending, preview, and compilation.
- A visual self-correction loop may render previews, inspect clipping / color shifts, adjust settings, and repeat. It must not claim Adobe-rendered fidelity.

### UX and community
- Consider a TUI or web preset mixer after the core engine and tests stabilize.
- Support semantic profile discovery using tags and profile vectors.
- Treat reverse-engineering a look from before/after image pairs as research with ambiguity and optimization limits.

### Interoperability
- XMP for Lightroom / Camera Raw.
- 3D .cube LUT for applications that support the format.
- Grain, vignette, local masks, and other spatial or stochastic effects cannot be represented faithfully in a conventional 3D color LUT.

## 4. 3D LUT exporter

src/chromadna/lut_exporter.py provides an initial vectorized RGB-lattice transform and .cube writer. The default grid is 33 × 33 × 33 (35,937 samples), with red varying fastest, then green, then blue.

The initial implementation models selected global settings, tone curves, HSL bands, split-toning-like controls, vibrance, and saturation. These are approximations, not an exact reproduction of Adobe Camera Raw. Temperature / tint, exposure, tonal recovery, HSL weighting, and color grading are simplified. Camera profiles, local adjustments, masks, grain, and spatial effects are not represented. Verify generated LUT behavior in each target application.

CLI integration is a follow-up: add a lut subcommand that loads a catalog profile or blends profiles, then calls write_cube_lut_atomic. Do not document the command as available until it exists and is tested.

## 5. Roadmap

1. Restore and validate the core Python package and catalog.
2. Add tests for XMP parsing, schema validation, curve sanitation, blending, compiler safety, preview behavior, and LUT generation.
3. Integrate the LUT exporter into the CLI and test header, sample count, ordering, identity behavior, and atomic output.
4. Add CI, type checks, linting, and packaging verification.
5. Improve color science with perceptual spaces and measured reference fixtures.
6. Explore FastMCP, semantic search, TUI/web mixer, and image-pair look fitting.

## 6. Agent operating instructions

1. Read this file, README.md, SKILL.md, pyproject.toml, and the actual source tree.
2. Inspect implementation before editing; do not assume a command exists because it appears in a roadmap.
3. Preserve public APIs unless a migration is deliberate and documented.
4. Add tests with each behavior change. Run the full test suite and quality checks.
5. Validate generated XMP and LUT outputs, avoid overwriting source RAW files, and use atomic writes.
6. Distinguish implemented, tested, approximate, and planned capabilities.
7. Prefer direct commits to main when explicitly requested; do not open a PR unless asked.
8. Check licenses and provenance before copying preset collections or proprietary profile data.

## 7. Suggested next task

Integrate lut_exporter.py into the actual CLI only after inspecting cli.py. Add chromadna lut --dna <id> --out <path> and weighted --mix support, validate malformed weights and IDs, then test a small LUT size before generating the default 33-cubed output.
