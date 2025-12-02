"""LogParserのテスト"""
# pyright: reportPrivateUsage=false

import re

import pytest

from act_lens.models import FailureInfo
from act_lens.parser import LogParser


class TestLogParser:
    """LogParserクラスのテスト"""

    @pytest.fixture
    def parser(self) -> LogParser:
        """LogParserインスタンスを生成"""
        return LogParser()

    def test_detect_build_failure(self, parser: LogParser) -> None:
        """BUILD_FAILUREタイプを正しく検出"""
        log = "[CI/test] ❌ Failure - Main Run tests"
        error_type = parser._detect_error_type(log)
        assert error_type == "BUILD_FAILURE"

    def test_detect_assertion_error(self, parser: LogParser) -> None:
        """ASSERTIONタイプを正しく検出"""
        log = "AssertionError: expected 5 but got 3"
        error_type = parser._detect_error_type(log)
        assert error_type == "ASSERTION"

    def test_detect_import_error(self, parser: LogParser) -> None:
        """IMPORTタイプを正しく検出"""
        log = "ModuleNotFoundError: No module named 'foo'"
        error_type = parser._detect_error_type(log)
        assert error_type == "IMPORT"

    def test_success_pattern_prevents_false_positive(self, parser: LogParser) -> None:
        """成功パターンがある場合、誤検知を防ぐ"""
        log = """
        [CI/test] ✅ Success - Main Run tests
        [CI/test] ✅ Success - Complete job
        Error: Job 'test' failed
        """
        error_type = parser._detect_error_type(log)
        # UNKNOWNエラーのみで、成功マークがあり、実際のexit codeがない場合
        assert error_type is None

    def test_real_failure_detected_despite_success_marks(self, parser: LogParser) -> None:
        """成功マークがあっても実際のエラーは検出"""
        log = """
        [CI/test] ✅ Success - Set up job
        [CI/test] ❌ Failure - Main Run tests
        [CI/test] ✅ Success - Complete job
        Error: Job 'test' failed
        """
        error_type = parser._detect_error_type(log)
        assert error_type == "BUILD_FAILURE"

    def test_extract_workflow_name(self, parser: LogParser) -> None:
        """ワークフロー名を正しく抽出"""
        lines = [
            "INFO[0000] Using docker host",
            "[Test Workflow/job-name] Starting",
        ]
        workflow = parser._extract_workflow_name(lines)
        assert workflow == "Test Workflow"

    def test_extract_workflow_name_unknown(self, parser: LogParser) -> None:
        """ワークフロー名が見つからない場合unknownを返す"""
        lines = ["Some random log line"]
        workflow = parser._extract_workflow_name(lines)
        assert workflow == "unknown"

    def test_extract_error_message_with_failure(self, parser: LogParser) -> None:
        """Failureメッセージを抽出"""
        lines = [
            "[CI/test] ❌ Failure - Main Run tests",
            "exitcode '1': failure",
        ]
        message = parser._extract_error_message(lines)
        assert "Failure - Main Run tests" in message

    def test_extract_location_python_traceback(self, parser: LogParser) -> None:
        """Pythonのトレースバックからファイルパスと行番号を抽出"""
        lines = [
            "Traceback (most recent call last):",
            '  File "tests/test_example.py", line 42, in test_function',
            "    assert result == expected",
        ]
        file_path, line_number = parser._extract_location(lines)
        assert file_path == "tests/test_example.py"
        assert line_number == 42

    def test_extract_location_not_found(self, parser: LogParser) -> None:
        """ファイルパス・行番号が見つからない場合None"""
        lines = ["Some random log without file info"]
        file_path, line_number = parser._extract_location(lines)
        assert file_path is None
        assert line_number is None

    def test_extract_stack_trace(self, parser: LogParser) -> None:
        """スタックトレースを正しく抽出"""
        lines = [
            "Some log line",
            "Traceback (most recent call last):",
            '  File "test.py", line 1',
            "    raise ValueError()",
            "ValueError: test error",
            "Next log line",
        ]
        stack_trace = parser._extract_stack_trace(lines)
        assert stack_trace is not None
        assert "Traceback" in stack_trace
        assert "ValueError" in stack_trace

    def test_extract_stack_trace_none_if_not_found(self, parser: LogParser) -> None:
        """Tracebackがない場合はNone"""
        lines = ["No traceback here", "Just normal logs"]
        stack_trace = parser._extract_stack_trace(lines)
        assert stack_trace is None

    def test_parse_returns_none_if_no_error(self, parser: LogParser) -> None:
        """エラーがない場合はNoneを返す"""
        log = """
        [CI/test] ✅ Success - Main Run tests
        [CI/test] ✅ Success - Complete job
        """
        result = parser.parse(log, workflow="ci.yml")
        assert result is None

    def test_parse_returns_failure_info(self, parser: LogParser) -> None:
        """エラーがある場合はFailureInfoを返す"""
        log = """
        [Test/job] ❌ Failure - Main Run tests
        exitcode '1': failure
        """
        result = parser.parse(log, workflow="test.yml")
        assert isinstance(result, FailureInfo)
        assert result.workflow == "test.yml"
        assert result.error_type == "BUILD_FAILURE"

    def test_error_patterns_are_valid_regex(self, parser: LogParser) -> None:
        """ERROR_PATTERNSがすべて有効な正規表現"""
        for pattern, _ in parser.ERROR_PATTERNS:
            try:
                re.compile(pattern)
            except re.error as e:
                pytest.fail(f"Invalid regex pattern: {pattern} - {e}")

    def test_success_patterns_are_valid_regex(self, parser: LogParser) -> None:
        """SUCCESS_PATTERNSがすべて有効な正規表現"""
        for pattern in parser.SUCCESS_PATTERNS:
            try:
                re.compile(pattern)
            except re.error as e:
                pytest.fail(f"Invalid regex pattern: {pattern} - {e}")
