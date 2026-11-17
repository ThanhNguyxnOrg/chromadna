## Summary

Describe the change and the user problem it solves.

## Change type

- [ ] Bug fix
- [ ] Feature
- [ ] Documentation
- [ ] Tests / tooling
- [ ] Packaging / release

## Verification

List the exact commands run and their results.

- [ ] `python -m pytest -q`
- [ ] `node --check scripts/setup.mjs` (when setup code changes)
- [ ] `python -m build` and `python scripts/smoke_test_wheel.py` (when packaging changes)
- [ ] Documentation and examples reviewed

## Compatibility and data provenance

- [ ] Public CLI / MCP behavior remains consistent or migration is documented.
- [ ] Any third-party preset/LUT content has a verified redistribution license and attribution.
- [ ] No private photos, RAW files, credentials, or unrelated generated outputs are included.
- [ ] Unsupported Adobe effects and approximate rendering limits are described accurately.

## Checklist

- [ ] Tests cover the changed behavior.
- [ ] Root `SKILL.md` matches `skills/chromadna/SKILL.md` when either Skill changes.
- [ ] Documentation and changelog are updated when needed.
- [ ] The PR is focused and has no unrelated changes.
