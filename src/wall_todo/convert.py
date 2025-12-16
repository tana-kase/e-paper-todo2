"""Convert uploaded images for e-paper display."""

from pathlib import Path
from PIL import Image

UPLOADS_DIR = Path(__file__).parent.parent.parent / "uploads"
IMAGES_DIR = Path(__file__).parent.parent.parent / "images"

TARGET_WIDTH = 480
TARGET_HEIGHT = 800
GRAYSCALE_LEVELS = 4  # e-paper supports 4 levels


def convert_to_grayscale_4level(img: Image.Image) -> Image.Image:
    """
    Convert image to 4-level grayscale for e-paper.

    Args:
        img: PIL Image

    Returns:
        4-level grayscale image
    """
    # Convert to grayscale
    gray = img.convert("L")

    # Quantize to 4 levels (0, 85, 170, 255)
    def quantize(pixel: int) -> int:
        if pixel < 64:
            return 0
        elif pixel < 128:
            return 85
        elif pixel < 192:
            return 170
        else:
            return 255

    pixels = list(gray.getdata())
    quantized = [quantize(p) for p in pixels]
    gray.putdata(quantized)

    return gray


def convert_image(input_path: Path, output_path: Path) -> None:
    """
    Convert a single image for e-paper display.

    - Resize to fit 480x800 (scale up if smaller, scale down if larger)
    - Maintain aspect ratio with letterboxing (white padding)
    - Convert to 4-level grayscale

    Args:
        input_path: Source image path
        output_path: Destination path for converted image
    """
    img = Image.open(input_path)

    # Calculate scale to fit within 480x800 while maintaining aspect ratio
    scale_w = TARGET_WIDTH / img.width
    scale_h = TARGET_HEIGHT / img.height
    scale = min(scale_w, scale_h)

    new_width = int(img.width * scale)
    new_height = int(img.height * scale)

    # Resize (scale up or down)
    img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Create white background and paste resized image centered (letterbox)
    result = Image.new("L", (TARGET_WIDTH, TARGET_HEIGHT), 255)
    x = (TARGET_WIDTH - new_width) // 2
    y = (TARGET_HEIGHT - new_height) // 2

    # Convert to grayscale before pasting
    gray_img = convert_to_grayscale_4level(img_resized)
    result.paste(gray_img, (x, y))

    result.save(output_path, "PNG")


def process_uploads() -> int:
    """
    Process all images in uploads/ directory.
    Converts to e-paper format, moves to images/, deletes original.

    Returns:
        Number of images processed
    """
    if not UPLOADS_DIR.exists():
        UPLOADS_DIR.mkdir(parents=True)
        print(f"Created uploads directory: {UPLOADS_DIR}")
        return 0

    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    processed = 0
    for file in UPLOADS_DIR.iterdir():
        if file.suffix.lower() in (".png", ".jpg", ".jpeg", ".gif", ".bmp"):
            output_path = IMAGES_DIR / f"{file.stem}.png"
            try:
                convert_image(file, output_path)
                file.unlink()  # Delete original
                print(f"Converted: {file.name} -> {output_path.name}")
                processed += 1
            except Exception as e:
                print(f"Error converting {file.name}: {e}")

    return processed


if __name__ == "__main__":
    count = process_uploads()
    if count == 0:
        print(f"No images to process. Place images in: {UPLOADS_DIR}")
    else:
        print(f"Processed {count} image(s)")
