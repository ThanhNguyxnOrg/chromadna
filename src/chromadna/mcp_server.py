"""FastMCP Server for ChromaDNA: Expose Color DNA discovery, blending, photo matching,
Before/After preview rendering, XMP compilation, and 3D LUT (.cube) export to AI Agents.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from mcp.server.fastmcp import FastMCP

from .blender import assert_profile_blendable, blend_dna_profiles
from .compiler import write_xmp_atomic
from .lut_exporter import write_cube_lut_atomic
from .matcher import adapt_dna_to_image, analyze_image_metrics, recommend_dna_profiles
from .previewer import render_before_after
from .schema import clamp_slider

# Resolve default catalog path relative to repo root or environment override
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CATALOG_PATH = Path(os.environ.get("CHROMADNA_CATALOG", REPO_ROOT / "data" / "color_dna_catalog.json"))

mcp = FastMCP(
    name="ChromaDNA",
    instructions=(
        "ChromaDNA is a color grading engine for Adobe Lightroom / Camera Raw and video editors. "
        "Always inspect available Color DNA profiles first with `list_color_dna`. "
        "When a user provides an input photo, call `analyze_photo` or `match_photo_to_dna` to compensate "
        "Exposure and White Balance before compiling an `.xmp` preset or `.cube` 3D LUT."
    ),
)


def _load_profiles(catalog_path: Optional[str] = None) -> List[Dict[str, Any]]:
    path = Path(catalog_path) if catalog_path else DEFAULT_CATALOG_PATH
    if not path.exists():
        raise FileNotFoundError(
            f"Color DNA catalog not found at '{path}'. Run `chromadna mine <preset_folder>` first."
        )
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload.get("profiles", [])


def _get_profile(profiles: List[Dict[str, Any]], dna_id: str) -> Dict[str, Any]:
    for prof in profiles:
        if prof.get("id") == dna_id:
            return prof
    available = [p.get("id") for p in profiles[:10]]
    raise KeyError(f"Color DNA ID '{dna_id}' not found. Sample available IDs: {available}")


def _apply_overrides(dna: Dict[str, Any], slider_overrides: Optional[Dict[str, float]]) -> Dict[str, Any]:
    """Apply validated slider tweaks (e.g., {"GrainAmount": 15, "Contrast2012": 10}) onto a DNA dict."""
    if not slider_overrides:
        return dna
    cloned = json.loads(json.dumps(dna))
    sliders = cloned.setdefault("sliders", {})
    for key, raw_val in slider_overrides.items():
        clamped = clamp_slider(key, raw_val)
        if clamped is None:
            raise ValueError(f"Unsupported or invalid slider override: {key!r}.")
        sliders[key] = clamped
    # Enforce ACR Grain vs. Sharpness rule
    if sliders.get("GrainAmount", 0) > 0 and sliders.get("Sharpness", 0) > 10:
        sliders["Sharpness"] = 10
    return cloned


@mcp.tool()
def list_color_dna(
    tag: Optional[str] = None,
    category: Optional[str] = None,
    catalog_path: Optional[str] = None,
) -> Dict[str, Any]:
    """List available Color DNA profiles from the catalog, optionally filtered by mood tag or category.

    Args:
        tag: Optional mood tag filter (e.g., "matte", "warm-golden", "teal-shadows", "film-grain", "moody").
        category: Optional category filter (e.g., "Film Emulation", "Cinematic Teal & Orange").
        catalog_path: Optional custom path to color_dna_catalog.json.
    """
    profiles = _load_profiles(catalog_path)
    results = []
    for p in profiles:
        if tag and tag.lower() not in [t.lower() for t in p.get("tags", [])]:
            continue
        if category and category.lower() not in p.get("category", "").lower():
            continue
        results.append(
            {
                "id": p["id"],
                "category": p.get("category", "Uncategorized"),
                "profile_kind": p.get("profile_kind", "creative_look"),
                "blendable": p.get("blendable", True),
                "tags": p.get("tags", []),
                "key_sliders": {
                    k: p["sliders"][k]
                    for k in ("Contrast2012", "Highlights2012", "Shadows2012", "Vibrance", "Saturation", "GrainAmount")
                    if k in p.get("sliders", {})
                },
            }
        )
    return {"total_matched": len(results), "profiles": results}


@mcp.tool()
def inspect_color_dna(dna_id: str, catalog_path: Optional[str] = None) -> Dict[str, Any]:
    """Inspect the full mathematical sliders and Tone Curves of a specific Color DNA profile.

    Args:
        dna_id: The exact Color DNA ID (e.g., "film_emulation_001").
        catalog_path: Optional custom path to color_dna_catalog.json.
    """
    profiles = _load_profiles(catalog_path)
    return _get_profile(profiles, dna_id)


@mcp.tool()
def analyze_photo(image_path: str, top_k: int = 3, catalog_path: Optional[str] = None) -> Dict[str, Any]:
    """Analyze an input photo's luminance, dynamic range, and RGB color cast, and recommend matching Color DNAs.

    Args:
        image_path: Path to the target photo (.jpg, .png, .webp).
        top_k: Number of recommended Color DNA profiles to return (default: 3).
        catalog_path: Optional custom path to color_dna_catalog.json.
    """
    img_file = Path(image_path)
    if not img_file.exists():
        raise FileNotFoundError(f"Image not found at '{image_path}'.")

    metrics = analyze_image_metrics(img_file)
    recommendations: List[Dict[str, Any]] = []
    try:
        profiles = _load_profiles(catalog_path)
        recs = recommend_dna_profiles(metrics, profiles, top_k=top_k)
        recommendations = [{"id": r["id"], "category": r["category"], "tags": r["tags"]} for r in recs]
    except FileNotFoundError:
        pass

    return {"image_path": str(img_file.resolve()), "metrics": metrics, "recommended_dna": recommendations}


@mcp.tool()
def blend_color_dna(
    weights: Dict[str, float],
    preset_name: str,
    output_xmp_path: str,
    slider_overrides: Optional[Dict[str, float]] = None,
    preview_image_path: Optional[str] = None,
    preview_output_path: Optional[str] = None,
    catalog_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Mathematically blend 2 or more Color DNA profiles by weight (interpolating sliders & Tone Curves)
    and compile the hybrid style into an Adobe Lightroom .xmp preset.

    Args:
        weights: Mapping of Color DNA ID to weight, e.g. {"film_emulation_001": 0.7, "cinematic_teal_orange_002": 0.3}.
        preset_name: Display name of the preset inside Lightroom.
        output_xmp_path: Destination path for the compiled .xmp file.
        slider_overrides: Optional dict of slider tweaks applied after blending (e.g., {"GrainAmount": 12}).
        preview_image_path: Optional source photo path to generate a Before/After JPEG preview.
        preview_output_path: Optional destination path for the Before/After preview JPEG.
        catalog_path: Optional custom path to color_dna_catalog.json.
    """
    if not weights:
        raise ValueError("Provide at least one dna_id: weight entry in `weights`.")

    profiles = _load_profiles(catalog_path)
    weighted_list: List[Tuple[Dict[str, Any], float]] = [
        (_get_profile(profiles, dna_id), float(w)) for dna_id, w in weights.items()
    ]
    non_blendable = [dna.get("id", "unknown") for dna, _ in weighted_list if dna.get("blendable") is False]
    if non_blendable:
        raise ValueError(
            "These profiles are marked non-blendable and cannot be mixed: "
            + ", ".join(non_blendable)
        )

    blended = blend_dna_profiles(weighted_list)
    blended = _apply_overrides(blended, slider_overrides)

    xmp_file = write_xmp_atomic(blended, Path(output_xmp_path), preset_name=preset_name)
    result: Dict[str, Any] = {
        "status": "success",
        "xmp_path": str(xmp_file.resolve()),
        "preset_name": preset_name,
        "blended_tags": blended.get("tags", []),
        "resulting_sliders": blended.get("sliders", {}),
    }

    if preview_image_path:
        prev_out = Path(preview_output_path) if preview_output_path else xmp_file.with_suffix(".preview.jpg")
        rendered = render_before_after(Path(preview_image_path), blended, prev_out)
        result["preview_path"] = str(rendered.resolve())

    return result


