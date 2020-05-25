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
    def parser(cls):
        @generate
        def p():
            name = yield spaces() >> quoted() << spaces1()
            parentIndex = yield integer() << spaces1()
            (x, y, z) = yield parens(sepBy1(number(), spaces1())) << spaces1()
            (qx, qy, qz) = yield parens(sepBy1(number(), spaces1())) << spaces1()
            comment = yield keyValue('//', (many(letter())).parsecmap(concatFn))
            return cls(name=name, parentIndex=parentIndex, position=(x, y, z), orientation=(qx, qy, qz), comment=comment)
        return p

    @classmethod
    def parse(cls, data: str):
        return cls.parser().parse(data)

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
    def parser(cls):
        @generate
        def p():
            index = yield spaces() >> keyValue('vert', integer()) << spaces1()
            (u, v) = yield parens(sepBy1(number(), spaces1())) << spaces1()
            weightStart = yield integer() << spaces1()
            weightCount = yield integer() << spaces()
            return cls(index=index, uv=(u, v), weightStart=weightStart, weightCount=weightCount)
        return p

    @classmethod
    def parse(cls, data: str):
        return cls.parser().parse(data)

    def to_string(self):
        (u, v) = self.uv
        return f'\tvert {self.index} ( {u} {v} ) {self.weightStart} {self.weightCount}'


class Tri:
    def __init__(self, index: int, verts: Tuple[int, int, int]):
        self.index = index
        self.verts = verts

    @classmethod
    def parser(cls):
        @generate
        def p():
            index = yield spaces() >> keyValue('tri', integer()) << spaces1()
            (v1, v2, v3) = yield sepBy1(integer(), spaces1()) << spaces()
            return cls(index=index, verts=(v1, v2, v3))
        return p

    @classmethod
    def parse(cls, data: str):
        return cls.parser().parse(data)

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
    def parser(cls):
        @generate
        def p():
            index = yield spaces() >> keyValue('weight', integer()) << spaces1()
            jointIndex = yield integer() << spaces1()
            bias = yield number() << spaces1()
            (x, y, z) = yield parens(sepBy1(number(), spaces1())) << spaces()
            return cls(index=index, jointIndex=jointIndex, bias=bias, position=(x, y, z))
        return p

    @classmethod
    def parse(cls, data: str):
        return cls.parser().parse(data)

    def to_string(self):
        (x, y, z) = self.position
        return f'\tweight {self.index} {self.jointIndex} {self.bias} ( {x} {y} {z} )'


class Mesh:
    def __init__(self, comment: str, shader: str, verts: List[Vert], tris: List[Tri], weights: List[Weight]):
        self.comment = comment
        self.shader = shader
        self.verts = verts
        self.tris = tris
        self.weights = weights

    @classmethod
    def parser(cls):
        @generate
        def p():
            comment = yield string('mesh') >> spaces1() >> string('{') >> spaces1() >> keyValue('//', toLineEnd()) << spaces1()
            shader = yield keyValue('shader', quoted()) << spaces1()
            numverts = yield keyValue('numverts', integer()) << spaces()
            verts = yield many1(Vert.parser()) << spaces()
            assert len(verts) == numverts
            numtris = yield keyValue('numtris', integer()) << spaces()
            tris = yield many1(Tri.parser()) << spaces()
            assert len(tris) == numtris
            numweights = yield keyValue('numweights', integer()) << spaces()
            weights = yield many1(Weight.parser()) << spaces() << string('}') << spaces()
            assert len(weights) == numweights
            return Mesh(comment=comment, shader=shader, verts=verts, tris=tris, weights=weights)
        return p

    @classmethod
    def parse(cls, data: str):
        return cls.parser().parse(data)

    def to_string(self):
        return ''
