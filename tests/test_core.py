import numpy as np
from chromadna.schema import clamp_slider
from chromadna.miner import dna_to_vector, mine_directory, parse_xmp_string, parse_lrtemplate_string
from chromadna.blender import blend_dna_profiles
from chromadna.compiler import build_xmp_xml, write_xmp_atomic
from chromadna.lut_exporter import _hsl_to_rgb_vec, _rgb_to_hsl_vec, generate_cube_lut_string, transform_rgb_lattice


def sample_dna(name="sample", contrast=0):
    return {
        "id": name,
        "category": "Film Emulation",
        "tags": ["film-grain"],
        "sliders": {"Contrast2012": contrast, "Saturation": -10, "GrainAmount": 20, "Sharpness": 45},
        "tone_curves": {
            "ToneCurvePV2012": [[0, 12], [128, 130], [255, 245]],
            "ToneCurvePV2012Red": [[0, 0], [255, 255]],
            "ToneCurvePV2012Green": [[0, 0], [255, 255]],
            "ToneCurvePV2012Blue": [[0, 0], [255, 255]],
        },
    }


def test_clamp_slider_rejects_unknown_and_bounds_known_values():
    assert clamp_slider("NotARealSlider", 10) is None
    assert clamp_slider("Contrast2012", 1000) == 100
    assert clamp_slider("Contrast2012", float("nan")) is None
    assert clamp_slider("Contrast2012", float("inf")) is None
    assert clamp_slider("Contrast2012", True) is None


def test_blend_normalizes_weights_and_returns_valid_profile():
    blended = blend_dna_profiles([(sample_dna("a", 20), 3.0), (sample_dna("b", -20), 1.0)])
    assert blended["sliders"]["Contrast2012"] == 10
    assert blended["sliders"]["Sharpness"] == 10


def test_build_xmp_xml_and_raw_protection(tmp_path):
    dna = sample_dna("test", 15)
    xml_text = build_xmp_xml(dna, preset_name="Test Preset & Look")
    assert "Test Preset &amp; Look" in xml_text
    raw_file = tmp_path / "IMG_001.CR3"
    raw_file.write_bytes(b"RAW")
    try:
        write_xmp_atomic(dna, tmp_path / "IMG_001.xmp", preset_name="Collision")
        assert False, "Expected FileExistsError when RAW with same stem exists"
    except FileExistsError:
        pass


def test_write_xmp_atomic_cleans_temp_file_on_replace_failure(tmp_path, monkeypatch):
    def failing_replace(src, dst):
        raise OSError("disk full")

    monkeypatch.setattr("chromadna.compiler.os.replace", failing_replace)
    out_path = tmp_path / "out.xmp"
    try:
        write_xmp_atomic(sample_dna(), out_path, preset_name="FailTest")
        assert False, "Expected OSError"
    except OSError:
        pass
    assert list(tmp_path.glob("*.tmp")) == []


def test_parse_lrtemplate_and_lut_export():
    dna = parse_lrtemplate_string("s = { settings = { Contrast2012 = 25, Vibrance = 15, ToneCurvePV2012 = {0, 5, 255, 250} } }")
    assert dna["sliders"]["Contrast2012"] == 25
    cube_str = generate_cube_lut_string(dna, title='Test "LUT"', size=5)
    assert "LUT_3D_SIZE 5" in cube_str
    assert len([ln for ln in cube_str.splitlines() if ln and not ln.startswith("#") and not ln[0].isalpha()]) == 125


def test_modern_color_grading_and_grain_fields_are_supported():
    assert clamp_slider("ColorGradeShadowHue", 215) == 215
    assert clamp_slider("ColorGradeMidtoneSat", 22) == 22
    assert clamp_slider("ColorGradeHighlightLum", -15) == -15
    assert clamp_slider("ColorGradeBalance", 18) == 18
    assert clamp_slider("GrainRoughness", 65) == 65

    parsed = parse_xmp_string(
        '<x:xmpmeta xmlns:x="adobe:ns:meta/"><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">'
        '<rdf:Description xmlns:crs="http://ns.adobe.com/camera-raw-settings/1.0/" '
        'crs:ColorGradeShadowHue="215" crs:ColorGradeShadowSat="25" crs:GrainRoughness="60"/>'
        "</rdf:RDF></x:xmpmeta>"
    )
    assert parsed["sliders"]["ColorGradeShadowHue"] == 215
    assert parsed["sliders"]["ColorGradeShadowSat"] == 25
    assert parsed["sliders"]["GrainRoughness"] == 60


