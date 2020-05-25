import pytest
from .context import md5anim


class TestHierarchy:
    def test_parse_nocomment(self):
        text = '"origin"\t-1 3 0\t//'
        hierarchy = md5anim.Hierarchy.parse(text)
        assert hierarchy.jointName == 'origin'
        assert hierarchy.parentJointIndex == -1
        assert hierarchy.flags == 3
        assert hierarchy.startIndex == 0
        assert hierarchy.comment == ''

    def test_parse_noslashes(self):
        text = '"origin"\t-1 3 0\t'
        hierarchy = md5anim.Hierarchy.parse(text)
        assert hierarchy.jointName == 'origin'
        assert hierarchy.parentJointIndex == -1
        assert hierarchy.flags == 3
        assert hierarchy.startIndex == 0
        assert hierarchy.comment == ''

    def test_parse_comment(self):
        text = '"origin"\t-1 3 0\t//  ( Tx Ty )'
        hierarchy = md5anim.Hierarchy.parse(text)
        assert hierarchy.jointName == 'origin'
        assert hierarchy.parentJointIndex == -1
        assert hierarchy.flags == 3
        assert hierarchy.startIndex == 0
        assert hierarchy.comment == '  ( Tx Ty )'

    def test_parse_nontrivial(self):
        text = '"target"\t0 7 2\t// origin ( Tx Ty Tz )'
        hierarchy = md5anim.Hierarchy.parse(text)
        assert hierarchy.jointName == 'target'
        assert hierarchy.parentJointIndex == 0
        assert hierarchy.flags == 7
        assert hierarchy.startIndex == 2
        assert hierarchy.comment == ' origin ( Tx Ty Tz )'

    def test_parse_nontrivial_alternative(self):
        text = '"Rhand"\t9 56 24\t// Rloarm ( Qx Qy Qz )'
        hierarchy = md5anim.Hierarchy.parse(text)
        assert hierarchy.jointName == 'Rhand'
        assert hierarchy.parentJointIndex == 9
        assert hierarchy.flags == 56
        assert hierarchy.startIndex == 24
        assert hierarchy.comment == ' Rloarm ( Qx Qy Qz )'

    def test_tostring(self):
        text = '"Rhand"\t9 56 24\t// Rloarm ( Qx Qy Qz )'
        hierarchy = md5anim.Hierarchy.parse(text)
        assert hierarchy.to_string() == text


class TestBound:
    def test_parse(self):
        text = '( -29.7891 -29.7891 191.4453 ) ( 17.2734 22.4375 275.6641 )'
        bound = md5anim.Bound.parse(text)
        assert bound.min == (-29.7891, -29.7891, 191.4453)
        assert bound.max == (17.2734, 22.4375, 275.6641)

    def test_tostring(self):
        text = '( -29.7891 -29.7891 191.4453 ) ( 17.2734 22.4375 275.6641 )'
        bound = md5anim.Bound.parse(text)
        assert bound.to_string() == text


class TestBaseFramePart:
    def test_parse(self):
        text = '( -0.4375 242.2109 0.5078 ) ( -0.0326106442 -0.9382 0.0516446 )'
        baseFramePart = md5anim.BaseFramePart.parse(text)
        assert baseFramePart.position == (-0.4375, 242.2109, 0.5078)
        assert baseFramePart.orientation == (-0.0326106442, -0.9382, 0.0516446)

    def test_tostring(self):
        text = '( -0.4375 242.2109 0.5078 ) ( -0.0326106442 -0.9382 0.0516446 )'
        baseFramePart = md5anim.BaseFramePart.parse(text)
        assert baseFramePart.to_string() == text


class TestBaseFrame:
    BASEFRAME_SAMPLE = '''baseframe {
\t( 0 0 0 ) ( -0.7071067812 0 0 )
\t( -190.9219 66.2344 106.6172 ) ( 0 0 0 )
\t( -0.4375 242.2109 0.5078 ) ( -0.0326106442 -0.938224635 0.0516446341 )
}
'''

    def test_parse(self):
        text = TestBaseFrame.BASEFRAME_SAMPLE
        baseFrame = md5anim.BaseFrame.parse(text)
        assert len(baseFrame.parts) == 3

    def test_tostring(self):
        text = TestBaseFrame.BASEFRAME_SAMPLE
        baseFrame = md5anim.BaseFrame.parse(text)
        assert baseFrame.to_string() == text


class TestFramePart:
    def test_parse(self):
        text = '1.8516 -11.9141 -0.9287547379 -0.2488'
        framePart = md5anim.FramePart.parse(text)
        assert framePart.values == [1.8516, -11.9141, -0.9287547379, -0.2488]

    def test_tostring(self):
        text = '1.8516 -11.9141 -0.9287547379 -0.2488'
        framePart = md5anim.FramePart.parse(text)
        assert framePart.to_string() == text


