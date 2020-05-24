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
            name = yield spaces() >> string('"') >> regex(r'[^\\"]+') << string('"')
            parentIndex = yield spaces() >> integer()
            x = yield spaces() >> string('(') >> spaces() >> number()
            y = yield space() >> number()
            z = yield space() >> number() << spaces() << string(')')
            position = (x, y, z)
            qx = yield spaces() >> string('(') >> spaces() >> number()
            qy = yield space() >> number()
            qz = yield space() >> number() << spaces() << string(')')
            orientation = (qx, qy, qz)
            comment = yield spaces() >> string('//') >> spaces() >> (many(letter())).parsecmap(concatFn)
            return cls(name=name, parentIndex=parentIndex, position=position, orientation=orientation, comment=comment)
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
            index = yield spaces() >> string("vert") >> space() >> integer()
            u = yield spaces() >> string('(') >> spaces() >> number() << space()
            v = yield number() << spaces() << string(')') << spaces()
            uv = (u, v)
            weightStart = yield integer() << spaces()
            weightCount = yield integer()
            return cls(index=index, uv=uv, weightStart=weightStart, weightCount=weightCount)
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
            index = yield spaces() >> string("tri") >> spaces() >> integer()
            v1 = yield spaces() >> integer()
            v2 = yield spaces() >> integer()
            v3 = yield spaces() >> integer()
            verts = (v1, v2, v3)
            return cls(index=index, verts=verts)
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
            index = yield spaces() >> string("weight") >> spaces() >> integer()
            jointIndex = yield spaces() >> integer()
            bias = yield spaces() >> number()
            x = yield spaces() >> string('(') >> spaces() >> number()
            y = yield spaces() >> number()
            z = yield spaces() >> number() << spaces() << string(')')
            position = (x, y, z)
            return cls(index=index, jointIndex=jointIndex, bias=bias, position=position)
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
