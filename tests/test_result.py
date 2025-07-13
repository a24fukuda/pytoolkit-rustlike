from typing import Any

import pytest

from pytoolkit_rustlike import Err, Ok, Result, Nothing, Option, Some, UnwrapError


class TestOk:
    def test_is_ok(self):
        ok = Ok(42)
        assert ok.is_ok() is True

    def test_is_err(self):
        ok = Ok(42)
        assert ok.is_err() is False

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
        ok: Ok[int, Exception] = Ok(42)
        error = ValueError("test error")
        result = ok.and_then(lambda x: Err[int, Exception](error))
        assert result.is_err()
        with pytest.raises(UnwrapError, match="test error"):
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
        err: Err[int, ValueError] = Err(ValueError("test"))
        assert err.is_ok() is False

    def test_is_err(self):
        err: Err[int, ValueError] = Err(ValueError("test"))
        assert err.is_err() is True

    def test_unwrap_raises_exception(self):
        error = ValueError("test error")
        err: Err[int, ValueError] = Err(error)
        with pytest.raises(UnwrapError, match="test error"):
            err.unwrap()

    def test_unwrap_or(self):
        err: Err[int, ValueError] = Err(ValueError("test"))
        assert err.unwrap_or(42) == 42

    def test_map(self):
        err: Err[int, ValueError] = Err(ValueError("test"))
        result = err.map(lambda x: x * 2)
        assert result.is_err()
        with pytest.raises(UnwrapError, match="test"):
            result.unwrap()

    def test_and_then(self):
        err: Err[int, ValueError] = Err(ValueError("test"))
        result = err.and_then(lambda x: Ok(x * 2))
        assert result.is_err()
        with pytest.raises(UnwrapError, match="test"):
            result.unwrap()

    def test_match_calls_err_function(self):
        error = ValueError("test error")
        err: Err[int, ValueError] = Err(error)
        result = err.match(
            ok=lambda x: f"success: {x}",
            err=lambda e: f"error: {e}"
        )
        assert result == "error: test error"

    def test_match_with_different_return_types(self):
        err: Err[str, RuntimeError] = Err(RuntimeError("runtime error"))
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
        runtime_error: Err[str, RuntimeError] = Err(RuntimeError("runtime error"))
        value_error: Err[str, ValueError] = Err(ValueError("value error"))

        assert runtime_error.is_err()
        assert value_error.is_err()

        with pytest.raises(UnwrapError):
            runtime_error.unwrap()

        with pytest.raises(UnwrapError):
            value_error.unwrap()


class TestResultChaining:
    def test_map_chaining(self):
        result = Ok(10).map(lambda x: x * 2).map(lambda x: x + 1)
        assert result.is_ok()
        assert result.unwrap() == 21

    def test_and_then_chaining(self):
        def divide_by_two(x: int) -> Result[float, Exception]:
            return Ok(x / 2.0)

        def to_string(x: float) -> Result[str, Exception]:
            return Ok(str(x))

        result = Ok(10).and_then(divide_by_two).and_then(to_string)
        assert result.is_ok()
        assert result.unwrap() == "5.0"

    def test_mixed_chaining_with_error(self):
        def fail_function(x: int) -> Result[int, Exception]:
            return Err[int, Exception](ValueError("failed"))

        result = Ok(10).and_then(fail_function).map(lambda x: x * 2)
        assert result.is_err()
        with pytest.raises(UnwrapError, match="failed"):
            result.unwrap()


class TestResultMatch:
    def test_match_chaining_with_ok(self):
        def process_value(x: int) -> Result[str, Exception]:
            if x > 0:
                return Ok(f"positive: {x}")
            else:
                return Err[str, Exception](ValueError("negative value"))

        result = Ok(42).and_then(process_value).match(
            ok=lambda x: f"processed {x}",
            err=lambda e: f"failed: {e}"
        )
        assert result == "processed positive: 42"

    def test_match_chaining_with_error(self):
        def process_value(x: int) -> Result[str, Exception]:
            if x > 0:
                return Ok(f"positive: {x}")
            else:
                return Err[str, Exception](ValueError("negative value"))

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


