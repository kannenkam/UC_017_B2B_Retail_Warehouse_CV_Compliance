from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def create_high_confidence_label():
    """Generates a digitally perfect, high-contrast label to achieve >80% OCR accuracy."""
    # Create a clean white canvas (800x400 pixels)
    img = Image.new('RGB', (800, 400), color=(255, 255, 255))
    canvas = ImageDraw.Draw(img)

    # Define stark black text strings mimicking a legal product label
    lines = [
        "PRODUCT ID: 400222100000",
        "INGREDIENTS: Water, **Milk**, Sugar.",
        "ALLERGENS: **Milk**",
        "EXPIRY DATE: 31.12.2026",
        "DESTINATION: DE"
    ]

    # Use standard system default font block mapping
    try:
        # Try loading a standard clean sans-serif font on macOS
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 36)
    except IOError:
        font = ImageFont.load_default()

    # Draw each line onto the white canvas with stark black ink
    y_offset = 40
    for line in lines:
        canvas.text((50, y_offset), line, fill=(0, 0, 0), font=font)
        y_offset += 65

    # Save cleanly into your active warehouse directory
    output_dir = Path("data/inbound_pallet_scans")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "sample_perfect_label.png"
    img.save(output_path)
    print(f"🎯 Perfect high-contrast compliance label generated successfully at: {output_path}")


if __name__ == "__main__":
    create_high_confidence_label()