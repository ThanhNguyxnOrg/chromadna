"""Mathematical preset interpolation & multi-DNA blending engine."""

from typing import Any, Dict, List, Tuple
import numpy as np
from .schema import DEFAULT_CURVE, TONE_CURVE_KEYS, clamp_slider, sanitize_curve


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


def blend_dna_profiles(weighted_profiles: List[Tuple[Dict[str, Any], float]]) -> Dict[str, Any]:
    """Blend N Color DNA dictionaries using normalized weights."""
    total_weight = sum(w for _, w in weighted_profiles)
    if total_weight <= 0:
        raise ValueError("Total blend weight must be greater than 0.")
    normalized = [(dna, w / total_weight) for dna, w in weighted_profiles]
    all_slider_keys = set()
    for dna, _ in normalized:
        all_slider_keys.update(dna.get("sliders", {}).keys())
    blended_sliders: Dict[str, Any] = {}
    for key in sorted(all_slider_keys):
        acc = sum(float(dna.get("sliders", {}).get(key, 0.0)) * weight for dna, weight in normalized)
        clamped = clamp_slider(key, acc)
        if clamped is not None and clamped != 0:
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
