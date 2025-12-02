"""parser.pyのduration抽出テスト"""
# pyright: reportPrivateUsage=false

from act_lens.parser import LogParser


class TestDurationExtraction:
    """実行時間抽出のテスト"""

    def test_extract_duration_milliseconds(self):
        """ミリ秒形式の実行時間を抽出"""
        log: str = """
        [Test/job]   ❌  Failure - Main Test [106.819485ms]
        """
        parser = LogParser()
        duration = parser._extract_duration(log.split("\n"))
        assert duration is not None
        assert abs(duration - 0.106819485) < 0.001

    def test_extract_duration_seconds(self):
        """秒形式の実行時間を抽出"""
        log: str = """
        [CI/test]   ✅  Success - Main Install [9.988223336s]
        """
        parser = LogParser()
        duration = parser._extract_duration(log.split("\n"))
        assert duration is not None
        assert abs(duration - 9.988223336) < 0.001

    def test_extract_duration_minutes(self):
        """分秒形式の実行時間を抽出"""
        log: str = """
        [Build/compile]   ✅  Success - Main Build [2m 30s]
        """
        parser = LogParser()
        duration = parser._extract_duration(log.split("\n"))
        assert duration == 150.0  # 2分30秒 = 150秒

    def test_extract_duration_no_match(self):
        """実行時間が見つからない場合はNoneを返す"""
        log: str = """
        [Test/job]   ❌  Failure - Main Test
        """
        parser = LogParser()
        duration = parser._extract_duration(log.split("\n"))
        assert duration is None

    def test_extract_duration_uses_last_match(self):
        """複数ある場合は最後のものを使用"""
        log: str = """
        [Test/step1]   ✅  Success [1.5s]
        [Test/step2]   ✅  Success [2.5s]
        [Test/step3]   ❌  Failure [3.5s]
        """
        parser = LogParser()
        duration = parser._extract_duration(log.split("\n"))
        assert duration == 3.5
