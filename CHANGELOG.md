# Changelog

Notable user-facing changes are recorded here. Version numbers follow the project version in `pyproject.toml`.

## 0.2.1 — Unreleased

- Hardened blend-weight validation and rejected non-blendable utility/video-reference profiles in creative workflows.
- Made preview rendering reuse the LUT transform kernel for supported operations.
- Bundled the default 451-profile catalog in built Python wheels.
- Expanded automated tests and the Ubuntu / Windows / macOS CI matrix.
- Synchronized the root and canonical Agent Skill documentation.
- Added maintainer guidance, contribution templates, and catalog provenance documentation.
- Removed the GitHub Actions workflow that automatically imported and committed third-party community presets. Catalog refresh is now an explicit maintainer action.
- Added a manual GitHub Release workflow. PyPI and npm publishing remain separate and are not performed by that workflow.

## 0.2.0

- Initial public ChromaDNA CLI, local MCP server, Agent Skill, preset catalog, XMP compiler, preview renderer, and 3D LUT exporter.
