from typing import Tuple, List
from md5model.parsec import *
from md5model.helpers import *


class Joint:
    def __init__(self, name: str, parentIndex: int, position: Tuple[float, float, float], orientation: Tuple[float, float, float, float], comment: str):
        self.name = name
        self.parentIndex = parentIndex
        self.position = position
        self.orientation = orientation
        self.comment = comment

    @classmethod
    def parse(cls, data: str):
        @generate
        def parser():
            name = yield spaces1() >> quoted() << spaces1()
            parentIndex = yield integer() << spaces1()
            (x, y, z) = yield parens(sepBy1(number(), spaces1())) << spaces1()
            (qx, qy, qz) = yield parens(sepBy1(number(), spaces1())) << spaces1()
            comment = yield string('//') >> spaces1() >> (many(letter())).parsecmap(concatFn)
            return cls(name=name, parentIndex=parentIndex, position=(x, y, z), orientation=(qx, qy, qz), comment=comment)
        return parser.parse(data)

    def to_string(self):
        (x, y, z) = self.position
        (qx, qy, qz) = self.orientation
        return f'\t"{self.name}"\t{self.parentIndex} ( {x} {y} {z} ) ( {qx} {qy} {qz} )\t\t// {self.comment}'


class Vert:
    def __init__(self, index: int, uv: Tuple[float, float], weightStart: int, weightCount: int):
        self.index = index
        self.uv = uv
        self.weightStart = weightStart
        self.weightCount = weightCount

    @classmethod
    def parse(cls, data: str):
        @generate
        def parser():
            index = yield spaces1() >> keyValue('vert', integer()) << spaces1()
            (u, v) = yield parens(sepBy1(number(), spaces1())) << spaces1()
            weightStart = yield integer() << spaces1()
            weightCount = yield integer()
            return cls(index=index, uv=(u, v), weightStart=weightStart, weightCount=weightCount)
        return parser.parse(data)

    def to_string(self):
        (u, v) = self.uv
        return f'\tvert {self.index} ( {u} {v} ) {self.weightStart} {self.weightCount}'


class Tri:
    def __init__(self, index: int, verts: Tuple[int, int, int]):
        self.index = index
        self.verts = verts

    @classmethod
    def parse(cls, data: str):
        @generate
        def parser():
            index = yield spaces1() >> keyValue('tri', integer()) << spaces1()
            (v1, v2, v3) = yield sepBy1(integer(), spaces1())
            return cls(index=index, verts=(v1, v2, v3))
        return parser.parse(data)

    def to_string(self):
        (v1, v2, v3) = self.verts
        return f'\ttri {self.index} {v1} {v2} {v3}'


class Weight:
    def __init__(self, index: int, jointIndex: int, bias: float, position: Tuple[float, float, float]):
        self.index = index
        self.jointIndex = jointIndex
        self.bias = bias
        self.position = position

    @classmethod
    def parse(cls, data: str):
        @generate
        def parser():
            index = yield spaces1() >> keyValue('weight', integer()) << spaces1()
            jointIndex = yield integer() << spaces1()
            bias = yield number() << spaces1()
            (x, y, z) = yield parens(sepBy1(number(), spaces1()))
            return cls(index=index, jointIndex=jointIndex, bias=bias, position=(x, y, z))
        return parser.parse(data)

    def to_string(self):
        (x, y, z) = self.position
        return f'\tweight {self.index} {self.jointIndex} {self.bias} ( {x} {y} {z} )'


class Mesh:
    def __init__(self, comment: str, shader: str, verts: List[Vert], tris: List[Tri], weights):
        self.comment = comment
        self.shader = shader
        self.verts = verts
        self.tris = tris
        self.weights = weights
