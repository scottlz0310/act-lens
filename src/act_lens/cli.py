"""CLIエントリーポイント"""

from pathlib import Path
from typing import Annotated

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
    workflow: Annotated[
        str | None, typer.Option("--workflow", "-w", help="ワークフローファイル名")
    ] = None,
    job: Annotated[str | None, typer.Option("--job", "-j", help="実行するジョブ名")] = None,
    preview: Annotated[bool, typer.Option("--preview", "-p", help="プレビュー表示")] = False,
    compact: Annotated[
        bool, typer.Option("--compact", help="簡潔モード（エラーサマリーのみ）")
    ] = False,
    no_clipboard: Annotated[
        bool, typer.Option("--no-clipboard", help="クリップボードにコピーしない")
    ] = False,
    output: Annotated[Path | None, typer.Option("--output", "-o", help="出力ファイルパス")] = None,
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="詳細ログ表示")] = False,
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
        console.print(log, markup=False)  # マークアップを無効化
        console.print("[dim]--- ログ終了 ---[/dim]\n")

    # ログ解析
    parser = LogParser()
    failure = parser.parse(log, workflow)

    if not failure:
        console.print("[yellow]警告:[/yellow] エラー情報を抽出できませんでした")
        return

    # Markdown生成
    formatter = MarkdownFormatter()
    report = formatter.format(failure, compact=compact)

    # プレビュー表示
    if preview:
        console.print("\n[dim]--- レポート ---[/dim]")
        console.print(report, markup=False)  # マークアップを無効化
        console.print("[dim]--- レポート終了 ---[/dim]\n")

    # ファイル保存
    if output:
        # パストラバーサルを防ぐため絶対パスに解決
        resolved_output = output.resolve()
        # 親ディレクトリが存在することを確認
        if not resolved_output.parent.exists():
            console.print(
                f"[red]エラー:[/red] 親ディレクトリが存在しません: {resolved_output.parent}"
            )
            return
        resolved_output.write_text(report, encoding="utf-8")
        console.print(f"[green]✓[/green] 保存: [bold]{resolved_output}[/bold]")
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
