"""Strict Adobe Camera Raw (crs:*) schema bounds, defaults, and parameter classification."""

import math
from typing import Any, Dict, List, Tuple

TECHNICAL_SLIDERS = {
    "Temperature", "Tint", "Exposure2012", "IncrementalTemperature", "IncrementalTint",
}

SLIDER_BOUNDS: Dict[str, Tuple[float, float, type]] = {
    "Temperature": (2000, 50000, int), "Tint": (-150, 150, int),
    "IncrementalTemperature": (-100, 100, int), "IncrementalTint": (-100, 100, int),
    "Exposure2012": (-5.0, 5.0, float), "Contrast2012": (-100, 100, int),
    "Highlights2012": (-100, 100, int), "Shadows2012": (-100, 100, int),
    "Whites2012": (-100, 100, int), "Blacks2012": (-100, 100, int),
    "Texture": (-100, 100, int), "Clarity2012": (-100, 100, int),
    "Dehaze": (-100, 100, int), "Vibrance": (-100, 100, int), "Saturation": (-100, 100, int),
    "ParametricShadows": (-100, 100, int), "ParametricDarks": (-100, 100, int),
    "ParametricLights": (-100, 100, int), "ParametricHighlights": (-100, 100, int),
    "ParametricShadowSplit": (10, 70, int), "ParametricMidtoneSplit": (20, 80, int),
    "ParametricHighlightSplit": (30, 90, int),
    "HueAdjustmentRed": (-100, 100, int), "HueAdjustmentOrange": (-100, 100, int),
    "HueAdjustmentYellow": (-100, 100, int), "HueAdjustmentGreen": (-100, 100, int),
    "HueAdjustmentAqua": (-100, 100, int), "HueAdjustmentBlue": (-100, 100, int),
    "HueAdjustmentPurple": (-100, 100, int), "HueAdjustmentMagenta": (-100, 100, int),
    "SaturationAdjustmentRed": (-100, 100, int), "SaturationAdjustmentOrange": (-100, 100, int),
    "SaturationAdjustmentYellow": (-100, 100, int), "SaturationAdjustmentGreen": (-100, 100, int),
    "SaturationAdjustmentAqua": (-100, 100, int), "SaturationAdjustmentBlue": (-100, 100, int),
    "SaturationAdjustmentPurple": (-100, 100, int), "SaturationAdjustmentMagenta": (-100, 100, int),
    "LuminanceAdjustmentRed": (-100, 100, int), "LuminanceAdjustmentOrange": (-100, 100, int),
    "LuminanceAdjustmentYellow": (-100, 100, int), "LuminanceAdjustmentGreen": (-100, 100, int),
    "LuminanceAdjustmentAqua": (-100, 100, int), "LuminanceAdjustmentBlue": (-100, 100, int),
    "LuminanceAdjustmentPurple": (-100, 100, int), "LuminanceAdjustmentMagenta": (-100, 100, int),
    "SplitToningShadowHue": (0, 360, int), "SplitToningShadowSaturation": (0, 100, int),
    "SplitToningHighlightHue": (0, 360, int), "SplitToningHighlightSaturation": (0, 100, int),
    "SplitToningBalance": (-100, 100, int),
    "ColorGradeShadowHue": (0, 360, int), "ColorGradeShadowSat": (0, 100, int),
    "ColorGradeShadowLum": (-100, 100, int), "ColorGradeMidtoneHue": (0, 360, int),
    "ColorGradeMidtoneSat": (0, 100, int), "ColorGradeMidtoneLum": (-100, 100, int),
    "ColorGradeHighlightHue": (0, 360, int), "ColorGradeHighlightSat": (0, 100, int),
    "ColorGradeHighlightLum": (-100, 100, int), "ColorGradeBalance": (-100, 100, int),
    "ColorGradeBlending": (0, 100, int), "ColorGradeGlobalHue": (0, 360, int),
    "ColorGradeGlobalSat": (0, 100, int), "ColorGradeGlobalLum": (-100, 100, int),
    "Sharpness": (0, 150, int), "SharpenRadius": (0.5, 3.0, float),
    "SharpenDetail": (0, 100, int), "SharpenEdgeMasking": (0, 100, int),
    "LuminanceSmoothing": (0, 100, int), "ColorNoiseReduction": (0, 100, int),
    "PostCropVignetteAmount": (-100, 100, int), "PostCropVignetteMidpoint": (0, 100, int),
    "PostCropVignetteFeather": (0, 100, int), "PostCropVignetteRoundness": (-100, 100, int),
    "GrainAmount": (0, 100, int), "GrainSize": (0, 100, int), "GrainFrequency": (0, 100, int),
    "GrainRoughness": (0, 100, int),
    "ShadowTint": (-100, 100, int), "RedHue": (-100, 100, int),
    "RedSaturation": (-100, 100, int), "GreenHue": (-100, 100, int),
    "GreenSaturation": (-100, 100, int), "BlueHue": (-100, 100, int),
    "BlueSaturation": (-100, 100, int),
}

TONE_CURVE_KEYS = ["ToneCurvePV2012", "ToneCurvePV2012Red", "ToneCurvePV2012Green", "ToneCurvePV2012Blue"]
DEFAULT_CURVE: List[List[int]] = [[0, 0], [255, 255]]


def clamp_slider(name: str, value: Any) -> Any:
    """Validate and clamp a slider value to legal Adobe Camera Raw bounds."""
    if name not in SLIDER_BOUNDS:
        return None
    min_val, max_val, dtype = SLIDER_BOUNDS[name]
    if isinstance(value, bool):
        return None
    try:
        num = float(value)
    except (ValueError, TypeError, OverflowError):
        return None
    if not math.isfinite(num):
        return None
    clamped = max(min_val, min(max_val, num))
    return int(round(clamped)) if dtype is int else round(clamped, 2)


def sanitize_curve(points: List[List[int]]) -> List[List[int]]:
    """Ensure curve points are strictly monotonic in X within [0, 255]."""
    if not points or len(points) < 2:
        return [[0, 0], [255, 255]]
    cleaned = []
    for pt in points:
        if len(pt) != 2:
            continue
        x = int(max(0, min(255, round(pt[0]))))
        y = int(max(0, min(255, round(pt[1]))))
        cleaned.append([x, y])
    cleaned.sort(key=lambda p: p[0])
    dedup: List[List[int]] = []
    for x, y in cleaned:
        if dedup and dedup[-1][0] == x:
            dedup[-1][1] = y
        else:
            dedup.append([x, y])
    return dedup if len(dedup) >= 2 else [[0, 0], [255, 255]]