class TestNewRustMethods:
    def test_expect_on_ok(self):
        ok = Ok(42)
        assert ok.expect("Should have value") == 42

    def test_expect_on_err(self):
        err: Err[int, ValueError] = Err(ValueError("original error"))
        with pytest.raises(RuntimeError, match="Custom message: original error"):
            err.expect("Custom message")

    def test_unwrap_err_on_ok(self):
        ok = Ok(42)
        with pytest.raises(RuntimeError, match="Called unwrap_err on Ok value: 42"):
            ok.unwrap_err()

    def test_unwrap_err_on_err(self):
        error = ValueError("test error")
        err: Err[int, ValueError] = Err(error)
        assert err.unwrap_err() is error

    def test_map_err_on_ok(self):
        ok = Ok(42)
        result = ok.map_err(lambda e: RuntimeError(f"wrapped: {e}"))
        assert result.is_ok()
        assert result.unwrap() == 42

    def test_map_err_on_err(self):
        err: Err[int, ValueError] = Err(ValueError("original"))
        result = err.map_err(lambda e: RuntimeError(f"wrapped: {e}"))
        assert result.is_err()
        unwrapped_err = result.unwrap_err()
        assert isinstance(unwrapped_err, RuntimeError)
        assert str(unwrapped_err) == "wrapped: original"

    def test_or_else_on_ok(self):
        ok = Ok(42)
        result = ok.or_else(lambda e: Ok(0))
        assert result.is_ok()
        assert result.unwrap() == 42

    def test_or_else_on_err_returns_ok(self):
        err: Err[int, ValueError] = Err(ValueError("error"))
        result = err.or_else(lambda e: Ok(99))
        assert result.is_ok()
        assert result.unwrap() == 99

    def test_or_else_on_err_returns_err(self):
        err: Err[int, ValueError] = Err(ValueError("original"))
        result = err.or_else(lambda e: Err[int, RuntimeError](RuntimeError("new error")))
        assert result.is_err()
        unwrapped_err = result.unwrap_err()
        assert isinstance(unwrapped_err, RuntimeError)
        assert str(unwrapped_err) == "new error"

    def test_chaining_with_new_methods(self):
        def safe_divide(x: int, y: int) -> Result[float, ValueError]:
            if y == 0:
                return Err[float, ValueError](ValueError("Division by zero"))
            return Ok(x / y)

        def format_result(x: float) -> Result[str, ValueError]:
            return Ok(f"{x:.2f}")

        result = (
            safe_divide(10, 2)
            .and_then(format_result)
            .map_err(lambda e: RuntimeError(f"Math error: {e}"))
        )
        assert result.is_ok()
        assert result.unwrap() == "5.00"

        error_result = (
            safe_divide(10, 0)
            .and_then(format_result)
            .map_err(lambda e: RuntimeError(f"Math error: {e}"))
        )
        assert error_result.is_err()
        err = error_result.unwrap_err()
        assert isinstance(err, RuntimeError)
        assert "Math error: Division by zero" in str(err)


    def test_match_returns_result_type(self):
        def success_to_result(x: int) -> Result[str, Exception]:
            return Ok(f"value: {x}")

        def error_to_result(e: Exception) -> Result[str, RuntimeError]:
            return Err[str, RuntimeError](RuntimeError(f"wrapped: {e}"))

        ok_result = Ok(42).match(
            ok=success_to_result,
            err=error_to_result
        )
        assert ok_result.is_ok()
        assert ok_result.unwrap() == "value: 42"

        err_result: Err[int, ValueError] = Err(ValueError("original"))
        err_match_result = err_result.match(
            ok=success_to_result,
            err=error_to_result
        )
        assert err_match_result.is_err()
        with pytest.raises(UnwrapError, match="wrapped: original"):
            err_match_result.unwrap()


class TestSome:
    def test_is_some(self):
        some = Some(42)
        assert some.is_some() is True

    def test_is_none(self):
        some = Some(42)
        assert some.is_none() is False

    def test_unwrap(self):
        some = Some(42)
        assert some.unwrap() == 42

    def test_unwrap_or(self):
        some = Some(42)
        assert some.unwrap_or(0) == 42

    def test_map(self):
        some = Some(42)
        result = some.map(lambda x: x * 2)
        assert isinstance(result, Some)
        assert result.unwrap() == 84

    def test_and_then(self):
        some = Some(42)
        result = some.and_then(lambda x: Some(x * 2))
        assert isinstance(result, Some)
        assert result.unwrap() == 84

    def test_and_then_to_nothing(self):
        some = Some(42)
        result = some.and_then(lambda x: Nothing[int]())
        assert isinstance(result, Nothing)

    def test_match(self):
        some = Some(42)
        result = some.match(some=lambda x: x * 2, nothing=lambda: 0)
        assert result == 84


