import pytest
from .context import helpers
from .context import parsec


class TestHelpers:
    def test_numberstring(self):
        assert helpers.numberString().parse("12345") == '12345'


class TestPositiveInteger:
    def test_match(self):
        assert helpers.positiveInteger().parse("12345") == 12345

    def test_partial(self):
        assert helpers.positiveInteger().parse("3.14") == 3

    def test_nomatch(self):
        with pytest.raises(parsec.ParseError):
            helpers.positiveInteger().parse("-86")


class TestNegativeInteger:
    def test_match(self):
        assert helpers.negativeInteger().parse("-10") == -10

    def test_partial(self):
        assert helpers.negativeInteger().parse("-51.1") == -51

    def test_nomatch(self):
        with pytest.raises(parsec.ParseError):
            helpers.negativeInteger().parse("22")


class TestDecimal:
    def test_match_positive(self):
        assert helpers.decimal().parse("4.25") == 4.25

    def test_match_negative(self):
        assert helpers.decimal().parse("-5.36") == -5.36

    def test_match_negative_zero(self):
        assert helpers.decimal().parse("-0.705") == -0.705

    def test_partial(self):
        assert helpers.decimal().parse("10.05x") == 10.05

    def test_nomatch(self):
        with pytest.raises(parsec.ParseError):
            helpers.decimal().parse("-4")
