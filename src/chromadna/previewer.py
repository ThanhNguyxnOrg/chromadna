"""Approximate Before/After renderer using the LUT exporter's shared RGB transform."""

from pathlib import Path
from typing import Any, Dict

import numpy as np
from PIL import Image, ImageDraw

from .lut_exporter import transform_rgb_lattice


def render_before_after(
    image_path: Path,
    dna: Dict[str, Any],
    output_path: Path,
    max_width: int = 800,
) -> Path:
    """Render a side-by-side approximation using the same transform kernel as .cube export."""
    original = Image.open(image_path).convert("RGB")
    if original.width > max_width:
        ratio = max_width / float(original.width)
        original = original.resize(
            (max_width, max(1, int(original.height * ratio))),
            Image.Resampling.LANCZOS,
        )

    source = np.asarray(original, dtype=np.float32) / 255.0
    transformed = transform_rgb_lattice(
        source.reshape(-1, 3),
        dna,
    ).reshape(source.shape)
    after = Image.fromarray(
        np.clip(np.rint(transformed * 255.0), 0, 255).astype(np.uint8)
    )

    width, height = original.size
    canvas = Image.new("RGB", (width * 2 + 8, height), color=(20, 20, 20))
    canvas.paste(original, (0, 0))
    canvas.paste(after, (width + 8, 0))
    draw = ImageDraw.Draw(canvas)
    draw.rectangle([10, 10, 95, 32], fill=(0, 0, 0))
    draw.text((18, 15), "BEFORE", fill=(255, 255, 255))
    draw.rectangle([width + 18, 10, width + 150, 32], fill=(0, 0, 0))
    draw.text((width + 26, 15), "AFTER (DNA)", fill=(255, 220, 100))

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path, quality=92)
    return output_path
