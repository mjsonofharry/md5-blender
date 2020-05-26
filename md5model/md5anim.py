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
    (minX, minY, minZ) = yield spaces() >> parens(sepBy1(number(), spaces1())) << spaces()
    (maxX, maxY, maxZ) = yield spaces() >> parens(sepBy1(number(), spaces1())) << spaces()
    return Bound(min=(minX, minY, minZ), max=(maxX, maxY, maxZ))


@generate
def BaseFramePartParser():
    (x, y, z) = yield spaces() >> parens(sepBy1(number(), spaces1())) << spaces()
    (qx, qy, qz) = yield spaces() >> parens(sepBy1(number(), spaces1())) << spaces()
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


class Hierarchy:
    def __init__(self, jointName: str, parentJointIndex: int, flags: int, startIndex: int, comment: str):
        self.jointName = jointName
        self.parentJointIndex = parentJointIndex
        self.flags = flags
        self.startIndex = startIndex
        self.comment = comment

    @classmethod
    def parse(cls, data: str):
        return HierarchyParser.parse(data)

    def to_string(self):
        return f'"{self.jointName}"\t{self.parentJointIndex} {self.flags} {self.startIndex}\t//{self.comment}'


class Bound:
    def __init__(self, min: Tuple[float, float, float], max: Tuple[float, float, float]):
        self.min = min
        self.max = max

    @classmethod
    def parse(cls, data: str):
        return BoundParser.parse(data)

    def to_string(self):
        (minX, minY, minZ) = self.min
        (maxX, maxY, maxZ) = self.max
        return f'( {minX} {minY} {minZ} ) ( {maxX} {maxY} {maxZ} )'


class BaseFramePart:
    def __init__(self, position: Tuple[float, float, float], orientation: Tuple[float, float, float]):
        self.position = position
        self.orientation = orientation

    @classmethod
    def parse(cls, data: str):
        return BaseFramePartParser.parse(data)

    def to_string(self):
        (x, y, z) = self.position
        (qx, qy, qz) = self.orientation
        return f'( {x} {y} {z} ) ( {qx} {qy} {qz} )'


class BaseFrame:
    def __init__(self, parts: List[BaseFramePart]):
        self.parts = parts

    @classmethod
    def parse(cls, data: str):
        return BaseFrameParser.parse(data)

    def to_string(self):
        parts = [x.to_string() for x in self.parts]
        return mkString(parts, start='baseframe {\n\t', sep='\n\t', end='\n}\n')


class FramePart:
    def __init__(self, values: List[float]):
        self.values = values

    @classmethod
    def parse(cls, data: str):
        return FramePartParser.parse(data)

    def to_string(self):
        return mkString([str(x) for x in self.values], sep=' ')


class Frame:
    def __init__(self, index: int, parts: List[FramePart]):
        self.index = index
        self.parts = parts

    @classmethod
    def parse(cls, data: str):
        return FrameParser.parse(data)

    def to_string(self):
        parts = [x.to_string() for x in self.parts]
        return mkString(parts, start=f'frame {self.index} ' + '{\n\t', sep='\n\t', end='\n}\n')


class Md5Anim:
    def __init__(self, version: int, commandline: str, numJoints: int, frameRate: int, numAnimatedComponents: int, hierarchies: List[Hierarchy], bounds: List[Bound], baseframe: Frame, frames: List[Frame]):
        self.version = version
        self.commandline = commandline
        self.numJoints = numJoints
        self.frameRate = frameRate
        self.numAnimatedComponents = numAnimatedComponents
        self.hierarchies = hierarchies
        self.bounds = bounds
        self.baseframe = baseframe
        self.frames = frames

    @classmethod
    def parse(cls, data: str):
        return Md5AnimParser.parse(data)

    def to_string(self):
        version = f'MD5Version {self.version}\n'
        commandline = f'commandline "{self.commandline}"\n\n'

        numFrames = f'numFrames {len(self.frames)}\n'
        numJoints = f'numJoints {self.numJoints}\n'
        frameRate = f'frameRate {self.frameRate}\n'
        numAnimatedComponents = f'numAnimatedComponents {self.numAnimatedComponents}\n\n'

        hierarchies = mkString([x.to_string() for x in self.hierarchies],
                               start='hierarchy {\n\t', sep='\n\t', end='\n}\n\n')

        bounds = mkString([x.to_string() for x in self.bounds],
                          start='bounds {\n\t', sep='\n\t', end='\n}\n\n')

        baseframe = f'{self.baseframe.to_string()}\n'

        frames = mkString([x.to_string() for x in self.frames], sep='\n')

        return version + commandline + numFrames + numJoints + frameRate + numAnimatedComponents + hierarchies + bounds + baseframe + frames
