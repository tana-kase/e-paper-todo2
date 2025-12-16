# フェーズ0 技術検証結果

実施日: 2025-12-16

## 非機能要件

| 要件 | 内容 |
|------|------|
| 処理時間 | e-paper描画まで1分以内（画面クリア含む） |
| 画質 | ぼやけて見えないこと（十分な解像度） |
| 画面クリア | 5回に1回フルリフレッシュ（ゴースト防止） |

参考: [Makerguides - Partial Refresh of e-Paper Display](https://www.makerguides.com/partial-refresh-e-paper-display-esp32/)

## ハードウェア仕様: Waveshare 7.5inch e-Paper HAT

| 項目 | 仕様 |
|------|------|
| 解像度 | 800×480（縦長使用時: 480×800） |
| グレースケール | 4階調（白・ライトグレー・ダークグレー・黒） |
| 全画面更新 | 4秒 |
| 部分更新 | 0.4秒 |
| 4階調更新 | 2.1秒 |
| 消費電力 | 26.4mW（待機時ほぼ0） |

### 注意事項

- 部分更新を繰り返すと残像（ゴースト）が悪化し、ディスプレイ損傷の可能性あり
- 数回の部分更新後には全画面更新が必要（推奨: 5回に1回）
- V2版（2023年9月以降販売）は `7.5V2` プログラムを使用

### 処理時間見積もり

```
PNG生成（WeasyPrint）: 12.5秒
e-Paper全画面更新:     4.0秒
合計:                 約17秒 → 1分以内の要件を満たす ✅
```

### デザインへの影響

4階調対応のため、グレー背景（#f5f5f5）は実機でライトグレーとして表示される。
白黒2色ではないため、現在のデザインはそのまま使用可能。

参考:
- [Waveshare 7.5inch e-Paper HAT Manual](https://www.waveshare.com/wiki/7.5inch_e-Paper_HAT_Manual)
- [Waveshare 7.5inch e-Paper HAT Product Page](https://www.waveshare.com/7.5inch-e-paper-hat.htm)

## 意思決定: フォント選定

**決定: Zen Kurenaido を採用**

### 比較したフォント

| フォント | 特徴 | 評価 |
|---------|------|------|
| Noto Sans CJK JP | ゴシック、モダン | △ 冷たい印象 |
| Noto Serif CJK JP | 明朝体、フォーマル | ○ 落ち着き |
| **Zen Kurenaido** | 筆ペン風、手書き感 | ◎ 暖かみ |

### 採用理由

1. ウォルナット+暖色照明の空間に合う暖かみ
2. 手書き感がありパーソナルな印象
3. 可読性を保ちつつ柔らかい雰囲気

### フォントファイル

- `fonts/ZenKurenaido-Regular.ttf`
- Google Fonts: https://fonts.google.com/specimen/Zen+Kurenaido
- ライセンス: OFL (Open Font License)

---

## 意思決定: タスク表示の行数

**決定: 1行強制（CSS `text-overflow: ellipsis`）**

### 検証結果

| パターン | 10件表示 | 問題 |
|---------|---------|------|
| 1行強制 | ✅ 余裕あり | なし |
| 2行許容 | ⚠️ ギリギリ | 長いタスクが多いと窮屈 |
| 3行許容 | ❌ 限界 | フッターと重なる |
| 全部2行 | ❌ 溢れる | 8件目までしか表示されない |

### 採用理由

1. 10件表示を保証するため
2. 整然とした見た目を維持
3. タスク名が長い場合でもレイアウトが崩れない

### CSS実装

```css
.task {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
```

---

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