class TestFrame:
    FRAME_SAMPLE = '''frame 0 {
\t0 0
\t-190.9219 66.2344 106.6172
\t-0.4375 242.2109 0.5078 -0.0326106442 -0.938224635 0.0516446341
\t0 0 0
\t-5.9375 1.4063 3.0859 -1
\t0.6557705442 -0.1422142902 -0.7179641486
}
'''

    def test_parse(self):
        text = TestFrame.FRAME_SAMPLE
        frame = md5anim.Frame.parse(text)
        assert frame.index == 0
        assert len(frame.parts) == 6
        assert len(frame.parts[0].values) == 2
        assert len(frame.parts[1].values) == 3
        assert len(frame.parts[2].values) == 6
        assert len(frame.parts[3].values) == 3
        assert len(frame.parts[4].values) == 4
        assert len(frame.parts[5].values) == 3

    def test_tostring(self):
        text = TestFrame.FRAME_SAMPLE
        frame = md5anim.Frame.parse(text)
        assert frame.to_string() == text


class TestHierarchy:
    def test_parse_nocomment(self):
        text = '"origin"\t-1 3 0\t//'
        hierarchy = md5anim.Hierarchy.parse(text)
        assert hierarchy.jointName == 'origin'
        assert hierarchy.parentJointIndex == -1
        assert hierarchy.flags == 3
        assert hierarchy.startIndex == 0
        assert hierarchy.comment == ''

    def test_parse_noslashes(self):
        text = '"origin"\t-1 3 0\t'
        hierarchy = md5anim.Hierarchy.parse(text)
        assert hierarchy.jointName == 'origin'
        assert hierarchy.parentJointIndex == -1
        assert hierarchy.flags == 3
        assert hierarchy.startIndex == 0
        assert hierarchy.comment == ''

    def test_parse_comment(self):
        text = '"origin"\t-1 3 0\t//  ( Tx Ty )'
        hierarchy = md5anim.Hierarchy.parse(text)
        assert hierarchy.jointName == 'origin'
        assert hierarchy.parentJointIndex == -1
        assert hierarchy.flags == 3
        assert hierarchy.startIndex == 0
        assert hierarchy.comment == '  ( Tx Ty )'

    def test_parse_nontrivial(self):
        text = '"target"\t0 7 2\t// origin ( Tx Ty Tz )'
        hierarchy = md5anim.Hierarchy.parse(text)
        assert hierarchy.jointName == 'target'
        assert hierarchy.parentJointIndex == 0
        assert hierarchy.flags == 7
        assert hierarchy.startIndex == 2
        assert hierarchy.comment == ' origin ( Tx Ty Tz )'

    def test_parse_nontrivial_alternative(self):
        text = '"Rhand"\t9 56 24\t// Rloarm ( Qx Qy Qz )'
        hierarchy = md5anim.Hierarchy.parse(text)
        assert hierarchy.jointName == 'Rhand'
        assert hierarchy.parentJointIndex == 9
        assert hierarchy.flags == 56
        assert hierarchy.startIndex == 24
        assert hierarchy.comment == ' Rloarm ( Qx Qy Qz )'

    def test_tostring(self):
        text = '"Rhand"\t9 56 24\t// Rloarm ( Qx Qy Qz )'
        hierarchy = md5anim.Hierarchy.parse(text)
        assert hierarchy.to_string() == text


class TestBound:
    def test_parse(self):
        text = '( -29.7891 -29.7891 191.4453 ) ( 17.2734 22.4375 275.6641 )'
        bound = md5anim.Bound.parse(text)
        assert bound.min == (-29.7891, -29.7891, 191.4453)
        assert bound.max == (17.2734, 22.4375, 275.6641)

    def test_tostring(self):
        text = '( -29.7891 -29.7891 191.4453 ) ( 17.2734 22.4375 275.6641 )'
        bound = md5anim.Bound.parse(text)
        assert bound.to_string() == text


class TestBaseFramePart:
    def test_parse(self):
        text = '( -0.4375 242.2109 0.5078 ) ( -0.0326106442 -0.9382 0.0516446 )'
        baseFramePart = md5anim.BaseFramePart.parse(text)
        assert baseFramePart.position == (-0.4375, 242.2109, 0.5078)
        assert baseFramePart.orientation == (-0.0326106442, -0.9382, 0.0516446)

    def test_tostring(self):
        text = '( -0.4375 242.2109 0.5078 ) ( -0.0326106442 -0.9382 0.0516446 )'
        baseFramePart = md5anim.BaseFramePart.parse(text)
        assert baseFramePart.to_string() == text


class TestBaseFrame:
    BASEFRAME_SAMPLE = '''baseframe {
\t( 0 0 0 ) ( -0.7071067812 0 0 )
\t( -190.9219 66.2344 106.6172 ) ( 0 0 0 )
\t( -0.4375 242.2109 0.5078 ) ( -0.0326106442 -0.938224635 0.0516446341 )
}
'''

    def test_parse(self):
        text = TestBaseFrame.BASEFRAME_SAMPLE
        baseFrame = md5anim.BaseFrame.parse(text)
        assert len(baseFrame.parts) == 3

    def test_tostring(self):
        text = TestBaseFrame.BASEFRAME_SAMPLE
        baseFrame = md5anim.BaseFrame.parse(text)
        assert baseFrame.to_string() == text


