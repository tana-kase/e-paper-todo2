"""Main entry point for wall-todo."""

from pathlib import Path

from .todoist import get_api_key, get_today_tasks
from .renderer import render_board

OUTPUT_PATH = Path(__file__).parent.parent.parent / "output.png"


def main() -> None:
    """Fetch tasks from Todoist and generate PNG image."""
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


if __name__ == "__main__":
    main()