def test_hsl_round_trip_covers_all_six_sectors():
    # Cover every 60-degree sector including [300, 360) magenta
    hues = np.array([0.0, 30.0, 60.0, 90.0, 120.0, 150.0, 180.0, 210.0, 240.0, 270.0, 300.0, 330.0, 355.0], dtype=np.float32)
    sats = np.full_like(hues, 0.85)
    lums = np.full_like(hues, 0.5)
    rgb = _hsl_to_rgb_vec(hues, sats, lums)

    # Specifically verify 330 deg magenta: R=1.0, G=0.0, B=0.5
    magenta = _hsl_to_rgb_vec(
        np.array([330.0], dtype=np.float32),
        np.array([1.0], dtype=np.float32),
        np.array([0.5], dtype=np.float32),
    )[0]
    np.testing.assert_allclose(magenta, np.array([1.0, 0.0, 0.5], dtype=np.float32), atol=1e-5)

    h_back, s_back, l_back = _rgb_to_hsl_vec(rgb)
    np.testing.assert_allclose(h_back, hues, atol=1e-3)
    np.testing.assert_allclose(s_back, sats, atol=1e-5)
    np.testing.assert_allclose(l_back, lums, atol=1e-5)


def test_modern_color_grading_modifies_rgb_lattice_across_all_zones():
    neutral = np.array([[0.15, 0.15, 0.15], [0.5, 0.5, 0.5], [0.85, 0.85, 0.85]], dtype=np.float32)
    base = transform_rgb_lattice(neutral, {"sliders": {}, "tone_curves": {}})

    for sliders in (
        {"ColorGradeShadowHue": 220, "ColorGradeShadowSat": 40},
        {"ColorGradeMidtoneHue": 40, "ColorGradeMidtoneSat": 40},
        {"ColorGradeHighlightHue": 330, "ColorGradeHighlightSat": 40},
        {"ColorGradeGlobalHue": 140, "ColorGradeGlobalSat": 35},
    ):
        graded = transform_rgb_lattice(neutral, {"sliders": sliders, "tone_curves": {}})
        assert not np.allclose(graded, base), f"Expected RGB output change for {sliders}"


def test_miner_deduplication_distinguishes_rgb_channel_curves(tmp_path):
    p1 = tmp_path / "warm_red_curve.xmp"
    p2 = tmp_path / "cool_blue_curve.xmp"
    p1.write_text(
        '<x:xmpmeta xmlns:x="adobe:ns:meta/"><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">'
        '<rdf:Description xmlns:crs="http://ns.adobe.com/camera-raw-settings/1.0/">'
        '<crs:ToneCurvePV2012Red><rdf:Seq><rdf:li>0, 0</rdf:li><rdf:li>128, 165</rdf:li><rdf:li>255, 255</rdf:li></rdf:Seq></crs:ToneCurvePV2012Red>'
        '</rdf:Description></rdf:RDF></x:xmpmeta>',
        encoding="utf-8",
    )
    p2.write_text(
        '<x:xmpmeta xmlns:x="adobe:ns:meta/"><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">'
        '<rdf:Description xmlns:crs="http://ns.adobe.com/camera-raw-settings/1.0/">'
        '<crs:ToneCurvePV2012Blue><rdf:Seq><rdf:li>0, 0</rdf:li><rdf:li>128, 165</rdf:li><rdf:li>255, 255</rdf:li></rdf:Seq></crs:ToneCurvePV2012Blue>'
        '</rdf:Description></rdf:RDF></x:xmpmeta>',
        encoding="utf-8",
    )
    catalog = mine_directory(tmp_path, similarity_threshold=0.992)
    assert len(catalog) == 2
    assert np.linalg.norm(dna_to_vector(catalog[0]) - dna_to_vector(catalog[1])) > 0.1
