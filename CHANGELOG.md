# Changelog

Notable user-facing changes are recorded here. Version numbers follow the project version in `pyproject.toml`.

## 1.0.1 — 2026-11-19

- Fixed HSL-to-RGB conversion in sector `[300°, 360°)` so magenta hues map to `(C, 0, X)` instead of `(C, X, 0)` in both `.cube` 3D LUTs and Before/After previews.
- Replaced linear averaging of 0°–360° hue sliders with saturation-weighted circular vector blending and deterministic fallback for opposite hues.
- Used neutral Adobe Camera Raw defaults when blending sliders whose neutral value is non-zero (such as `ParametricMidtoneSplit` and `SharpenRadius`).
- Added 3-way `ColorGrade*` shadow, midtone, highlight, and global tint/luminance modeling to `transform_rgb_lattice`.
- Fixed MCP `blend_color_dna` boolean weight coercion (`float(w)`) and removed redundant non-blendable filtering in favor of the shared validator.
- Added EXIF orientation normalization (`ImageOps.exif_transpose`) to `render_before_after` and guaranteed temporary file cleanup on failure in `write_xmp_atomic`.
- Expanded miner deduplication feature vectors to include all four tone curves (`RGB`, `Red`, `Green`, `Blue`) and default-centered slider normalization.
- Added CLI `inspect`, repeatable `--override Key=Value`, graceful `--mix` validation, MCP `match_photo_to_dna` `output_cube_path`, and catalog `mtime` caching.
- Synchronized all version manifests and Agent Skill metadata to `1.0.1`.

## 1.0.0 — 2026-11-17

First stable release of ChromaDNA.

- Provides preset mining for supported .xmp, embedded XMP in .dng, and legacy .lrtemplate sources.
- Adds compatible Color DNA blending, photo analysis, image-specific exposure / white-balance estimates, XMP compilation, and 3D .cube LUT export.
- Includes an approximate Before / After preview renderer using the shared transform kernel for supported operations.
- Ships a local FastMCP server and Agent Skill, with setup guidance for multiple coding agents and MCP clients.
- Bundles the default 451-profile community catalog in standalone Python wheels, with source provenance, revision, hashes, and license notices.
- Rejects invalid blend weights and prevents non-blendable utility / video-reference profiles from entering creative workflows.
- Includes cross-platform CI for Python 3.10, 3.11, and 3.12 on Ubuntu, Windows, and macOS, plus isolated wheel-install smoke testing.
- Community preset refresh remains a deliberate maintainer action; the project does not automatically fetch and commit upstream preset changes.
- GitHub Releases include wheel and source archives. PyPI and npm publishing are not part of this release workflow.

## 0.2.0

- Added the standalone Python CLI, XMP compiler, approximate Before / After preview renderer, and initial starter catalog.
