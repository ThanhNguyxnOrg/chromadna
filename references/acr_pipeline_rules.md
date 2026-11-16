# Adobe Camera Raw (ACR) Color Science & Pipeline Rules

1. **Processing Order in ACR Engine:**
   - White Balance (`Temperature`, `Tint`) -> Basic Tone (`Exposure2012`, `Contrast2012`, `Highlights2012`, `Shadows2012`, `Whites2012`, `Blacks2012`) -> Presence (`Texture`, `Clarity2012`, `Dehaze`, `Vibrance`, `Saturation`) -> Parametric & Point Tone Curves (`ToneCurvePV2012*`) -> HSL / Color Mixer -> Color Grading (3-Way Wheels) -> Detail (`Sharpness`) -> Effects (`PostCropVignette*`, `Grain*`) -> Camera Calibration.
2. **Matte Film Look (Lifted Blacks):**
   - Achieved by raising the `(0, 0)` point on `ToneCurvePV2012` to `(0, 12)`–`(0, 22)` while placing a control anchor at `(32, 30)` to prevent midtones from washing out.
3. **Teal & Orange Separation:**
   - Achieved via `CameraCalibration` (`BluePrimaryHue` shifted `-15` to `-35`, `RedPrimaryHue` shifted `+5` to `+15`) combined with `ColorGradeShadowHue` around `200–220` (cyan/teal) and `ColorGradeMidtoneHue` / `HighlightHue` around `35–48` (warm gold/skin).
4. **Preventing Double-Saturation:**
   - Steep Tone Curves increase perceived chroma. When `Contrast2012 > 20` or Tone Curve slope > 1.25 in midtones, keep `Saturation <= 0` and modulate color density with `Vibrance` instead.
