"""Todoist API client for fetching tasks."""

import os
from dotenv import load_dotenv
import requests


def get_api_key() -> str:
    """Load API key from environment."""
    load_dotenv()
    key = os.getenv("API_KEY")
    return key if key else ""


def fetch_tasks(api_key: str, filter_query: str = "today") -> list[dict]:
    """
    Fetch tasks from Todoist API.

    Args:
        api_key: Todoist API token
        filter_query: Filter query (default: "today")

    Returns:
        List of task dictionaries, empty list on error
    """
    if not api_key:
        return []

    try:
        response = requests.get(
            "https://api.todoist.com/rest/v2/tasks",
            params={"filter": filter_query},
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError):
        return []


def get_today_tasks(api_key: str, limit: int = 10) -> list[dict]:
    """
    Get today's tasks with a limit.

    Args:
        api_key: Todoist API token
        limit: Maximum number of tasks to return (default: 10)

    Returns:
        List of task dictionaries
    """
    tasks = fetch_tasks(api_key, "today")
    return tasks[:limit]
