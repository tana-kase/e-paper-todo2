# wall-todo

Raspberry PiとE-Paperディスプレイで作る、壁掛けToDoボード。

<img src="https://github.com/user-attachments/assets/f0be3290-f1ac-48a7-bca3-155f3c874861" width="50%" />

## これは何？

Todoistの「今日やること」を部屋の壁に常時表示するプロジェクトです。

スマホを開かなくても、ふと目に入るところにタスクがあるだけで、自然と手が動く。そんな体験を目指して作りました。

## 特徴

- **見ようとしなくても見える** - 部屋の壁にボードがあり、視界に自然に入る
- **省エネ設計** - タスクに変更がなければ画面を書き換えない
- **手書き風フォント** - Zen Kurenaido で温かみのあるデザイン
- **タスク0のときは画像表示** - やることがない日は好きな画像を表示

## 技術スタック

- **ハードウェア**: Raspberry Pi Zero 2 W + Waveshare 7.5インチ E-Paper HAT
- **言語**: Python 3.11
- **主要ライブラリ**:
  - WeasyPrint - HTML→PNG変換
  - PyMuPDF - PDF処理
  - Jinja2 - テンプレートエンジン
  - Pillow - 画像処理
  - waveshare-epaper - E-Paper制御

## セットアップ

詳細な手順は [docs/raspi-setup-instructions.md](docs/raspi-setup-instructions.md) を参照してください。

### クイックスタート

```bash
# プロジェクトをクローン
git clone https://github.com/tana-kase/e-paper-todo2.git
cd e-paper-todo2

# 仮想環境を作成
python3 -m venv .venv
source .venv/bin/activate

# 依存関係をインストール
pip install -e .

# 環境変数を設定
cp .env.example .env
# .env に Todoist API キーを設定

# 実行
python -m wall_todo.main
```

## 使い方

### タスクの追加

- 「Todoistに『メール返信 今日』を追加」
- 「Todoistに『掃除 今日』を追加」

### タスクの完了

- 「Todoistで『メール返信』を完了」

最大1分後にボードから消えます。

### フォールバック画像の追加

タスクがない日に表示する画像を設定できます：

```bash
# uploads/ に画像を配置
cp your-image.jpg uploads/

# 次回実行時に自動的に 480x800px、4階調グレースケールに変換され images/ に保存されます
```

## 運用

### 定期実行（cron）

毎分実行する設定：

```bash
crontab -e
```

以下を追加：

```
* * * * * cd /home/pi/e-paper-todo2 && .venv/bin/python -m wall_todo.main >> /tmp/wall-todo.log 2>&1
```

### タスク変更検知

前回と同じタスクの場合は画面更新をスキップします。これによりE-Paperの寿命を延ばします。

## ドキュメント

- [仕様書](todo-board-spec.md) - プロジェクトの背景と設計思想
- [技術検証結果](docs/spike-results.md) - 採用技術の検証記録
- [セットアップ手順](docs/raspi-setup-instructions.md) - Raspberry Piのセットアップ詳細

## 開発

### コード規約

プロジェクトのコード規約は [CLAUDE.md](CLAUDE.md) を参照してください。

### フォーマット

```bash
source .venv/bin/activate
black .
```

## ライセンス

MIT License

このプロジェクトは個人利用を想定して作られています。

## 謝辞

- [Waveshare](https://www.waveshare.com/) - E-Paper HAT
- [Todoist](https://todoist.com/) - タスク管理API
- [Google Fonts](https://fonts.google.com/) - Zen Kurenaido フォント
