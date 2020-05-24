from .parsec import *


def concatFn(x):
    '''Convert list to string'''
    return ''.join(x)


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
