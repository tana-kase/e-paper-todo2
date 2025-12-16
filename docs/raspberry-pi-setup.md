# Raspberry Pi Zero 2 W セットアップ手順

## 必要なもの

- Raspberry Pi Zero 2 W
- Waveshare 7.5inch e-Paper HAT (V2)
- microSDカード (8GB以上)
- 電源アダプタ

## 1. Raspberry Pi OSのインストール

1. Raspberry Pi Imagerを使用してRaspberry Pi OS Liteをインストール
2. SSHを有効化（boot パーティションに空の `ssh` ファイルを作成）
3. Wi-Fi設定（`wpa_supplicant.conf` を作成）

## 2. SPIの有効化

```bash
sudo raspi-config
# Interfacing Options -> SPI -> Yes
sudo reboot
```

## 3. システム依存関係のインストール

```bash
sudo apt-get update
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    python3-pil \
    python3-numpy \
    libopenjp2-7 \
    libjpeg-dev \
    fonts-noto-cjk \
    git
```

## 4. プロジェクトのセットアップ

```bash
# プロジェクトをクローン
cd ~
git clone <repository-url> wall-todo
cd wall-todo

# 仮想環境を作成
python3 -m venv .venv
source .venv/bin/activate

# 依存関係をインストール
pip install -e .
pip install waveshare-epaper RPi.GPIO spidev
```

## 5. Zen Kurenaidoフォントのインストール

```bash
mkdir -p ~/.local/share/fonts
cp fonts/ZenKurenaido-Regular.ttf ~/.local/share/fonts/
fc-cache -fv
```

## 6. 環境変数の設定

```bash
cp .env.example .env
nano .env
# API_KEY=your_todoist_api_token_here
```

Todoist APIトークンは https://todoist.com/app/settings/integrations/developer から取得

## 7. 動作確認

```bash
source .venv/bin/activate
python -m src.wall_todo.main
```

## 8. cronの設定（定期実行）

```bash
crontab -e
```

以下を追加（15分ごとに実行）:

```
*/15 * * * * cd /home/pi/wall-todo && .venv/bin/python -m src.wall_todo.main >> /tmp/wall-todo.log 2>&1
```

## 9. フォールバック画像の設定

`images/` フォルダにPNG画像（480x800px）を配置すると、タスクがない日に表示されます。

```bash
# 例: 画像を追加
cp your-image.png ~/wall-todo/images/
```

## トラブルシューティング

### SPIエラー

```bash
# SPIが有効か確認
ls /dev/spi*
# /dev/spidev0.0 と /dev/spidev0.1 が表示されるはず
```

### フォントが表示されない

```bash
# フォントキャッシュを再構築
fc-cache -fv
fc-list | grep -i zen
```

### e-paperが反応しない

```bash
# 配線を確認
# VCC -> 3.3V
# GND -> GND
# DIN -> MOSI (GPIO10)
# CLK -> SCLK (GPIO11)
# CS  -> CE0 (GPIO8)
# DC  -> GPIO25
# RST -> GPIO17
# BUSY -> GPIO24
```

## ディレクトリ構成

```
~/wall-todo/
├── .env                 # APIキー
├── .venv/               # Python仮想環境
├── fonts/               # フォントファイル
├── images/              # フォールバック画像
├── output.png           # 生成された画像
└── src/wall_todo/       # ソースコード
```
