"""
PyToolkit Rustlike - 例外クラス定義

このモジュールはResultとOptionで使用する例外クラスを定義しています。
"""


class UnwrapError(Exception):
    """Resultのunwrapメソッドで発生する例外"""

    def __init__(self, error_value: object) -> None:
        self.error_value = error_value
        super().__init__(f"Called unwrap on Err value: {error_value}")