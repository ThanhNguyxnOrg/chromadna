# ChromaDNA maintenance hardening design

Date: 2026-11-17

## Intent

Bring the public ChromaDNA repository's documentation, install guidance, agent skill, validation behavior, tests, dependency policy, and release path into alignment with the working implementation. The intended audience is developers and AI agents installing or operating the CLI/MCP integration.

## Goals

- Remove incorrect statements that the public repository is private.
- Keep the two supported Skill entry points synchronized.
- Reject invalid blend weights and non-creative profiles consistently across CLI and MCP blend/match/preview/LUT operations.
- Reject unknown or invalid MCP slider overrides instead of silently ignoring them.
- Use one shared approximate RGB transform for preview rendering and LUT generation.
- Add regression tests for the above and expand build/test checks.
- Bound direct dependency versions and provide a controlled workflow that generates/commits uv.lock and creates a GitHub Release/tag with built archives.

## Non-goals

- Do not claim pixel-identical Adobe Camera Raw rendering.
- Do not expose a hosted MCP endpoint.
- Do not publish to PyPI or npm.
- Do not change repository visibility or create a pull request.

## Approaches considered

1. Documentation-only cleanup: lowest risk but leaves the validation and preview/LUT drift unchanged.
2. A focused maintenance patch (selected): fix documentation and known cross-interface correctness gaps, share the transform kernel, expand tests, bound dependencies, and create manual release automation. This addresses the reported issues without changing the product architecture.
3. A color-engine redesign: potentially improves fidelity, but requires reference images, editor-side validation, and a separate design effort; it is not suitable for this maintenance pass.

## Constraints and decisions

- Preserve Python 3.10+ support.
- Keep dependencies compatible with NumPy 1.x/2.x, Pillow 10-13, and MCP 1.x using explicit upper bounds.
- Generate a full uv.lock with the online resolver in the GitHub-hosted release workflow; this execution environment cannot reach GitHub/PyPI to resolve package metadata.
- GitHub Release creation is manual and tag/version-matched. The workflow builds wheel and source archives, but does not publish to package registries.
- Commit directly to main; no PR or issue creation.
