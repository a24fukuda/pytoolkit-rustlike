from typing import Any

import pytest

from pytoolkit_rustlike import Nothing, Option, Some, UnwrapError, as_option, some


class TestOption:
    """Option抽象基底クラスのテスト"""

    def test_cannot_instantiate_option_directly(self):
        with pytest.raises(TypeError):
            Option()  # type: ignore


class TestSome:
    """Someクラスのテスト"""

    def test_is_some(self):
        some = Some(42)
        assert some.is_some() is True

    def test_is_nothing(self):
        some = Some(42)
        assert some.is_nothing() is False

    def test_unwrap(self):
        some = Some(42)
        assert some.unwrap() == 42

    def test_unwrap_or(self):
        some = Some(42)
        assert some.unwrap_or(0) == 42

    def test_expect(self):
        some = Some(42)
        assert some.expect("Should have value") == 42

    def test_unwrap_or_else(self):
        some = Some(42)
        assert some.unwrap_or_else(lambda: 0) == 42

    def test_map(self):
        some = Some(42)
        result = some.map(lambda x: x * 2)
        assert result.is_some()
        assert result.unwrap() == 84

    def test_map_or(self):
        some = Some(42)
        assert some.map_or(0, lambda x: x * 2) == 84

    def test_map_or_else(self):
        some = Some(42)
        assert some.map_or_else(lambda: 0, lambda x: x * 2) == 84

    def test_and_then(self):
        some = Some(42)
        result = some.and_then(lambda x: Some(x * 2))
        assert result.is_some()
        assert result.unwrap() == 84

    def test_and_then_to_nothing(self):
        some = Some(42)
        result = some.and_then(lambda x: Nothing[int]())
        assert result.is_nothing()

    def test_filter_passes(self):
        some_even = Some(42)

        # フィルタに通る場合
        result = some_even.filter(lambda x: x % 2 == 0)
        assert result.is_some()
        assert result.unwrap() == 42

    def test_filter_fails(self):
        some_odd = Some(43)

        # フィルタに通らない場合
        result = some_odd.filter(lambda x: x % 2 == 0)
        assert result.is_nothing()

    def test_or_else_no_change(self):
        some = Some(42)
        assert some.or_else(lambda: Some(99)).unwrap() == 42

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
        assert result.is_nothing()

    def test_or_(self):
        some = Some(42)
        nothing1 = Nothing[int]()

        # Some or anything = Some
        result = some.or_(nothing1)
        assert result.is_some()
        assert result.unwrap() == 42

    def test_inspect(self):
        inspected_values: list[int] = []

        def capture(value: int) -> None:
            inspected_values.append(value)

        some = Some(42)
        result = some.inspect(capture)

        assert result is some  # 同じインスタンスを返す
        assert inspected_values == [42]

    def test_iter(self):
        some = Some(42)

        # Someの場合は値を1つ返す
        values = list(some)
        assert values == [42]

        # for文でも使用可能
        result_values: list[int] = []
        for value in some:
            result_values.append(value)
        assert result_values == [42]

    def test_match(self):
        some = Some(42)
        result = some.match(some=lambda x: x * 2, nothing=lambda: 0)
        assert result == 84


