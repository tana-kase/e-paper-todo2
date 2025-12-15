# CLAUDE.md

このファイルはClaude Codeがプロジェクトで作業する際のガイドラインです。

## コード規約

### フォーマット
- Pythonコードは **black** でフォーマットする
- コードを書いたら `black .` を実行すること

### 型定義
- 関数の引数と戻り値には型ヒントを付ける
- 内部変数の型は推論に任せる（明示的なアノテーション不要）
- 過度に複雑な型は避け、シンプルさを優先

```python
# Good
def fetch_tasks(token: str) -> list[dict]:
    tasks = []  # 型アノテーション不要
    ...

# Avoid
def fetch_tasks(token: str) -> List[Dict[str, Union[str, int, None]]]:
    tasks: List[Dict[str, Union[str, int, None]]] = []
    ...
```

### シンプルさ
- 過度な抽象化を避ける
- 必要になるまで機能を追加しない（YAGNI）
- コメントは「なぜ」を説明する場合のみ
