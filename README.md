# pytoolkit-result

型安全性と関数型プログラミング機能を備えた、Rust風のResult型のPython実装

## 概要

このライブラリは、成功した値（`Ok[T]`）またはエラー（`Err[T]`）のいずれかを表現する`Result[T]`型を提供します。予期されるエラー条件に対して例外を避けることで、エラーハンドリングをより明示的で型安全にすることを目的としています。

## 機能

- **型安全なエラーハンドリング**: 成功とエラーケースの明示的な処理
- **関数型プログラミングサポート**: 計算をチェーンするためのmapとbind操作
- **抽象基底クラス**: Resultの直接インスタンス化を防止
- **Rust風API**: Rust開発者にとって馴染みのあるインターフェース

## 必要環境

- Python 3.13+
- uv（依存関係管理用）

## インストール

```bash
uv sync
```

## 使用方法

### 基本的な使用方法

```python
from pytoolkit_result.result import Ok, Err, Result

# 成功の結果を作成
success: Result[int] = Ok(42)
print(success.is_ok())        # True
print(success.unwrap())       # 42
print(success.unwrap_or(0))   # 42

# エラーの結果を作成
error: Result[int] = Err(ValueError("何かが間違っています"))
print(error.is_ok())          # False
print(error.unwrap_or(0))     # 0
# error.unwrap()              # ValueError が発生
```

### 関数型操作

```python
# map操作 - Okの場合に値を変換
result = Ok(10).map(lambda x: x * 2)
print(result.unwrap())  # 20

# ErrでのmapはそのままErrを返す
error_result = Err[int](ValueError("エラー")).map(lambda x: x * 2)
print(error_result.is_error())  # True

# and_thenで操作をチェーン
def divide_by_two(x: int) -> Result[float]:
    return Ok(x / 2.0)

def to_string(x: float) -> Result[str]:
    return Ok(str(x))

result = Ok(10).and_then(divide_by_two).and_then(to_string)
print(result.unwrap())  # "5.0"
```

### エラーハンドリングパターン

```python
def safe_divide(a: int, b: int) -> Result[float]:
    if b == 0:
        return Err[float](ValueError("ゼロ除算"))
    return Ok(a / b)

# 結果を処理
result = safe_divide(10, 2)
if result.is_ok():
    print(f"結果: {result.unwrap()}")
else:
    print(f"エラー: {result.unwrap_or(0)}")

# または、デフォルト値にunwrap_orを使用
value = safe_divide(10, 0).unwrap_or(0.0)
print(value)  # 0.0
```

### メソッドチェーン

```python
# 複数の操作をチェーン
result = (Ok(100)
    .map(lambda x: x // 2)        # 50
    .and_then(lambda x: Ok(x - 10) if x > 10 else Err[int](ValueError("小さすぎます")))  # 40
    .map(lambda x: x * 2))        # 80

print(result.unwrap())  # 80
```

## APIリファレンス

### Result[T]（抽象基底クラス）

- `is_ok() -> bool`: これがOk値の場合にTrueを返す
- `is_error() -> bool`: これがErr値の場合にTrueを返す
- `unwrap() -> T`: 値を返すかエラーを発生させる
- `unwrap_or(default: T) -> T`: 値またはデフォルト値を返す
- `map(f: Callable[[T], U]) -> Result[U]`: Okの場合に値を変換
- `and_then(f: Callable[[T], Result[U]]) -> Result[U]`: Result返却操作をチェーン

### Ok[T]

型Tの値を含む成功した結果を表現します。

### Err[T]

例外を含むエラー結果を表現します。

## 開発

開発用の依存関係をインストール：

```bash
uv sync --group dev
```

テストの実行：

```bash
uv run pytest
```

型チェックの実行：

```bash
uv run pyright
```

リンティングの実行：

```bash
uv run ruff check
```

リンティング問題の修正：

```bash
uv run ruff check --fix
```

コードのフォーマット：

```bash
uv run ruff format
```

## ビルド

```bash
uv build
```

## ライセンス

このプロジェクトはMITライセンスの下でライセンスされています。