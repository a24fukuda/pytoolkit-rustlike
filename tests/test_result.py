import pytest

from pytoolkit_result.result import Err, Ok, Result


class TestOk:
    def test_is_ok(self):
        ok = Ok(42)
        assert ok.is_ok() is True

    def test_is_error(self):
        ok = Ok(42)
        assert ok.is_error() is False

    def test_unwrap(self):
        ok = Ok(42)
        assert ok.unwrap() == 42

    def test_unwrap_or(self):
        ok = Ok(42)
        assert ok.unwrap_or(0) == 42

    def test_map(self):
        ok = Ok(42)
        result = ok.map(lambda x: x * 2)
        assert isinstance(result, Ok)
        assert result.unwrap() == 84

    def test_and_then_returns_ok(self):
        ok = Ok(42)
        result = ok.and_then(lambda x: Ok(x * 2))
        assert isinstance(result, Ok)
        assert result.unwrap() == 84

    def test_and_then_returns_err(self):
        ok = Ok(42)
        error = ValueError("test error")
        result = ok.and_then(lambda x: Err[int](error))
        assert isinstance(result, Err)
        with pytest.raises(ValueError, match="test error"):
            result.unwrap()


class TestErr:
    def test_is_ok(self):
        err: Err[int] = Err(ValueError("test"))
        assert err.is_ok() is False

    def test_is_error(self):
        err: Err[int] = Err(ValueError("test"))
        assert err.is_error() is True

    def test_unwrap_raises_exception(self):
        error = ValueError("test error")
        err: Err[int] = Err(error)
        with pytest.raises(ValueError, match="test error"):
            err.unwrap()

    def test_unwrap_or(self):
        err: Err[int] = Err(ValueError("test"))
        assert err.unwrap_or(42) == 42

    def test_map(self):
        err: Err[int] = Err(ValueError("test"))
        result = err.map(lambda x: x * 2)
        assert isinstance(result, Err)
        with pytest.raises(ValueError, match="test"):
            result.unwrap()

    def test_and_then(self):
        err: Err[int] = Err(ValueError("test"))
        result = err.and_then(lambda x: Ok(x * 2))
        assert isinstance(result, Err)
        with pytest.raises(ValueError, match="test"):
            result.unwrap()


class TestResultAbstract:
    def test_cannot_instantiate_result_directly(self):
        with pytest.raises(TypeError):
            Result()  # type: ignore


class TestResultTypes:
    def test_ok_with_string(self):
        ok = Ok("hello")
        assert ok.unwrap() == "hello"

    def test_ok_with_list(self):
        ok = Ok([1, 2, 3])
        assert ok.unwrap() == [1, 2, 3]

    def test_err_with_different_exceptions(self):
        runtime_error: Err[str] = Err(RuntimeError("runtime error"))
        value_error: Err[str] = Err(ValueError("value error"))

        assert runtime_error.is_error()
        assert value_error.is_error()

        with pytest.raises(RuntimeError):
            runtime_error.unwrap()

        with pytest.raises(ValueError):
            value_error.unwrap()


class TestResultChaining:
    def test_map_chaining(self):
        result = Ok(10).map(lambda x: x * 2).map(lambda x: x + 1)
        assert isinstance(result, Ok)
        assert result.unwrap() == 21

    def test_and_then_chaining(self):
        def divide_by_two(x: int) -> Result[float]:
            return Ok(x / 2.0)

        def to_string(x: float) -> Result[str]:
            return Ok(str(x))

        result = Ok(10).and_then(divide_by_two).and_then(to_string)
        assert isinstance(result, Ok)
        assert result.unwrap() == "5.0"

    def test_mixed_chaining_with_error(self):
        def fail_function(x: int) -> Result[int]:
            return Err[int](ValueError("failed"))

        result = Ok(10).and_then(fail_function).map(lambda x: x * 2)
        assert isinstance(result, Err)
        with pytest.raises(ValueError, match="failed"):
            result.unwrap()
