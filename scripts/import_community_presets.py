#!/usr/bin/env python3
"""Import the pinned EmulsionPresets XMP catalog into ChromaDNA."""
from __future__ import annotations
import hashlib, json, re, sys, urllib.error, urllib.parse, urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from chromadna.miner import infer_style_tags, parse_xmp_string

UPSTREAM = "peva3/EmulsionPresets"
REVISION = "4312c978a3331ed69f87fd47c98a9c2a3caa2d26"
RAW = f"https://raw.githubusercontent.com/{UPSTREAM}/{REVISION}"
EXPECTED = 451
CRS = "{http://ns.adobe.com/camera-raw-settings/1.0/}"
RDF = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}"

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "ChromaDNA-community-import/1.0"})
    with urllib.request.urlopen(req, timeout=45) as response:
        return response.read()

def normalize_slug(value):
    return re.sub(r"[^a-z0-9]+", "_", str(value).lower()).strip("_")


def build_profile_ids(items):
    """Create stable IDs, suffixing only normalized-slug collisions by source path."""
    bases = [normalize_slug(item.get("slug") or "") for item in items]
    if any(not base for base in bases):
        raise RuntimeError("Every upstream preset must have a non-empty slug")
    paths = [str(item.get("file") or "") for item in items]
    if any(not path for path in paths) or len(paths) != len(set(paths)):
        raise RuntimeError("Every upstream preset must have a unique source file path")
    counts = {base: bases.count(base) for base in set(bases)}
    profile_ids = []
    for base, path in zip(bases, paths):
        suffix = f"_{hashlib.sha256(path.encode('utf-8')).hexdigest()[:8]}" if counts[base] > 1 else ""
        profile_ids.append(f"emulsion_{base}{suffix}")
    if len(profile_ids) != len(set(profile_ids)):
        raise RuntimeError("Unable to generate unique stable profile IDs")
    return profile_ids


def parse_metadata(raw):
    root = ET.fromstring(raw)
    metadata, unsupported = {}, set()
    known = {"Temperature","Tint","IncrementalTemperature","IncrementalTint","Exposure2012",
      "Contrast2012","Highlights2012","Shadows2012","Whites2012","Blacks2012","Texture",
      "Clarity2012","Dehaze","Vibrance","Saturation","ParametricShadows","ParametricDarks",
      "ParametricLights","ParametricHighlights","ParametricShadowSplit","ParametricMidtoneSplit",
      "ParametricHighlightSplit","SplitToningShadowHue","SplitToningShadowSaturation",
      "SplitToningHighlightHue","SplitToningHighlightSaturation","SplitToningBalance",
      "ColorGradeShadowHue","ColorGradeShadowSat","ColorGradeMidtoneHue","ColorGradeMidtoneSat",
      "ColorGradeHighlightHue","ColorGradeHighlightSat","ColorGradeBalance","ColorGradeBlending",
      "ColorGradeGlobalHue","ColorGradeGlobalSat","ColorGradeShadowLum","ColorGradeMidtoneLum",
      "ColorGradeHighlightLum","ColorGradeGlobalLum","Sharpness","SharpenRadius","SharpenDetail",
      "SharpenEdgeMasking","LuminanceSmoothing","ColorNoiseReduction","PostCropVignetteAmount",
      "PostCropVignetteMidpoint","PostCropVignetteFeather","PostCropVignetteRoundness",
      "GrainAmount","GrainSize","GrainFrequency","GrainRoughness","ShadowTint","RedHue",
      "RedSaturation","GreenHue","GreenSaturation","BlueHue","BlueSaturation"}
    def record(name, value):
        metadata[name] = str(value)
        try:
            float(value)
            numeric = True
        except (TypeError, ValueError):
            numeric = False
        if numeric and name not in known and not name.startswith(("HueAdjustment","SaturationAdjustment","LuminanceAdjustment")):
            unsupported.add(name)

    for desc in root.iter(f"{RDF}Description"):
        for key, value in desc.attrib.items():
            if key.startswith(CRS):
                record(key[len(CRS):], value)
        for child in desc:
            if child.tag.startswith(CRS):
                name = child.tag[len(CRS):]
                values = [li.text.strip() for li in child.iter(f"{RDF}li") if li.text and li.text.strip()]
                record(name, values if values else (child.text.strip() if child.text else ""))
    return metadata, sorted(unsupported)

