"""データモデル定義"""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class FailureInfo(BaseModel):
    """ワークフロー失敗情報"""

    workflow: str = Field(..., description="ワークフローファイル名（例: ci.yml）")
    job: str = Field(..., description="ジョブ名（例: test）")
    step: str = Field(..., description="ステップ名（例: Run pytest）")
    timestamp: datetime = Field(..., description="失敗発生時刻")
    duration: float = Field(..., ge=0, description="実行時間（秒）")
    error_type: str = Field(..., description="エラータイプ（例: ASSERTION, TIMEOUT）")
    message: str = Field(..., description="エラーメッセージ")
    file_path: str | None = Field(None, description="エラー発生ファイルパス")
    line_number: int | None = Field(None, ge=1, description="エラー発生行番号")
    context_lines: list[str] = Field(default_factory=list, description="コード前後の行")
    stack_trace: str | None = Field(None, description="スタックトレース全体")

    @field_validator("error_type")
    @classmethod
    def validate_error_type(cls, v: str) -> str:
        """エラータイプを大文字に正規化"""
        return v.upper()

    def format_duration(self) -> str:
        """実行時間を人間可読形式にフォーマット"""
        if self.duration < 60:
            return f"{self.duration:.1f}秒"
        minutes = int(self.duration // 60)
        seconds = self.duration % 60
        return f"{minutes}分{seconds:.1f}秒"

    def get_location(self) -> str | None:
        """エラー発生箇所を文字列で取得"""
        if self.file_path and self.line_number:
            return f"{self.file_path}:{self.line_number}"
        return self.file_path
