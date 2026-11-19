"""Mathematical preset interpolation & multi-DNA blending engine."""

import math
from typing import Any, Dict, List, Tuple
import numpy as np
from .schema import (
    DEFAULT_CURVE,
    HUE_SATURATION_PAIRS,
    TONE_CURVE_KEYS,
    clamp_slider,
    get_slider_default,
    sanitize_curve,
)

HUE_TO_SAT_KEY: Dict[str, str] = dict(HUE_SATURATION_PAIRS)


def resample_curve(points: List[List[int]], grid_size: int = 16) -> np.ndarray:
    """Resample a non-uniform Tone Curve onto a uniform X grid [0..255]."""
    arr = np.array(sanitize_curve(points), dtype=np.float32)
    x_grid = np.linspace(0, 255, grid_size)
    y_interp = np.interp(x_grid, arr[:, 0], arr[:, 1])
    return np.column_stack((x_grid, y_interp))


def simplify_curve(resampled: np.ndarray, tolerance: float = 1.2) -> List[List[int]]:
    """Reduce redundant collinear points while preserving curve inflection."""
    pts = [[int(round(x)), int(round(y))] for x, y in resampled]
    if len(pts) <= 3:
        return sanitize_curve(pts)
    kept = [pts[0]]
    for i in range(1, len(pts) - 1):
        x0, y0 = kept[-1]
        x1, y1 = pts[i]
        x2, y2 = pts[i + 1]
        expected_y = y0 + (y2 - y0) * ((x1 - x0) / max(1, x2 - x0))
        if abs(y1 - expected_y) >= tolerance:
            kept.append([x1, y1])
    kept.append(pts[-1])
    return sanitize_curve(kept)


def is_blendable_profile(dna: Dict[str, Any]) -> bool:
    """Return whether a profile represents a creative look that can be blended."""
    return (
        dna.get("blendable") is not False
        and dna.get("profile_kind") not in {"utility", "video_reference"}
    )


def assert_profile_blendable(dna: Dict[str, Any]) -> None:
    """Raise a useful error when a utility or video-reference profile is used as a look."""
    if not isinstance(dna, dict):
        raise ValueError("A Color DNA profile must be a mapping.")
    if not is_blendable_profile(dna):
        profile_id = dna.get("id", "unknown")
        profile_kind = dna.get("profile_kind", "non-blendable")
        raise ValueError(
            f"Color DNA profile '{profile_id}' ({profile_kind}) is not a blendable creative look."
        )


def _normalize_weighted_profiles(
    weighted_profiles: List[Tuple[Dict[str, Any], float]],
) -> List[Tuple[Dict[str, Any], float]]:
    """Validate blend inputs and return finite, non-negative, normalized weights."""
    try:
        entries = list(weighted_profiles)
    except TypeError as exc:
        raise ValueError("Provide one or more (profile, weight) pairs.") from exc
    if not entries:
        raise ValueError("Provide at least one profile to blend.")

    parsed: List[Tuple[Dict[str, Any], float]] = []
    for index, entry in enumerate(entries):
        if not isinstance(entry, (tuple, list)) or len(entry) != 2:
            raise ValueError(f"Blend item {index + 1} must contain a profile and a weight.")
        dna, raw_weight = entry
        assert_profile_blendable(dna)
        if isinstance(raw_weight, bool):
            raise ValueError(f"Blend weight {index + 1} must be a finite non-negative number.")
        try:
            weight = float(raw_weight)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError(f"Blend weight {index + 1} must be a finite non-negative number.") from exc
        if not math.isfinite(weight) or weight < 0:
            raise ValueError(f"Blend weight {index + 1} must be a finite non-negative number.")
        parsed.append((dna, weight))

    try:
        total_weight = math.fsum(weight for _, weight in parsed)
    except OverflowError as exc:
        raise ValueError("Total blend weight must be finite.") from exc
    if not math.isfinite(total_weight) or total_weight <= 0:
        raise ValueError("Total blend weight must be finite and greater than 0.")
    return [(dna, weight / total_weight) for dna, weight in parsed]


def _blend_circular_hue(
    normalized: List[Tuple[Dict[str, Any], float]],
    hue_key: str,
    sat_key: str,
) -> float:
    """Compute saturation-weighted circular mean for a 0..360 degree hue slider."""
    sin_sum = 0.0
    cos_sum = 0.0
    dominant_hue = 0.0
    dominant_mass = -1.0

    for dna, weight in normalized:
        sliders = dna.get("sliders", {})
        raw_sat = sliders.get(sat_key, 0.0)
        sat = max(0.0, float(raw_sat)) if raw_sat is not None else 0.0
        mass = weight * sat
        if mass <= 0.0:
            continue
        hue = float(sliders.get(hue_key, 0.0)) % 360.0
        rad = math.radians(hue)
        sin_sum += mass * math.sin(rad)
        cos_sum += mass * math.cos(rad)
        if mass > dominant_mass:
            dominant_mass = mass
            dominant_hue = hue

    if dominant_mass <= 0.0:
        return 0.0
    if math.hypot(sin_sum, cos_sum) < 1e-6:
        angle = dominant_hue
    else:
        angle = math.degrees(math.atan2(sin_sum, cos_sum)) % 360.0
    if angle >= 359.5 or abs(angle - 360.0) < 1e-6:
        return 0.0
    return angle


def blend_dna_profiles(weighted_profiles: List[Tuple[Dict[str, Any], float]]) -> Dict[str, Any]:
    """Blend N compatible Color DNA dictionaries using validated normalized weights."""
    normalized = _normalize_weighted_profiles(weighted_profiles)
    all_slider_keys = set()
    for dna, _ in normalized:
        all_slider_keys.update(dna.get("sliders", {}).keys())
    blended_sliders: Dict[str, Any] = {}
    for key in sorted(all_slider_keys):
        if key in HUE_TO_SAT_KEY:
            acc = _blend_circular_hue(normalized, key, HUE_TO_SAT_KEY[key])
            clamped = clamp_slider(key, acc)
            if clamped is not None:
                sat_key = HUE_TO_SAT_KEY[key]
                has_sat = any(
                    float(dna.get("sliders", {}).get(sat_key, 0.0)) > 0.0 and w > 0.0
                    for dna, w in normalized
                )
                if clamped != 0 or has_sat:
                    blended_sliders[key] = clamped
            continue

        default_val = float(get_slider_default(key))
        acc = math.fsum(
            float(dna.get("sliders", {}).get(key, default_val)) * weight
            for dna, weight in normalized
        )
        clamped = clamp_slider(key, acc)
        if clamped is not None and clamped != get_slider_default(key):
            blended_sliders[key] = clamped
    if blended_sliders.get("GrainAmount", 0) > 0 and blended_sliders.get("Sharpness", 0) > 10:
        blended_sliders["Sharpness"] = 10
    blended_curves: Dict[str, List[List[int]]] = {}
    for ck in TONE_CURVE_KEYS:
        acc_grid = np.zeros((16, 2), dtype=np.float32)
        for dna, weight in normalized:
            raw_curve = dna.get("tone_curves", {}).get(ck, DEFAULT_CURVE)
            acc_grid += resample_curve(raw_curve, grid_size=16) * weight
        blended_curves[ck] = simplify_curve(acc_grid)
    merged_tags = sorted({tag for dna, _ in normalized for tag in dna.get("tags", [])})
    return {"id": "blended_custom_dna", "category": "Blended Hybrid", "tags": merged_tags,
            "sliders": blended_sliders, "tone_curves": blended_curves}
