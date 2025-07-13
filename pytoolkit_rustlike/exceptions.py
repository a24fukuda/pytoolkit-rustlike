"""
PyToolkit Rustlike - 例外クラス定義

このモジュールはResultとOptionで使用する例外クラスを定義しています。
"""


class UnwrapError(Exception):
    """Resultのunwrapメソッドで発生する例外"""
    pass
