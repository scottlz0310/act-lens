"""Markdown形式でレポート生成"""

from act_lens.models import FailureInfo


class MarkdownFormatter:
    """FailureInfoからMarkdownレポートを生成"""

    def format(self, failure: FailureInfo, compact: bool = False) -> str:
        """
        AIチャット用のMarkdownレポートを生成

        Args:
            failure: 失敗情報
            compact: Trueの場合は簡潔モード（デフォルト: False=詳細）

        Returns:
            Markdownテキスト
        """
        if compact:
            return self._format_compact(failure)

        # デフォルト: 詳細モード
        sections = [
            self._header(failure),
            self._error_summary(failure),
            self._error_details(failure),
            self._stack_trace(failure),
        ]

        return "\n\n".join(filter(None, sections))

    def _header(self, failure: FailureInfo) -> str:
        """ヘッダーセクション"""
        return f"""## 🔍 Act-Lens Failure Report

**Workflow**: {failure.workflow} → {failure.job} → {failure.step}
**Failed at**: {failure.timestamp.strftime("%Y-%m-%d %H:%M:%S")}
**Duration**: {failure.format_duration()}"""

    def _error_summary(self, failure: FailureInfo) -> str:
        """エラーサマリーセクション"""
        lines: list[str] = ["### Error Summary", f"- Type: `{failure.error_type}`"]

        if location := failure.get_location():
            lines.append(f"- Location: `{location}`")

        lines.append(f"- Message: {failure.message}")

        return "\n".join(lines)

    def _error_details(self, failure: FailureInfo) -> str | None:
        """エラー詳細セクション"""
        if not failure.context_lines:
            return None

        lines: list[str] = ["### Error Details", "```python"]
        lines.extend(failure.context_lines)
        lines.append("```")

        return "\n".join(lines)

    def _stack_trace(self, failure: FailureInfo) -> str | None:
        """スタックトレースセクション"""
        if not failure.stack_trace:
            return None

        return f"""### Stack Trace
```
{failure.stack_trace}
```"""

    def _format_compact(self, failure: FailureInfo) -> str:
        """簡潔モード: エラーサマリーのみ"""
        return f"""## 🔍 Act-Lens Failure Report (Compact)

**Workflow**: {failure.workflow} → {failure.job}
**Error**: `{failure.error_type}`
**Message**: {failure.message}"""
