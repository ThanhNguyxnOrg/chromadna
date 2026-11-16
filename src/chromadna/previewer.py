"""Fast offline vectorized preview renderer (Before / After comparison) without Lightroom."""

from pathlib import Path
from typing import Any, Dict
import numpy as np
from PIL import Image, ImageDraw
from .schema import DEFAULT_CURVE, sanitize_curve


def _build_lut(curve_points: list) -> np.ndarray:
    pts = np.array(sanitize_curve(curve_points), dtype=np.float32)
    x_vals = np.arange(256, dtype=np.float32)
    lut = np.interp(x_vals, pts[:, 0], pts[:, 1])
    return np.clip(lut, 0, 255).astype(np.uint8)


def render_before_after(image_path: Path, dna: Dict[str, Any], output_path: Path, max_width: int = 800) -> Path:
    """Apply approximate Exposure, Contrast, Tone Curves, and Saturation to render a Before/After JPEG."""
    orig = Image.open(image_path).convert("RGB")
    if orig.width > max_width:
        ratio = max_width / float(orig.width)
        orig = orig.resize((max_width, int(orig.height * ratio)), Image.Resampling.LANCZOS)
    arr = np.asarray(orig, dtype=np.float32) / 255.0
    sliders, curves = dna.get("sliders", {}), dna.get("tone_curves", {})
    ev = float(sliders.get("Exposure2012", 0.0))
    if ev != 0.0:
        arr = arr * (2.0 ** (ev * 0.75))
    contrast = float(sliders.get("Contrast2012", 0)) / 100.0
    if contrast != 0.0:
        factor = 1.0 + (contrast * 0.45)
        arr = (arr - 0.5) * factor + 0.5
    temp = float(sliders.get("IncrementalTemperature", 0)) / 100.0
    if temp != 0.0:
        arr[:, :, 0] += temp * 0.08
        arr[:, :, 2] -= temp * 0.08
    arr = np.clip(arr * 255.0, 0, 255).astype(np.uint8)
    lut_r = _build_lut(curves.get("ToneCurvePV2012Red", DEFAULT_CURVE))
    lut_g = _build_lut(curves.get("ToneCurvePV2012Green", DEFAULT_CURVE))
    lut_b = _build_lut(curves.get("ToneCurvePV2012Blue", DEFAULT_CURVE))
    lut_rgb = _build_lut(curves.get("ToneCurvePV2012", DEFAULT_CURVE))
    arr[:, :, 0] = lut_rgb[lut_r[arr[:, :, 0]]]
    arr[:, :, 1] = lut_rgb[lut_g[arr[:, :, 1]]]
    arr[:, :, 2] = lut_rgb[lut_b[arr[:, :, 2]]]
    sat, vib = float(sliders.get("Saturation", 0)) / 100.0, float(sliders.get("Vibrance", 0)) / 100.0
    chroma_scale = 1.0 + (sat * 0.5) + (vib * 0.25)
    if abs(chroma_scale - 1.0) > 0.01:
        f_arr = arr.astype(np.float32)
        lum = 0.2126 * f_arr[:, :, 0] + 0.7152 * f_arr[:, :, 1] + 0.0722 * f_arr[:, :, 2]
        lum_3d = lum[:, :, None]
        f_arr = lum_3d + (f_arr - lum_3d) * chroma_scale
        arr = np.clip(f_arr, 0, 255).astype(np.uint8)
    after_img = Image.fromarray(arr, mode="RGB")
    w, h = orig.size
    canvas = Image.new("RGB", (w * 2 + 8, h), color=(20, 20, 20))
    canvas.paste(orig, (0, 0))
    canvas.paste(after_img, (w + 8, 0))
    draw = ImageDraw.Draw(canvas)
    draw.rectangle([10, 10, 95, 32], fill=(0, 0, 0))
    draw.text((18, 15), "BEFORE", fill=(255, 255, 255))
    draw.rectangle([w + 18, 10, w + 150, 32], fill=(0, 0, 0))
    draw.text((w + 26, 15), "AFTER (DNA)", fill=(255, 220, 100))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path, quality=92)
    return output_path
