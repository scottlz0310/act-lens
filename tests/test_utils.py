"""Utilsのテスト"""

from pathlib import Path
from unittest.mock import MagicMock, patch

from act_lens.utils import copy_to_clipboard, save_report


class TestUtils:
    """ユーティリティ関数のテスト"""

    @patch("act_lens.utils.pyperclip")
    def test_copy_to_clipboard_success(self, mock_pyperclip: MagicMock) -> None:
        """クリップボードコピーが成功"""
        text = "Test content"
        result = copy_to_clipboard(text)
        mock_pyperclip.copy.assert_called_once_with(text)
        assert result is True

    @patch("act_lens.utils.pyperclip")
    def test_copy_to_clipboard_failure(self, mock_pyperclip: MagicMock) -> None:
        """クリップボードコピーが失敗した場合False"""
        mock_pyperclip.copy.side_effect = Exception("Clipboard error")
        result = copy_to_clipboard("test")
        assert result is False

    def test_save_report_creates_directory(self, tmp_path: Path) -> None:
        """レポート保存時にディレクトリが作成される"""
        output_dir = tmp_path / ".act-lens"
        content = "# Test Report"

        filepath = save_report(content, output_dir=output_dir)

        assert output_dir.exists()
        assert filepath.exists()
        assert filepath.parent == output_dir

    def test_save_report_content(self, tmp_path: Path) -> None:
        """レポート内容が正しく保存される"""
        output_dir = tmp_path / ".act-lens"
        content = "# Test Report\n\nSome content"

        filepath = save_report(content, output_dir=output_dir)

        saved_content = filepath.read_text()
        assert saved_content == content

    def test_save_report_filename_format(self, tmp_path: Path) -> None:
        """ファイル名が正しいフォーマット"""
        output_dir = tmp_path / ".act-lens"

        filepath = save_report("test", output_dir=output_dir)

        # failure_YYYYMMDD_HHMMSS.md形式
        assert filepath.name.startswith("failure_")
        assert filepath.name.endswith(".md")
        assert len(filepath.stem) == len("failure_20250128_123456")

    def test_save_report_multiple_files(self, tmp_path: Path) -> None:
        """複数のレポートが保存できる"""
        import time

        output_dir = tmp_path / ".act-lens"

        filepath1 = save_report("report1", output_dir=output_dir)
        time.sleep(1.1)  # ファイル名のタイムスタンプが異なるよう待機
        filepath2 = save_report("report2", output_dir=output_dir)

        assert filepath1 != filepath2
        assert filepath1.exists()
        assert filepath2.exists()
        assert len(list(output_dir.glob("*.md"))) == 2
