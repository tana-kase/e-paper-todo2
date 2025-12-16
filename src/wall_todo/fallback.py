"""Fallback image selection for when there are no tasks."""

import hashlib
from datetime import date
from pathlib import Path

IMAGES_DIR = Path(__file__).parent.parent.parent / "images"


def get_fallback_image(target_date: date | None = None) -> Path | None:
    """
    Select a fallback image based on the date.
    Same date always returns the same image.

    Args:
        target_date: Date to use for selection (default: today)

    Returns:
        Path to the selected image, or None if no images available
    """
    if target_date is None:
        target_date = date.today()

    # Get all image files
    if not IMAGES_DIR.exists():
        return None

    images = sorted(
        [f for f in IMAGES_DIR.iterdir() if f.suffix.lower() in (".png", ".jpg", ".jpeg")]
    )

    if not images:
        return None

    # Use date-based hash to select image (same date = same image)
    date_str = target_date.isoformat()
    hash_value = int(hashlib.md5(date_str.encode()).hexdigest(), 16)
    index = hash_value % len(images)

    return images[index]


if __name__ == "__main__":
    from datetime import timedelta

    print(f"Images directory: {IMAGES_DIR}")
    print(f"Exists: {IMAGES_DIR.exists()}")

    # Test with different dates
    today = date.today()
    for i in range(3):
        d = today + timedelta(days=i)
        img = get_fallback_image(d)
        print(f"{d}: {img}")
