# ChromaDNA

**Extract, analyze, blend, and compile photographic color profiles.**

ChromaDNA is a Python toolkit for working with Adobe Camera Raw (ACR) / Lightroom-style develop settings as reusable, composable color profiles.

## Project status

This repository is being initialized. The original implementation source is being restored into this repository incrementally; this README is an initial repository file, **not a claim that the full application has been uploaded or verified**.

## Intended capabilities

- Import develop settings from XMP sidecars and Lightroom template data.
- Analyze and compare color adjustments.
- Store reusable color DNA profiles in a catalog.
- Blend profiles with weighted combinations.
- Compile profile data back into XMP.
- Optionally generate approximate previews and match suggestions.

## Important limitation

Any preview renderer is an approximation. It should not be represented as pixel-identical to Adobe Camera Raw or Lightroom. Actual compatibility must be verified by importing generated XMP into the target Adobe application.

## Development

The package layout, CLI, schemas, tests, and CI will be documented here as the implementation is restored.

## License

Not yet selected.