class TestNothing:
    """Nothingクラスのテスト"""

    def test_is_some(self):
        nothing = Nothing[Any]()
        assert nothing.is_some() is False

    def test_is_nothing(self):
        nothing = Nothing[Any]()
        assert nothing.is_nothing() is True

    def test_unwrap_raises(self):
        nothing = Nothing[Any]()
        with pytest.raises(UnwrapError, match="Called unwrap on None"):
            nothing.unwrap()

    def test_unwrap_or(self):
        nothing = Nothing[int]()
        assert nothing.unwrap_or(42) == 42

    def test_expect_raises(self):
        nothing = Nothing[int]()
        with pytest.raises(UnwrapError, match="Custom message: called expect on None"):
            nothing.expect("Custom message")

    def test_unwrap_or_else(self):
        nothing = Nothing[int]()
        assert nothing.unwrap_or_else(lambda: 99) == 99

    def test_map(self):
        nothing = Nothing[int]()
        result = nothing.map(lambda x: x * 2)
        assert result.is_nothing()

    def test_map_or(self):
        nothing = Nothing[int]()
        assert nothing.map_or(0, lambda x: x * 2) == 0

    def test_map_or_else(self):
        nothing = Nothing[int]()
        assert nothing.map_or_else(lambda: 99, lambda x: x * 2) == 99

    def test_and_then(self):
        nothing = Nothing[int]()
        result = nothing.and_then(lambda x: Some(x * 2))
        assert result.is_nothing()

    def test_filter(self):
        nothing = Nothing[int]()

        # Nothingの場合
        result = nothing.filter(lambda x: x % 2 == 0)
        assert result.is_nothing()

    def test_or_else_returns_some(self):
        nothing = Nothing[int]()
        assert nothing.or_else(lambda: Some(99)).unwrap() == 99

    def test_or_else_returns_nothing(self):
        nothing = Nothing[int]()
        assert nothing.or_else(lambda: Nothing[int]()).is_nothing()

    def test_and_(self):
        some2 = Some("hello")
        nothing = Nothing[int]()

        # Nothing and anything = Nothing
        result = nothing.and_(some2)
        assert result.is_nothing()

    def test_or_(self):
        some = Some(42)
        nothing1 = Nothing[int]()
        nothing2 = Nothing[int]()

        # Nothing or Some = Some
        result = nothing1.or_(some)
        assert result.is_some()
        assert result.unwrap() == 42

        # Nothing or Nothing = Nothing
        result = nothing1.or_(nothing2)
        assert result.is_nothing()

    def test_inspect_no_effect(self):
        inspected_values: list[int] = []

        def capture(value: int) -> None:
            inspected_values.append(value)

        nothing = Nothing[int]()
        result = nothing.inspect(capture)

        assert result is nothing
        assert inspected_values == []  # 変化なし

    def test_iter(self):
        nothing = Nothing[int]()

        # Nothingの場合は空
        values = list(nothing)
        assert values == []

        # for文でも使用可能
        result_values: list[int] = []
        for value in nothing:
            result_values.append(value)
        assert result_values == []  # 変化なし

    def test_match(self):
        nothing = Nothing[int]()
        result = nothing.match(some=lambda x: x * 2, nothing=lambda: 42)
        assert result == 42

    def test_new_instance_behavior(self):
        nothing1 = Nothing[Any]()
        nothing2 = Nothing[Any]()
        assert nothing1 is not nothing2
        assert nothing1 != nothing2


class TestAsOption:
    """as_option関数のテスト"""

    def test_as_option_with_value(self):
        result = as_option(42)
        assert result.is_some()
        assert result.unwrap() == 42

    def test_as_option_with_none(self):
        result: Option[Any] = as_option(None)
        assert result.is_nothing()

    def test_as_option_with_string(self):
        result = as_option("hello")
        assert result.is_some()
        assert result.unwrap() == "hello"

    def test_as_option_with_empty_string(self):
        # 空文字列でも値として扱われる
        result = as_option("")
        assert result.is_some()
        assert result.unwrap() == ""

    def test_as_option_with_zero(self):
        # 0でも値として扱われる
        result = as_option(0)
        assert result.is_some()
        assert result.unwrap() == 0

    def test_as_option_with_false(self):
        # Falseでも値として扱われる
        result = as_option(False)
        assert result.is_some()
        assert result.unwrap() is False

    def test_as_option_chaining(self):
        # as_optionの結果をメソッドチェーンで使用
        result = as_option(42).map(lambda x: x * 2).unwrap_or(0)
        assert result == 84

        result = as_option(None).map(lambda x: x * 2).unwrap_or(0)  # type: ignore
        assert result == 0


