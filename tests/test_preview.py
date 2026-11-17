import numpy as np
from PIL import Image

from chromadna.lut_exporter import transform_rgb_lattice
from chromadna.previewer import render_before_after


def test_preview_uses_same_transform_as_lut_export(tmp_path):
    y, x = np.mgrid[0:48, 0:48]
    source = np.stack(
        (
            (x * 5 + y * 2) % 256,
            (x * 3 + y * 7) % 256,
            (x * 11 + y * 13) % 256,
        ),
        axis=-1,
    ).astype(np.uint8)
    image_path = tmp_path / "input.png"
    output_path = tmp_path / "preview.png"
    Image.fromarray(source).save(image_path)

    dna = {
        "sliders": {
            "Contrast2012": 18,
            "Highlights2012": -30,
            "Shadows2012": 20,
            "HueAdjustmentRed": 25,
            "SaturationAdjustmentBlue": -20,
            "SplitToningShadowHue": 215,
            "SplitToningShadowSaturation": 35,
            "SplitToningHighlightHue": 42,
            "SplitToningHighlightSaturation": 18,
        },
        "tone_curves": {
            "ToneCurvePV2012": [[0, 8], [64, 52], [192, 205], [255, 250]],
            "ToneCurvePV2012Red": [[0, 0], [255, 255]],
            "ToneCurvePV2012Green": [[0, 0], [255, 255]],
            "ToneCurvePV2012Blue": [[0, 0], [255, 255]],
        },
    }

    expected = transform_rgb_lattice(
        source.astype(np.float32).reshape(-1, 3) / 255.0,
        dna,
    ).reshape(source.shape)
    expected_pixel = np.clip(np.rint(expected[40, 20] * 255), 0, 255).astype(np.uint8)

    rendered_path = render_before_after(image_path, dna, output_path)
    rendered = np.asarray(Image.open(rendered_path).convert("RGB"))

    # The AFTER panel starts after the source image plus an 8-pixel divider.
    # y=40 avoids the preview label overlay.
    np.testing.assert_array_equal(rendered[40, 48 + 8 + 20], expected_pixel)


def test_identity_preview_preserves_source_pixels_in_after_panel(tmp_path):
    source = np.full((48, 48, 3), (40, 120, 210), dtype=np.uint8)
    image_path = tmp_path / "identity.png"
    output_path = tmp_path / "identity-preview.png"
    Image.fromarray(source).save(image_path)

    render_before_after(image_path, {"sliders": {}, "tone_curves": {}}, output_path)
    rendered = np.asarray(Image.open(output_path).convert("RGB"))

    np.testing.assert_array_equal(rendered[40, 48 + 8 + 20], source[40, 20])