@mcp.tool()
def match_photo_to_dna(
    image_path: str,
    dna_id: str,
    output_xmp_path: str,
    preset_name: str = "ChromaDNA Matched",
    slider_overrides: Optional[Dict[str, float]] = None,
    preview_output_path: Optional[str] = None,
    catalog_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Auto-compensate Exposure and White Balance of a Color DNA profile to match a target photo's lighting,
    then compile a tailored `.xmp` preset and optional Before/After comparison image.

    Args:
        image_path: Path to the target photo (.jpg, .png, .webp).
        dna_id: Base Color DNA ID from the catalog.
        output_xmp_path: Destination path for the compiled .xmp file.
        preset_name: Display name inside Lightroom.
        slider_overrides: Optional manual slider adjustments applied after auto-matching.
        preview_output_path: Optional destination path for the Before/After JPEG comparison.
        catalog_path: Optional custom path to color_dna_catalog.json.
    """
    img_file = Path(image_path)
    if not img_file.exists():
        raise FileNotFoundError(f"Image not found at '{image_path}'.")

    profiles = _load_profiles(catalog_path)
    base_dna = _get_profile(profiles, dna_id)
    adapted_dna, metrics = adapt_dna_to_image(base_dna, img_file)
    adapted_dna = _apply_overrides(adapted_dna, slider_overrides)

    xmp_file = write_xmp_atomic(adapted_dna, Path(output_xmp_path), preset_name=preset_name)
    result: Dict[str, Any] = {
        "status": "success",
        "xmp_path": str(xmp_file.resolve()),
        "image_metrics": metrics,
        "computed_technical_offsets": {
            k: adapted_dna["sliders"][k]
            for k in ("Exposure2012", "Highlights2012", "IncrementalTemperature", "IncrementalTint")
            if k in adapted_dna.get("sliders", {})
        },
    }

    if preview_output_path:
        rendered = render_before_after(img_file, adapted_dna, Path(preview_output_path))
        result["preview_path"] = str(rendered.resolve())

    return result


@mcp.tool()
def render_preview(
    image_path: str,
    dna_id: str,
    output_preview_path: str,
    slider_overrides: Optional[Dict[str, float]] = None,
    catalog_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Render a fast side-by-side Before/After JPEG preview applying a Color DNA onto an image without Lightroom.

    Args:
        image_path: Source photo path (.jpg, .png, .webp).
        dna_id: Color DNA ID to simulate.
        output_preview_path: Destination JPEG path for the Before/After comparison.
        slider_overrides: Optional slider tweaks to preview before exporting XMP.
        catalog_path: Optional custom path to color_dna_catalog.json.
    """
    profiles = _load_profiles(catalog_path)
    dna = _get_profile(profiles, dna_id)
    assert_profile_blendable(dna)
    dna = _apply_overrides(dna, slider_overrides)
    out_file = render_before_after(Path(image_path), dna, Path(output_preview_path))
    return {"status": "success", "preview_path": str(out_file.resolve())}


@mcp.tool()
def compile_xmp_preset(
    dna_id: str,
    preset_name: str,
    output_xmp_path: str,
    group_name: str = "ChromaDNA",
    slider_overrides: Optional[Dict[str, float]] = None,
    catalog_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Compile a Color DNA profile (with optional custom slider tweaks) into a valid Adobe Camera Raw .xmp file.

    Args:
        dna_id: Color DNA ID from the catalog.
        preset_name: Preset display name inside Lightroom.
        output_xmp_path: Destination .xmp file path (must not collide with an existing RAW file stem).
        group_name: Preset folder/group name inside Lightroom (default: "ChromaDNA").
        slider_overrides: Optional dict of Camera Raw slider adjustments.
        catalog_path: Optional custom path to color_dna_catalog.json.
    """
    profiles = _load_profiles(catalog_path)
    dna = _apply_overrides(_get_profile(profiles, dna_id), slider_overrides)
    xmp_file = write_xmp_atomic(dna, Path(output_xmp_path), preset_name=preset_name, group_name=group_name)
    return {
        "status": "success",
        "xmp_path": str(xmp_file.resolve()),
        "preset_name": preset_name,
        "group_name": group_name,
    }


@mcp.tool()
def export_cube_lut(
    output_cube_path: str,
    dna_id: Optional[str] = None,
    weights: Optional[Dict[str, float]] = None,
    title: str = "ChromaDNA LUT",
    size: int = 33,
    slider_overrides: Optional[Dict[str, float]] = None,
    catalog_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Export a single Color DNA or a blended multi-DNA mix as a standard 33x33x33 .cube 3D LUT
    compatible with DaVinci Resolve, Adobe Premiere Pro, Final Cut Pro, and CapCut.

    Args:
        output_cube_path: Destination .cube file path.
        dna_id: Single Color DNA ID (provide either `dna_id` or `weights`).
        weights: Optional blend weights dict e.g. {"film_emulation_001": 0.7, "cinematic_teal_orange_002": 0.3}.
        title: Title embedded inside the .cube file header.
        size: 3D LUT cube resolution (default: 33, standard for video NLEs).
        slider_overrides: Optional slider adjustments applied before baking the LUT.
        catalog_path: Optional custom path to color_dna_catalog.json.
    """
    profiles = _load_profiles(catalog_path)
    has_dna_id = dna_id is not None
    has_weights = weights is not None
    if has_dna_id == has_weights:
        raise ValueError("Provide exactly one of `dna_id` or `weights` to export a 3D LUT.")
    if has_weights:
        if not weights:
            raise ValueError("The `weights` mapping must contain at least one profile.")
        weighted_list = [(_get_profile(profiles, k), v) for k, v in weights.items()]
        target_dna = blend_dna_profiles(weighted_list)
    else:
        target_dna = _get_profile(profiles, dna_id)
        assert_profile_blendable(target_dna)

    target_dna = _apply_overrides(target_dna, slider_overrides)
    cube_file = write_cube_lut_atomic(target_dna, Path(output_cube_path), title=title, size=size)
    return {
        "status": "success",
        "cube_path": str(cube_file.resolve()),
        "title": title,
        "grid_size": f"{size}x{size}x{size}",
    }


def main() -> None:
    """Entry point for stdio MCP transport."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
