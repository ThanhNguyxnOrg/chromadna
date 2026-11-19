"""Data miner: Extract, normalize, classify, and deduplicate Color DNA from .xmp, .dng, and .lrtemplate."""

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from .schema import (
    DEFAULT_CURVE,
    SLIDER_BOUNDS,
    TECHNICAL_SLIDERS,
    TONE_CURVE_KEYS,
    clamp_slider,
    get_slider_default,
    sanitize_curve,
)

CRS_NS = "{http://ns.adobe.com/camera-raw-settings/1.0/}"
RDF_NS = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}"


def extract_xmp_packet_from_bytes(raw_bytes: bytes) -> Optional[str]:
    """Extract embedded <x:xmpmeta>...</x:xmpmeta> XML packet from binary files like .dng."""
    start_tag, end_tag = b"<x:xmpmeta", b"</x:xmpmeta>"
    start_idx = raw_bytes.find(start_tag)
    if start_idx == -1:
        return None
    end_idx = raw_bytes.find(end_tag, start_idx)
    if end_idx == -1:
        return None
    packet = raw_bytes[start_idx:end_idx + len(end_tag)]
    return packet.decode("utf-8", errors="ignore")


def parse_xmp_string(xml_text: str) -> Dict[str, Any]:
    """Parse an XMP XML string into clean sliders and tone curves."""
    root = ET.fromstring(xml_text)
    sliders: Dict[str, Any] = {}
    curves: Dict[str, List[List[int]]] = {}
    for desc in root.iter(f"{RDF_NS}Description"):
        for attr_key, attr_val in desc.attrib.items():
            if attr_key.startswith(CRS_NS):
                short_name = attr_key[len(CRS_NS):]
                if short_name in TECHNICAL_SLIDERS:
                    continue
                clamped = clamp_slider(short_name, attr_val)
                if clamped is not None:
                    sliders[short_name] = clamped
        for child in desc:
            if not child.tag.startswith(CRS_NS):
                continue
            short_name = child.tag[len(CRS_NS):]
            if short_name in TONE_CURVE_KEYS:
                pts: List[List[int]] = []
                for li in child.iter(f"{RDF_NS}li"):
                    if li.text and "," in li.text:
                        parts = li.text.strip().split(",")
                        if len(parts) == 2:
                            pts.append([int(float(parts[0])), int(float(parts[1]))])
                curves[short_name] = sanitize_curve(pts)
            elif short_name not in TECHNICAL_SLIDERS and child.text:
                clamped = clamp_slider(short_name, child.text.strip())
                if clamped is not None:
                    sliders[short_name] = clamped
    for ck in TONE_CURVE_KEYS:
        if ck not in curves:
            curves[ck] = [list(p) for p in DEFAULT_CURVE]
    return {"sliders": sliders, "tone_curves": curves}


def parse_lrtemplate_string(lua_text: str) -> Dict[str, Any]:
    """Parse legacy Lightroom .lrtemplate Lua table files into sliders and tone curves."""
    sliders: Dict[str, Any] = {}
    curves: Dict[str, List[List[int]]] = {}
    for match in re.finditer(r"([A-Za-z0-9_]+)\s*=\s*(-?\d+(?:\.\d+)?)\s*,?", lua_text):
        key, val = match.group(1), match.group(2)
        if key in TECHNICAL_SLIDERS:
            continue
        clamped = clamp_slider(key, val)
        if clamped is not None:
            sliders[key] = clamped
    for ck in TONE_CURVE_KEYS:
        curve_match = re.search(rf"{ck}\s*=\s*\{{([^}}]+)\}}", lua_text)
        if curve_match:
            nums = [int(float(x.strip())) for x in curve_match.group(1).split(",") if x.strip()]
            pts = [[nums[i], nums[i + 1]] for i in range(0, len(nums) - 1, 2)]
            curves[ck] = sanitize_curve(pts)
        else:
            curves[ck] = [list(p) for p in DEFAULT_CURVE]
    return {"sliders": sliders, "tone_curves": curves}