class TestNothing:
    def test_is_some(self):
        nothing = Nothing[Any]()
        assert nothing.is_some() is False

    def test_is_none(self):
        nothing = Nothing[Any]()
        assert nothing.is_none() is True

    def test_unwrap_raises(self):
        nothing = Nothing[Any]()
        with pytest.raises(UnwrapError, match="Called unwrap on None"):
            nothing.unwrap()

    def test_unwrap_or(self):
        nothing = Nothing[int]()
        assert nothing.unwrap_or(42) == 42

    def test_map(self):
        nothing = Nothing[int]()
        result = nothing.map(lambda x: x * 2)
        assert isinstance(result, Nothing)

    def test_and_then(self):
        nothing = Nothing[int]()
        result = nothing.and_then(lambda x: Some(x * 2))
        assert isinstance(result, Nothing)

    def test_match(self):
        nothing = Nothing[int]()
        result = nothing.match(some=lambda x: x * 2, nothing=lambda: 42)
        assert result == 42

    def test_new_instance_behavior(self):
        nothing1 = Nothing[Any]()
        nothing2 = Nothing[Any]()
        assert nothing1 is not nothing2
        assert nothing1 != nothing2


class TestOptionGeneric:
    def test_some_with_string(self):
        some = Some("hello")
        assert some.unwrap() == "hello"
        result = some.map(lambda x: x.upper())
        assert result.unwrap() == "HELLO"

    def test_some_with_list(self):
        some = Some([1, 2, 3])
        assert some.unwrap() == [1, 2, 3]
        result = some.map(lambda x: len(x))
        assert result.unwrap() == 3

    def test_chaining_operations(self):
        some = Some(10)
        result = (
            some.map(lambda x: x * 2)
            .and_then(lambda x: Some(x + 5))
            .map(lambda x: str(x))
        )
        assert result.unwrap() == "25"

    def test_chaining_with_nothing(self):
        some = Some(10)
        result = (
            some.map(lambda x: x * 2)
            .and_then(lambda x: Nothing[int]())
            .map(lambda x: str(x))
        )
        assert isinstance(result, Nothing)


class TestOptionPolymorphism:
    def test_option_interface(self):
        options: list[Option[int]] = [Some(42), Nothing()]

        for option in options:
            assert isinstance(option.is_some(), bool)
            assert isinstance(option.is_none(), bool)
            assert option.unwrap_or(0) >= 0

    def test_option_map_polymorphism(self):
        options: list[Option[int]] = [Some(42), Nothing()]

        results = [opt.map(lambda x: x * 2) for opt in options]

        assert isinstance(results[0], Some)
        assert results[0].unwrap() == 84
        assert isinstance(results[1], Nothing)

    def test_option_match_polymorphism(self):
        options: list[Option[int]] = [Some(42), Nothing()]

        results = [
            opt.match(some=lambda x: f"Value: {x}", nothing=lambda: "No value")
            for opt in options
        ]

        assert results[0] == "Value: 42"
        assert results[1] == "No value"


