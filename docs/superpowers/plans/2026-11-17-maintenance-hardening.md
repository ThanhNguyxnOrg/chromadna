# ChromaDNA Maintenance Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Align ChromaDNA docs and agent entry points, harden shared validation, expand regression coverage, and provide reproducible dependency/release automation.

**Architecture:** Keep the existing Python CLI, shared core modules, and local FastMCP server. Centralize profile/weight validation in the blender module, route previews through the LUT transform kernel, and use GitHub Actions for lockfile generation and GitHub Release creation.

**Tech Stack:** Python 3.10+, NumPy, Pillow, FastMCP, pytest, uv, GitHub Actions.

**Spec:** docs/superpowers/specs/2026-11-17-maintenance-hardening-design.md

## Global Constraints

- Preserve Python 3.10+ support.
- Use dependency bounds: NumPy >=1.24,<3.0; Pillow >=10,<14; MCP >=1,<2.
- Keep the GitHub repository public; do not change visibility.
- No PyPI/npm publication.
- Do not create PRs or issues; commit directly to main.
- Preview/LUT remain approximations, never pixel-identical ACR output.

## Review Focus

- Negative, boolean, NaN, and infinite blend weights must be rejected.
- Utility and video-reference profiles must not enter creative blend/match/preview/LUT workflows.
- Unknown, non-numeric, NaN, and infinite MCP overrides must fail loudly.
- Preview pixels outside the label overlay must equal the shared transform kernel's output.
- The release workflow must reject a tag that does not match pyproject.toml and must not recreate an existing tag.

---

### Task 1: Shared profile and numeric validation

**Files:**
- Modify: src/chromadna/schema.py
- Modify: src/chromadna/blender.py
- Modify: src/chromadna/matcher.py
- Modify: src/chromadna/cli.py
- Modify: src/chromadna/mcp_server.py
- Test: tests/test_core.py
- Test: tests/test_blender.py
- Test: tests/test_mcp_server.py

- [ ] Add tests for invalid numeric slider values, bad blend weights, non-blendable profile kinds, and invalid MCP overrides.
- [ ] Implement finite numeric checks in clamp_slider.
- [ ] Centralize blendability and weight checks in blender.py.
- [ ] Apply the shared guard to direct-profile match, preview, and LUT paths.
- [ ] Run the complete pytest suite.

### Task 2: Shared preview/LUT transform

**Files:**
- Modify: src/chromadna/previewer.py
- Test: tests/test_preview.py

- [ ] Add a preview test that computes expected pixels with transform_rgb_lattice.
- [ ] Replace the duplicate preview math with the shared LUT transform.
- [ ] Run preview and full-suite tests.

### Task 3: Public docs, Skill synchronization, and metadata

**Files:**
- Modify: README.md
- Modify: docs/COMPATIBILITY.md
- Modify: docs/INSTALL_WITH_AI.md
- Modify: CONTEXT.md
- Modify: SKILL.md
- Modify: skills/chromadna/SKILL.md
- Modify: tasks/community-preset-catalog-ingestion.yml
- Modify: plugin.json
- Modify: .claude-plugin/plugin.json
- Modify: .codex-plugin/plugin.json

- [ ] Remove false private-repository instructions.
- [ ] Synchronize root and canonical Skill files byte-for-byte.
- [ ] Replace stale synthetic profile IDs in examples with actual catalog IDs.
- [ ] Correct outdated implementation roadmap statements and task YAML line breaks.
- [ ] Update plugin metadata to 0.2.1.

### Task 4: Dependency and release automation

**Files:**
- Modify: pyproject.toml
- Modify: .github/workflows/ci.yml
- Modify: .github/workflows/community-presets.yml
- Create: .github/workflows/release.yml

- [ ] Add compatible direct-dependency upper bounds and a build dependency.
- [ ] Make CI use uv.lock when present while retaining bootstrap fallback before first lock generation.
- [ ] Upgrade checkout/setup-python actions to Node 24-compatible majors.
- [ ] Add a manual release workflow that generates uv.lock, verifies tests/build, commits the lock with the app identity, and creates a matching GitHub Release/tag.
- [ ] Do not publish packages to PyPI/npm.

### Task 5: Verify and review

- [ ] Verify the root and canonical Skill copies are identical.
- [ ] Verify no stale private-repository claims or synthetic IDs remain in published docs.
- [ ] Run the full CI matrix and inspect the new run.
- [ ] Inspect the committed tree and release workflow source.
- [ ] Record any action requiring a manual workflow dispatch.
