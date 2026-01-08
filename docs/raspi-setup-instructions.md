# Raspberry Pi Zero 2 W セットアップ手順（詳細版）

## 前提条件

- Raspberry Pi Zero 2 W（OS インストール済み、SSH接続可能）
- Waveshare 7.5inch e-Paper HAT (V2) が接続済み
- Wi-Fi接続済み
- SSHでアクセス可能な状態

---

## Step 1: SSH接続

```bash
ssh pi@<raspberry-piのIPアドレス>
```

接続できたら次へ進む。

---

## Step 2: SPIの有効化

e-Paperディスプレイとの通信にSPIが必要。

```bash
sudo raspi-config
```

メニュー操作:
1. `Interface Options` を選択
2. `SPI` を選択
3. `Yes` を選択して有効化
4. `Finish` で終了

再起動:
```bash
sudo reboot
```

再起動後、再度SSH接続。

SPIが有効か確認:
```bash
ls /dev/spi*
```

期待される出力:
```
/dev/spidev0.0  /dev/spidev0.1
```

---

## Step 3: システム依存関係のインストール

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
    git \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info
```

これには数分かかる。

---

## Step 4: プロジェクトのクローン

```bash
cd ~
git clone https://github.com/tana-kase/e-paper-todo2 wall-todo
cd wall-todo
```

> **注意**: リポジトリURLは実際のものに置き換える

---

## Step 5: Python仮想環境のセットアップ

```bash
python3 -m venv .venv
source .venv/bin/activate
```

プロンプトが `(.venv)` で始まることを確認。

---

## Step 6: Python依存関係のインストール

```bash
pip install --upgrade pip
pip install -e .
pip install waveshare-epaper RPi.GPIO spidev
```

> **注意**: Raspberry Pi Zero 2 Wではインストールに時間がかかる（10-20分）

---

## Step 7: Zen Kurenaidoフォントのインストール

```bash
mkdir -p ~/.local/share/fonts
cp fonts/ZenKurenaido-Regular.ttf ~/.local/share/fonts/
fc-cache -fv
```

フォントが認識されたか確認:
```bash
fc-list | grep -i zen
```

期待される出力:
```
/home/pi/.local/share/fonts/ZenKurenaido-Regular.ttf: Zen Kurenaido:style=Regular
```

---

## Step 8: 環境変数の設定

```bash
cp .env.example .env
nano .env
```

以下を編集:
```
API_KEY=your_todoist_api_token_here
```

Todoist APIトークンの取得先:
https://todoist.com/app/settings/integrations/developer

保存: `Ctrl+O` → `Enter` → `Ctrl+X`

---

## Step 9: 動作確認

```bash
source .venv/bin/activate
python -m src.wall_todo.main
```

期待される出力（タスクがある場合）:
```
Generated X tasks to /home/pi/wall-todo/output.png
Not on Raspberry Pi. Would display (partial): /home/pi/wall-todo/output.png
```

または（Raspberry Pi上で実行時）:
```
Generated X tasks to /home/pi/wall-todo/output.png
Displayed: /home/pi/wall-todo/output.png
```

**e-Paperにタスクが表示されれば成功！**

---

## Step 10: cronの設定（毎分実行）

```bash
crontab -e
```

初回は エディタを選択（nanoを推奨: 1を入力）

以下の行を追加:
```
* * * * * cd /home/pi/wall-todo && .venv/bin/python -m src.wall_todo.main >> /tmp/wall-todo.log 2>&1
```

保存して終了。

cron設定を確認:
```bash
crontab -l
```

---

## Step 11: ログの確認

1分待ってからログを確認:
```bash
tail -f /tmp/wall-todo.log
```

`Ctrl+C` で終了。

---

## トラブルシューティング

### SPIエラー

```bash
ls /dev/spi*
```

何も表示されない場合:
1. `sudo raspi-config` でSPIを再度有効化
2. 再起動

### フォントが表示されない

```bash
rm -rf ~/.cache/fontconfig
fc-cache -fv
fc-list | grep -i zen
```

### e-Paperが反応しない

配線を確認:
| e-Paper | Raspberry Pi |
|---------|--------------|
| VCC | 3.3V (Pin 1) |
| GND | GND (Pin 6) |
| DIN | MOSI / GPIO10 (Pin 19) |
| CLK | SCLK / GPIO11 (Pin 23) |
| CS | CE0 / GPIO8 (Pin 24) |
| DC | GPIO25 (Pin 22) |
| RST | GPIO17 (Pin 11) |
| BUSY | GPIO24 (Pin 18) |

### メモリ不足

```bash
free -h
```

スワップを増やす:
```bash
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# CONF_SWAPSIZE=100 を CONF_SWAPSIZE=512 に変更
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

### ログにエラーがない場合

手動で実行してエラーを確認:
```bash
cd ~/wall-todo
source .venv/bin/activate
python -m src.wall_todo.main
```

---

## フォールバック画像の追加（オプション）

タスクがない日に表示する画像を追加:

```bash
# SCPで画像を転送（ローカルPCから実行）
scp your-image.png pi@<raspberry-pi-ip>:~/wall-todo/uploads/
```

次回のcron実行時に自動変換される（480x800、4階調グレースケール）。

---

## 完了チェックリスト

- [ ] SSH接続できる
- [ ] SPI有効化済み（`/dev/spidev0.0` が存在）
- [ ] システム依存関係インストール済み
- [ ] プロジェクトクローン済み
- [ ] Python仮想環境セットアップ済み
- [ ] Python依存関係インストール済み
- [ ] Zen Kurenaidoフォントインストール済み
- [ ] `.env` にAPIキー設定済み
- [ ] `python -m src.wall_todo.main` が成功
- [ ] e-Paperに表示される
- [ ] cron設定済み
- [ ] 毎分更新されている
