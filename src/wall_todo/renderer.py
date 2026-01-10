"""HTML rendering and PNG conversion."""

import io
import shutil
from pathlib import Path

import fitz  # PyMuPDF
from jinja2 import Environment, FileSystemLoader
from PIL import Image
from weasyprint import HTML

from .fallback import get_fallback_image

TEMPLATE_DIR = Path(__file__).parent / "templates"
TARGET_WIDTH = 480
TARGET_HEIGHT = 800


def render_html(tasks: list[dict]) -> str:
    """
    Render HTML from tasks using Jinja2 template.

    Args:
        tasks: List of task dictionaries with 'content' key

    Returns:
        Rendered HTML string
    """
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("board.html")

    return template.render(tasks=tasks)


def html_to_png(html_content: str, output_path: str | Path) -> None:
    """
    Convert HTML to PNG image.

    Args:
        html_content: HTML string to convert
        output_path: Path to save the PNG file
    """
    # HTML -> PDF
    pdf_bytes = HTML(string=html_content).write_pdf()

    # PDF -> PNG (high resolution)
    pdf_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = pdf_doc[0]
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
    img_data = pix.tobytes("png")
    pdf_doc.close()

    # Resize to exact dimensions
    img = Image.open(io.BytesIO(img_data))
    img_resized = img.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
    img_resized.save(output_path)


def render_board(tasks: list[dict], output_path: str | Path) -> bool:
    """
    Render tasks to PNG image. Uses fallback image if no tasks.

    Args:
        tasks: List of task dictionaries
        output_path: Path to save the PNG file

    Returns:
        True if tasks were rendered, False if fallback image was used
    """
    if not tasks:
        fallback = get_fallback_image()
        if fallback:
            shutil.copy(fallback, output_path)
            return False
        # No fallback available, render empty task list
    html = render_html(tasks)
    html_to_png(html, output_path)
    return True