class TestSomeFunction:
    """some関数のテスト"""

    def test_some_with_value(self):
        result = some(42)
        assert result.is_some()
        assert result.unwrap() == 42

    def test_some_with_string(self):
        result = some("hello")
        assert result.is_some()
        assert result.unwrap() == "hello"

    def test_some_with_empty_string(self):
        # 空文字列でもSomeを作成
        result = some("")
        assert result.is_some()
        assert result.unwrap() == ""

    def test_some_with_zero(self):
        # 0でもSomeを作成
        result = some(0)
        assert result.is_some()
        assert result.unwrap() == 0

    def test_some_with_false(self):
        # FalseでもSomeを作成
        result = some(False)
        assert result.is_some()
        assert result.unwrap() is False

    def test_some_with_none_raises_error(self):
        # Noneを渡すとValueErrorが発生（型ヒントでは許可されないが実行時チェック）
        with pytest.raises(ValueError, match="Cannot create Some with None value"):
            some(None)  # type: ignore # 意図的にNoneを渡してエラーをテスト

    def test_some_chaining(self):
        # some関数の結果をメソッドチェーンで使用
        result = some(42).map(lambda x: x * 2).unwrap()
        assert result == 84

    def test_some_vs_as_option_comparison(self):
        # someとas_optionの動作比較
        value = 42

        # 同じ値に対して同じ結果
        some_result = some(value)
        as_option_result = as_option(value)

        assert some_result.unwrap() == as_option_result.unwrap()

        # Noneに対する違い
        as_option_none: Option[Any] = as_option(None)
        assert as_option_none.is_nothing()

        # someはNoneでエラー（型ヒントでは許可されないが実行時チェック）
        with pytest.raises(ValueError):
            some(None)  # type: ignore


class TestOptionIntegration:
    """Option型の統合テスト"""

    def test_option_map_polymorphism(self):
        options: list[Option[int]] = [Some(42), Nothing()]

        results = [opt.map(lambda x: x * 2) for opt in options]

        assert results[0].is_some()
        assert results[0].unwrap() == 84
        assert results[1].is_nothing()

    def test_option_match_polymorphism(self):
        options: list[Option[int]] = [Some(42), Nothing()]

        results = [
            opt.match(some=lambda x: f"Value: {x}", nothing=lambda: "No value")
            for opt in options
        ]

        assert results[0] == "Value: 42"
        assert results[1] == "No value"

    def test_integration_with_as_option(self):
        # as_optionと他のOption操作の統合テスト
        values = [42, None, 0, "hello", None]
        options = [as_option(v) for v in values]  # type: ignore

        # mapで変換
        mapped = [opt.map(lambda x: str(x).upper()) for opt in options]

        assert mapped[0].unwrap() == "42"
        assert mapped[1].is_nothing()
        assert mapped[2].unwrap() == "0"
        assert mapped[3].unwrap() == "HELLO"
        assert mapped[4].is_nothing()

    def test_integration_with_some_function(self):
        # some関数と他のOption操作の統合テスト
        values = [42, 0, "hello", False, ""]

        # some関数で全てSomeに変換
        options = [some(v) for v in values]

        # 全てSomeであることを確認
        assert all(opt.is_some() for opt in options)

        # フィルタリング
        filtered = [opt.filter(lambda x: bool(x)) for opt in options]

        # 42, "hello"のみ残る（0, False, ""は除外）
        assert filtered[0].unwrap() == 42  # 42は真
        assert filtered[1].is_nothing()  # 0は偽
        assert filtered[2].unwrap() == "hello"  # "hello"は真
        assert filtered[3].is_nothing()  # Falseは偽
        assert filtered[4].is_nothing()  # ""は偽

    def test_factory_functions_comparison(self):
        # ファクトリ関数の使い分けテスト
        test_values = [42, "hello", 0, False, ""]

        for value in test_values:
            # someとas_optionは同じ結果（None以外）
            some_result = some(value)
            as_option_result = as_option(value)

            assert some_result.unwrap() == as_option_result.unwrap()

        # Noneの場合の違い
        as_option_none: Option[Any] = as_option(None)
        assert as_option_none.is_nothing()

        # someはNoneを受け付けない（型ヒントでは許可されないが実行時チェック）
        with pytest.raises(ValueError):
            some(None)  # type: ignore
