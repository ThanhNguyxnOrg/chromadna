# Contributing to ChromaDNA

Thanks for helping improve ChromaDNA. This project combines a Python color-processing library, CLI, local MCP server, Agent Skill, and a provenance-aware catalog of Lightroom / Camera Raw settings.

Please keep changes focused, testable, and honest about rendering limitations.

## Before you start

- Read the [README](README.md), [Agent and Client Compatibility](docs/COMPATIBILITY.md), and [Community Catalog Maintenance](docs/COMMUNITY_CATALOG.md) when your change touches those areas.
- For substantial changes, open an issue first to discuss the proposed behavior. For a small typo or isolated documentation fix, a pull request can be opened directly.
- Do not include private photographs, RAW files, paid preset packs, credentials, or unrelated generated outputs in a contribution.

## Development setup

Requirements: Python 3.10 or newer. Node.js 22.20+ and npm are only needed to test the optional multi-agent setup helper.

```bash
git clone https://github.com/ThanhNguyxnOrg/chromadna.git
cd chromadna
python -m pip install -e ".[dev]"
```

## Checks to run

Run the complete Python test suite:

```bash
python -m pytest -q
```

For changes to the setup helper:

```bash
node --check scripts/setup.mjs
node scripts/setup.mjs --all --dry-run
```

For packaging changes:

```bash
python -m build
python scripts/smoke_test_wheel.py
```

The wheel smoke test installs the built wheel into an isolated environment outside the checkout and checks that the bundled catalog can be read. Do not claim a packaging change is verified if this step was skipped.

CI tests Python 3.10, 3.11, and 3.12 on Ubuntu, Windows, and macOS. Please include the exact command and result in your pull request description.

## Where changes belong

- `src/chromadna/`: Python library, CLI, MCP server, color math, XMP and LUT handling.
- `tests/`: regression and integration tests. Add tests alongside behavior changes.
- `data/color_dna_catalog.json`: canonical application catalog.
- `data/sources/`: third-party notices, provenance reports, and source metadata.
- `scripts/`: local setup, platform launchers, packaging checks, and maintainer utilities.
- `skills/chromadna/SKILL.md`: canonical Agent Skill. Keep the root `SKILL.md` byte-for-byte synchronized with it.
- `docs/`: user and maintainer documentation.
- `.github/workflows/`: CI and deliberate release automation. Do not add scheduled jobs that download or commit third-party presets without maintainer review.

## Preset, LUT, and source-data contributions

Only contribute preset or LUT material when its license clearly permits redistribution in this repository.

For each third-party item, retain:

- Original project or author URL.
- Exact upstream revision or release identifier.
- Source file path and a SHA-256 checksum where applicable.
- The applicable license and attribution text.
- Any unsupported Adobe metadata or effects that were not converted.

Do not assume that every file in an external repository shares the same license. Do not add material from paid packs, private collections, or sources with unclear redistribution rights. Never present an upstream preset as authored by ChromaDNA.

The community importer is a **manual maintainer tool**, not a scheduled GitHub Actions workflow. See [Community Catalog Maintenance](docs/COMMUNITY_CATALOG.md) before using it.

## Code and documentation guidelines

- Preserve Python 3.10 compatibility.
- Add type hints to new public functions and keep errors actionable.
- Validate finite numeric inputs and filesystem paths at public interfaces.
- Keep CLI, MCP, and library behavior consistent.
- Avoid silently dropping unsupported slider fields or metadata.
- Mark heuristic estimates and approximate preview/LUT behavior explicitly.
- Update examples when public command names, arguments, or profile IDs change.
- Keep the root and canonical Skill files synchronized.

## Pull requests

1. Use a focused branch such as `fix/blend-weight-validation`, `feat/profile-search`, or `docs/install-guide`.
2. Use a descriptive commit message. Conventional Commit prefixes such as `fix:`, `feat:`, `docs:`, and `test:` are encouraged.
3. Explain the problem and the behavior change.
4. List tests and checks actually run, including failures or skipped checks.
5. Mention compatibility, migration, licensing, and documentation impact.
6. Keep each pull request focused. Do not combine unrelated refactors with a bug fix.

Do not change the project version for ordinary contributions. Version bumps and GitHub Releases are maintainer-managed. ChromaDNA is a Python project: do not add npm publishing steps or publish to npm.

## License

By submitting a code contribution, you agree that the contribution may be distributed under the repository's MIT license. Third-party preset and LUT assets remain subject to their own source licenses and notices.
