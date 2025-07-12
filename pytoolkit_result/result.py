from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, Generic, TypeVar

T = TypeVar("T")
U = TypeVar("U")


class Result(ABC, Generic[T]):
    @abstractmethod
    def is_ok(self) -> bool:
        raise NotImplementedError()

    def is_error(self) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def unwrap(self) -> T:
        raise NotImplementedError()

    @abstractmethod
    def unwrap_or(self, default: T) -> T:
        raise NotImplementedError()

    @abstractmethod
    def map(self, f: Callable[[T], U]) -> Result[U]:
        raise NotImplementedError()

    @abstractmethod
    def and_then(self, f: Callable[[T], Result[U]]) -> Result[U]:
        raise NotImplementedError()

    @abstractmethod
    def match(self, ok: Callable[[T], U], err: Callable[[Exception], U]) -> U:
        raise NotImplementedError()


@dataclass(frozen=True)
class Ok(Result[T]):
    _value: T

    def is_ok(self) -> bool:
        return True

    def is_error(self) -> bool:
        return False

    def unwrap(self) -> T:
        return self._value

    def unwrap_or(self, default: T) -> T:
        return self._value

    def map(self, f: Callable[[T], U]) -> Result[U]:
        return Ok(f(self._value))

    def and_then(self, f: Callable[[T], Result[U]]) -> Result[U]:
        return f(self._value)

    def match(self, ok: Callable[[T], U], err: Callable[[Exception], U]) -> U:
        return ok(self._value)


@dataclass(frozen=True)
class Err(Result[T]):
    _error: Exception

    def is_ok(self) -> bool:
        return False

    def is_error(self) -> bool:
        return True

    def unwrap(self) -> T:
        raise self._error

    def unwrap_or(self, default: T) -> T:
        return default

    def map(self, f: Callable[[T], U]) -> Result[U]:
        return Err(self._error)

    def and_then(self, f: Callable[[T], Result[U]]) -> Result[U]:
        return Err(self._error)

    def match(self, ok: Callable[[T], U], err: Callable[[Exception], U]) -> U:
        return err(self._error)
