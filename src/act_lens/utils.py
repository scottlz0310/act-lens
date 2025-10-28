"""ユーティリティ関数"""

from pathlib import Path

import pyperclip
from rich.console import Console

console = Console()


def copy_to_clipboard(text: str) -> bool:
    """
    クリップボードにテキストをコピー

    Args:
        text: コピーするテキスト

    Returns:
        成功した場合True
    """
    try:
        pyperclip.copy(text)
        return True
    except Exception as e:
        console.print(f"[red]クリップボードコピー失敗:[/red] {e}")
        return False


def save_report(content: str, output_dir: Path = Path(".act-lens")) -> Path:
    """
    レポートをファイルに保存

    Args:
        content: 保存する内容
        output_dir: 保存先ディレクトリ

    Returns:
        保存したファイルのパス
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    from datetime import datetime

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"failure_{timestamp}.md"

    output_file.write_text(content, encoding="utf-8")
    return output_file
