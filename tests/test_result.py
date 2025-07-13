import pytest

from pytoolkit_rustlike import Err, Nothing, Ok, Option, Result, Some, UnwrapError


class TestResult:
    """Result抽象基底クラスのテスト"""

    def test_cannot_instantiate_result_directly(self):
        with pytest.raises(TypeError):
            Result()  # type: ignore


class TestOk:
    """Okクラスのテスト"""

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

    def test_expect(self):
        ok = Ok(42)
        assert ok.expect("Should have value") == 42

    def test_unwrap_err_raises(self):
        ok = Ok(42)
        with pytest.raises(RuntimeError, match="Called unwrap_err on Ok value: 42"):
            ok.unwrap_err()

    def test_expect_err_raises(self):
        ok = Ok(42)
        with pytest.raises(
            RuntimeError, match="Test message: called expect_err on Ok value: 42"
        ):
            ok.expect_err("Test message")

    def test_map(self):
        ok = Ok(42)
        result = ok.map(lambda x: x * 2)
        assert result.is_ok()
        assert result.unwrap() == 84

    def test_map_err_no_change(self):
        ok = Ok(42)
        result = ok.map_err(lambda e: RuntimeError(f"wrapped: {e}"))
        assert result.is_ok()
        assert result.unwrap() == 42

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
        with pytest.raises(UnwrapError, match="Called unwrap on Err value"):
            result.unwrap()

    def test_or_else_no_change(self):
        ok = Ok(42)
        result = ok.or_else(lambda e: Ok(0))
        assert result.is_ok()
        assert result.unwrap() == 42

    def test_match_calls_ok_function(self):
        ok = Ok(42)
        result = ok.match(ok=lambda x: f"success: {x}", err=lambda e: f"error: {e}")
        assert result == "success: 42"

    def test_match_with_different_return_types(self):
        ok = Ok("hello")
        result = ok.match(ok=lambda x: len(x), err=lambda e: -1)
        assert result == 5

    def test_inspect(self):
        inspected_values: list[int] = []

        def capture(value: int) -> None:
            inspected_values.append(value)

        ok = Ok(42)
        result = ok.inspect(capture)

        assert result is ok  # 同じインスタンスを返す
        assert inspected_values == [42]

    def test_inspect_err_no_effect(self):
        inspected_errors: list[str] = []

        def capture_error(error: Exception) -> None:
            inspected_errors.append(str(error))

        ok = Ok(42)
        result = ok.inspect_err(capture_error)

        assert result is ok
        assert inspected_errors == []  # 変化なし

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

    def test_or_(self):
        ok = Ok(42)
        err2: Err[int, str] = Err("error2")

        # Ok or anything = Ok
        result = ok.or_(err2)
        assert result.is_ok()
        assert result.unwrap() == 42

    def test_iter(self):
        ok = Ok(42)

        # Okの場合は値を1つ返す
        values = list(ok)
        assert values == [42]

        # for文でも使用可能
        result_values: list[int] = []
        for value in ok:
            result_values.append(value)
        assert result_values == [42]



