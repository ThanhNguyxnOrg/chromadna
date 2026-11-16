"""3D LUT (.cube) exporter for ChromaDNA.

The color operations are practical approximations, not an implementation of
Adobe Camera Raw's proprietary rendering pipeline.
"""
import os
import uuid
from pathlib import Path
from typing import Any, Dict, Tuple

import numpy as np

from .schema import DEFAULT_CURVE, sanitize_curve

HSL_BANDS: Tuple[Tuple[str, float], ...] = (
    ("Red", 0.0), ("Orange", 30.0), ("Yellow", 60.0), ("Green", 120.0),
    ("Aqua", 180.0), ("Blue", 240.0), ("Purple", 280.0), ("Magenta", 320.0),
)


def _rgb_to_hsl_vec(rgb: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Convert an (N, 3) RGB array in [0, 1] to H, S, L arrays."""
    r, g, b = rgb[:, 0], rgb[:, 1], rgb[:, 2]
    c_max = np.maximum(np.maximum(r, g), b)
    c_min = np.minimum(np.minimum(r, g), b)
    delta = c_max - c_min
    lum = 0.5 * (c_max + c_min)
    sat = np.zeros_like(lum)
    mask = delta > 1e-6
    denom = 1.0 - np.abs(2.0 * lum - 1.0)
    sat[mask] = delta[mask] / np.maximum(1e-6, denom[mask])
    sat = np.clip(sat, 0.0, 1.0)
    hue = np.zeros_like(lum)
    r_mask, g_mask, b_mask = mask & (c_max == r), mask & (c_max == g), mask & (c_max == b)
    hue[r_mask] = 60.0 * (((g[r_mask] - b[r_mask]) / delta[r_mask]) % 6.0)
    hue[g_mask] = 60.0 * (((b[g_mask] - r[g_mask]) / delta[g_mask]) + 2.0)
    hue[b_mask] = 60.0 * (((r[b_mask] - g[b_mask]) / delta[b_mask]) + 4.0)
    return hue % 360.0, sat, lum


def _hsl_to_rgb_vec(hue: np.ndarray, sat: np.ndarray, lum: np.ndarray) -> np.ndarray:
    """Convert vectorized H, S, L arrays to an (N, 3) RGB array."""
    c = (1.0 - np.abs(2.0 * lum - 1.0)) * sat
    x = c * (1.0 - np.abs(((hue / 60.0) % 2.0) - 1.0))
    m = lum - 0.5 * c
    r1, g1, b1 = np.zeros_like(hue), np.zeros_like(hue), np.zeros_like(hue)
    h = hue % 360.0
    masks = (
        (h >= 0) & (h < 60), (h >= 60) & (h < 120),
        (h >= 120) & (h < 180), (h >= 180) & (h < 240),
        (h >= 240) & (h < 300), (h >= 300) & (h < 360),
    )
    r1[masks[0]], g1[masks[0]] = c[masks[0]], x[masks[0]]
    r1[masks[1]], g1[masks[1]] = x[masks[1]], c[masks[1]]
    g1[masks[2]], b1[masks[2]] = c[masks[2]], x[masks[2]]
    g1[masks[3]], b1[masks[3]] = x[masks[3]], c[masks[3]]
    r1[masks[4]], b1[masks[4]] = x[masks[4]], c[masks[4]]
    r1[masks[5]], g1[masks[5]] = c[masks[5]], x[masks[5]]
    return np.clip(np.stack([r1 + m, g1 + m, b1 + m], axis=-1), 0.0, 1.0)


def _eval_curve(channel: np.ndarray, curve_points: list) -> np.ndarray:
    """Evaluate an ACR-style [0, 255] tone curve on a [0, 1] channel."""
    points = np.asarray(sanitize_curve(curve_points), dtype=np.float32) / 255.0
    return np.interp(np.clip(channel, 0.0, 1.0), points[:, 0], points[:, 1])


def _hue_to_rgb_unit(hue_deg: float) -> np.ndarray:
    hue = np.array([hue_deg % 360.0], dtype=np.float32)
    return _hsl_to_rgb_vec(hue, np.ones_like(hue), np.full_like(hue, 0.5))[0]


def transform_rgb_lattice(lattice: np.ndarray, dna: Dict[str, Any]) -> np.ndarray:
    """Apply the approximate ChromaDNA pipeline to an (N, 3) RGB lattice."""
    if lattice.ndim != 2 or lattice.shape[1] != 3:
        raise ValueError("RGB lattice must have shape (N, 3).")
    if not np.all(np.isfinite(lattice)):
        raise ValueError("RGB lattice must contain only finite values.")
    rgb = np.clip(np.asarray(lattice, dtype=np.float32), 0.0, 1.0).copy()
    sliders, curves = dna.get("sliders", {}), dna.get("tone_curves", {})

    # 1. Simplified white-balance approximation.
    temp = float(sliders.get("IncrementalTemperature", 0)) / 100.0
    tint = float(sliders.get("IncrementalTint", 0)) / 100.0
    if temp:
        rgb[:, 0] += temp * 0.08
        rgb[:, 2] -= temp * 0.08
    if tint:
        rgb[:, 1] += tint * 0.06
        rgb[:, 0] -= tint * 0.03
        rgb[:, 2] -= tint * 0.03
    rgb = np.clip(rgb, 0.0, 1.0)

    # 2. Exposure.
    ev = float(sliders.get("Exposure2012", 0.0))
    if ev:
        rgb = np.clip(rgb * (2.0 ** (ev * 0.75)), 0.0, 1.0)

    # 3. Approximate tonal recovery using smooth luminance masks.
    lum = 0.2126 * rgb[:, 0] + 0.7152 * rgb[:, 1] + 0.0722 * rgb[:, 2]
    highlights = float(sliders.get("Highlights2012", 0)) / 100.0
    shadows = float(sliders.get("Shadows2012", 0)) / 100.0
    whites = float(sliders.get("Whites2012", 0)) / 100.0
    blacks = float(sliders.get("Blacks2012", 0)) / 100.0
    if highlights:
        mask = np.clip((lum - 0.5) * 2.0, 0.0, 1.0) ** 1.5
        rgb += (highlights * 0.22 * mask)[:, None]
    if shadows:
        mask = np.clip((0.5 - lum) * 2.0, 0.0, 1.0) ** 1.5
        rgb += (shadows * 0.22 * mask)[:, None]
    if whites:
        mask = np.clip((lum - 0.75) * 4.0, 0.0, 1.0)
        rgb += (whites * 0.15 * mask)[:, None]
    if blacks:
        mask = np.clip((0.25 - lum) * 4.0, 0.0, 1.0)
        rgb += (blacks * 0.15 * mask)[:, None]
    rgb = np.clip(rgb, 0.0, 1.0)

    # 4. Contrast.
    contrast = float(sliders.get("Contrast2012", 0)) / 100.0
    if contrast:
        factor = 1.0 + contrast * 0.45
        rgb = np.clip((rgb - 0.5) * factor + 0.5, 0.0, 1.0)

    # 5. Per-channel curves, then master RGB curve.
    rgb[:, 0] = _eval_curve(rgb[:, 0], curves.get("ToneCurvePV2012Red", DEFAULT_CURVE))
    rgb[:, 1] = _eval_curve(rgb[:, 1], curves.get("ToneCurvePV2012Green", DEFAULT_CURVE))
    rgb[:, 2] = _eval_curve(rgb[:, 2], curves.get("ToneCurvePV2012Blue", DEFAULT_CURVE))
    master = curves.get("ToneCurvePV2012", DEFAULT_CURVE)
    for channel in range(3):
        rgb[:, channel] = _eval_curve(rgb[:, channel], master)
    rgb = np.clip(rgb, 0.0, 1.0)

    # 6. Eight-band HSL mixer with Gaussian hue weighting.
    has_hsl = any(
        sliders.get(f"{prefix}Adjustment{band}", 0) != 0
        for prefix in ("Hue", "Saturation", "Luminance")
        for band, _ in HSL_BANDS
    )
    if has_hsl:
        hue, sat, lightness = _rgb_to_hsl_vec(rgb)
        d_hue, d_sat, d_lum = np.zeros_like(hue), np.zeros_like(sat), np.zeros_like(lightness)
        for band, center in HSL_BANDS:
            h_adj = float(sliders.get(f"HueAdjustment{band}", 0)) / 100.0
            s_adj = float(sliders.get(f"SaturationAdjustment{band}", 0)) / 100.0
            l_adj = float(sliders.get(f"LuminanceAdjustment{band}", 0)) / 100.0
            if not (h_adj or s_adj or l_adj):
                continue
            dist = np.abs((hue - center + 180.0) % 360.0 - 180.0)
            weight = np.exp(-0.5 * (dist / 26.0) ** 2) * np.clip(sat * 2.5, 0.0, 1.0)
            d_hue += h_adj * 25.0 * weight
            d_sat += s_adj * 0.45 * weight
            d_lum += l_adj * 0.20 * weight
        hue = (hue + d_hue) % 360.0
        sat = np.clip(sat + d_sat, 0.0, 1.0)
        lightness = np.clip(lightness + d_lum, 0.0, 1.0)
        rgb = _hsl_to_rgb_vec(hue, sat, lightness)

    # 7. Simplified split-toning / color-grading tint.
    shadow_hue = float(sliders.get("SplitToningShadowHue", 0))
    shadow_sat = float(sliders.get("SplitToningShadowSaturation", 0)) / 100.0
    highlight_hue = float(sliders.get("SplitToningHighlightHue", 0))
    highlight_sat = float(sliders.get("SplitToningHighlightSaturation", 0)) / 100.0
    if shadow_sat > 0.0 or highlight_sat > 0.0:
        lum_st = 0.2126 * rgb[:, 0] + 0.7152 * rgb[:, 1] + 0.0722 * rgb[:, 2]
        if shadow_sat > 0.0:
            tint_rgb = _hue_to_rgb_unit(shadow_hue) - 0.5
            weight = (1.0 - lum_st) ** 2 * (shadow_sat * 0.35)
            rgb += weight[:, None] * tint_rgb[None, :]
        if highlight_sat > 0.0:
            tint_rgb = _hue_to_rgb_unit(highlight_hue) - 0.5
            weight = lum_st ** 2 * (highlight_sat * 0.35)
            rgb += weight[:, None] * tint_rgb[None, :]
        rgb = np.clip(rgb, 0.0, 1.0)

    # 8. Global vibrance and saturation.
    saturation = float(sliders.get("Saturation", 0)) / 100.0
    vibrance = float(sliders.get("Vibrance", 0)) / 100.0
    if saturation or vibrance:
        luminance = 0.2126 * rgb[:, 0] + 0.7152 * rgb[:, 1] + 0.0722 * rgb[:, 2]
        chroma = np.max(rgb, axis=1) - np.min(rgb, axis=1)
        vib_weight = 1.0 - np.clip(chroma, 0.0, 1.0)
        scale = 1.0 + saturation * 0.55 + vibrance * 0.45 * vib_weight
        rgb = luminance[:, None] + (rgb - luminance[:, None]) * scale[:, None]
        rgb = np.clip(rgb, 0.0, 1.0)
    return rgb


def generate_cube_lut_string(
    dna: Dict[str, Any], title: str = "ChromaDNA LUT", size: int = 33
) -> str:
    """Generate a .cube 3D LUT payload (default 33³ samples)."""
    if not isinstance(size, int) or isinstance(size, bool) or not 2 <= size <= 65:
        raise ValueError("LUT size must be an integer between 2 and 65.")
    axis = np.linspace(0.0, 1.0, size, dtype=np.float32)
    # Axes are ordered B, G, R so red varies fastest in the flattened lattice.
    b_grid, g_grid, r_grid = np.meshgrid(axis, axis, axis, indexing="ij")
    lattice = np.stack((r_grid.ravel(), g_grid.ravel(), b_grid.ravel()), axis=-1)
    transformed = transform_rgb_lattice(lattice, dna)
    safe_title = str(title).replace('"', "'").replace("\n", " ").strip() or "ChromaDNA LUT"
    header = [
        "# Generated by ChromaDNA 3D LUT Exporter",
        f'TITLE "{safe_title}"',
        f"LUT_3D_SIZE {size}",
        "DOMAIN_MIN 0.0 0.0 0.0",
        "DOMAIN_MAX 1.0 1.0 1.0",
        "",
    ]
    rows = [f"{r:.6f} {g:.6f} {b:.6f}" for r, g, b in transformed]
    return "\n".join(header + rows) + "\n"


def write_cube_lut_atomic(
    dna: Dict[str, Any], output_path: Path,
    title: str = "ChromaDNA LUT", size: int = 33,
) -> Path:
    """Atomically write a .cube file and return its final path."""
    output_path = Path(output_path)
    if output_path.suffix.lower() != ".cube":
        output_path = output_path.with_suffix(".cube")
    cube_text = generate_cube_lut_string(dna, title=title, size=size)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = output_path.with_name(f".{output_path.name}.{uuid.uuid4().hex[:8]}.tmp")
    try:
        tmp_path.write_text(cube_text, encoding="utf-8", newline="\n")
        os.replace(tmp_path, output_path)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()
    return output_path
