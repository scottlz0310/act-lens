"""CLIエントリーポイント"""

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

from act_lens.formatter import MarkdownFormatter
from act_lens.parser import LogParser
from act_lens.runner import ActRunner
from act_lens.utils import copy_to_clipboard, save_report

app = typer.Typer(help="actの出力をレンズで覗いて整形するCLIツール")
console = Console()


@app.command()
def main(
    workflow: str = typer.Option(
        None, "--workflow", "-w", help="ワークフローファイル名（例: ci.yml）"
    ),
    job: str = typer.Option(None, "--job", "-j", help="実行するジョブ名"),
    preview: bool = typer.Option(False, "--preview", "-p", help="プレビュー表示"),
    no_clipboard: bool = typer.Option(
        False, "--no-clipboard", help="クリップボードにコピーしない"
    ),
    output: Path = typer.Option(None, "--output", "-o", help="出力ファイルパス"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="詳細ログ表示"),
) -> None:
    """act実行してエラーログを整形"""
    console.print(Panel.fit("🔍 [bold cyan]Act-Lens[/bold cyan]", border_style="cyan"))

    # act実行
    runner = ActRunner()
    log, exit_code = runner.run_act(workflow, job)

    if exit_code == 0:
        console.print("[green]✓[/green] 成功 - エラーなし")
        return

    if verbose:
        console.print("\n[dim]--- ログ ---[/dim]")
        console.print(log)
        console.print("[dim]--- ログ終了 ---[/dim]\n")

    # ログ解析
    parser = LogParser()
    failure = parser.parse(log, workflow)

    if not failure:
        console.print("[yellow]警告:[/yellow] エラー情報を抽出できませんでした")
        return

    # Markdown生成
    formatter = MarkdownFormatter()
    report = formatter.format(failure)

    # プレビュー表示
    if preview:
        console.print("\n[dim]--- レポート ---[/dim]")
        console.print(report)
        console.print("[dim]--- レポート終了 ---[/dim]\n")

    # ファイル保存
    if output:
        output.write_text(report, encoding="utf-8")
        console.print(f"[green]✓[/green] 保存: [bold]{output}[/bold]")
    else:
        saved_path = save_report(report)
        console.print(f"[green]✓[/green] 保存: [bold]{saved_path}[/bold]")

    # クリップボードコピー
    if not no_clipboard:
        if copy_to_clipboard(report):
            console.print("[green]✓[/green] クリップボードにコピーしました")
        else:
            console.print("[yellow]警告:[/yellow] クリップボードコピーに失敗")

    console.print("\n[cyan]AIチャットに貼り付けて修正方法を聞いてください！[/cyan]")


if __name__ == "__main__":
    app()
