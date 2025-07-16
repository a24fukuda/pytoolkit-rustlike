# pytoolkit-rustlike

型安全性と関数型プログラミング機能を備えた、Rust 風の Result 型と Option 型の Python 実装

## 概要

このライブラリは、関数型プログラミングにおけるエラーハンドリングと null 安全性のための 2 つの主要な型を提供します：

- **Result 型**: 成功した値（`Ok[T]`）またはエラー（`Err[T, E]`）のいずれかを表現し、予期されるエラー条件に対して例外を避けることで、エラーハンドリングをより明示的で型安全にします。
- **Option 型**: 値を含む（`Some[T]`）か値の不在（`Nothing`）を表現し、null 値の処理をより明示的で型安全にします。

## 機能

### Result 型

- **型安全なエラーハンドリング**: 成功とエラーケースの明示的な処理
- **関数型プログラミングサポート**: 計算をチェーンするための map と bind 操作
- **抽象基底クラス**: Result の直接インスタンス化を防止

### Option 型

- **型安全な null 処理**: 値の存在・不在を明示的に処理
- **関数型プログラミングサポート**: map、and_then、match 操作による計算のチェーン
- **不変設計**: 安全性のため frozen データクラスを使用

### 共通機能

- **Rust 風 API**: Rust 開発者にとって馴染みのあるインターフェース
- **統合された設計**: Result 型と Option 型を同一モジュールで提供

## 必要環境

- Python 3.13+
- uv（依存関係管理用）

## インストール

```bash
uv sync
```

## 使用方法

### Result 型の基本的な使用方法

```python
from pytoolkit_rustlike import Ok, Err, Result

# 成功の結果を作成
success: Result[int, Exception] = Ok(42)
print(success.is_ok())        # True
print(success.unwrap())       # 42
print(success.unwrap_or(0))   # 42

# エラーの結果を作成
error: Result[int, ValueError] = Err(ValueError("何かが間違っています"))
print(error.is_ok())          # False
print(error.unwrap_or(0))     # 0
# error.unwrap()              # UnwrapError が発生
```

### Option 型の基本的な使用方法

```python
from pytoolkit_rustlike import Some, Nothing, Option

# 値を持つオプションを作成
some_value: Option[int] = Some(42)
print(some_value.is_some())        # True
print(some_value.unwrap())         # 42
print(some_value.unwrap_or(0))     # 42

# 空のオプションを作成
nothing: Option[int] = Nothing()
print(nothing.is_some())           # False
print(nothing.is_nothing())        # True
print(nothing.unwrap_or(0))        # 0
# nothing.unwrap()                 # UnwrapError が発生
```

### Result 型の関数型操作

```python
# map操作 - Okの場合に値を変換
result = Ok(10).map(lambda x: x * 2)
print(result.unwrap())  # 20

# ErrでのmapはそのままErrを返す
error_result = Err[int, ValueError](ValueError("エラー")).map(lambda x: x * 2)
print(error_result.is_err())  # True

# and_thenで操作をチェーン
def divide_by_two(x: int) -> Result[float, Exception]:
    return Ok(x / 2.0)

def to_string(x: float) -> Result[str, Exception]:
    return Ok(str(x))

result = Ok(10).and_then(divide_by_two).and_then(to_string)
print(result.unwrap())  # "5.0"
```

### Option 型の関数型操作

```python
# map操作 - Someの場合に値を変換
option = Some(10).map(lambda x: x * 2)
print(option.unwrap())  # 20

# NothingでのmapはNothingを返す
nothing_result = Nothing[int]().map(lambda x: x * 2)
print(nothing_result.is_nothing())  # True

# and_thenで操作をチェーン
def divide_by_two(x: int) -> Option[float]:
    return Some(x / 2.0)

def to_string(x: float) -> Option[str]:
    return Some(str(x))

result = Some(10).and_then(divide_by_two).and_then(to_string)
print(result.unwrap())  # "5.0"
```

### エラーハンドリングパターン

```python
def safe_divide(a: int, b: int) -> Result[float, ValueError]:
    if b == 0:
        return Err(ValueError("ゼロ除算"))
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
    .and_then(lambda x: Ok(x - 10) if x > 10 else Err(ValueError("小さすぎます")))  # 40
    .map(lambda x: x * 2))        # 80

print(result.unwrap())  # 80
```

## API リファレンス

### Result[T, E]（抽象基底クラス）

成功値(T)またはエラー値(E)のいずれかを表現する型です。

#### 基本メソッド

- `is_ok() -> bool`: これが Ok 値の場合に True を返す
- `is_err() -> bool`: これが Err 値の場合に True を返す
- `unwrap() -> T`: Ok 値を返すか、UnwrapError 例外を発生させる
- `unwrap_or(default: T) -> T`: Ok 値またはデフォルト値を返す
- `expect(msg: str) -> T`: Ok 値を返すか、カスタムメッセージで RuntimeError を発生させる
- `unwrap_err() -> E`: Err 値を返すか、RuntimeError を発生させる
- `expect_err(msg: str) -> E`: Err 値を返すか、カスタムメッセージで RuntimeError を発生させる

#### 変換メソッド

- `map(f: Callable[[T], U]) -> Result[U, E]`: Ok の場合に値を変換
- `map_err(f: Callable[[E], F]) -> Result[T, F]`: Err の場合にエラーを変換
- `map_or(default: U, f: Callable[[T], U]) -> U`: Ok の場合は変換、Err の場合はデフォルト値
- `map_or_else(err_f: Callable[[E], U], ok_f: Callable[[T], U]) -> U`: Ok/Err に応じて異なる関数を適用

