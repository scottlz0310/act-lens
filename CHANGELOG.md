# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-10-28

### Added - MVP Release 🎉

#### Core Features
- **act実行とログキャプチャ**: actコマンドを実行してログを取得
- **エラー検出**: 11種類のエラーパターン認識（ASSERTION, TIMEOUT, SYNTAX, IMPORT, BUILD_FAILURE等）
- **Markdown整形**: AIチャットに貼り付けやすい形式で出力
- **クリップボード統合**: 自動的にクリップボードにコピー
- **ファイル保存**: `.act-lens/`ディレクトリに履歴保存

#### Error Detection
- 成功パターンフィルタリングで誤検知を防止
- スタックトレース抽出
- ファイルパスと行番号の検出
- 実行時間の自動抽出（ms/s/m形式対応）

#### CLI
- `act-lens`: デフォルトで全ワークフロー実行
- `act-lens --workflow ci.yml`: 特定ワークフロー指定
- `act-lens --job test`: 特定ジョブ指定
- Rich統合で美しいターミナル出力

#### Quality Assurance
- **テストカバレッジ**: 76%（主要モジュール97-100%）
- **リント**: ruff（check + format）
- **型チェック**: mypy
- **セキュリティ**: bandit + safety
- **CI/CD**: GitHub Actions完全統合
- **Pre-commit hooks**: 自動品質チェック

### Technical Details

#### Dependencies（4つ厳守）
- typer>=0.12.0 - モダンCLIフレームワーク
- rich>=13.7.0 - 美しいターミナル出力
- pydantic>=2.0 - データバリデーション
- pyperclip>=1.8.0 - クリップボード操作

#### Architecture
- **シンプル**: 約500行（目標300-400行を若干超過だが許容範囲）
- **単一責任**: actログの整形に特化
- **拡張性**: 必要になってから機能追加

### Design Philosophy

**ci-helperプロジェクトの教訓を活かした設計**:
- ❌ API統合不要 - 手動貼り付けの方が柔軟
- ❌ 複数プロバイダー対応不要 - Markdownで十分
- ❌ キャッシュ/コスト管理不要 - シンプルさ優先
- ✅ 「実行 → 整形 → コピー」のみに集中

### Installation

```bash
# uvを使用（推奨）
uv tool install git+https://github.com/scottlz0310/act-lens.git

# pipxを使用
pipx install git+https://github.com/scottlz0310/act-lens.git
```

**Note**: PyPIには公開していません。GitHubリポジトリから直接インストールしてください。

### Prerequisites

- Python 3.11以上
- act (GitHub Actions local runner)
- Docker

### Known Limitations

- actローカル実行専用（GitHub Actions本番ログは対象外）
- CLI統合テスト未実装（手動テスト済み）
- コンテキスト行抽出は未実装（TODO）

### Future Considerations (Phase 2以降)

実際に使って効果を検証してから検討：
- より詳細なエラー解析
- カスタムパターン対応
- 統計情報表示

---

## [Unreleased]

### Changed
- `.actrc`に`--rm`オプション追加推奨（Dockerコンテナ自動削除）

[0.1.0]: https://github.com/scottlz0310/act-lens/releases/tag/v0.1.0
