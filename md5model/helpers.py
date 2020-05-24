from .parsec import *


def concatFn(x):
    return ''.join(x)


def numberString():
    return many1(digit()).parsecmap(concatFn)


def positiveInteger():
    return numberString().parsecmap(int)


def negativeInteger():
    return string('-') >> positiveInteger().parsecmap(lambda x: -x)


def integer():
    return negativeInteger() ^ positiveInteger()


def decimal():
    @generate
    def p():
        lhs = yield ((string('-') + numberString()).parsecmap(concatFn) ^ numberString())
        rhs = yield string('.') >> numberString()
        return float(f'{lhs}.{rhs}')
    return p


def number():
    return decimal() ^ integer()
