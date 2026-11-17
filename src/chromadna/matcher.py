"""Image-to-DNA analyzer & automatic Exposure / White Balance compensation."""

import copy
from pathlib import Path
from typing import Any, Dict, List, Tuple
import numpy as np
from PIL import Image
from .blender import assert_profile_blendable, is_blendable_profile


def analyze_image_metrics(image_path: Path) -> Dict[str, float]:
    """Analyze luminance, contrast spread, and RGB color cast of a target photo."""
    img = Image.open(image_path).convert("RGB")
    img.thumbnail((512, 512))
    arr = np.asarray(img, dtype=np.float32) / 255.0
    lum = 0.2126 * arr[:, :, 0] + 0.7152 * arr[:, :, 1] + 0.0722 * arr[:, :, 2]
    mean_lum = float(np.mean(lum))
    p05, p95 = float(np.percentile(lum, 5)), float(np.percentile(lum, 95))
    dynamic_spread = p95 - p05
    mean_r, mean_g, mean_b = float(np.mean(arr[:, :, 0])), float(np.mean(arr[:, :, 1])), float(np.mean(arr[:, :, 2]))
    warmth_bias = mean_r - mean_b
    tint_bias = mean_g - 0.5 * (mean_r + mean_b)
    return {"mean_luminance": round(mean_lum, 4), "p05_shadow": round(p05, 4),
            "p95_highlight": round(p95, 4), "dynamic_spread": round(dynamic_spread, 4),
            "warmth_bias": round(warmth_bias, 4), "tint_bias": round(tint_bias, 4)}


def adapt_dna_to_image(dna: Dict[str, Any], image_path: Path) -> Tuple[Dict[str, Any], Dict[str, float]]:
    """Compute technical Exposure & White Balance offsets so the creative Color DNA fits the photo."""
    assert_profile_blendable(dna)
    metrics = analyze_image_metrics(image_path)
    adapted = copy.deepcopy(dna)
    sliders = adapted.setdefault("sliders", {})
    lum_error = 0.46 - metrics["mean_luminance"]
    exp_offset = float(np.clip(lum_error * 2.2, -1.25, 1.25))
    if abs(exp_offset) >= 0.08:
        sliders["Exposure2012"] = round(exp_offset, 2)
    if metrics["p95_highlight"] > 0.88:
        sliders["Highlights2012"] = int(max(-100, sliders.get("Highlights2012", 0) - 25))
    wb_temp = int(np.clip(-metrics["warmth_bias"] * 60, -20, 20))
    wb_tint = int(np.clip(-metrics["tint_bias"] * 60, -15, 15))
    if abs(wb_temp) >= 3:
        sliders["IncrementalTemperature"] = wb_temp
    if abs(wb_tint) >= 3:
        sliders["IncrementalTint"] = wb_tint
    return adapted, metrics


def recommend_dna_profiles(metrics: Dict[str, float], catalog: List[Dict[str, Any]], top_k: int = 3) -> List[Dict[str, Any]]:
    """Score catalog profiles based on image lighting characteristics."""
    if not isinstance(top_k, int) or isinstance(top_k, bool) or top_k < 1:
        raise ValueError("top_k must be a positive integer.")
    scored: List[Tuple[float, Dict[str, Any]]] = []
    for prof in catalog:
        if not is_blendable_profile(prof):
            continue
        score = 0.0
        tags = set(prof.get("tags", []))
        if metrics["dynamic_spread"] > 0.70 and "high-contrast" in tags: score += 1.5
        if metrics["dynamic_spread"] < 0.45 and "low-contrast" in tags: score += 1.5
        if metrics["mean_luminance"] < 0.35 and "moody" in tags: score += 1.2
        if metrics["warmth_bias"] > 0.05 and "warm-golden" in tags: score += 1.0
        scored.append((score, prof))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [p for _, p in scored[:top_k]]
