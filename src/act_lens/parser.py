"""ログ解析とエラー抽出"""

import re
from datetime import datetime

from act_lens.models import FailureInfo


class LogParser:
    """actのログからエラー情報を抽出"""

    # エラーパターン（優先度順）
    ERROR_PATTERNS = [
        (r"AssertionError", "ASSERTION"),
        (r"TimeoutError|timed out", "TIMEOUT"),
        (r"SyntaxError", "SYNTAX"),
        (r"ImportError|ModuleNotFoundError", "IMPORT"),
        (r"AttributeError", "ATTRIBUTE"),
        (r"TypeError", "TYPE"),
        (r"ValueError", "VALUE"),
        (r"KeyError", "KEY"),
        (r"IndexError", "INDEX"),
        (r"FileNotFoundError", "FILE_NOT_FOUND"),
        (r"PermissionError", "PERMISSION"),
        (
            r"❌\s*(Failure|failed)|"
            r"Error: Process completed with exit code [1-9]",
            "BUILD_FAILURE",
        ),
        (r"Error:", "UNKNOWN"),
    ]

    # 成功パターン（これらがあればエラーなしと判定）
    SUCCESS_PATTERNS = [
        r"✅.*Success",
        r"All checks passed",
        r"Success: no issues found",
    ]

    def parse(self, log: str, workflow: str | None = None) -> FailureInfo | None:
        """
        ログからFailureInfo抽出

        Args:
            log: actの出力ログ
            workflow: ワークフローファイル名（省略時はログから抽出）

        Returns:
            FailureInfo（エラーが見つからない場合はNone）
        """
        lines = log.split("\n")

        # エラータイプ判定
        error_type = self._detect_error_type(log)
        if not error_type:
            return None

        # ワークフロー名抽出（指定されていない場合）
        if not workflow:
            workflow = self._extract_workflow_name(lines)

        # エラーメッセージ抽出
        message = self._extract_error_message(lines)

        # ファイルパスと行番号抽出
        file_path, line_number = self._extract_location(lines)

        # スタックトレース抽出
        stack_trace = self._extract_stack_trace(lines)

        # コンテキスト行抽出
        context_lines = self._extract_context(lines, file_path, line_number)

        # ジョブ・ステップ情報抽出
        job, step = self._extract_job_step(lines)

        return FailureInfo(
            workflow=workflow,
            job=job,
            step=step,
            timestamp=datetime.now(),
            duration=0.0,  # TODO: ログから実行時間を抽出
            error_type=error_type,
            message=message,
            file_path=file_path,
            line_number=line_number,
            context_lines=context_lines,
            stack_trace=stack_trace,
        )

    def _extract_workflow_name(self, lines: list[str]) -> str:
        """ワークフロー名をログから抽出"""
        for line in lines:
            # actログ: "INFO[0000] Using docker host ..."
            # ワークフロー: "[Workflow name/job]"
            if match := re.search(r"\[([^/\]]+)/", line):
                return match.group(1)
        return "unknown"

    def _detect_error_type(self, log: str) -> str | None:
        """エラータイプを検出"""
        # まず実際のエラー（BUILD_FAILUREなど）をチェック
        for pattern, error_type in self.ERROR_PATTERNS:
            if re.search(pattern, log, re.IGNORECASE):
                # UNKNOWNタイプの場合のみ、成功パターンでフィルタリング
                if error_type == "UNKNOWN":
                    has_success = any(re.search(p, log) for p in self.SUCCESS_PATTERNS)
                    # 成功マークがあり、実際のexit codeエラーがない場合は無視
                    if has_success and not re.search(r"exit code [1-9]|❌.*failed", log):
                        continue
                return error_type
        return None

    def _extract_error_message(self, lines: list[str]) -> str:
        """エラーメッセージを抽出"""
        for line in reversed(lines):
            if "Error" in line or "FAILED" in line:
                return line.strip()
        return "エラーメッセージが見つかりません"

    def _extract_location(self, lines: list[str]) -> tuple[str | None, int | None]:
        """ファイルパスと行番号を抽出"""
        # Python形式: "  File "test.py", line 42"
        for line in lines:
            match = re.search(r'File "([^"]+)", line (\d+)', line)
            if match:
                return match.group(1), int(match.group(2))
        return None, None

    def _extract_stack_trace(self, lines: list[str]) -> str | None:
        """スタックトレースを抽出"""
        trace_lines: list[str] = []
        in_trace = False

        for line in lines:
            if "Traceback" in line:
                in_trace = True
            if in_trace:
                trace_lines.append(line)
                if line.strip() and not line.startswith(" "):
                    break

        return "\n".join(trace_lines) if trace_lines else None

    def _extract_context(
        self, lines: list[str], file_path: str | None, line_number: int | None
    ) -> list[str]:
        """エラー発生箇所のコンテキスト行を抽出"""
        # TODO: ファイルを読んで前後3行を取得
        return []

    def _extract_job_step(self, lines: list[str]) -> tuple[str, str]:
        """ジョブ名とステップ名を抽出"""
        job = "unknown"
        step = "unknown"

        for line in lines:
            if match := re.search(r"\[([^\]]+)\]\s+(.+)", line):
                job = match.group(1)
                step = match.group(2).strip()

        return job, step
