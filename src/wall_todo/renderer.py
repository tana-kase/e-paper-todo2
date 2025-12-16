"""HTML rendering and PNG conversion."""

import io
from datetime import datetime, timezone, timedelta
from pathlib import Path

JST = timezone(timedelta(hours=9))

import fitz  # PyMuPDF
from jinja2 import Environment, FileSystemLoader
from PIL import Image
from weasyprint import HTML

TEMPLATE_DIR = Path(__file__).parent / "templates"
TARGET_WIDTH = 480
TARGET_HEIGHT = 800


def render_html(tasks: list[dict], updated_at: datetime | None = None) -> str:
    """
    Render HTML from tasks using Jinja2 template.

    Args:
        tasks: List of task dictionaries with 'content' key
        updated_at: Timestamp for footer (default: now)

    Returns:
        Rendered HTML string
    """
    if updated_at is None:
        updated_at = datetime.now(JST)

    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("board.html")

    return template.render(
        tasks=tasks,
        updated_at=updated_at.strftime("%m.%d %H:%M"),
    )


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


def render_board(tasks: list[dict], output_path: str | Path) -> None:
    """
    Render tasks to PNG image.

    Args:
        tasks: List of task dictionaries
        output_path: Path to save the PNG file
    """
    html = render_html(tasks)
    html_to_png(html, output_path)


if __name__ == "__main__":
    # Test with dummy data
    dummy_tasks = [
        {"content": "買い物に行く"},
        {"content": "日本語テスト：漢字・ひらがな・カタカナ"},
        {"content": "これは30文字を超える非常に長いタスク名のテストです。省略されるはずです。"},
    ]

    output = Path(__file__).parent.parent.parent / "output.png"
    print(f"Output path: {output}")
    render_board(dummy_tasks, output)
    print(f"Generated: {output}")
