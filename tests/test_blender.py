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
