"""runner.pyのテスト"""

from pathlib import Path
from unittest.mock import MagicMock, patch

from act_lens.runner import ActRunner


class TestActRunner:
    """ActRunnerクラスのテスト"""

    def test_init_default_workflow_dir(self):
        """デフォルトのワークフローディレクトリで初期化"""
        runner = ActRunner()
        assert runner.workflow_dir == Path(".github/workflows")

    def test_init_custom_workflow_dir(self):
        """カスタムワークフローディレクトリで初期化"""
        custom_dir = Path("/custom/path")
        runner = ActRunner(workflow_dir=custom_dir)
        assert runner.workflow_dir == custom_dir

    def test_list_workflows_no_dir(self, tmp_path):
        """ディレクトリが存在しない場合は空リストを返す"""
        runner = ActRunner(workflow_dir=tmp_path / "nonexistent")
        workflows = runner.list_workflows()
        assert workflows == []

    def test_list_workflows_empty_dir(self, tmp_path):
        """空ディレクトリの場合は空リストを返す"""
        workflow_dir = tmp_path / "workflows"
        workflow_dir.mkdir(parents=True)
        runner = ActRunner(workflow_dir=workflow_dir)
        workflows = runner.list_workflows()
        assert workflows == []

    def test_list_workflows_with_files(self, tmp_path):
        """ワークフローファイルがある場合はリストを返す"""
        workflow_dir = tmp_path / "workflows"
        workflow_dir.mkdir(parents=True)

        # ワークフローファイル作成
        (workflow_dir / "ci.yml").touch()
        (workflow_dir / "release.yaml").touch()
        (workflow_dir / "readme.md").touch()  # 無視される

        runner = ActRunner(workflow_dir=workflow_dir)
        workflows = runner.list_workflows()

        assert len(workflows) == 2
        assert "ci.yml" in workflows
        assert "release.yaml" in workflows
        assert "readme.md" not in workflows

    @patch("act_lens.runner.subprocess.run")
    def test_run_act_success(self, mock_run):
        """actコマンド実行成功"""
        mock_run.return_value = MagicMock(
            stdout="Success output",
            stderr="",
            returncode=0,
        )

        runner = ActRunner()
        output, returncode = runner.run_act()

        assert "Success output" in output
        assert returncode == 0
        mock_run.assert_called_once()

    @patch("act_lens.runner.subprocess.run")
    def test_run_act_with_workflow(self, mock_run):
        """ワークフロー指定でactコマンド実行"""
        mock_run.return_value = MagicMock(
            stdout="Output",
            stderr="",
            returncode=0,
        )

        runner = ActRunner()
        runner.run_act(workflow="ci.yml")

        # コマンド引数を確認
        call_args = mock_run.call_args[0][0]
        assert "act" in call_args
        assert "-W" in call_args
        assert str(Path(".github/workflows/ci.yml")) in str(call_args)

    @patch("act_lens.runner.subprocess.run")
    def test_run_act_with_job(self, mock_run):
        """ジョブ指定でactコマンド実行"""
        mock_run.return_value = MagicMock(
            stdout="Output",
            stderr="",
            returncode=0,
        )

        runner = ActRunner()
        runner.run_act(job="test")

        # コマンド引数を確認
        call_args = mock_run.call_args[0][0]
        assert "-j" in call_args
        assert "test" in call_args

    @patch("act_lens.runner.subprocess.run")
    def test_run_act_failure(self, mock_run):
        """actコマンド実行失敗"""
        mock_run.return_value = MagicMock(
            stdout="",
            stderr="Error: act failed",
            returncode=1,
        )

        runner = ActRunner()
        output, returncode = runner.run_act()

        assert "Error: act failed" in output
        assert returncode == 1