class TestErr:
    """Errクラスのテスト"""

    def test_is_ok(self):
        err: Err[int, ValueError] = Err(ValueError("test"))
        assert err.is_ok() is False

    def test_is_err(self):
        err: Err[int, ValueError] = Err(ValueError("test"))
        assert err.is_err() is True

    def test_unwrap_raises_exception(self):
        error = ValueError("test error")
        err: Err[int, ValueError] = Err(error)
        with pytest.raises(UnwrapError, match="Called unwrap on Err value"):
            err.unwrap()

    def test_unwrap_or(self):
        err: Err[int, ValueError] = Err(ValueError("test"))
        assert err.unwrap_or(42) == 42

    def test_expect_raises(self):
        err: Err[int, ValueError] = Err(ValueError("original error"))
        with pytest.raises(RuntimeError, match="Custom message: original error"):
            err.expect("Custom message")

    def test_unwrap_err(self):
        error = ValueError("test error")
        err: Err[int, ValueError] = Err(error)
        assert err.unwrap_err() is error

    def test_expect_err(self):
        error = ValueError("test error")
        err: Err[int, ValueError] = Err(error)
        assert err.expect_err("Should be error") is error

    def test_map_no_change(self):
        err: Err[int, ValueError] = Err(ValueError("test"))
        result = err.map(lambda x: x * 2)
        assert result.is_err()
        with pytest.raises(UnwrapError, match="Called unwrap on Err value"):
            result.unwrap()

    def test_map_err(self):
        err: Err[int, ValueError] = Err(ValueError("original"))
        result = err.map_err(lambda e: RuntimeError(f"wrapped: {e}"))
        assert result.is_err()
        unwrapped_err = result.unwrap_err()
        assert isinstance(unwrapped_err, RuntimeError)
        assert str(unwrapped_err) == "wrapped: original"

    def test_and_then_no_change(self):
        err: Err[int, ValueError] = Err(ValueError("test"))
        result = err.and_then(lambda x: Ok(x * 2))
        assert result.is_err()
        with pytest.raises(UnwrapError, match="Called unwrap on Err value"):
            result.unwrap()

    def test_or_else_returns_ok(self):
        err: Err[int, ValueError] = Err(ValueError("error"))
        result = err.or_else(lambda e: Ok(99))
        assert result.is_ok()
        assert result.unwrap() == 99

    def test_or_else_returns_err(self):
        err: Err[int, ValueError] = Err(ValueError("original"))
        result = err.or_else(
            lambda e: Err[int, RuntimeError](RuntimeError("new error"))
        )
        assert result.is_err()
        unwrapped_err = result.unwrap_err()
        assert isinstance(unwrapped_err, RuntimeError)
        assert str(unwrapped_err) == "new error"

    def test_match_calls_err_function(self):
        error = ValueError("test error")
        err: Err[int, ValueError] = Err(error)
        result = err.match(ok=lambda x: f"success: {x}", err=lambda e: f"error: {e}")
        assert result == "error: test error"

    def test_match_with_different_return_types(self):
        err: Err[str, RuntimeError] = Err(RuntimeError("runtime error"))
        result = err.match(ok=lambda x: len(x), err=lambda e: -1)
        assert result == -1

    def test_inspect_no_effect(self):
        inspected_values: list[int] = []

        def capture(value: int) -> None:
            inspected_values.append(value)

        err: Err[int, ValueError] = Err(ValueError("error"))
        result = err.inspect(capture)

        assert result is err
        assert inspected_values == []  # 変化なし

    def test_inspect_err(self):
        inspected_errors: list[str] = []

        def capture_error(error: Exception) -> None:
            inspected_errors.append(str(error))

        err: Err[int, Exception] = Err(ValueError("test error"))
        result = err.inspect_err(capture_error)

        assert result is err  # 同じインスタンスを返す
        assert inspected_errors == ["test error"]

    def test_and_(self):
        ok2: Ok[str, Exception] = Ok("hello")
        err: Err[int, Exception] = Err(ValueError("error"))

        # Err and anything = Err（元のエラー）
        result = err.and_(ok2)
        assert result.is_err()
        assert result.unwrap_err() is err.unwrap_err()

    def test_or_(self):
        err1: Err[int, ValueError] = Err(ValueError("error1"))
        err2: Err[int, str] = Err("error2")

        # Err or Ok = Ok
        result = err1.or_(Ok(99))
        assert result.is_ok()
        assert result.unwrap() == 99

        # Err or Err = 第二引数のErr
        result = err1.or_(err2)
        assert result.is_err()
        assert result.unwrap_err() == "error2"

    def test_iter(self):
        err: Err[int, ValueError] = Err(ValueError("error"))

        # Errの場合は空
        values = list(err)
        assert values == []

        # for文でも使用可能
        result_values: list[int] = []
        for value in err:
            result_values.append(value)
        assert result_values == []  # 変化なし



class TestResultIntegration:
    """Result型の統合テスト"""

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
        assert option.is_nothing()
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
            if opt.is_nothing():
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
        assert option.is_nothing()

        # エラーケース
        result = parse_number("invalid").and_then(double_if_present)
        assert result.is_err()
        assert result.unwrap_err() == "'invalid' は有効な数値ではありません"