class TestOptionRustMethods:
    def test_expect_on_some(self):
        some = Some(42)
        assert some.expect("Should have value") == 42

    def test_expect_on_nothing(self):
        nothing = Nothing[int]()
        with pytest.raises(UnwrapError, match="Custom message: called expect on None"):
            nothing.expect("Custom message")

    def test_unwrap_or_else(self):
        some = Some(42)
        nothing = Nothing[int]()
        
        assert some.unwrap_or_else(lambda: 0) == 42
        assert nothing.unwrap_or_else(lambda: 99) == 99

    def test_map_or(self):
        some = Some(42)
        nothing = Nothing[int]()
        
        assert some.map_or(0, lambda x: x * 2) == 84
        assert nothing.map_or(0, lambda x: x * 2) == 0

    def test_map_or_else(self):
        some = Some(42)
        nothing = Nothing[int]()
        
        assert some.map_or_else(lambda: 0, lambda x: x * 2) == 84
        assert nothing.map_or_else(lambda: 99, lambda x: x * 2) == 99

    def test_filter(self):
        some_even = Some(42)
        some_odd = Some(43)
        nothing = Nothing[int]()
        
        # フィルタに通る場合
        result = some_even.filter(lambda x: x % 2 == 0)
        assert result.is_some()
        assert result.unwrap() == 42
        
        # フィルタに通らない場合
        result = some_odd.filter(lambda x: x % 2 == 0)
        assert result.is_none()
        
        # Nothingの場合
        result = nothing.filter(lambda x: x % 2 == 0)
        assert result.is_none()

    def test_or_else(self):
        some = Some(42)
        nothing = Nothing[int]()
        
        assert some.or_else(lambda: Some(99)).unwrap() == 42
        assert nothing.or_else(lambda: Some(99)).unwrap() == 99
        assert nothing.or_else(lambda: Nothing[int]()).is_none()

    def test_and_(self):
        some1 = Some(42)
        some2 = Some("hello")
        nothing = Nothing[int]()
        
        # Some and Some = 第二引数のSome
        result = some1.and_(some2)
        assert result.is_some()
        assert result.unwrap() == "hello"
        
        # Some and Nothing = Nothing
        result = some1.and_(nothing)
        assert result.is_none()
        
        # Nothing and anything = Nothing
        result = nothing.and_(some2)
        assert result.is_none()

    def test_or_(self):
        some = Some(42)
        nothing1 = Nothing[int]()
        nothing2 = Nothing[int]()
        
        # Some or anything = Some
        result = some.or_(nothing1)
        assert result.is_some()
        assert result.unwrap() == 42
        
        # Nothing or Some = Some
        result = nothing1.or_(some)
        assert result.is_some()
        assert result.unwrap() == 42
        
        # Nothing or Nothing = Nothing
        result = nothing1.or_(nothing2)
        assert result.is_none()

    def test_inspect(self):
        inspected_values: list[int] = []
        
        def capture(value: int) -> None:
            inspected_values.append(value)
        
        some = Some(42)
        result = some.inspect(capture)
        
        assert result is some  # 同じインスタンスを返す
        assert inspected_values == [42]
        
        # Nothingの場合は何もしない
        nothing = Nothing[int]()
        result = nothing.inspect(capture)
        
        assert result is nothing
        assert inspected_values == [42]  # 変化なし

    def test_iter(self):
        some = Some(42)
        nothing = Nothing[int]()
        
        # Someの場合は値を1つ返す
        values = list(some)
        assert values == [42]
        
        # Nothingの場合は空
        values = list(nothing)
        assert values == []
        
        # for文でも使用可能
        result_values: list[int] = []
        for value in some:
            result_values.append(value)
        assert result_values == [42]
        
        for value in nothing:
            result_values.append(value)
        assert result_values == [42]  # 変化なし

    def test_complex_chaining_with_new_methods(self):
        def safe_parse(s: str) -> Option[int]:
            try:
                return Some(int(s))
            except ValueError:
                return Nothing[int]()
        
        # 成功ケース
        result = (
            safe_parse("42")
            .filter(lambda x: x > 0)
            .map_or_else(lambda: "No positive number", lambda x: f"Value: {x}")
        )
        assert result == "Value: 42"
        
        # フィルタで除外されるケース
        result = (
            safe_parse("-5")
            .filter(lambda x: x > 0)
            .map_or_else(lambda: "No positive number", lambda x: f"Value: {x}")
        )
        assert result == "No positive number"
        
        # パースエラーケース
        result = (
            safe_parse("invalid")
            .filter(lambda x: x > 0)
            .map_or_else(lambda: "No positive number", lambda x: f"Value: {x}")
        )
        assert result == "No positive number"


class TestOptionAbstract:
    def test_cannot_instantiate_option_directly(self):
        with pytest.raises(TypeError):
            Option()  # type: ignore


