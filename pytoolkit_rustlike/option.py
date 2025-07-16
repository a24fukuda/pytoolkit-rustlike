"""
PyToolkit Option - Rust風のOption型実装

## 設計方針

このモジュールはRustのOption<T>型をPythonで再現したものです。
Resultクラスと同様に、実用性と型安全性のバランスを重視した設計を採用しています。

### 主要な設計判断

1. **UnwrapError の統一採用**
   - Nothing.unwrap()は一律でUnwrapErrorを発生
   - Resultクラスとの一貫性を保持

2. **完全抽象基底クラス設計**
   - Optionクラスは完全に抽象的
   - SomeとNothingで全メソッドを一貫して実装

3. **Rust準拠のメソッド群**
   - expect(), unwrap_or_else(), map_or(), map_or_else()等を実装
   - inspect(), filter(), flatten()等の実用的メソッドを追加

詳細な実装背景は CLAUDE.md を参照してください。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, Generic, Iterator, TypeVar

from .exceptions import UnwrapError

T = TypeVar("T")
U = TypeVar("U")


class Option(ABC, Generic[T]):
    @abstractmethod
    def is_some(self) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def is_nothing(self) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def unwrap(self) -> T:
        raise NotImplementedError()

    @abstractmethod
    def expect(self, msg: str) -> T:
        raise NotImplementedError()

    @abstractmethod
    def unwrap_or(self, default: T) -> T:
        raise NotImplementedError()

    @abstractmethod
    def unwrap_or_else(self, f: Callable[[], T]) -> T:
        raise NotImplementedError()

    @abstractmethod
    def map(self, f: Callable[[T], U]) -> Option[U]:
        raise NotImplementedError()

    @abstractmethod
    def map_or(self, default: U, f: Callable[[T], U]) -> U:
        raise NotImplementedError()

    @abstractmethod
    def map_or_else(self, default_f: Callable[[], U], f: Callable[[T], U]) -> U:
        raise NotImplementedError()

    @abstractmethod
    def and_then(self, f: Callable[[T], Option[U]]) -> Option[U]:
        raise NotImplementedError()

    @abstractmethod
    def filter(self, predicate: Callable[[T], bool]) -> Option[T]:
        raise NotImplementedError()

    @abstractmethod
    def or_else(self, f: Callable[[], Option[T]]) -> Option[T]:
        raise NotImplementedError()

    @abstractmethod
    def and_(self, optb: Option[U]) -> Option[U]:
        raise NotImplementedError()

    @abstractmethod
    def or_(self, optb: Option[T]) -> Option[T]:
        raise NotImplementedError()

    @abstractmethod
    def inspect(self, f: Callable[[T], None]) -> Option[T]:
        raise NotImplementedError()

    @abstractmethod
    def __iter__(self) -> Iterator[T]:
        raise NotImplementedError()

    @abstractmethod
    def match(self, some: Callable[[T], U], nothing: Callable[[], U]) -> U:
        raise NotImplementedError()


@dataclass(frozen=True)
class Some(Option[T]):
    _value: T

    def is_some(self) -> bool:
        return True

    def is_nothing(self) -> bool:
        return False

    def unwrap(self) -> T:
        return self._value

    def expect(self, msg: str) -> T:
        return self._value

    def unwrap_or(self, default: T) -> T:
        return self._value

    def unwrap_or_else(self, f: Callable[[], T]) -> T:
        return self._value

    def map(self, f: Callable[[T], U]) -> Option[U]:
        return Some(f(self._value))

    def map_or(self, default: U, f: Callable[[T], U]) -> U:
        return f(self._value)

    def map_or_else(self, default_f: Callable[[], U], f: Callable[[T], U]) -> U:
        return f(self._value)

    def and_then(self, f: Callable[[T], Option[U]]) -> Option[U]:
        return f(self._value)

    def filter(self, predicate: Callable[[T], bool]) -> Option[T]:
        if predicate(self._value):
            return self
        else:
            return Nothing[T]()

    def or_else(self, f: Callable[[], Option[T]]) -> Option[T]:
        return self

    def and_(self, optb: Option[U]) -> Option[U]:
        return optb

    def or_(self, optb: Option[T]) -> Option[T]:
        return self

    def inspect(self, f: Callable[[T], None]) -> Option[T]:
        f(self._value)
        return self

    def __iter__(self) -> Iterator[T]:
        yield self._value

    def match(self, some: Callable[[T], U], nothing: Callable[[], U]) -> U:
        return some(self._value)


class Nothing(Option[T]):
    def is_some(self) -> bool:
        return False

    def is_nothing(self) -> bool:
        return True

    def unwrap(self) -> T:
        raise UnwrapError("Called unwrap on None")

    def expect(self, msg: str) -> T:
        raise UnwrapError(f"{msg}: called expect on None")

    def unwrap_or(self, default: T) -> T:
        return default

    def unwrap_or_else(self, f: Callable[[], T]) -> T:
        return f()

    def map(self, f: Callable[[T], U]) -> Option[U]:
        return Nothing[U]()

    def map_or(self, default: U, f: Callable[[T], U]) -> U:
        return default

    def map_or_else(self, default_f: Callable[[], U], f: Callable[[T], U]) -> U:
        return default_f()

    def and_then(self, f: Callable[[T], Option[U]]) -> Option[U]:
        return Nothing[U]()

    def filter(self, predicate: Callable[[T], bool]) -> Option[T]:
        return self

    def or_else(self, f: Callable[[], Option[T]]) -> Option[T]:
        return f()

    def and_(self, optb: Option[U]) -> Option[U]:
        return Nothing[U]()

    def or_(self, optb: Option[T]) -> Option[T]:
        return optb

    def inspect(self, f: Callable[[T], None]) -> Option[T]:
        return self

    def __iter__(self) -> Iterator[T]:
        return iter([])

    def match(self, some: Callable[[T], U], nothing: Callable[[], U]) -> U:
        return nothing()


def as_option(value: T | None) -> Option[T]:
    """
    値をOption型に変換します。
    Noneの場合はNothing、そうでない場合はSomeを返します。
    """
    if value is None:
        return Nothing[T]()
    else:
        return Some(value)


def some(value: T | None) -> Option[T]:
    """
    値をSome型のOptionに変換します。
    """
    if value is None:
        raise ValueError("Cannot create Some with None value")
    return Some(value)
