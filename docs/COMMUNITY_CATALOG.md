# Community Catalog Maintenance

## Current catalog

The checked-in `data/color_dna_catalog.json` contains 451 profiles imported from [peva3/EmulsionPresets](https://github.com/peva3/EmulsionPresets) at pinned revision `4312c978a3331ed69f87fd47c98a9c2a3caa2d26`.

The upstream catalog declares an MIT license. ChromaDNA retains the upstream license text and attribution in [THIRD_PARTY_NOTICES.md](../data/sources/THIRD_PARTY_NOTICES.md). Per-file source paths, hashes, and import results are recorded in [emulsionpresets-import-report.json](../data/sources/emulsionpresets-import-report.json).

The imported presets remain third-party works. ChromaDNA does not claim authorship of their recipes.

## No automatic upstream import

The GitHub Actions workflow that downloaded and committed upstream community presets has been removed. There is no schedule or background workflow that changes the catalog. Normal CI only validates the repository's checked-in content.

The Python importer remains at `scripts/import_community_presets.py` as a manual maintainer utility so the catalog can be reproduced from its pinned source when intentionally updating or auditing it.

## Rebuild or update procedure

Run from the repository root:

```bash
python -m pip install -e ".[dev]"
python scripts/import_community_presets.py
```

The importer fetches the pinned upstream manifest, license, and XMP files, then rewrites:

- `data/color_dna_catalog.json`
- `data/sources/emulsionpresets-import-report.json`
- `data/sources/THIRD_PARTY_NOTICES.md`

The importer currently expects 451 source entries at the pinned revision. It is not an automatic update-to-latest command. To adopt a newer upstream revision, a maintainer must first inspect that revision's license and manifest, update the pin and expected entry count in the importer, and review representative XMP files.

After import:

1. Review the full catalog diff; do not accept a mass change just because the script exited successfully.
2. Confirm each imported entry has a unique stable ID, provenance, source SHA-256, and the correct blendable/profile-kind classification.
3. Inspect any failed files and unsupported numeric-field report entries.
4. Run `python -m pytest -q`.
5. Run `python -m build` and `python scripts/smoke_test_wheel.py` when packaging or catalog bundling changes.
6. Verify the license and attribution text has not been removed or replaced.
7. Submit the reviewed catalog change through the normal maintainer contribution process.

Do not import paid presets, private user collections, or content whose license does not clearly permit redistribution. Do not copy camera profiles, DCP files, embedded LUTs, or local-mask data unless their redistribution rights and implementation support have been separately reviewed.