#### チェーンメソッド

- `and_then(f: Callable[[T], Result[U, E]]) -> Result[U, E]`: Ok の場合に Result を返す関数をチェーン
- `or_else(f: Callable[[E], Result[T, F]]) -> Result[T, F]`: Err の場合に Result を返す関数をチェーン
- `unwrap_or_else(f: Callable[[E], T]) -> T`: Err の場合に関数を実行してデフォルト値を取得

#### 論理演算メソッド

- `and_(res: Result[U, E]) -> Result[U, E]`: 両方が Ok の場合に第二引数の Result を返す
- `or_(res: Result[T, F]) -> Result[T, F]`: 第一引数が Ok なら第一引数、Err なら第二引数を返す

#### デバッグ・観察メソッド

- `inspect(f: Callable[[T], None]) -> Result[T, E]`: Ok の場合に副作用関数を実行
- `inspect_err(f: Callable[[E], None]) -> Result[T, E]`: Err の場合に副作用関数を実行

#### イテレータ・パターンマッチング

- `__iter__() -> Iterator[T]`: Ok の場合は値を 1 つ含むイテレータ、Err の場合は空のイテレータ
- `match(ok: Callable[[T], U], err: Callable[[E], U]) -> U`: パターンマッチング

#### Ok[T, E]

型 T の値を含む成功した結果を表現します。

#### Err[T, E]

型 E のエラー値を含むエラー結果を表現します。

### Option[T]（抽象基底クラス）

値の存在または不在を型安全に表現する型です。

#### 基本メソッド

- `is_some() -> bool`: 値を含む場合に True を返す
- `is_nothing() -> bool`: 値を含まない場合に True を返す
- `unwrap() -> T`: Some 値を返すか、UnwrapError 例外を発生させる
- `unwrap_or(default: T) -> T`: Some 値またはデフォルト値を返す
- `expect(msg: str) -> T`: Some 値を返すか、カスタムメッセージで UnwrapError 例外を発生させる
- `unwrap_or_else(f: Callable[[], T]) -> T`: Nothing の場合に関数を実行してデフォルト値を取得

#### 変換メソッド

- `map(f: Callable[[T], U]) -> Option[U]`: Some の場合に値を変換
- `map_or(default: U, f: Callable[[T], U]) -> U`: Some の場合は変換、Nothing の場合はデフォルト値
- `map_or_else(default_f: Callable[[], U], f: Callable[[T], U]) -> U`: Some/Nothing に応じて異なる関数を適用

#### チェーンメソッド

- `and_then(f: Callable[[T], Option[U]]) -> Option[U]`: Some で Option を返す関数をチェーン
- `or_else(f: Callable[[], Option[T]]) -> Option[T]`: Nothing の場合に Option を返す関数をチェーン

#### フィルタリング

- `filter(predicate: Callable[[T], bool]) -> Option[T]`: 条件を満たす Some のみを通す

#### 論理演算メソッド

- `and_(optb: Option[U]) -> Option[U]`: 両方が Some の場合に第二引数の Option を返す
- `or_(optb: Option[T]) -> Option[T]`: 第一引数が Some なら第一引数、Nothing なら第二引数を返す

#### デバッグ・観察メソッド

- `inspect(f: Callable[[T], None]) -> Option[T]`: Some の場合に副作用関数を実行

#### イテレータ・パターンマッチング

- `__iter__() -> Iterator[T]`: Some の場合は値を 1 つ含むイテレータ、Nothing の場合は空のイテレータ
- `match(some: Callable[[T], U], nothing: Callable[[], U]) -> U`: パターンマッチング

#### Some[T]

型 T の値を含む Option を表現します。

#### Nothing[T]

値を含まない Option を表現します。

### UnwrapError

`unwrap()`や`expect()`メソッドで発生する例外です。元のエラー値へのアクセスは提供せず、シンプルな例外種別として機能します。元のエラー値が必要な場合は`unwrap_err()`や`match()`メソッドを使用してください。

```python
from pytoolkit_rustlike import Err, UnwrapError

# UnwrapErrorをキャッチ
try:
    Err(ValueError("original error")).unwrap()
except UnwrapError as e:
    print(f"UnwrapErrorが発生: {e}")
    # 元のエラー値にアクセスするには unwrap_err() を使用
    err_result = Err(ValueError("original error"))
    original_error = err_result.unwrap_err()
    print(f"元のエラー: {original_error}")
```

### Option型のコンストラクタ関数

#### as_option(value: T | None) -> Option[T]

値をOption型に変換します。Noneの場合はNothing、そうでない場合はSomeを返します。

```python
from pytoolkit_rustlike import as_option

# None値をOption型に変換
opt1 = as_option(None)      # Nothing[T]()
print(opt1.is_nothing())    # True

# 通常の値をOption型に変換
opt2 = as_option(42)        # Some(42)
print(opt2.unwrap())        # 42
```

#### some(value: T | None) -> Option[T]

値をSome型のOptionに変換します。None値が渡された場合はValueErrorを発生させます。

```python
from pytoolkit_rustlike import some

# 有効な値でSomeを作成
opt = some(42)              # Some(42)
print(opt.unwrap())         # 42

# None値でSomeを作成しようとするとエラー
try:
    some(None)              # ValueError が発生
except ValueError as e:
    print(f"エラー: {e}")
```

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

このプロジェクトは MIT ライセンスの下でライセンスされています。
