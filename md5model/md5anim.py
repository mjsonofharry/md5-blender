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
        return ''


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
        return ''


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
        return ''


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
        return ''


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
        return ''


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
        return ''


class Md5Anim:
    def __init__(self, version: int, commandline: str, frameRate: int, numAnimatedComponents: int, hierarchies: List[Hierarchy], bounds: List[Bound], baseframe: Frame, frames: List[Frame]):
        self.version = version
        self.commandline = commandline
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
            return None
        return p

    @classmethod
    def parse(cls, data: str):
        return cls.parser().parse(data)

    def to_string(self):
        return ''
