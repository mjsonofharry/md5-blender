from typing import Tuple, List
from md5model.parsec import *
from md5model.helpers import *


class Hierarchy:
    def __init__(self, jointName: str, parentJointIndex: int, flags: int, startIndex: int, comment: str):
        self.jointName = jointName
        self.parentJointIndex = parentJointIndex
        self.flags = flags
        self.startIndex = startIndex
        self.comment = comment

    @classmethod
    def parser(cls):
        @generate
        def p():
            jointName = yield spaces() >> quoted() << spaces1()
            parentJointIndex = yield integer() << spaces1()
            flags = yield integer() << spaces1()
            startIndex = yield integer()
            comment = yield slashyComment()
            return cls(jointName=jointName, parentJointIndex=parentJointIndex, flags=flags, startIndex=startIndex, comment=comment)
        return p

    @classmethod
    def parse(cls, data: str):
        return cls.parser().parse(data)

    def to_string(self):
        return f'"{self.jointName}"\t{self.parentJointIndex} {self.flags} {self.startIndex}\t//{self.comment}'


class Bound:
    def __init__(self, min: Tuple[float, float, float], max: Tuple[float, float, float]):
        self.min = min
        self.max = max

    @classmethod
    def parser(cls):
        @generate
        def p():
            (minX, minY, minZ) = yield spaces() >> parens(sepBy1(number(), spaces1())) << spaces()
            (maxX, maxY, maxZ) = yield spaces() >> parens(sepBy1(number(), spaces1())) << spaces()
            return cls(min=(minX, minY, minZ), max=(maxX, maxY, maxZ))
        return p

    @classmethod
    def parse(cls, data: str):
        return cls.parser().parse(data)

    def to_string(self):
        (minX, minY, minZ) = self.min
        (maxX, maxY, maxZ) = self.max
        return f'( {minX} {minY} {minZ} ) ( {maxX} {maxY} {maxZ} )'


class BaseFramePart:
    def __init__(self, position: Tuple[float, float, float], orientation: Tuple[float, float, float]):
        self.position = position
        self.orientation = orientation

    @classmethod
    def parser(cls):
        @generate
        def p():
            (x, y, z) = yield spaces() >> parens(sepBy1(number(), spaces1())) << spaces()
            (qx, qy, qz) = yield spaces() >> parens(sepBy1(number(), spaces1())) << spaces()
            return cls(position=(x, y, z), orientation=(qx, qy, qz))
        return p

    @classmethod
    def parse(cls, data: str):
        return cls.parser().parse(data)

    def to_string(self):
        (x, y, z) = self.position
        (qx, qy, qz) = self.orientation
        return f'( {x} {y} {z} ) ( {qx} {qy} {qz} )'


class BaseFrame:
    def __init__(self, parts: List[BaseFramePart]):
        self.parts = parts

    @classmethod
    def parser(cls):
        @generate
        def p():
            parts = yield string('baseframe') >> spaces() >> string('{') >> spaces() >> many1(BaseFramePart.parser()) << spaces() << string('}')
            return cls(parts=parts)
        return p

    @classmethod
    def parse(cls, data: str):
        return cls.parser().parse(data)

    def to_string(self):
        parts = [x.to_string() for x in self.parts]
        return mkString(parts, start='baseframe {\n\t', sep='\n\t', end='\n}\n')


class FramePart:
    def __init__(self, values: List[float]):
        self.values = values

    @classmethod
    def parser(cls):
        @generate
        def p():
            values = yield spaces() >> sepBy1(number(), space())
            return cls(values=values)
        return p

    @classmethod
    def parse(cls, data: str):
        return cls.parser().parse(data)

    def to_string(self):
        return mkString([str(x) for x in self.values], sep=' ')


class Frame:
    def __init__(self, index: int, parts: List[FramePart]):
        self.index = index
        self.parts = parts

    @classmethod
    def parser(cls):
        @generate
        def p():
            index = yield keyValue('frame', integer()) << spaces() << string('{') << spaces()
            parts = yield sepBy1(FramePart.parser(), spaces1()) << spaces() << string('}') << spaces()
            return cls(index=index, parts=parts)
        return p

    @classmethod
    def parse(cls, data: str):
        return cls.parser().parse(data)

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
    def parser(cls):
        @generate
        def p():
            version = yield keyValue('MD5Version', integer()) << spaces1()
            commandline = yield keyValue('commandline', quoted()) << spaces1()
            numFrames = yield keyValue('numFrames', integer()) << spaces1()
            numJoints = yield keyValue('numJoints', integer()) << spaces1()
            frameRate = yield keyValue('frameRate', integer()) << spaces1()
            numAnimatedComponents = yield keyValue('numAnimatedComponents', integer()) << spaces1()
            hierarchies = yield string('hierarchy') >> spaces1() >> string('{') >> spaces() >> many1(Hierarchy.parser()) << spaces() << string('}') << spaces1()
            bounds = yield string('bounds') >> spaces1() >> string('{') >> spaces() >> many1(Bound.parser()) << spaces() << string('}') << spaces1()
            baseframe = yield BaseFrame.parser() << spaces1()
            frames = yield many1(Frame.parser()) << spaces()
            assert len(frames) == numFrames
            return cls(version=version, commandline=commandline, numJoints=numJoints, frameRate=frameRate, numAnimatedComponents=numAnimatedComponents, hierarchies=hierarchies, bounds=bounds, baseframe=baseframe, frames=frames)
        return p

    @classmethod
    def parse(cls, data: str):
        return cls.parser().parse(data)

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
