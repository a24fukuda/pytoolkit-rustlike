import pytest

from pytoolkit_rustlike import Err, Nothing, UnwrapError


class TestUnwrapError:
    def test_err_unwrap_raises_unwrap_error(self):
        err: Err[int, ValueError] = Err(ValueError("original error"))

        with pytest.raises(UnwrapError, match="Called unwrap on Err value"):
            err.unwrap()

    def test_err_unwrap_with_different_error_types(self):
        # さまざまなエラー型でUnwrapErrorが発生することを確認
        test_cases = [
            Err[int, ValueError](ValueError("test")),
            Err[int, str]("string error"),
            Err[str, int](404),
            Err[int, dict[str, str]]({"error": "dict error"}),
        ]

        for err in test_cases:
            with pytest.raises(UnwrapError, match="Called unwrap on Err value"):
                err.unwrap()

    def test_nothing_unwrap_raises_unwrap_error(self):
        nothing = Nothing[int]()

        with pytest.raises(UnwrapError, match="Called unwrap on None"):
            nothing.unwrap()

    def test_nothing_expect_raises_unwrap_error(self):
        nothing = Nothing[int]()

        with pytest.raises(UnwrapError, match="Custom message: called expect on None"):
            nothing.expect("Custom message")
