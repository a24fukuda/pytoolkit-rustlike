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
        assert result.is_ok()
        assert result.unwrap() == 84

    def test_and_then_returns_ok(self):
        ok = Ok(42)
        result = ok.and_then(lambda x: Ok(x * 2))
        assert result.is_ok()
        assert result.unwrap() == 84

    def test_and_then_returns_err(self):
        ok = Ok(42)
        error = ValueError("test error")
        result = ok.and_then(lambda x: Err[int](error))
        assert result.is_error()
        with pytest.raises(ValueError, match="test error"):
            result.unwrap()

    def test_match_calls_ok_function(self):
        ok = Ok(42)
        result = ok.match(
            ok=lambda x: f"success: {x}",
            err=lambda e: f"error: {e}"
        )
        assert result == "success: 42"

    def test_match_with_different_return_types(self):
        ok = Ok("hello")
        result = ok.match(
            ok=lambda x: len(x),
            err=lambda e: -1
        )
        assert result == 5


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
        assert result.is_error()
        with pytest.raises(ValueError, match="test"):
            result.unwrap()

    def test_and_then(self):
        err: Err[int] = Err(ValueError("test"))
        result = err.and_then(lambda x: Ok(x * 2))
        assert result.is_error()
        with pytest.raises(ValueError, match="test"):
            result.unwrap()

    def test_match_calls_err_function(self):
        error = ValueError("test error")
        err: Err[int] = Err(error)
        result = err.match(
            ok=lambda x: f"success: {x}",
            err=lambda e: f"error: {e}"
        )
        assert result == "error: test error"

    def test_match_with_different_return_types(self):
        err: Err[str] = Err(RuntimeError("runtime error"))
        result = err.match(
            ok=lambda x: len(x),
            err=lambda e: -1
        )
        assert result == -1


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
        assert result.is_ok()
        assert result.unwrap() == 21

    def test_and_then_chaining(self):
        def divide_by_two(x: int) -> Result[float]:
            return Ok(x / 2.0)

        def to_string(x: float) -> Result[str]:
            return Ok(str(x))

        result = Ok(10).and_then(divide_by_two).and_then(to_string)
        assert result.is_ok()
        assert result.unwrap() == "5.0"

    def test_mixed_chaining_with_error(self):
        def fail_function(x: int) -> Result[int]:
            return Err[int](ValueError("failed"))

        result = Ok(10).and_then(fail_function).map(lambda x: x * 2)
        assert result.is_error()
        with pytest.raises(ValueError, match="failed"):
            result.unwrap()


class TestResultMatch:
    def test_match_chaining_with_ok(self):
        def process_value(x: int) -> Result[str]:
            if x > 0:
                return Ok(f"positive: {x}")
            else:
                return Err[str](ValueError("negative value"))

        result = Ok(42).and_then(process_value).match(
            ok=lambda x: f"processed {x}",
            err=lambda e: f"failed: {e}"
        )
        assert result == "processed positive: 42"

    def test_match_chaining_with_error(self):
        def process_value(x: int) -> Result[str]:
            if x > 0:
                return Ok(f"positive: {x}")
            else:
                return Err[str](ValueError("negative value"))

        result = Ok(-5).and_then(process_value).match(
            ok=lambda x: f"processed {x}",
            err=lambda e: f"failed: {e}"
        )
        assert result == "failed: negative value"

    def test_match_with_complex_types(self):
        data = {"name": "Alice", "age": 30}
        ok = Ok(data)
        result = ok.match(
            ok=lambda d: f"{d['name']} is {d['age']} years old",
            err=lambda e: "No user data"
        )
        assert result == "Alice is 30 years old"

    def test_match_returns_result_type(self):
        def success_to_result(x: int) -> Result[str]:
            return Ok(f"value: {x}")

        def error_to_result(e: Exception) -> Result[str]:
            return Err[str](RuntimeError(f"wrapped: {e}"))

        ok_result = Ok(42).match(
            ok=success_to_result,
            err=error_to_result
        )
        assert ok_result.is_ok()
        assert ok_result.unwrap() == "value: 42"

        err_result: Err[int] = Err(ValueError("original"))
        err_match_result = err_result.match(
            ok=success_to_result,
            err=error_to_result
        )
        assert err_match_result.is_error()
        with pytest.raises(RuntimeError, match="wrapped: original"):
            err_match_result.unwrap()
