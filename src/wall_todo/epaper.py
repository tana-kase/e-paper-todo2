"""E-paper display module for Waveshare 7.5inch V2."""

from datetime import datetime
from pathlib import Path

from PIL import Image

# Display dimensions
DISPLAY_WIDTH = 800
DISPLAY_HEIGHT = 480


def should_full_refresh() -> bool:
    """
    Determine if full refresh is needed (every 5 minutes).

    Returns:
        True if current minute is divisible by 5
    """
    return datetime.now().minute % 5 == 0


def is_raspberry_pi() -> bool:
    """Check if running on Raspberry Pi."""
    try:
        with open("/proc/device-tree/model", "r") as f:
            return "Raspberry Pi" in f.read()
    except FileNotFoundError:
        return False


def display_image(image_path: str | Path, force_full_refresh: bool = False) -> bool:
    """
    Display PNG image on e-paper.

    Automatically performs full refresh every 5 minutes to prevent ghosting.

    Args:
        image_path: Path to PNG image (480x800)
        force_full_refresh: Force full refresh regardless of time

    Returns:
        True if displayed successfully, False otherwise
    """
    image_path = Path(image_path)
    if not image_path.exists():
        print(f"Error: Image not found: {image_path}")
        return False

    full_refresh = force_full_refresh or should_full_refresh()

    if not is_raspberry_pi():
        refresh_type = "full refresh" if full_refresh else "partial"
        print(f"Not on Raspberry Pi. Would display ({refresh_type}): {image_path}")
        return True

    try:
        # Import Waveshare library (only available on Raspberry Pi)
        from waveshare_epd import epd7in5_V2

        epd = epd7in5_V2.EPD()
        epd.init()

        # Full refresh to prevent ghosting (every 5 minutes)
        if full_refresh:
            epd.Clear()
            print("Full refresh performed")

        # Load and rotate image (480x800 portrait -> 800x480 landscape for display)
        img = Image.open(image_path)
        img_rotated = img.rotate(90, expand=True)

        # Display image
        epd.display(epd.getbuffer(img_rotated))
        epd.sleep()

        print(f"Displayed: {image_path}")
        return True

    except ImportError:
        print("Error: waveshare_epd library not installed")
        print("Install with: pip install waveshare-epaper")
        return False
    except Exception as e:
        print(f"Error displaying image: {e}")
        return False


def clear_display() -> bool:
    """
    Clear e-paper display (full refresh).

    Returns:
        True if cleared successfully, False otherwise
    """
    if not is_raspberry_pi():
        print("Not on Raspberry Pi. Would clear display.")
        return True

    try:
        from waveshare_epd import epd7in5_V2

        epd = epd7in5_V2.EPD()
        epd.init()
        epd.Clear()
        epd.sleep()

        print("Display cleared")
        return True

    except ImportError:
        print("Error: waveshare_epd library not installed")
        return False
    except Exception as e:
        print(f"Error clearing display: {e}")
        return False
