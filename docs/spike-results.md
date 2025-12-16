# フェーズ0 技術検証結果

実施日: 2025-12-16

## 非機能要件

| 要件 | 内容 |
|------|------|
| 処理時間 | e-paper描画まで1分以内（画面クリア含む） |
| 画質 | ぼやけて見えないこと（十分な解像度） |
| 画面クリア | 5回に1回フルリフレッシュ（ゴースト防止） |

参考: [Makerguides - Partial Refresh of e-Paper Display](https://www.makerguides.com/partial-refresh-e-paper-display-esp32/)

## 意思決定: HTML→PNG変換方式

**決定: WeasyPrint + PyMuPDF + Pillow を採用**

### 比較検証結果

| 方法 | 時間 | メモリ | Zero 2 W対応 |
|------|------|--------|--------------|
| **WeasyPrint** | 12.5秒 | 192MB | ✅ 動作可能 |
| Playwright | 未計測 | 推定300-500MB | ⚠️ 厳しい |

### 採用理由

1. **メモリ効率**: 192MB で Raspberry Pi Zero 2 W (512MB RAM) に収まる
2. **処理時間**: 12.5秒 で1分以内の要件を満たす
3. **依存の軽量さ**: Chromium不要でディスク・メモリ節約

### 却下理由 (Playwright)

- Chromiumが300-500MB消費し、512MB RAMでスワップ発生リスク
- インストールサイズが大きい（〜300MB）

---

## 1. HTML→PNG変換パイプライン

WeasyPrintは直接PNG出力をサポートしていないため、以下の組み合わせが必要。

```
HTML → WeasyPrint → PDF → PyMuPDF → PNG → Pillow → リサイズ
```

### 必要ライブラリ

| ライブラリ | 用途 |
|-----------|------|
| weasyprint | HTML→PDF変換 |
| pymupdf (fitz) | PDF→PNG変換 |
| pillow | 正確なサイズにリサイズ |

### サンプルコード

```python
from weasyprint import HTML
import fitz  # PyMuPDF
from PIL import Image
import io

def html_to_png(html_content: str, output_path: str, width: int = 480, height: int = 800):
    # HTML → PDF
    pdf_bytes = HTML(string=html_content).write_pdf()

    # PDF → PNG（高解像度）
    pdf_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = pdf_doc[0]
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
    img_data = pix.tobytes("png")
    pdf_doc.close()

    # リサイズして保存
    img = Image.open(io.BytesIO(img_data))
    img_resized = img.resize((width, height), Image.Resampling.LANCZOS)
    img_resized.save(output_path)
```

## 2. 日本語フォント

### システム依存関係（Dockerfile）

```dockerfile
fonts-noto-cjk
```

### CSS設定

```css
font-family: 'Noto Sans CJK JP', 'Noto Sans JP', sans-serif;
```

## 3. Todoist API

### 認証方式

Bearer Token認証

### エンドポイント

```
GET https://api.todoist.com/rest/v2/tasks?filter=today
```

### サンプルコード

```python
import os
from dotenv import load_dotenv
import requests

load_dotenv()
api_key = os.getenv('API_KEY')

response = requests.get(
    "https://api.todoist.com/rest/v2/tasks",
    params={"filter": "today"},
    headers={"Authorization": f"Bearer {api_key}"}
)

tasks = response.json()
```

### 必要ライブラリ

- python-dotenv
- requests

## 4. 出力仕様

| 項目 | 値 |
|------|-----|
| サイズ | 480x800px（縦長） |
| フォーマット | PNG |
| フォント | Noto Sans CJK JP |
| 基本フォントサイズ | 20px |

## 5. まとめ：必要な依存関係

### Python パッケージ

```
weasyprint
pymupdf
pillow
python-dotenv
requests
jinja2
```

### システムパッケージ（Dockerfile）

```
python3
python3-pip
python3-venv
libpango-1.0-0
libpangocairo-1.0-0
libgdk-pixbuf2.0-0
libffi-dev
shared-mime-info
fonts-noto-cjk
```
