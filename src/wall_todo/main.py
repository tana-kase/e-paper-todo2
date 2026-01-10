"""Main entry point for wall-todo."""

import json
import sys
from pathlib import Path

from .todoist import get_api_key, get_today_tasks
from .renderer import render_board
from .epaper import display_image
from .convert import process_uploads

OUTPUT_PATH = Path(__file__).parent.parent.parent / "output.png"
CACHE_PATH = Path(__file__).parent.parent.parent / ".tasks_cache.json"


def load_cached_tasks() -> list[dict] | None:
    """Load previously cached tasks from file."""
    if not CACHE_PATH.exists():
        return None
    try:
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def save_tasks_cache(tasks: list[dict]) -> None:
    """Save tasks to cache file."""
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)


def tasks_changed(current_tasks: list[dict], cached_tasks: list[dict] | None) -> bool:
    """Check if tasks have changed since last run."""
    if cached_tasks is None:
        return True
    return current_tasks != cached_tasks


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

    # Check if tasks have changed
    cached_tasks = load_cached_tasks()
    if not tasks_changed(tasks, cached_tasks):
        print("タスクに変更なし。再描画をスキップ")
        return

    # Tasks have changed, render and display
    used_fallback = not render_board(tasks, OUTPUT_PATH)

    if used_fallback:
        print(f"No tasks today. Fallback image saved to {OUTPUT_PATH}")
    else:
        print(f"Generated {len(tasks)} tasks to {OUTPUT_PATH}")

    if display_enabled:
        display_image(OUTPUT_PATH)

    # Save tasks to cache
    save_tasks_cache(tasks)


if __name__ == "__main__":
    main()
