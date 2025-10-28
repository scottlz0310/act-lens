# act-lens 設計ドキュメント

## プロジェクト概要

### 目的
ローカルでGitHub Actionsワークフローを実行（act使用）し、失敗時のログを整形してAIチャットに貼り付けやすくする軽量CLIツール。

### 名前の由来
**act-lens** = actの出力を「レンズ」で覗いて整形する
- 生のログを「見やすく」整形
- 必要な情報に「フォーカス」
- エラーを「クリア」に表示

### 背景
ci-helperプロジェクト（43,653行/94ファイル）の教訓：
- ❌ API統合は不要 → 手動貼り付けの方が柔軟
- ❌ 複数プロバイダー対応は過剰 → どのAIでもMarkdown貼り付けで十分
- ❌ キャッシュ・コスト管理は複雑すぎる → CIは毎回実行すべき
- ✅ 必要なのは「実行 → 整形 → コピー」のみ

### 設計原則
1. **シンプル第一** - 300-400行以内、過剰な機能を付けない
2. **単一責任** - CIログの整形に集中
3. **手動優先** - AIへの貼り付けは手動で行う（柔軟性と制御）
4. **拡張性** - 必要になってから機能追加

---

## コア機能（MVP）

### 1. ワークフロー実行
```bash
# インタラクティブ選択
$ act-lens

# 直接指定
$ act-lens --workflow ci.yml
```

### 2. 失敗ログの抽出と分析
- actの出力から失敗情報を抽出
- エラータイプ判定（ASSERTION, TIMEOUT, BUILD_FAILURE等）
- ファイルパス・行番号・スタックトレースの検出

### 3. Markdown形式で整形
```markdown
## 🔍 Act-Lens Failure Report

**Workflow**: ci.yml → test → Run pytest
**Failed at**: 2025-10-27 22:30:15
**Duration**: 12.5s

### Error Summary
- Type: ASSERTION_ERROR
- File: tests/test_calculation.py:42
- Message: AssertionError: assert 3 == 5

### Error Details
[コンテキスト付きコード]

### Stack Trace
[スタックトレース]
```

### 4. 出力オプション
- ファイル保存（`.act-lens/failures/`）
- クリップボードコピー（自動）
- ターミナルプレビュー（Rich使用）

---

## アーキテクチャ

### ファイル構造
```
act-lens/
├── pyproject.toml
├── README.md
└── src/
    └── act_lens/
        ├── __init__.py
        ├── cli.py           # CLIエントリーポイント（Typer）
        ├── runner.py        # act実行とログキャプチャ
        ├── parser.py        # ログ解析とエラー抽出
        ├── formatter.py     # Markdown生成
        ├── models.py        # Pydanticデータモデル
        └── utils.py         # ヘルパー関数

目標: 300-400行
```

### データフロー
```
ユーザー入力
  ↓
ワークフロー選択 (cli.py)
  ↓
act実行 (runner.py)
  ↓
ログ解析 (parser.py) → FailureInfo抽出
  ↓
Markdown生成 (formatter.py)
  ↓
出力 (ファイル/クリップボード/標準出力)
```

### データモデル（Pydantic）
```python
class FailureInfo(BaseModel):
    workflow: str              # "ci.yml"
    job: str                   # "test"
    step: str                  # "Run pytest"
    timestamp: datetime
    duration: float            # 秒数
    error_type: str            # "ASSERTION", "TIMEOUT", etc.
    message: str               # エラーメッセージ
    file_path: str | None      # "tests/test_calculation.py"
    line_number: int | None    # 42
    context_lines: list[str]   # コード前後の行
    stack_trace: str | None    # スタックトレース全体
```

**Pydantic採用理由**:
- 自動バリデーション（duration≥0、line_number≥1）
- JSON/辞書との相互変換が簡単
- 型安全性
- Typerとの自然な統合

---

## 技術スタック

### 依存関係（4つのみ）
```toml
dependencies = [
    "typer>=0.12.0",     # モダンなCLI（型ヒント、Rich統合）
    "rich>=13.7.0",      # 美しいターミナル出力
    "pydantic>=2.0",     # データバリデーション
    "pyperclip>=1.8.0",  # クリップボード操作
]
```

**Typer採用理由**:
- 型ヒント完全サポート
- 自動的な型変換とバリデーション
- Rich統合（美しい出力）
- インタラクティブプロンプト機能
- ドキュメント生成が簡単

