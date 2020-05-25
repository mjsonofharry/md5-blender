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
            (qx, qy, qz) = yield parens(sepBy1(number(), spaces1()))
            comment = yield slashyComment()
            return cls(name=name, parentIndex=parentIndex, position=(x, y, z), orientation=(qx, qy, qz), comment=comment)
        return p

    @classmethod
    def parse(cls, data: str):
        return cls.parser().parse(data)

    def to_string(self):
        (x, y, z) = self.position
        (qx, qy, qz) = self.orientation
        return f'"{self.name}"\t{self.parentIndex} ( {x} {y} {z} ) ( {qx} {qy} {qz} )\t\t// {self.comment}'


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
        return f'vert {self.index} ( {u} {v} ) {self.weightStart} {self.weightCount}'


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
        return f'tri {self.index} {v1} {v2} {v3}'


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
        return f'weight {self.index} {self.jointIndex} {self.bias} ( {x} {y} {z} )'


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
        comment = f'\t// {self.comment}\n'
        shader = f'\tshader "{self.shader}"\n\n'

        numverts = f'\tnumverts {len(self.verts)}'
        verts = mkString([x.to_string() for x in self.verts],
                         start='\n\t', sep='\n\t', end='\n\n')

        numtris = f'\tnumtris {len(self.tris)}'
        tris = mkString([x.to_string() for x in self.tris],
                        start='\n\t', sep='\n\t', end='\n\n')

        numweights = f'\tnumweights {len(self.weights)}'
        weights = mkString([x.to_string() for x in self.weights],
                           start='\n\t', sep='\n\t', end='\n')

        return 'mesh {\n' + comment + shader + numverts + verts + numtris + tris + numweights + weights + '}\n'


class Md5Mesh:
    def __init__(self, version: int, commandline: str, joints: List[Joint], meshes: List[Mesh]):
        self.version = version
        self.commandline = commandline
        self.joints = joints
        self.meshes = meshes

    @classmethod
    def parser(cls):
        @generate
        def p():
            version = yield keyValue('MD5Version', integer()) << spaces1()
            commandline = yield keyValue('commandline', quoted()) << spaces1()
            numJoints = yield keyValue('numJoints', integer()) << spaces1()
            numMeshes = yield keyValue('numMeshes', integer()) << spaces1()
            joints = yield string('joints') >> spaces1() >> string('{') >> spaces() >> many1(Joint.parser()) << spaces() << string('}') << spaces1()
            assert len(joints) == numJoints
            meshes = yield many1(Mesh.parser()) << spaces()
            assert len(meshes) == numMeshes
            return Md5Mesh(version=version, commandline=commandline, joints=joints, meshes=meshes)
        return p

    @classmethod
    def parse(cls, data: str):
        return cls.parser().parse(data)

    def to_string(self):
        version = f'MD5Version {self.version}\n'
        commandline = f'commandline "{self.commandline}"\n\n'

        numJoints = f'numJoints {len(self.joints)}\n'
        numMeshes = f'numMeshes {len(self.meshes)}\n\n'

        joints = mkString([x.to_string() for x in self.joints],
                          start='joints {\n\t', sep='\n\t', end='\n}\n\n')

        meshes = mkString([x.to_string() for x in self.meshes], sep='\n')

        return version + commandline + numJoints + numMeshes + joints + meshes
