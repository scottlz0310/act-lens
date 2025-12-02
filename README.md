# act-lens 🔍

[![CI](https://github.com/scottlz0310/act-lens/actions/workflows/ci.yml/badge.svg)](https://github.com/scottlz0310/act-lens/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

actの出力を「レンズ」で覗いて整形する軽量CLIツール

## 概要

**act-lens**は、ローカルでGitHub Actionsワークフローを実行（act使用）し、失敗時のログを整形してAIチャットに貼り付けやすくするツールです。

### 特徴

- 🎯 **シンプル** - 300-400行、依存関係4つのみ
- ⚡ **高速** - act実行時間 + 3秒以内
- 📋 **クリップボード対応** - 1コマンドでAIに貼り付け可能
- 🎨 **美しい出力** - Rich使用のターミナル表示

## インストール

```bash
# uv経由（推奨）
uv tool install git+https://github.com/scottlz0310/act-lens.git

# pipx経由
pipx install git+https://github.com/scottlz0310/act-lens.git
```

## 必要な環境

- Python 3.11以上
- [act](https://github.com/nektos/act) - GitHub Actionsローカル実行
- Docker - actの実行環境

**actの設定（推奨）:**

`.actrc`ファイルを作成してact-latestイメージを使用（GitHub Actions互換）：

```bash
echo "-P ubuntu-latest=ghcr.io/catthehacker/ubuntu:act-latest" > .actrc
```

注意: act-latestイメージは約18GBあります。

## 使い方

```bash
# 基本実行（ワークフロー選択）
act-lens

# ワークフロー直接指定
act-lens --workflow ci.yml

# プレビュー表示
act-lens --preview

# ヘルプ表示
act-lens --help
```

## 設計原則

1. **シンプル第一** - 過剰な機能を付けない
2. **単一責任** - CIログの整形に集中
3. **手動優先** - AIへの貼り付けは手動で行う
4. **拡張性** - 必要になってから機能追加

## 技術スタック

- **Typer** - モダンなCLIフレームワーク
- **Rich** - 美しいターミナル出力
- **Pydantic** - データバリデーション
- **pyperclip** - クリップボード操作

## 開発

```bash
# リポジトリクローン
git clone https://github.com/[user]/act-lens.git
cd act-lens

# 依存関係インストール
uv sync

# 開発モードで実行
uv run act-lens

# リント・テスト
uv run ruff check .
uv run mypy src
uv run pytest
```

### 開発者向け: pre-commit & pre-push フック

このリポジトリは `pre-commit` を利用して開発者の利便性と品質を保っています。導入済みの主要なフックは次の通りです。

- 基本的なコード整形・安全チェック: `ruff`, `bandit`, `safety`
- 文字列・改行・YAML の軽微な修正: `trailing-whitespace`, `end-of-file-fixer`, `check-yaml`
- マージコンフリクトや大きすぎるファイルの検出: `check-merge-conflict`, `check-added-large-files`
- `detect-secrets` によるシークレット漏洩の検出（`.secrets.baseline` を用いて既知の検出を無視）
- `pytest` は `pre-push` フックとして実行されます（軽量なのでローカルで自動チェックを実施）

導入手順:

```bash
# 依存関係のインストール
uv sync

# pre-commit のインストール
uv run pre-commit install

# シークレットのベースライン作成（初回のみ）
uv run detect-secrets scan > .secrets.baseline
# 必要に応じて .secrets.baseline をレビューしてコミット

# 手動チェック
uv run pre-commit run --all-files
```

注意:
- `detect-secrets` は false positive を返すことがあります。ベースラインを更新する前に検出結果をレビューしてください。
- `pytest` は push 時に自動実行されますが、CIでも再度チェックされます。


## ライセンス

MIT License

## 詳細ドキュメント

- [設計ドキュメント](docs/design.md)
- [コーディング規約](.github/copilot-instructions.md)
