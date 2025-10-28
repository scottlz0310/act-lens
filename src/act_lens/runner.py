"""act実行とログキャプチャ"""

import subprocess
from pathlib import Path

from rich.console import Console

console = Console()


class ActRunner:
    """actコマンドの実行とログキャプチャ"""

    def __init__(self, workflow_dir: Path = Path(".github/workflows")) -> None:
        self.workflow_dir = workflow_dir

    def list_workflows(self) -> list[str]:
        """利用可能なワークフローファイルを一覧取得"""
        if not self.workflow_dir.exists():
            return []

        workflows = list(self.workflow_dir.glob("*.yml")) + list(self.workflow_dir.glob("*.yaml"))
        return [w.name for w in workflows]

    def run_act(self, workflow: str | None = None, job: str | None = None) -> tuple[str, int]:
        """
        actコマンドを実行してログをキャプチャ

        Args:
            workflow: ワークフローファイル名（例: ci.yml）
            job: 実行するジョブ名（省略時は全ジョブ）

        Returns:
            (出力ログ, 終了コード)
        """
        cmd = ["act"]

        if workflow:
            cmd.extend(["-W", str(self.workflow_dir / workflow)])

        if job:
            cmd.extend(["-j", job])

        console.print(f"[cyan]実行中:[/cyan] {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5分タイムアウト
            )
            return result.stdout + result.stderr, result.returncode

        except subprocess.TimeoutExpired:
            console.print("[red]エラー:[/red] タイムアウト（5分）")
            return "", 124  # タイムアウト終了コード

        except FileNotFoundError:
            console.print(
                "[red]エラー:[/red] actコマンドが見つかりません。"
                "インストールしてください: https://github.com/nektos/act"
            )
            return "", 127  # コマンド not found
