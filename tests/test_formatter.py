"""MarkdownFormatterのテスト"""

import pytest

from act_lens.formatter import MarkdownFormatter
from act_lens.models import FailureInfo


class TestMarkdownFormatter:
    """MarkdownFormatterクラスのテスト"""

    @pytest.fixture
    def formatter(self) -> MarkdownFormatter:
        """MarkdownFormatterインスタンスを生成"""
        return MarkdownFormatter()

    @pytest.fixture
    def sample_failure(self) -> FailureInfo:
        """サンプルのFailureInfoを生成"""
        return FailureInfo(
            workflow="test.yml",
            job="test-job",
            step="Run tests",
            error_type="ASSERTION",
            message="AssertionError: expected 5 but got 3",
            file_path="tests/test_example.py",
            line_number=42,
            context_lines=["def test_example():", "    assert 5 == 3"],
            stack_trace="Traceback...",
        )

    def test_format_basic_structure(
        self, formatter: MarkdownFormatter, sample_failure: FailureInfo
    ) -> None:
        """基本的なMarkdown構造が生成される"""
        markdown = formatter.format(sample_failure)
        assert "# 🔍 Act-Lens Failure Report" in markdown
        assert "## Error Summary" in markdown
        assert "## Error Details" in markdown

    def test_format_contains_workflow_info(
        self, formatter: MarkdownFormatter, sample_failure: FailureInfo
    ) -> None:
        """ワークフロー情報が含まれる"""
        markdown = formatter.format(sample_failure)
        assert "test.yml" in markdown
        assert "test-job" in markdown
        assert "Run tests" in markdown

    def test_format_contains_error_type(
        self, formatter: MarkdownFormatter, sample_failure: FailureInfo
    ) -> None:
        """エラータイプが含まれる"""
        markdown = formatter.format(sample_failure)
        assert "`ASSERTION`" in markdown

    def test_format_contains_file_location(
        self, formatter: MarkdownFormatter, sample_failure: FailureInfo
    ) -> None:
        """ファイルパスと行番号が含まれる"""
        markdown = formatter.format(sample_failure)
        assert "tests/test_example.py" in markdown
        # Locationセクションに表示される形式
        assert "tests/test_example.py:42" in markdown

    def test_format_contains_error_message(
        self, formatter: MarkdownFormatter, sample_failure: FailureInfo
    ) -> None:
        """エラーメッセージが含まれる"""
        markdown = formatter.format(sample_failure)
        assert "expected 5 but got 3" in markdown

    def test_format_contains_stack_trace(
        self, formatter: MarkdownFormatter, sample_failure: FailureInfo
    ) -> None:
        """スタックトレースが含まれる"""
        markdown = formatter.format(sample_failure)
        assert "Traceback" in markdown
        assert "```" in markdown  # コードブロック

    def test_format_without_optional_fields(self, formatter: MarkdownFormatter) -> None:
        """オプショナルフィールドがなくてもフォーマット可能"""
        minimal_failure = FailureInfo(
            workflow="minimal.yml",
            job="job",
            step="step",
            error_type="UNKNOWN",
            message="Something failed",
        )
        markdown = formatter.format(minimal_failure)
        assert "# 🔍 Act-Lens Failure Report" in markdown
        assert "`UNKNOWN`" in markdown

    def test_format_duration_display(self, formatter: MarkdownFormatter) -> None:
        """実行時間が表示される"""
        failure = FailureInfo(
            workflow="test.yml",
            job="job",
            step="step",
            error_type="TIMEOUT",
            message="Timeout",
            duration=125.5,
        )
        markdown = formatter.format(failure)
        assert "Duration" in markdown
        # format_duration()の出力形式をチェック
        assert "2m 5s" in markdown or "125" in markdown
