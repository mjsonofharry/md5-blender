from typing import List
from .parsec import *


def concatFn(x: List):
    '''Convert list to string'''
    return ''.join(x)


def mkString(x: List[str], start: str = '', sep: str = '', end: str = ''):
    '''Join a list of strings with optional start, separator, and end strings'''
    return start + sep.join(x) + end


def formatNumber(number: float) -> str:
    rounded = round(number, 10)
    truncated = int(rounded)
    if (float(truncated) == rounded):
        return str(truncated)
    else:
        return f'{rounded:.10f}'


def whitespace():
    '''Parse whitespace only'''
    return regex(r'\s*', re.MULTILINE)


def notWhitespace():
    '''Parse until whitespace'''
    return regex(r'[^\s]+')


def toLineEnd():
    '''Parse to end of current line'''
    return regex(r'[^\n]+')


def endOfLine():
    '''Parse end of line'''
    return regex(r'[\n]')


def block(p):
    '''Apply `p` between `{` and `}`'''
    return spaces() >> string('{') >> spaces() >> p << spaces() << string('}') << spaces()


def slashyComment():
    '''Parse an optional comment in the form of `// this is a comment`'''
    return ((spaces() >> string('//') >> toLineEnd()) ^ spaces().parsecmap(lambda xs: '')).parsecmap(concatFn)


def quoted():
    '''Parse text between double-quotes'''
    return string('"') >> regex(r'[^\\"]+') << string('"')


def spaces1():
    '''Parse at least 1 whitespace character'''
    return space() >> spaces()


def parens(p):
    '''Apply `p` between parentheses'''
    return string('(') >> spaces() >> p << spaces() << string(')')


def keyValue(key: str, p):
    '''Apply `p` to the value in the context of `key value`'''
    return string(key) >> spaces1() >> p


def numberString():
    '''Parse 1 or more digits'''
    return many1(digit()).parsecmap(concatFn)


def positiveInteger():
    '''Parse a positive integer'''
    return numberString().parsecmap(int)


def negativeInteger():
    '''Parse a negative integer'''
    return string('-') >> positiveInteger().parsecmap(lambda x: -x)


def integer():
    '''Parse any integer'''
    return negativeInteger() ^ positiveInteger()


def decimal():
    '''Parse any decimal'''
    @generate
    def p():
        lhs = yield ((string('-') + numberString()).parsecmap(concatFn) ^ numberString())
        rhs = yield string('.') >> numberString()
        return float(f'{lhs}.{rhs}')
    return p


def number():
    '''Parse any decimal or integer'''
    return decimal() ^ integer()


def sequence(p, n):
    '''Parse `n` occurrences of `p` with space delimiters'''
    return count(p << spaces1(), n)