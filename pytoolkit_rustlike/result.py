"""
PyToolkit Result - Rust風のResult型実装

## 設計方針

このモジュールはRustのResult<T, E>型をPythonで再現したものです。
Rustの完全な仕様ではなく、実用性と型安全性のバランスを重視した設計を採用しています。

### 主要な設計判断

1. **and_then メソッドの型シグネチャ**
   - Rust: `fn and_then<U, F>(self, op: FnOnce(T) -> Result<U, F>) -> Result<U, F> where F: From<E>`
   - Python: `def and_then(self, f: Callable[[T], Result[U, E]]) -> Result[U, E]`

   理由:
   - Rustの90%以上の使用ケースはエラー型を保持する
   - Python版では型変換の複雑さを避け、実用性を重視
   - エラー型変換が必要な場合は明示的にmap_errを使用

2. **UnwrapError の採用**
   - Err.unwrap()は一律でUnwrapErrorを発生
   - _errorがException以外でも安全に動作
   - 元のエラー値はerror_valueプロパティで取得可能

3. **抽象クラス設計**
   - Resultクラスは完全に抽象的
   - OkとErrで全メソッドを一貫して実装
   - 型安全性と明確性を重視

### Rustとの相違点

- 型変換制約(`where F: From<E>`)の簡略化
- パフォーマンスよりも型安全性を優先
- Python的な例外処理との統合

詳細な実装背景は CLAUDE.md を参照してください。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, Generic, Iterator, TypeVar

from .exceptions import UnwrapError

T = TypeVar("T")
U = TypeVar("U")
E = TypeVar("E", default=Exception)
F = TypeVar("F", default=Exception)


class Result(ABC, Generic[T, E]):
    @abstractmethod
    def is_ok(self) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def is_err(self) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def unwrap(self) -> T:
        raise NotImplementedError()

    @abstractmethod
    def unwrap_or(self, default: T) -> T:
        raise NotImplementedError()

    @abstractmethod
    def map(self, f: Callable[[T], U]) -> Result[U, E]:
        raise NotImplementedError()

    @abstractmethod
    def and_then(self, f: Callable[[T], Result[U, E]]) -> Result[U, E]:
        """成功値に関数を適用し、新しいResultを返す。

        注意: Rustの完全な型シグネチャは以下の通りです:
        `fn and_then<U, F>(self, op: FnOnce(T) -> Result<U, F>) -> Result<U, F> where F: From<E>`

        この実装では実用性を重視し、エラー型Eを保持する簡略化した型シグネチャを採用しています。
        エラー型の変換が必要な場合は、明示的にmap_err()を使用してください。

        Args:
            f: 成功値を受け取り、新しいResultを返す関数

        Returns:
            成功時: f(value)の結果
            失敗時: 元のエラーを保持したErr
        """
        raise NotImplementedError()

    @abstractmethod
    def expect(self, msg: str) -> T:
        raise NotImplementedError()

    @abstractmethod
    def unwrap_err(self) -> E:
        raise NotImplementedError()

    @abstractmethod
    def map_err(self, f: Callable[[E], F]) -> Result[T, F]:
        raise NotImplementedError()

    @abstractmethod
    def or_else(self, f: Callable[[E], Result[T, F]]) -> Result[T, F]:
        raise NotImplementedError()

    @abstractmethod
    def unwrap_or_else(self, f: Callable[[E], T]) -> T:
        raise NotImplementedError()

    @abstractmethod
    def expect_err(self, msg: str) -> E:
        raise NotImplementedError()

    @abstractmethod
    def map_or(self, default: U, f: Callable[[T], U]) -> U:
        raise NotImplementedError()

    @abstractmethod
    def map_or_else(self, err_f: Callable[[E], U], ok_f: Callable[[T], U]) -> U:
        raise NotImplementedError()

    @abstractmethod
    def inspect(self, f: Callable[[T], None]) -> Result[T, E]:
        raise NotImplementedError()

    @abstractmethod
    def inspect_err(self, f: Callable[[E], None]) -> Result[T, E]:
        raise NotImplementedError()

    @abstractmethod
    def and_(self, res: Result[U, E]) -> Result[U, E]:
        raise NotImplementedError()

    @abstractmethod
    def or_(self, res: Result[T, F]) -> Result[T, F]:
        raise NotImplementedError()

    @abstractmethod
    def __iter__(self) -> Iterator[T]:
        raise NotImplementedError()

    @abstractmethod
    def match(self, ok: Callable[[T], U], err: Callable[[E], U]) -> U:
        raise NotImplementedError()


@dataclass(frozen=True)
class Ok(Result[T, E]):
    _value: T

    def is_ok(self) -> bool:
        return True

    def is_err(self) -> bool:
        return False

    def unwrap(self) -> T:
        return self._value

    def unwrap_or(self, default: T) -> T:
        return self._value

    def map(self, f: Callable[[T], U]) -> Result[U, E]:
        return Ok(f(self._value))

    def and_then(self, f: Callable[[T], Result[U, E]]) -> Result[U, E]:
        return f(self._value)

    def expect(self, msg: str) -> T:
        return self._value

    def unwrap_err(self) -> E:
        raise RuntimeError(f"Called unwrap_err on Ok value: {self._value}")

    def map_err(self, f: Callable[[E], F]) -> Result[T, F]:
        return Ok(self._value)

    def or_else(self, f: Callable[[E], Result[T, F]]) -> Result[T, F]:
        return Ok(self._value)

    def unwrap_or_else(self, f: Callable[[E], T]) -> T:
        return self._value

    def expect_err(self, msg: str) -> E:
        raise RuntimeError(f"{msg}: called expect_err on Ok value: {self._value}")

    def map_or(self, default: U, f: Callable[[T], U]) -> U:
        return f(self._value)

    def map_or_else(self, err_f: Callable[[E], U], ok_f: Callable[[T], U]) -> U:
        return ok_f(self._value)

    def inspect(self, f: Callable[[T], None]) -> Result[T, E]:
        f(self._value)
        return self

    def inspect_err(self, f: Callable[[E], None]) -> Result[T, E]:
        return self

    def and_(self, res: Result[U, E]) -> Result[U, E]:
        return res

    def or_(self, res: Result[T, F]) -> Result[T, F]:
        return Ok(self._value)

    def __iter__(self) -> Iterator[T]:
        yield self._value

    def match(self, ok: Callable[[T], U], err: Callable[[E], U]) -> U:
        return ok(self._value)


@dataclass(frozen=True)
class Err(Result[T, E]):
    _error: E

    def is_ok(self) -> bool:
        return False

    def is_err(self) -> bool:
        return True

    def unwrap(self) -> T:
        raise UnwrapError(self._error)

    def unwrap_or(self, default: T) -> T:
        return default

    def map(self, f: Callable[[T], U]) -> Result[U, E]:
        return Err[U, E](self._error)

    def and_then(self, f: Callable[[T], Result[U, E]]) -> Result[U, E]:
        return Err(self._error)

    def expect(self, msg: str) -> T:
        raise RuntimeError(f"{msg}: {self._error}")

    def unwrap_err(self) -> E:
        return self._error

    def map_err(self, f: Callable[[E], F]) -> Result[T, F]:
        return Err(f(self._error))

    def or_else(self, f: Callable[[E], Result[T, F]]) -> Result[T, F]:
        return f(self._error)

    def unwrap_or_else(self, f: Callable[[E], T]) -> T:
        return f(self._error)

    def expect_err(self, msg: str) -> E:
        return self._error

    def map_or(self, default: U, f: Callable[[T], U]) -> U:
        return default

    def map_or_else(self, err_f: Callable[[E], U], ok_f: Callable[[T], U]) -> U:
        return err_f(self._error)

    def inspect(self, f: Callable[[T], None]) -> Result[T, E]:
        return self

    def inspect_err(self, f: Callable[[E], None]) -> Result[T, E]:
        f(self._error)
        return self

    def and_(self, res: Result[U, E]) -> Result[U, E]:
        return Err(self._error)

    def or_(self, res: Result[T, F]) -> Result[T, F]:
        return res

    def __iter__(self) -> Iterator[T]:
        return iter([])

    def match(self, ok: Callable[[T], U], err: Callable[[E], U]) -> U:
        return err(self._error)