class TestComplexTypes:
    def test_result_with_option_success(self):
        result: Result[Option[int], str] = Ok(Some(42))
        assert result.is_ok()
        option = result.unwrap()
        assert option.is_some()
        assert option.unwrap() == 42

    def test_result_with_option_nothing(self):
        result: Result[Option[int], str] = Ok(Nothing[int]())
        assert result.is_ok()
        option = result.unwrap()
        assert option.is_none()
        assert option.unwrap_or(0) == 0

    def test_result_with_option_error(self):
        result: Result[Option[int], str] = Err("エラーが発生しました")
        assert result.is_err()
        assert result.unwrap_err() == "エラーが発生しました"

    def test_complex_chaining_with_option(self):
        def parse_number(s: str) -> Result[Option[int], str]:
            if not s:
                return Ok(Nothing[int]())
            try:
                return Ok(Some(int(s)))
            except ValueError:
                return Err(f"'{s}' は有効な数値ではありません")

        def double_if_present(opt: Option[int]) -> Result[Option[int], str]:
            if opt.is_none():
                return Ok(Nothing[int]())
            return Ok(Some(opt.unwrap() * 2))

        # 正常ケース
        result = parse_number("42").and_then(double_if_present)
        assert result.is_ok()
        option = result.unwrap()
        assert option.is_some()
        assert option.unwrap() == 84

        # 空文字ケース
        result = parse_number("").and_then(double_if_present)
        assert result.is_ok()
        option = result.unwrap()
        assert option.is_none()

        # エラーケース
        result = parse_number("invalid").and_then(double_if_present)
        assert result.is_err()
        assert result.unwrap_err() == "'invalid' は有効な数値ではありません"

    def test_result_with_list_and_custom_error(self):
        class ValidationError(Exception):
            pass

        def validate_positive_numbers(numbers: list[int]) -> Result[list[int], ValidationError]:
            if not numbers:
                return Err(ValidationError("リストが空です"))
            if any(n <= 0 for n in numbers):
                return Err(ValidationError("負の数値が含まれています"))
            return Ok(numbers)

        # 正常ケース
        result = validate_positive_numbers([1, 2, 3])
        assert result.is_ok()
        assert result.unwrap() == [1, 2, 3]

        # エラーケース
        result = validate_positive_numbers([])
        assert result.is_err()
        assert str(result.unwrap_err()) == "リストが空です"

        result = validate_positive_numbers([1, -2, 3])
        assert result.is_err()
        assert str(result.unwrap_err()) == "負の数値が含まれています"


class TestUnwrapError:
    def test_unwrap_error_with_exception(self):
        error = ValueError("original error")
        err: Err[int, ValueError] = Err(error)
        
        with pytest.raises(UnwrapError) as exc_info:
            err.unwrap()
        
        assert exc_info.value.error_value is error
        assert "Called unwrap on Err value: original error" in str(exc_info.value)

    def test_unwrap_error_with_non_exception(self):
        err: Err[int, str] = Err("string error")
        
        with pytest.raises(UnwrapError) as exc_info:
            err.unwrap()
        
        assert exc_info.value.error_value == "string error"
        assert "Called unwrap on Err value: string error" in str(exc_info.value)

    def test_unwrap_error_with_int(self):
        err: Err[str, int] = Err(404)
        
        with pytest.raises(UnwrapError) as exc_info:
            err.unwrap()
        
        assert exc_info.value.error_value == 404
        assert "Called unwrap on Err value: 404" in str(exc_info.value)

    def test_unwrap_error_preserves_original_error(self):
        # 元のエラー値がUnwrapErrorのerror_valueで確実に取得できることを確認
        original_errors = [
            ValueError("test"),
            "string error", 
            404,
            {"error": "dict error"},
            [1, 2, 3]
        ]
        
        for original_error in original_errors:
            err: Err[Any, Any] = Err(original_error)
            
            with pytest.raises(UnwrapError) as exc_info:
                err.unwrap()
            
            assert exc_info.value.error_value is original_error


