from pathlib import Path
import xml.etree.ElementTree as ET

import numpy as np
import pytest

from chromadna.blender import blend_dna_profiles
from chromadna.compiler import build_xmp_xml, write_xmp_atomic
from chromadna.lut_exporter import generate_cube_lut_string, transform_rgb_lattice
from chromadna.miner import parse_xmp_string
from chromadna.schema import clamp_slider


def sample_dna(name="sample", contrast=0):
    return {
        "id": name,
        "category": "Test",
        "tags": ["test"],
        "sliders": {"Contrast2012": contrast},
        "tone_curves": {"ToneCurvePV2012": [[0, 0], [255, 255]]},
    }


def test_clamp_slider_rejects_unknown_and_bounds_known_values():
    assert clamp_slider("NotARealSlider", 10) is None
    assert clamp_slider("Contrast2012", 1000) == 100


def test_blend_normalizes_weights_and_returns_valid_profile():
    result = blend_dna_profiles([(sample_dna("a", 20), 1), (sample_dna("b", 40), 1)])
    assert result["sliders"]["Contrast2012"] == 30
    assert result["tone_curves"]["ToneCurvePV2012"][0] == [0, 0]


def test_compiler_emits_well_formed_xmp_and_round_trips_supported_slider():
    payload = build_xmp_xml(sample_dna(contrast=24), "Test & Look")
    ET.fromstring(payload)
    parsed = parse_xmp_string(payload)
    assert parsed["sliders"]["Contrast2012"] == 24


def test_xmp_writer_refuses_raw_sidecar_collision(tmp_path: Path):
    raw = tmp_path / "frame.CR3"
    raw.write_bytes(b"raw placeholder")
    with pytest.raises(FileExistsError):
        write_xmp_atomic(sample_dna(), tmp_path / "frame.xmp", "Unsafe sidecar")


def test_lut_has_expected_header_and_sample_count():
    payload = generate_cube_lut_string(sample_dna(), title="Test LUT", size=3)
    rows = [line for line in payload.splitlines() if line and not line.startswith("#") and not line.startswith("TITLE") and not line.startswith("LUT_") and not line.startswith("DOMAIN_")]
    assert 'TITLE "Test LUT"' in payload
    assert len(rows) == 27


def test_identity_dna_preserves_rgb_lattice():
    source = np.array([[0.0, 0.25, 1.0], [0.5, 0.5, 0.5]], dtype=np.float32)
    result = transform_rgb_lattice(source, {"sliders": {}, "tone_curves": {}})
    np.testing.assert_allclose(result, source, atol=1e-5)


def test_modern_color_grading_and_grain_fields_are_supported():
    from chromadna.schema import SLIDER_BOUNDS

    assert clamp_slider("ColorGradeShadowHue", 210) == 210
    assert clamp_slider("ColorGradeHighlightSat", 120) == 100
    assert clamp_slider("ColorGradeBalance", -120) == -100
    assert clamp_slider("GrainRoughness", 45) == 45
    assert "ColorGradeShadowHue" in SLIDER_BOUNDS
    assert "ColorGradeHighlightLum" in SLIDER_BOUNDS