def infer_style_tags(sliders: Dict[str, Any], curves: Dict[str, List[List[int]]]) -> Tuple[str, List[str]]:
    """Automatically classify a Color DNA into a category and semantic mood tags."""
    tags: List[str] = []
    rgb_curve = curves.get("ToneCurvePV2012", DEFAULT_CURVE)
    black_lift = rgb_curve[0][1] if rgb_curve else 0
    white_drop = 255 - rgb_curve[-1][1] if rgb_curve else 0
    contrast, sat, vib, grain = (sliders.get(k, 0) for k in ("Contrast2012", "Saturation", "Vibrance", "GrainAmount"))
    shadow_hue, shadow_sat = sliders.get("SplitToningShadowHue", 0), sliders.get("SplitToningShadowSaturation", 0)
    hi_hue, hi_sat, blue_hue = sliders.get("SplitToningHighlightHue", 0), sliders.get("SplitToningHighlightSaturation", 0), sliders.get("BlueHue", 0)
    if black_lift >= 10: tags.append("matte")
    if white_drop >= 10: tags.append("soft-highlights")
    if grain >= 15: tags.append("film-grain")
    if contrast >= 20: tags.append("high-contrast")
    elif contrast <= -12: tags.append("low-contrast")
    if sat <= -20 or (sat + vib) <= -25: tags.extend(["desaturated", "moody"])
    elif vib >= 15 or sat >= 15: tags.append("vibrant")
    if (175 <= shadow_hue <= 225 and shadow_sat >= 10) or blue_hue <= -15: tags.append("teal-shadows")
    if (25 <= hi_hue <= 55 and hi_sat >= 10) or sliders.get("HueAdjustmentYellow", 0) <= -15: tags.append("warm-golden")
    if not tags: tags.append("balanced-natural")
    if "matte" in tags or "film-grain" in tags: category = "Film Emulation"
    elif "teal-shadows" in tags and "warm-golden" in tags: category = "Cinematic Teal & Orange"
    elif "moody" in tags or "desaturated" in tags: category = "Dark & Moody"
    elif "warm-golden" in tags: category = "Warm Editorial"
    else: category = "Clean & Versatile"
    return category, sorted(set(tags))


def dna_to_vector(dna: Dict[str, Any]) -> np.ndarray:
    """Convert Color DNA into a normalized feature vector for cosine deduplication."""
    vec: List[float] = []
    sliders = dna["sliders"]
    for key in sorted(SLIDER_BOUNDS.keys()):
        if key in TECHNICAL_SLIDERS:
            continue
        min_v, max_v, _ = SLIDER_BOUNDS[key]
        default_v = float(get_slider_default(key))
        val = float(sliders.get(key, default_v))
        span = max(1e-6, float(max_v - min_v))
        vec.append((val - default_v) / span)
    xs = np.linspace(0, 255, 8)
    identity = xs / 255.0
    for ck in TONE_CURVE_KEYS:
        curve = np.array(dna.get("tone_curves", {}).get(ck, DEFAULT_CURVE), dtype=float)
        ys = np.interp(xs, curve[:, 0], curve[:, 1]) / 255.0
        vec.extend((ys - identity).tolist())
    return np.array(vec, dtype=np.float32)


def mine_directory(input_dir: Path, similarity_threshold: float = 0.992) -> List[Dict[str, Any]]:
    """Recursively scan a directory of .xmp, .dng, and .lrtemplate files and build deduplicated Color DNA."""
    supported_exts = {".xmp", ".dng", ".lrtemplate"}
    files = sorted([p for p in input_dir.rglob("*") if p.suffix.lower() in supported_exts])
    catalog: List[Dict[str, Any]] = []
    vectors: List[np.ndarray] = []
    for idx, fpath in enumerate(files, start=1):
        ext, parsed = fpath.suffix.lower(), None
        try:
            if ext == ".xmp":
                parsed = parse_xmp_string(fpath.read_text(encoding="utf-8", errors="ignore"))
            elif ext == ".dng":
                xml_pkt = extract_xmp_packet_from_bytes(fpath.read_bytes())
                if xml_pkt: parsed = parse_xmp_string(xml_pkt)
            elif ext == ".lrtemplate":
                parsed = parse_lrtemplate_string(fpath.read_text(encoding="utf-8", errors="ignore"))
        except Exception:
            continue
        if not parsed:
            continue
        has_custom_curve = any(
            parsed["tone_curves"].get(ck, DEFAULT_CURVE) != DEFAULT_CURVE
            for ck in TONE_CURVE_KEYS
        )
        if not parsed["sliders"] and not has_custom_curve:
            continue
        vec = dna_to_vector(parsed)
        norm = np.linalg.norm(vec)
        if norm < 1e-6: continue
        unit_vec = vec / norm
        is_duplicate = any(float(np.dot(unit_vec, existing_vec)) >= similarity_threshold for existing_vec in vectors)
        if is_duplicate: continue
        category, tags = infer_style_tags(parsed["sliders"], parsed["tone_curves"])
        slug = re.sub(r"[^a-z0-9]+", "_", category.lower()).strip("_")
        dna_id = f"{slug}_{len(catalog) + 1:03d}"
        entry = {"id": dna_id, "category": category, "tags": tags, "source_hint": fpath.parent.name,
                 "sliders": parsed["sliders"], "tone_curves": parsed["tone_curves"]}
        catalog.append(entry)
        vectors.append(unit_vec)
    return catalog


def save_catalog(catalog: List[Dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"schema_version": "1.0", "total_profiles": len(catalog), "profiles": catalog}
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