### 外部ツール（前提条件）
- **act** - GitHub Actionsローカル実行
- **Docker** - actの実行環境

### 配布方法（PyPI不使用）
```bash
# uv経由（推奨）
$ uv tool install git+https://github.com/[user]/act-lens.git

# pipx経由
$ pipx install git+https://github.com/[user]/act-lens.git
```

**PyPI不使用の理由**:
- 削除不可問題
- uvやpipxで十分に代替可能
- 実験的な変更も気軽にできる
- バージョン管理はGitタグで十分

---

## コマンド仕様

### `act-lens` (デフォルト)
ワークフローを選択して実行

**オプション**:
- `--workflow TEXT` - ワークフロー直接指定
- `--job TEXT` - 特定ジョブのみ実行
- `--preview` - プレビュー表示
- `--no-clipboard` - クリップボードコピーなし
- `--output PATH` - カスタム出力先
- `--verbose` - 詳細ログ表示

### `act-lens list`
利用可能なワークフローを一覧表示

### `act-lens show [INDEX]`
過去の失敗レポートを表示
- `INDEX` 省略時は最新
- `--copy` でクリップボードにコピー

### `act-lens history`
実行履歴を表示
- `--limit INT` で表示件数指定

### `act-lens clean`
古いログを削除
- `--days INT` で保持日数指定（デフォルト: 7）
- `--all` で全削除

---

## 実装計画

### Phase 1: MVP（最小実装） ← 現在ここ
1. プロジェクト構造作成
2. `act-lens run` 基本実装
   - act実行とログキャプチャ
   - エラー解析
   - Markdown生成
   - クリップボードコピー
3. 基本的な動作確認

**目標**: 実際に使って効果を検証

### Phase 2: 使いやすさ向上
- インタラクティブなワークフロー選択
- `act-lens list` / `show` 実装
- エラーメッセージ改善
- Rich使用の出力改善

### Phase 3: 便利機能
- `act-lens history` 実装
- プレビュー機能強化
- 設定ファイル対応（オプション）

### Phase 4: TUI（将来的な拡張） 🎯
- Textualを使用したTUI実装
- リアルタイムログ表示
- ビジュアルなワークフロー選択
- `--no-tui` フラグでCLIモード維持

**方針**: CLIでMVP完成 → 効果検証 → TUI追加検討

---

## 意図的に実装しない機能

### ❌ AI API統合
**理由**: チャット欄への手動貼り付けの方が柔軟で、定額プラン外の課金を避けられる

### ❌ 自動修正提案
**理由**: AIの提案を見て手動で修正する方が安全で学習になる

### ❌ 複数フォーマット対応
**理由**: Markdownで十分。AIチャットはMarkdownを理解する

### ❌ キャッシュ機構
**理由**: CIは毎回実行すべき。キャッシュは複雑性を増す

### ❌ 統計・分析機能
**理由**: シンプルさを保つため。必要なら別ツールで

### ❌ Git統合
**理由**: コミット情報等は必要になってから

### ❌ 通知機能
**理由**: ターミナルで完結。通知は不要

---

## 成功指標

### 定量的
- **コード量**: 300-400行
- **依存関係**: 4つ（全て正当な理由あり）
- **実行時間**: act実行時間 + 3秒以内
- **生成ファイル**: 10KB以内

### 定性的
- ✅ 1コマンドで失敗ログをAIに渡せる
- ✅ 5分以内にセットアップ完了
- ✅ ドキュメント不要で直感的に使える
- ✅ ci-helperの複雑さを感じない

---

## ci-helperとの比較

| 観点 | ci-helper | act-lens |
|------|-----------|----------|
| **コード量** | 43,653行/94ファイル | ~400行/7ファイル |
| **依存関係** | 多数 | 4つ |
| **AI統合** | 複数プロバイダー対応 | なし（手動） |
| **キャッシュ** | 詳細な機構 | なし |
| **学習曲線** | 中〜高 | 低 |
| **用途** | 多機能・チーム向け | 個人・シンプル |

---

## まとめ

**act-lens**は、ci-helperの教訓を活かし、本当に必要な機能だけに絞った軽量ツール。

**コンセプト**:
- actの出力を「レンズ」で覗いて整形
- AIチャットへの貼り付けを簡単に
- シンプルで保守しやすい設計

**次のステップ**:
1. MVP実装（Phase 1）
2. 実際に使って効果検証
3. 必要に応じて機能追加（TUI等）
