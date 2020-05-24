import pytest
from .context import md5mesh


class TestJoint:
    def test_parse_nocomment(self):
        text = '	"origin"	-1 ( 0 0 0 ) ( 0 0 -0.7071067812 )		// '
        joint = md5mesh.Joint.parse(text)
        assert joint.name == 'origin'
        assert joint.parentIndex == -1
        assert joint.position == (0.0, 0.0, 0.0)
        assert joint.orientation == (0.0, 0.0, -0.7071067812)
        assert joint.comment == ''

    def test_parse_comment(self):
        text = '	"target"	0 ( 0 0 0 ) ( 0 0 -0.7071067812 )		// origin'
        joint = md5mesh.Joint.parse(text)
        assert joint.name == 'target'
        assert joint.parentIndex == 0
        assert joint.position == (0.0, 0.0, 0.0)
        assert joint.orientation == (0.0, 0.0, -0.7071067812)
        assert joint.comment == 'origin'

    def test_parse_nontrivial(self):
        text = '	"waist"	0 ( -0.465389 0 51.328655 ) ( -0.5394861067 -0.5394861067 -0.457 )		// origin'
        joint = md5mesh.Joint.parse(text)
        assert joint.name == 'waist'
        assert joint.parentIndex == 0
        assert joint.position == (-0.465389, 0, 51.328655)
        assert joint.orientation == (-0.5394861067, -0.5394861067, -0.457)
        assert joint.comment == 'origin'

    def test_parse_nontrivial_alternative(self):
        text = '	"Rhand"	9 ( -3.50706 -28.3922 58.702999 ) ( 0.3317336325 0.3162666777 -0.3598525295 )		// Rloarm'
        joint = md5mesh.Joint.parse(text)
        assert joint.name == 'Rhand'
        assert joint.parentIndex == 9
        assert joint.position == (-3.50706, -28.3922, 58.702999)
        assert joint.orientation == (0.3317336325, 0.3162666777, -0.3598525295)
        assert joint.comment == 'Rloarm'

    def test_tostring(self):
        joint = md5mesh.Joint(name='Rhand', parentIndex=9, position=(-3.50706, -28.3922, 58.702999),
                              orientation=(0.3317336325, 0.3162666777, -0.3598525295), comment='Rloarm')
        assert joint.to_string() == '	"Rhand"	9 ( -3.50706 -28.3922 58.702999 ) ( 0.3317336325 0.3162666777 -0.3598525295 )		// Rloarm'


class TestVert:
    def test_parse_match(self):
        text = '	vert 7 ( 0.574369 0.525882 ) 10 2'
        vert = md5mesh.Vert.parse(text)
        assert vert.index == 7
        assert vert.uv == (0.574369, 0.525882)
        assert vert.weightStart == 10
        assert vert.weightCount == 2

    def test_tostring(self):
        vert = md5mesh.Vert(index=7, uv=(0.574369, 0.525882),
                            weightStart=10, weightCount=2)
        assert vert.to_string() == '	vert 7 ( 0.574369 0.525882 ) 10 2'


class TestTri:
    def test_parse_match(self):
        text = '	tri 1019 707 690 691'
        tri = md5mesh.Tri.parse(text)
        assert tri.index == 1019
        assert tri.verts == (707, 690, 691)

    def test_tostring(self):
        tri = md5mesh.Tri(index=1019, verts=(707, 690, 691))
        assert tri.to_string() == '	tri 1019 707 690 691'


class TestWeight:
    def test_parse_match(self):
        text = '	weight 443 67 0.178646 ( -3.839379 26.337955 4.979258 )'
        weight = md5mesh.Weight.parse(text)
        assert weight.index == 443
        assert weight.jointIndex == 67
        assert weight.bias == 0.178646
        assert weight.position == (-3.839379, 26.337955, 4.979258)

    def test_tostring(self):
        weight = md5mesh.Weight(
            index=443, jointIndex=67, bias=0.178646, position=(-3.839379, 26.337955, 4.979258))
        assert weight.to_string() == '	weight 443 67 0.178646 ( -3.839379 26.337955 4.979258 )'
