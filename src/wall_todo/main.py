"""Main entry point for wall-todo."""

import sys
from pathlib import Path

from .todoist import get_api_key, get_today_tasks
from .renderer import render_board
from .epaper import display_image
from .convert import process_uploads

OUTPUT_PATH = Path(__file__).parent.parent.parent / "output.png"


def main() -> None:
    """Fetch tasks from Todoist, generate PNG, and display on e-paper."""
    # Check for --no-display flag
    display_enabled = "--no-display" not in sys.argv

    # Process any uploaded images first
    converted = process_uploads()
    if converted > 0:
        print(f"Converted {converted} uploaded image(s)")

    api_key = get_api_key()
    if not api_key:
        print("Error: API_KEY not set in .env")
        return

    tasks = get_today_tasks(api_key)
    used_fallback = not render_board(tasks, OUTPUT_PATH)

    if used_fallback:
        print(f"No tasks today. Fallback image saved to {OUTPUT_PATH}")
    else:
        print(f"Generated {len(tasks)} tasks to {OUTPUT_PATH}")

    if display_enabled:
        display_image(OUTPUT_PATH)


if __name__ == "__main__":
    main()