def main():
    catalog = json.loads(get(f"{RAW}/presets.json"))
    items = catalog.get("presets", [])
    if catalog.get("preset_count") != EXPECTED or len(items) != EXPECTED:
        raise RuntimeError(f"Expected {EXPECTED} upstream entries; got {len(items)}")
    profile_ids = build_profile_ids(items)
    normalized_slug_counts = {}
    for item in items:
        normalized = normalize_slug(item.get("slug") or "")
        normalized_slug_counts[normalized] = normalized_slug_counts.get(normalized, 0) + 1
    duplicate_source_slug_groups = sum(1 for count in normalized_slug_counts.values() if count > 1)
    license_text = get(f"{RAW}/LICENSE").decode("utf-8")
    if "MIT License" not in license_text or "peva3" not in license_text:
        raise RuntimeError("Pinned MIT license is missing or unexpected")
    profiles, entries, failures = [], [], []
    for item, profile_id in zip(items, profile_ids):
        try:
            path = str(item["file"])
            url = f"{RAW}/{urllib.parse.quote(path, safe='/')}"
            raw = get(url)
            metadata, unsupported = parse_metadata(raw)
            parsed = parse_xmp_string(raw.decode("utf-8"))
            sliders, curves = parsed["sliders"], parsed["tone_curves"]
            _, tags = infer_style_tags(sliders, curves)
            category = str(item.get("category") or "Uncategorized")
            utility = category == "Utility & Tools"
            video = category == "Video LUT Reference"
            profile = {
              "id": profile_id, "name": str(item["name"]), "category": category,
              "tags": sorted(set(tags + [re.sub(r"[^a-z0-9]+","-",category.lower()).strip("-")])),
              "source_hint": "EmulsionPresets",
              "profile_kind": "utility" if utility else ("video_reference" if video else "creative_look"),
              "blendable": not (utility or video), "sliders": sliders, "tone_curves": curves,
              "source_metadata": metadata,
              "provenance": {"repository": "https://github.com/" + UPSTREAM, "commit": REVISION,
                "file": path, "url": url, "license": "MIT", "sha256": hashlib.sha256(raw).hexdigest(),
                "description": str(item.get("description") or ""), "treatment": str(item.get("treatment") or ""),
                "unsupported_numeric_fields": unsupported, "source_slug": str(item["slug"])}
            }
            profiles.append(profile)
            entries.append({"id": profile_id, "file": path, "sha256": profile["provenance"]["sha256"],
                "slider_count": len(sliders), "unsupported_numeric_fields": unsupported,
                "source_slug": str(item["slug"])})
        except Exception as exc:
            failures.append({"file": item.get("file"), "name": item.get("name"), "error": str(exc)})
    report_path = Path("data/sources/emulsionpresets-import-report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    if failures or len(profiles) != EXPECTED or len({p["id"] for p in profiles}) != len(profiles):
        report_path.write_text(json.dumps({"source": UPSTREAM, "commit": REVISION,
          "expected": EXPECTED, "imported": len(profiles), "failures": failures,
          "entries": entries, "status": "failed"}, indent=2), encoding="utf-8")
        raise RuntimeError(f"Import failed: {len(profiles)}/{EXPECTED}; failures={len(failures)}")
    Path("data/color_dna_catalog.json").write_text(json.dumps({
      "schema_version": "1.1", "total_profiles": len(profiles), "profiles": profiles
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    report_path.write_text(json.dumps({"source": UPSTREAM, "commit": REVISION, "license": "MIT",
      "expected": EXPECTED, "imported": len(profiles), "failures": [],
      "duplicate_source_slug_groups": duplicate_source_slug_groups,
      "collision_safe_profile_ids": sum(1 for item in items if normalized_slug_counts[normalize_slug(item.get("slug") or "")] > 1),
      "unsupported_numeric_field_occurrences": sum(len(x["unsupported_numeric_fields"]) for x in entries),
      "entries": entries, "status": "success"}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    notices = Path("data/sources/THIRD_PARTY_NOTICES.md")
    notices.write_text("# Third-Party Preset Notices\n\n## EmulsionPresets\n\n"
      f"- Source: https://github.com/{UPSTREAM}\n- Pinned revision: {REVISION}\n"
      "- License: MIT; preserve the exact upstream LICENSE text below.\n"
      "- Imported XMP recipes remain attributed to their upstream author; ChromaDNA did not author them.\n\n"
      "Upstream MIT license text:\n\n" + license_text, encoding="utf-8")
    print(f"Imported {len(profiles)} presets from {UPSTREAM}@{REVISION}")

if __name__ == "__main__":
    try:
        main()
    except (urllib.error.URLError, json.JSONDecodeError, ET.ParseError, RuntimeError, KeyError) as exc:
        print(f"Community import failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
