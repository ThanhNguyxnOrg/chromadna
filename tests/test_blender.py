import pytest

from chromadna.blender import blend_dna_profiles


def profile(profile_id="look", **extra):
    return {
        "id": profile_id,
        "category": "Film Emulation",
        "tags": ["film-grain"],
        "sliders": {"Contrast2012": 10},
        "tone_curves": {},
        **extra,
    }


def test_blend_normalizes_finite_non_negative_weights():
    left = profile("left", sliders={"Contrast2012": 10})
    right = profile("right", sliders={"Contrast2012": 30})
    result = blend_dna_profiles([(left, 1), (right, 3)])
    assert result["sliders"]["Contrast2012"] == 25


def test_blend_circular_hue_wraps_across_zero_degrees():
    left = profile("left", sliders={"SplitToningShadowHue": 350, "SplitToningShadowSaturation": 40})
    right = profile("right", sliders={"SplitToningShadowHue": 10, "SplitToningShadowSaturation": 40})
    result = blend_dna_profiles([(left, 0.5), (right, 0.5)])
    assert result["sliders"]["SplitToningShadowHue"] == 0
    assert result["sliders"]["SplitToningShadowSaturation"] == 40


def test_blend_circular_hue_ignores_zero_saturation_profiles():
    neutral = profile("neutral", sliders={"ColorGradeMidtoneHue": 0, "ColorGradeMidtoneSat": 0})
    tinted = profile("tinted", sliders={"ColorGradeMidtoneHue": 220, "ColorGradeMidtoneSat": 40})
    result = blend_dna_profiles([(neutral, 0.5), (tinted, 0.5)])
    assert result["sliders"]["ColorGradeMidtoneHue"] == 220
    assert result["sliders"]["ColorGradeMidtoneSat"] == 20


def test_blend_circular_hue_opposite_colors_has_deterministic_fallback():
    left = profile("left", sliders={"SplitToningHighlightHue": 30, "SplitToningHighlightSaturation": 50})
    right = profile("right", sliders={"SplitToningHighlightHue": 210, "SplitToningHighlightSaturation": 20})
    result = blend_dna_profiles([(left, 0.5), (right, 0.5)])
    assert result["sliders"]["SplitToningHighlightHue"] == 30


def test_blend_uses_acr_neutral_defaults_for_missing_nonzero_sliders():
    unspecified = profile("unspecified", sliders={})
    custom = profile("custom", sliders={"ParametricMidtoneSplit": 60})
    result = blend_dna_profiles([(unspecified, 0.5), (custom, 0.5)])
    assert result["sliders"]["ParametricMidtoneSplit"] == 55


@pytest.mark.parametrize("weight", [-0.1, float("nan"), float("inf"), -float("inf"), True])
def test_blend_rejects_negative_non_finite_and_boolean_weights(weight):
    with pytest.raises(ValueError, match="weight"):
        blend_dna_profiles([(profile(), weight)])


def test_blend_rejects_empty_input_and_zero_total_weight():
    with pytest.raises(ValueError, match="at least one"):
        blend_dna_profiles([])
    with pytest.raises(ValueError, match="greater than 0"):
        blend_dna_profiles([(profile(), 0)])


@pytest.mark.parametrize(
    "blocked",
    [
        profile("utility", blendable=False),
        profile("video", profile_kind="video_reference"),
        profile("reset", profile_kind="utility", blendable=True),
    ],
)
def test_blend_rejects_utility_and_video_reference_profiles(blocked):
    with pytest.raises(ValueError, match="not a blendable creative look"):
        blend_dna_profiles([(blocked, 1)])
