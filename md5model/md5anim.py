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
            return None
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
            return None
        return p
    
    @classmethod
    def parse(cls, data: str):
        return cls.parser().parse(data)

    def to_string(self):
        return ''


class Frame:
    def __init__(self, values: List[float]):
        self.values = values

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
