import functools
import math
from typing import Tuple, List
from .implicits import implicits
from .parsec import *
from .helpers import *


@generate
def JointParser():
    name = yield spaces() >> quoted() << spaces1()
    parentIndex = yield integer() << spaces1()
    (x, y, z) = yield parens(sequence(number(), 3)) << spaces()
    (qx, qy, qz) = yield parens(sequence(number(), 3)) << spaces()
    comment = yield slashyComment()
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


def compute_w(qx: float, qy: float, qz: float) -> float:
    '''Compute `w` for a unit quaternion'''
    t = 1.0 - (qx * qx) - (qy * qy) - (qz * qz)
    if t < 0.0:
        return 0.0
    else:
        return -math.sqrt(t)


class Joint:
    def __init__(self, name: str, parentIndex: int, position: Tuple[float, float, float], orientation: Tuple[float, float, float, float], comment: str):
        self.name = name
        self.parentIndex = parentIndex
        self.position = position
        self.orientation = orientation
        self.comment = comment

    @classmethod
    def parse(cls, data: str):
        return JointParser.parse(data)

    @classmethod
    def from_bone(cls, bone, armature_object):
        parentIndex = [
            i for i, other_bone in enumerate(armature_object.data.bones)
            if bone.parent and other_bone.name == bone.parent.name
        ] + [-1]
        location, rotation, scale = bone.matrix_local.decompose()
        return cls(
            name=bone.name,
            parentIndex=parentIndex[0],
            position=location[:],
            orientation=(-rotation.normalized())[1:],
            comment=None
        )

    @property
    def to_string(self) -> str:
        (x, y, z) = self.position
        (qx, qy, qz) = self.orientation
        return f'"{self.name}"\t{self.parentIndex} ( {x} {y} {z} ) ( {qx} {qy} {qz} )\t\t//{self.comment}'

    @property
    @implicits('mathutils')
    @functools.lru_cache(maxsize=256)
    def matrix(self, mathutils):
        '''Get the translation matrix for the joint (returns `mathutils.Matrix`)'''
        translation = mathutils.Matrix.Translation(self.position)
        (qx, qy, qz) = self.orientation
        qw = compute_w(qx, qy, qz)
        q = -mathutils.Quaternion((qw, qx, qy, qz))
        return translation @ q.to_matrix().to_4x4()


class Vert:
    def __init__(self, index: int, uv: Tuple[float, float], weightStart: int, weightCount: int):
        self.index = index
        self.uv = uv
        self.weightStart = weightStart
        self.weightCount = weightCount

    @classmethod
    def parse(cls, data: str):
        return VertParser.parse(data)

    @property
    def to_string(self) -> str:
        (u, v) = self.uv
        return f'vert {self.index} ( {u} {v} ) {self.weightStart} {self.weightCount}'

    @property
    def weightEnd(self) -> int:
        return self.weightStart + self.weightCount


class Tri:
    def __init__(self, index: int, verts: Tuple[int, int, int]):
        self.index = index
        self.verts = verts

    @classmethod
    def parse(cls, data: str):
        return TriParser.parse(data)

    @property
    def to_string(self) -> str:
        (v1, v2, v3) = self.verts
        return f'tri {self.index} {v1} {v2} {v3}'


class Weight:
    def __init__(self, index: int, jointIndex: int, bias: float, position: Tuple[float, float, float]):
        self.index = index
        self.jointIndex = jointIndex
        self.bias = bias
        self.position = position

    @classmethod
    def parse(cls, data: str):
        return WeightParser.parse(data)

    @property
    def to_string(self) -> str:
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
    def parse(cls, data: str):
        return MeshParser.parse(data)

    @property
    def to_string(self) -> str:
        comment = f'\t//{self.comment}\n'
        shader = f'\tshader "{self.shader}"\n\n'

        numverts = f'\tnumverts {len(self.verts)}'
        verts = mkString([x.to_string for x in self.verts],
                         start='\n\t', sep='\n\t', end='\n\n')

        numtris = f'\tnumtris {len(self.tris)}'
        tris = mkString([x.to_string for x in self.tris],
                        start='\n\t', sep='\n\t', end='\n\n')

        numweights = f'\tnumweights {len(self.weights)}'
        weights = mkString([x.to_string for x in self.weights],
                           start='\n\t', sep='\n\t', end='\n')

        return 'mesh {\n' + comment + shader + numverts + verts + numtris + tris + numweights + weights + '}\n'


class Md5Mesh:
    def __init__(self, version: int, commandline: str, joints: List[Joint], meshes: List[Mesh]):
        self.version = version
        self.commandline = commandline
        self.joints = joints
        self.meshes = meshes

    @classmethod
    def parse(cls, data: str):
        return Md5MeshParser.parse(data)

    @property
    def to_string(self) -> str:
        version = f'MD5Version {self.version}\n'
        commandline = f'commandline "{self.commandline}"\n\n'

        numJoints = f'numJoints {len(self.joints)}\n'
        numMeshes = f'numMeshes {len(self.meshes)}\n\n'

        joints = mkString([x.to_string for x in self.joints],
                          start='joints {\n\t', sep='\n\t', end='\n}\n\n')

        meshes = mkString([x.to_string for x in self.meshes], sep='\n')

        return version + commandline + numJoints + numMeshes + joints + meshes

    @implicits('mathutils')
    def apply_weight_to_position(self, position, weight, mathutils):
        '''Adjust a vector using a single weight'''
        joint = self.joints[weight.jointIndex]
        adjust = ((joint.matrix @ mathutils.Vector(weight.position)) * weight.bias)
        return position + adjust

    @implicits('mathutils')
    def compute_global_vert_position(self, vert: Vert, mesh: Mesh, mathutils):
        '''Compute the global position of `vert` using weights from `mesh`'''
        weights = mesh.weights[vert.weightStart:vert.weightEnd]
        acc_init = mathutils.Vector((0.0, 0.0, 0.0))
        return functools.reduce(self.apply_weight_to_position, [acc_init, *weights])

    def vert_belongs_to_group(self, vert: Vert, mesh: Mesh, joint: Joint):
        '''Check if `vert` from `mesh` belongs to group associated with `joint`'''
        weights = mesh.weights[vert.weightStart:vert.weightEnd]
        names = [self.joints[weight.jointIndex].name for weight in weights]
        return joint.name in names
