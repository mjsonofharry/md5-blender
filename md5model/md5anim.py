from dataclasses import dataclass
from typing import Tuple, List
from .parsec import *
from .helpers import *


@generate
def HierarchyParser():
    jointName = yield spaces() >> quoted() << spaces1()
    parentJointIndex = yield integer() << spaces1()
    flags = yield integer() << spaces1()
    startIndex = yield integer()
    comment = yield slashyComment()
    return Hierarchy(jointName=jointName, parentJointIndex=parentJointIndex, flags=flags, startIndex=startIndex, comment=comment)


@generate
def BoundParser():
    (minX, minY, minZ) = yield spaces() >> parens(sequence(number(), 3) << spaces()) << spaces()
    (maxX, maxY, maxZ) = yield spaces() >> parens(sequence(number(), 3) << spaces()) << spaces()
    return Bound(min=(minX, minY, minZ), max=(maxX, maxY, maxZ))


@generate
def BaseFramePartParser():
    (x, y, z) = yield spaces() >> parens(sequence(number(), 3) << spaces()) << spaces()
    (qx, qy, qz) = yield spaces() >> parens(sequence(number(), 3) << spaces()) << spaces()
    return BaseFramePart(position=(x, y, z), orientation=(qx, qy, qz))


@generate
def BaseFrameParser():
    parts = yield keyValue('baseframe', block(many1(BaseFramePartParser)))
    return BaseFrame(parts=parts)


@generate
def FramePartParser():
    values = yield spaces() >> sepBy1(number(), space())
    return FramePart(values=values)


@generate
def FrameParser():
    index = yield keyValue('frame', integer())
    parts = yield block(sepBy1(FramePartParser, spaces1()))
    return Frame(index=index, parts=parts)


@generate
def Md5AnimParser():
    version = yield keyValue('MD5Version', integer()) << spaces1()
    commandline = yield keyValue('commandline', quoted()) << spaces1()
    numFrames = yield keyValue('numFrames', integer()) << spaces1()
    numJoints = yield keyValue('numJoints', integer()) << spaces1()
    frameRate = yield keyValue('frameRate', integer()) << spaces1()
    numAnimatedComponents = yield keyValue('numAnimatedComponents', integer()) << spaces1()
    hierarchies = yield keyValue('hierarchy', block(many1(HierarchyParser)))
    bounds = yield keyValue('bounds', block(many1(BoundParser)))
    baseframe = yield BaseFrameParser << spaces()
    frames = yield many1(FrameParser) << spaces()
    assert len(frames) == numFrames
    return Md5Anim(version=version, commandline=commandline, numJoints=numJoints, frameRate=frameRate, numAnimatedComponents=numAnimatedComponents, hierarchies=hierarchies, bounds=bounds, baseframe=baseframe, frames=frames)


@dataclass(frozen=True)
class Hierarchy:
    jointName: str
    parentJointIndex: int
    flags: int
    startIndex: int
    comment: str

    @classmethod
    def parse(cls, data: str):
        return HierarchyParser.parse(data)

    @property
    def to_string(self) -> str:
        return f'"{self.jointName}"\t{self.parentJointIndex} {self.flags} {self.startIndex}\t//{self.comment}'

    @property
    def expanded_flags(self) -> List[bool]:
        return [True if x == '1' else False for x in str(bin(56))[2:].zfill(6)[::-1]]


@dataclass(frozen=True)
class Bound:
    min: Tuple[float, float, float]
    max: Tuple[float, float, float]

    @classmethod
    def parse(cls, data: str):
        return BoundParser.parse(data)

    @property
    def to_string(self) -> str:
        (minX, minY, minZ) = [formatNumber(c) for c in self.min]
        (maxX, maxY, maxZ) = [formatNumber(c) for c in self.max]
        return f'( {minX} {minY} {minZ} ) ( {maxX} {maxY} {maxZ} )'


@dataclass(frozen=True)
class BaseFramePart:
    position: Tuple[float, float, float]
    orientation: Tuple[float, float, float]

    @classmethod
    def parse(cls, data: str):
        return BaseFramePartParser.parse(data)

    @property
    def to_string(self) -> str:
        (x, y, z) = [formatNumber(c) for c in self.position]
        (qx, qy, qz) = [formatNumber(c) for c in self.orientation]
        return f'( {x} {y} {z} ) ( {qx} {qy} {qz} )'


@dataclass(frozen=True)
class BaseFrame:
    parts: List[BaseFramePart]

    @classmethod
    def parse(cls, data: str):
        return BaseFrameParser.parse(data)

    @property
    def to_string(self) -> str:
        parts = [x.to_string for x in self.parts]
        return mkString(parts, start='baseframe {\n\t', sep='\n\t', end='\n}\n')


@dataclass(frozen=True)
class FramePart:
    values: List[float]

    @classmethod
    def parse(cls, data: str):
        return FramePartParser.parse(data)

    @property
    def to_string(self) -> str:
        return mkString([formatNumber(x) for x in self.values], sep=' ')


@dataclass(frozen=True)
class Frame:
    index: int
    parts: List[FramePart]

    @classmethod
    def parse(cls, data: str):
        return FrameParser.parse(data)

    @property
    def to_string(self) -> str:
        parts = [x.to_string for x in self.parts]
        return mkString(parts, start=f'frame {self.index} ' + '{\n\t', sep='\n\t', end='\n}\n')


@dataclass(frozen=True)
class Md5Anim:
    version: int
    commandline: str
    numJoints: int
    frameRate: int
    numAnimatedComponents: int
    hierarchies: List[Hierarchy]
    bounds: List[Bound]
    baseframe: Frame
    frames: List[Frame]

    @classmethod
    def parse(cls, data: str):
        return Md5AnimParser.parse(data)

    @property
    def to_string(self) -> str:
        version = f'MD5Version {self.version}\n'
        commandline = f'commandline "{self.commandline}"\n\n'

        numFrames = f'numFrames {len(self.frames)}\n'
        numJoints = f'numJoints {self.numJoints}\n'
        frameRate = f'frameRate {self.frameRate}\n'
        numAnimatedComponents = f'numAnimatedComponents {self.numAnimatedComponents}\n\n'

        hierarchies = mkString(
            [x.to_string for x in self.hierarchies],
            start='hierarchy {\n\t', sep='\n\t', end='\n}\n\n')

        bounds = mkString(
            [x.to_string for x in self.bounds],
            start='bounds {\n\t', sep='\n\t', end='\n}\n\n')

        baseframe = f'{self.baseframe.to_string}\n'

        frames = mkString([x.to_string for x in self.frames], sep='\n')

        return version + commandline + numFrames + numJoints + frameRate + numAnimatedComponents + hierarchies + bounds + baseframe + frames