class TestAdditionalRustMethods:
    def test_is_err(self):
        ok = Ok(42)
        err: Err[int, ValueError] = Err(ValueError("error"))
        
        assert ok.is_err() is False
        assert err.is_err() is True
        
        # is_err() は is_err() のエイリアス
        assert ok.is_err() == ok.is_err()
        assert err.is_err() == err.is_err()

    def test_unwrap_or_else(self):
        ok = Ok(42)
        err: Err[int, ValueError] = Err(ValueError("error"))
        
        assert ok.unwrap_or_else(lambda e: 0) == 42
        assert err.unwrap_or_else(lambda e: len(str(e))) == 5  # "error"の長さ

    def test_expect_err_on_ok(self):
        ok = Ok(42)
        with pytest.raises(RuntimeError, match="Test message: called expect_err on Ok value: 42"):
            ok.expect_err("Test message")

    def test_expect_err_on_err(self):
        error = ValueError("test error")
        err: Err[int, ValueError] = Err(error)
        assert err.expect_err("Should be error") is error

    def test_map_or(self):
        ok = Ok(42)
        err: Err[int, ValueError] = Err(ValueError("error"))
        
        assert ok.map_or(0, lambda x: x * 2) == 84
        assert err.map_or(0, lambda x: x * 2) == 0

    def test_map_or_else(self):
        ok = Ok(42)
        err: Err[int, ValueError] = Err(ValueError("error"))
        
        assert ok.map_or_else(lambda e: 0, lambda x: x * 2) == 84
        assert err.map_or_else(lambda e: len(str(e)), lambda x: x * 2) == 5

    def test_inspect(self):
        inspected_values: list[int] = []
        
        def capture(value: int) -> None:
            inspected_values.append(value)
        
        ok = Ok(42)
        result = ok.inspect(capture)
        
        assert result is ok  # 同じインスタンスを返す
        assert inspected_values == [42]
        
        # Errの場合は何もしない
        err: Err[int, ValueError] = Err(ValueError("error"))
        result = err.inspect(capture)
        
        assert result is err
        assert inspected_values == [42]  # 変化なし

    def test_inspect_err(self):
        inspected_errors: list[str] = []
        
        def capture_error(error: Exception) -> None:
            inspected_errors.append(str(error))
        
        err: Err[int, Exception] = Err(ValueError("test error"))
        result = err.inspect_err(capture_error)
        
        assert result is err  # 同じインスタンスを返す
        assert inspected_errors == ["test error"]
        
        # Okの場合は何もしない
        ok = Ok(42)
        result = ok.inspect_err(capture_error)
        
        assert result is ok
        assert inspected_errors == ["test error"]  # 変化なし

    def test_and_(self):
        ok1: Ok[int, Exception] = Ok(42)
        ok2: Ok[str, Exception] = Ok("hello")
        err: Err[int, Exception] = Err(ValueError("error"))
        
        # Ok and Ok = 第二引数のOk
        result = ok1.and_(ok2)
        assert result.is_ok()
        assert result.unwrap() == "hello"
        
        # Ok and Err = Err
        result = ok1.and_(err)
        assert result.is_err()
        
        # Err and anything = Err（元のエラー）
        result = err.and_(ok2)
        assert result.is_err()
        assert result.unwrap_err() is err.unwrap_err()

    def test_or_(self):
        ok = Ok(42)
        err1: Err[int, ValueError] = Err(ValueError("error1"))
        err2: Err[int, str] = Err("error2")
        
        # Ok or anything = Ok
        result = ok.or_(err2)
        assert result.is_ok()
        assert result.unwrap() == 42
        
        # Err or Ok = Ok
        result = err1.or_(Ok(99))
        assert result.is_ok()
        assert result.unwrap() == 99
        
        # Err or Err = 第二引数のErr
        result = err1.or_(err2)
        assert result.is_err()
        assert result.unwrap_err() == "error2"

    def test_iter(self):
        ok = Ok(42)
        err: Err[int, ValueError] = Err(ValueError("error"))
        
        # Okの場合は値を1つ返す
        values = list(ok)
        assert values == [42]
        
        # Errの場合は空
        values = list(err)
        assert values == []
        
        # for文でも使用可能
        result_values: list[int] = []
        for value in ok:
            result_values.append(value)
        assert result_values == [42]
        
        for value in err:
            result_values.append(value)
        assert result_values == [42]  # 変化なし

    def test_complex_chaining_with_new_methods(self):
        def safe_divide(x: int, y: int) -> Result[float, str]:
            if y == 0:
                return Err("Division by zero")
            return Ok(x / y)
        
        # 成功ケース
        result = (
            safe_divide(10, 2)
            .inspect(lambda x: None)  # 副作用（print削除）
            .map_or_else(
                lambda err: f"エラー: {err}",
                lambda x: f"結果: {x:.2f}"
            )
        )
        assert result == "結果: 5.00"
        
        # エラーケース
        result = (
            safe_divide(10, 0)
            .inspect_err(lambda e: None)  # エラー時の副作用（print削除）
            .map_or_else(
                lambda err: f"エラー: {err}",
                lambda x: f"結果: {x:.2f}"
            )
        )
        assert result == "エラー: Division by zero"
