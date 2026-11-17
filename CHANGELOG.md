# Changelog

Notable user-facing changes are recorded here. Version numbers follow the project version in `pyproject.toml`.

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

- Initial public ChromaDNA CLI, local MCP server, Agent Skill, preset catalog, XMP compiler, preview renderer, and 3D LUT exporter.
