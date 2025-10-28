"""FailureInfoモデルのテスト"""

from datetime import datetime

from act_lens.models import FailureInfo


class TestFailureInfo:
    """FailureInfoモデルのテスト"""

    def test_create_minimal_failure_info(self) -> None:
        """最小限のフィールドでFailureInfoを作成"""
        failure = FailureInfo(
            workflow="test.yml",
            job="test-job",
            step="Run tests",
            error_type="UNKNOWN",
            message="Test failed",
        )
        assert failure.workflow == "test.yml"
        assert failure.job == "test-job"
        assert failure.step == "Run tests"
        assert failure.error_type == "UNKNOWN"
        assert failure.message == "Test failed"

    def test_create_full_failure_info(self) -> None:
        """すべてのフィールドを指定してFailureInfoを作成"""
        timestamp = datetime.now()
        failure = FailureInfo(
            workflow="ci.yml",
            job="lint",
            step="Run ruff",
            timestamp=timestamp,
            duration=12.5,
            error_type="BUILD_FAILURE",
            message="Linting failed",
            file_path="src/main.py",
            line_number=42,
            context_lines=["def main():", "    pass"],
            stack_trace="Traceback...",
        )
        assert failure.timestamp == timestamp
        assert failure.duration == 12.5
        assert failure.file_path == "src/main.py"
        assert failure.line_number == 42
        assert len(failure.context_lines) == 2
        assert failure.stack_trace == "Traceback..."

    def test_optional_fields_default_to_none(self) -> None:
        """オプショナルフィールドのデフォルト値"""
        failure = FailureInfo(
            workflow="test.yml",
            job="job",
            step="step",
            error_type="UNKNOWN",
            message="error",
        )
        assert failure.timestamp is not None  # 自動生成
        assert failure.duration is None
        assert failure.file_path is None
        assert failure.line_number is None
        assert failure.context_lines == []
        assert failure.stack_trace is None

    def test_error_type_normalization(self) -> None:
        """エラータイプが正規化される"""
        failure = FailureInfo(
            workflow="test.yml",
            job="job",
            step="step",
            error_type="assertion",  # 小文字
            message="error",
        )
        assert failure.error_type == "ASSERTION"

    def test_format_duration_seconds(self) -> None:
        """秒単位の実行時間フォーマット"""
        failure = FailureInfo(
            workflow="test.yml",
            job="job",
            step="step",
            error_type="TIMEOUT",
            message="timeout",
            duration=45.0,
        )
        formatted = failure.format_duration()
        assert formatted == "45.0秒"

    def test_format_duration_minutes(self) -> None:
        """分単位の実行時間フォーマット"""
        failure = FailureInfo(
            workflow="test.yml",
            job="job",
            step="step",
            error_type="TIMEOUT",
            message="timeout",
            duration=125.5,
        )
        formatted = failure.format_duration()
        assert formatted == "2m 5s"

    def test_format_duration_none(self) -> None:
        """実行時間がNoneの場合"""
        failure = FailureInfo(
            workflow="test.yml",
            job="job",
            step="step",
            error_type="UNKNOWN",
            message="error",
        )
        formatted = failure.format_duration()
        assert formatted == "0.0秒"

    def test_get_location_with_file_and_line(self) -> None:
        """ファイルパスと行番号がある場合"""
        failure = FailureInfo(
            workflow="test.yml",
            job="job",
            step="step",
            error_type="ASSERTION",
            message="error",
            file_path="tests/test_example.py",
            line_number=42,
        )
        location = failure.get_location()
        assert location == "tests/test_example.py:42"

    def test_get_location_file_only(self) -> None:
        """ファイルパスのみの場合"""
        failure = FailureInfo(
            workflow="test.yml",
            job="job",
            step="step",
            error_type="ASSERTION",
            message="error",
            file_path="tests/test_example.py",
        )
        location = failure.get_location()
        assert location == "tests/test_example.py"

    def test_get_location_none(self) -> None:
        """ファイルパスがない場合"""
        failure = FailureInfo(
            workflow="test.yml",
            job="job",
            step="step",
            error_type="UNKNOWN",
            message="error",
        )
        location = failure.get_location()
        assert location == "場所不明"

    def test_context_lines_empty_list(self) -> None:
        """context_linesが空リスト"""
        failure = FailureInfo(
            workflow="test.yml",
            job="job",
            step="step",
            error_type="UNKNOWN",
            message="error",
            context_lines=[],
        )
        assert failure.context_lines == []
