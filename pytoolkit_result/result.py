from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, Generic, NoReturn, TypeVar, cast

T = TypeVar("T")
U = TypeVar("U")


class Result(ABC, Generic[T]):
    @abstractmethod
    def is_ok(self) -> bool:
        raise NotImplementedError

    def is_error(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def unwrap(self) -> T:
        raise NotImplementedError

    @abstractmethod
    def unwrap_or(self, default: T) -> T:
        raise NotImplementedError

    def map(self, f: Callable[[T], U]) -> Result[U]:
        if self.is_ok():
            return Ok(f(cast(Ok[T], self)._value))  # type: ignore
        return cast(Err, self)  # type: ignore

    def and_then(self, f: Callable[[T], Result[U]]) -> Result[U]:
        if self.is_ok():
            return f(cast(Ok[T], self)._value)  # type: ignore
        return cast(Err, self)  # type: ignore


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


@dataclass(frozen=True)
class Err(Result[T]):
    _error: Exception

    def is_ok(self) -> bool:
        return False

    def is_error(self) -> bool:
        return True

    def unwrap(self) -> NoReturn:
        raise self._error

    def unwrap_or(self, default: T) -> T:
        return default
