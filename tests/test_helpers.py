import pytest
from .context import helpers
from .context import parsec


class TestHelpers:
    def test_quoted(self):
        assert helpers.quoted().parse('"hello world" this is not included') == 'hello world'

    def test_parens(self):
        assert helpers.parens(parsec.digit()).parse('(5) 32') == '5'

    def test_keyvalue(self):
        assert helpers.keyValue("key", parsec.letter()).parse('key A') == 'A'

    def test_numberstring(self):
        assert helpers.numberString().parse('12345') == '12345'


class TestSpaces1:
    def test_min(self):
        assert (helpers.spaces1() >> parsec.string(
            'yes')).parse(' yes') == 'yes'

    def test_extra(self):
        assert (helpers.spaces1() >> parsec.string(
            'yes')).parse('  yes') == 'yes'

    def test_insufficient(self):
        with pytest.raises(parsec.ParseError):
            (helpers.spaces1() >> parsec.string('no')).parse('no')


class TestSlashyComment:
    def test_nothing(self):
        assert helpers.slashyComment().parse('') == ''

    def test_spaces(self):
        assert helpers.slashyComment().parse('   ') == ''

    def test_slashes(self):
        assert helpers.slashyComment().parse('//') == ''

    def test_slasheswithspace(self):
        assert helpers.slashyComment().parse('// ') == ' '

    def test_slasheswithspaces(self):
        assert helpers.slashyComment().parse('  //  ') == '  '

    def test_comment(self):
        assert helpers.slashyComment().parse('//comment') == 'comment'

    def test_commentwithspaces(self):
        assert helpers.slashyComment().parse(' // comment') == ' comment'


class TestPositiveInteger:
    def test_match(self):
        assert helpers.positiveInteger().parse('12345') == 12345

    def test_partial(self):
        assert helpers.positiveInteger().parse('3.14') == 3

    def test_nomatch(self):
        with pytest.raises(parsec.ParseError):
            helpers.positiveInteger().parse('-86')


class TestNegativeInteger:
    def test_match(self):
        assert helpers.negativeInteger().parse('-10') == -10

    def test_partial(self):
        assert helpers.negativeInteger().parse('-51.1') == -51

    def test_nomatch(self):
        with pytest.raises(parsec.ParseError):
            helpers.negativeInteger().parse('22')


class TestDecimal:
    def test_match_positive(self):
        assert helpers.decimal().parse('4.25') == 4.25

    def test_match_negative(self):
        assert helpers.decimal().parse('-5.36') == -5.36

    def test_match_negative_zero(self):
        assert helpers.decimal().parse('-0.705') == -0.705

    def test_partial(self):
        assert helpers.decimal().parse('10.05x') == 10.05

    def test_nomatch(self):
        with pytest.raises(parsec.ParseError):
            helpers.decimal().parse('-4')
