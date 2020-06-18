import math
from dataclasses import dataclass
from typing import Tuple, List
from .parsec import *
from .helpers import *


@generate
def JointParser():
    name = yield spaces() >> quoted() << spaces1()
    parentIndex = yield integer() << spaces1()
    (x, y, z) = yield parens(sequence(number(), 3)) << spaces()
    (qx, qy, qz) = yield parens(sequence(number(), 3)) << spaces()
    comment = yield slashyComment() ^ spaces()
    return Joint(name=name, parentIndex=parentIndex, position=(x, y, z), orientation=(qx, qy, qz), comment=comment)


@generate
def VertParser():
    index = yield spaces() >> keyValue('vert', integer()) << spaces1()
    (u, v) = yield parens(sepBy1(number(), spaces1())) << spaces1()
    weightStart = yield integer() << spaces1()
    weightCount = yield integer() << spaces()
    return Vert(index=index, uv=(u, v), weightStart=weightStart, weightCount=weightCount)


@generate
def WeightParser():
    index = yield spaces() >> keyValue('weight', integer()) << spaces1()
    jointIndex = yield integer() << spaces1()
    bias = yield number() << spaces1()
    (x, y, z) = yield parens(sepBy1(number(), spaces1())) << spaces()
    return Weight(index=index, jointIndex=jointIndex, bias=bias, position=(x, y, z))


@generate
def TriParser():
    index = yield spaces() >> keyValue('tri', integer()) << spaces1()
    (v1, v2, v3) = yield sepBy1(integer(), spaces1()) << spaces()
    return Tri(index=index, verts=(v1, v2, v3))


@generate
def MeshParser():
    comment = yield string('mesh') >> spaces1() >> string('{') >> slashyComment() << spaces1()
    shader = yield keyValue('shader', quoted()) << spaces1()
    numverts = yield keyValue('numverts', integer()) << spaces()
    verts = yield many1(VertParser) << spaces()
    assert len(verts) == numverts
    numtris = yield keyValue('numtris', integer()) << spaces()
    tris = yield many1(TriParser) << spaces()
    assert len(tris) == numtris
    numweights = yield keyValue('numweights', integer()) << spaces()
    weights = yield many1(WeightParser) << spaces() << string('}') << spaces()
    assert len(weights) == numweights
    return Mesh(comment=comment, shader=shader, verts=verts, tris=tris, weights=weights)


@generate
def Md5MeshParser():
    version = yield keyValue('MD5Version', integer()) << spaces1()
    commandline = yield keyValue('commandline', quoted()) << spaces1()
    numJoints = yield keyValue('numJoints', integer()) << spaces1()
    numMeshes = yield keyValue('numMeshes', integer()) << spaces1()
    joints = yield keyValue('joints', block(many1(JointParser)))
    assert len(joints) == numJoints
    meshes = yield many1(MeshParser) << spaces()
    assert len(meshes) == numMeshes
    return Md5Mesh(version=version, commandline=commandline, joints=joints, meshes=meshes)


@dataclass(frozen=True)
class Joint:
    name: str
    parentIndex: int
    position: Tuple[float, float, float]
    orientation: Tuple[float, float, float]
    comment: str

    @classmethod
    def parse(cls, data: str):
        return JointParser.parse(data)

    @property
    def to_string(self) -> str:
        (x, y, z) = [formatNumber(c) for c in self.position]
        (qx, qy, qz) = [formatNumber(c) for c in self.orientation]
        return f'"{self.name}"\t{self.parentIndex} ( {x} {y} {z} ) ( {qx} {qy} {qz} )\t\t//{self.comment}'


@dataclass(frozen=True)
class Vert:
    index: int
    uv: Tuple[float, float]
    weightStart: int
    weightCount: int

    @classmethod
    def parse(cls, data: str):
        return VertParser.parse(data)

    @property
    def to_string(self) -> str:
        (u, v) = [formatNumber(c) for c in self.uv]
        return f'vert {self.index} ( {u} {v} ) {self.weightStart} {self.weightCount}'

    @property
    def weightEnd(self) -> int:
        return self.weightStart + self.weightCount


@dataclass(frozen=True)
class Tri:
    index: int
    verts: Tuple[int, int, int]

    @classmethod
    def parse(cls, data: str):
        return TriParser.parse(data)

    @property
    def to_string(self) -> str:
        (v1, v2, v3) = self.verts
        return f'tri {self.index} {v1} {v2} {v3}'


@dataclass(frozen=True)
class Weight:
    index: int
    jointIndex: int
    bias: float
    position: Tuple[float, float, float]

    @classmethod
    def parse(cls, data: str):
        return WeightParser.parse(data)

    @property
    def to_string(self) -> str:
        (x, y, z) = [formatNumber(c) for c in self.position]
        return f'weight {self.index} {self.jointIndex} {formatNumber(self.bias)} ( {x} {y} {z} )'


@dataclass(frozen=True)
class Mesh:
    comment: str
    shader: str
    verts: List[Vert]
    tris: List[Tri]
    weights: List[Weight]

    @classmethod
    def parse(cls, data: str):
        return MeshParser.parse(data)

    @property
    def to_string(self) -> str:
        comment = f'\t//{self.comment}\n'
        shader = f'\tshader "{self.shader}"\n\n'

        numverts = f'\tnumverts {len(self.verts)}'
        verts = mkString(
            [x.to_string for x in self.verts],
            start='\n\t', sep='\n\t', end='\n\n')

        numtris = f'\tnumtris {len(self.tris)}'
        tris = mkString(
            [x.to_string for x in self.tris],
            start='\n\t', sep='\n\t', end='\n\n')

        numweights = f'\tnumweights {len(self.weights)}'
        weights = mkString(
            [x.to_string for x in self.weights],
            start='\n\t', sep='\n\t', end='\n')

        return 'mesh {\n' + comment + shader + numverts + verts + numtris + tris + numweights + weights + '}\n'


@dataclass(frozen=True)
class Md5Mesh:
    version: int
    commandline: str
    joints: List[Joint]
    meshes: List[Mesh]

    @classmethod
    def parse(cls, data: str):
        return Md5MeshParser.parse(data)

    @property
    def to_string(self) -> str:
        version = f'MD5Version {self.version}\n'
        commandline = f'commandline "{self.commandline}"\n\n'

        numJoints = f'numJoints {len(self.joints)}\n'
        numMeshes = f'numMeshes {len(self.meshes)}\n\n'

        joints = mkString(
            [x.to_string for x in self.joints],
            start='joints {\n\t', sep='\n\t', end='\n}\n\n')

        meshes = mkString([x.to_string for x in self.meshes], sep='\n')

        return version + commandline + numJoints + numMeshes + joints + meshes