class TestFramePart:
    def test_parse(self):
        text = '1.8516 -11.9141 -0.9287547379 -0.2488'
        framePart = md5anim.FramePart.parse(text)
        assert framePart.values == [1.8516, -11.9141, -0.9287547379, -0.2488]

    def test_tostring(self):
        text = '1.8516 -11.9141 -0.9287547379 -0.2488'
        framePart = md5anim.FramePart.parse(text)
        assert framePart.to_string() == text


class TestFrame:
    FRAME_SAMPLE = '''frame 0 {
\t0 0
\t-190.9219 66.2344 106.6172
\t-0.4375 242.2109 0.5078 -0.0326106442 -0.938224635 0.0516446341
\t0 0 0
\t-5.9375 1.4063 3.0859 -1
\t0.6557705442 -0.1422142902 -0.7179641486
}
'''

    def test_parse(self):
        text = TestFrame.FRAME_SAMPLE
        frame = md5anim.Frame.parse(text)
        assert frame.index == 0
        assert len(frame.parts) == 6
        assert len(frame.parts[0].values) == 2
        assert len(frame.parts[1].values) == 3
        assert len(frame.parts[2].values) == 6
        assert len(frame.parts[3].values) == 3
        assert len(frame.parts[4].values) == 4
        assert len(frame.parts[5].values) == 3

    def test_tostring(self):
        text = TestFrame.FRAME_SAMPLE
        frame = md5anim.Frame.parse(text)
        assert frame.to_string() == text


class TestMd5Anim:
    MD5ANIM_SAMPLE = '''MD5Version 10
commandline "anim maps/fred/e3/chain/chain.mb -parent chaingunbone Lhand"

numFrames 5
numJoints 3
frameRate 24
numAnimatedComponents 11

hierarchy {
\t"origin"\t-1 3 0\t//  ( Tx Ty )
\t"target"\t0 7 2\t// origin ( Tx Ty Tz )
\t"waist"\t0 63 5\t// origin ( Tx Ty Tz Qx Qy Qz )
}

bounds {
\t( -29.7891 -29.7891 191.4453 ) ( 17.2734 22.4375 275.6641 )
\t( -29.6875 -29.6875 191.4453 ) ( 17.2734 22.4531 275.6641 )
\t( -29.5938 -29.5938 191.4453 ) ( 17.2734 22.4688 275.6641 )
\t( -29.4922 -29.4922 191.4453 ) ( 17.2734 22.4766 275.6641 )
\t( -29.3906 -29.3906 191.4453 ) ( 17.2734 22.4844 275.6641 )
}

baseframe {
	( 0 0 0 ) ( -0.7071067812 0 0 )
	( -190.9219 66.2344 106.6172 ) ( 0 0 0 )
	( -0.4375 242.2109 0.5078 ) ( -0.0326106442 -0.938224635 0.0516446341 )
	( 7.7578 1.8906 0.7578 ) ( 0.08233249 0 0 )
	( -7.8281 2.1484 0.7109 ) ( 0.08233249 0 0 )
}

frame 0 {
\t0 0
\t-190.9219 66.2344 106.6172
\t-0.4375 242.2109 0.5078 -0.0326106442 -0.938224635 0.0516446341
}

frame 1 {
\t0 0
\t-190.9219 66.2344 106.6172
\t-0.4375 242.2109 0.5078 -0.0326106442 -0.938224635 0.0516446341
}

frame 2 {
\t0 0
\t-190.9219 66.2344 106.6172
\t-0.4375 242.2109 0.5078 -0.0326106442 -0.938224635 0.0516446341
}

frame 3 {
\t0 0
\t-190.9219 66.2344 106.6172
\t-0.4375 242.2109 0.5078 -0.0326106442 -0.938224635 0.0516446341
}

frame 4 {
\t0 0
\t-190.9219 66.2344 106.6172
\t-0.4375 242.2109 0.5078 -0.0326106442 -0.938224635 0.0516446341
}
'''

    def test_parse(self):
        text = TestMd5Anim.MD5ANIM_SAMPLE
        anim = md5anim.Md5Anim.parse(text)
        assert anim.version == 10
        assert anim.commandline == 'anim maps/fred/e3/chain/chain.mb -parent chaingunbone Lhand'
        assert len(anim.frames) == 5
        assert anim.numJoints == 3
        assert anim.numAnimatedComponents == 11
        assert len(anim.hierarchies) == 3
        assert len(anim.bounds) == 5
        assert len(anim.baseframe.parts) == 5
        assert len(anim.frames) == 5

    def test_tostring(self):
        text = TestMd5Anim.MD5ANIM_SAMPLE
        anim = md5anim.Md5Anim.parse(text)
        assert anim.to_string() == text
