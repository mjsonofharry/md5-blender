import pytest
from .context import md5mesh


class TestJoint:
    def test_parse_nocomment(self):
        text = '\t"origin"\t-1 ( 0 0 0 ) ( 0 0 -0.7071067812 )\t\t// '
        joint = md5mesh.Joint.parse(text)
        assert joint.name == 'origin'
        assert joint.parentIndex == -1
        assert joint.position == (0.0, 0.0, 0.0)
        assert joint.orientation == (0.0, 0.0, -0.7071067812)
        assert joint.comment == ''

    def test_parse_comment(self):
        text = '\t"target"\t0 ( 0 0 0 ) ( 0 0 -0.7071067812 )\t\t// origin'
        joint = md5mesh.Joint.parse(text)
        assert joint.name == 'target'
        assert joint.parentIndex == 0
        assert joint.position == (0.0, 0.0, 0.0)
        assert joint.orientation == (0.0, 0.0, -0.7071067812)
        assert joint.comment == 'origin'

    def test_parse_nontrivial(self):
        text = '\t"waist"\t0 ( -0.465389 0 51.328655 ) ( -0.5394861067 -0.5394861067 -0.457 )\t\t// origin'
        joint = md5mesh.Joint.parse(text)
        assert joint.name == 'waist'
        assert joint.parentIndex == 0
        assert joint.position == (-0.465389, 0, 51.328655)
        assert joint.orientation == (-0.5394861067, -0.5394861067, -0.457)
        assert joint.comment == 'origin'

    def test_parse_nontrivial_alternative(self):
        text = '\t"Rhand"\t9 ( -3.50706 -28.3922 58.702999 ) ( 0.3317336325 0.3162666777 -0.3598525295 )\t\t// Rloarm'
        joint = md5mesh.Joint.parse(text)
        assert joint.name == 'Rhand'
        assert joint.parentIndex == 9
        assert joint.position == (-3.50706, -28.3922, 58.702999)
        assert joint.orientation == (0.3317336325, 0.3162666777, -0.3598525295)
        assert joint.comment == 'Rloarm'

    def test_tostring(self):
        joint = md5mesh.Joint(name='Rhand', parentIndex=9, position=(-3.50706, -28.3922, 58.702999),
                              orientation=(0.3317336325, 0.3162666777, -0.3598525295), comment='Rloarm')
        assert joint.to_string() == '"Rhand"\t9 ( -3.50706 -28.3922 58.702999 ) ( 0.3317336325 0.3162666777 -0.3598525295 )\t\t// Rloarm'


class TestVert:
    def test_parse_match(self):
        text = '\tvert 7 ( 0.574369 0.525882 ) 10 2'
        vert = md5mesh.Vert.parse(text)
        assert vert.index == 7
        assert vert.uv == (0.574369, 0.525882)
        assert vert.weightStart == 10
        assert vert.weightCount == 2

    def test_tostring(self):
        vert = md5mesh.Vert(index=7, uv=(0.574369, 0.525882),
                            weightStart=10, weightCount=2)
        assert vert.to_string() == 'vert 7 ( 0.574369 0.525882 ) 10 2'


class TestTri:
    def test_parse_match(self):
        text = '\ttri 1019 707 690 691'
        tri = md5mesh.Tri.parse(text)
        assert tri.index == 1019
        assert tri.verts == (707, 690, 691)

    def test_tostring(self):
        tri = md5mesh.Tri(index=1019, verts=(707, 690, 691))
        assert tri.to_string() == 'tri 1019 707 690 691'


class TestWeight:
    def test_parse_match(self):
        text = '\tweight 443 67 0.178646 ( -3.839379 26.337955 4.979258 )'
        weight = md5mesh.Weight.parse(text)
        assert weight.index == 443
        assert weight.jointIndex == 67
        assert weight.bias == 0.178646
        assert weight.position == (-3.839379, 26.337955, 4.979258)

    def test_tostring(self):
        weight = md5mesh.Weight(
            index=443, jointIndex=67, bias=0.178646, position=(-3.839379, 26.337955, 4.979258))
        assert weight.to_string() == 'weight 443 67 0.178646 ( -3.839379 26.337955 4.979258 )'


class TestMesh:
    def test_parse_match(self):
        text = '''mesh {
\t// meshes: com1_eye
\tshader "models/monsters/zombie/commando/com1_eye"

\tnumverts 8
\tvert 0 ( 0.004951 0.004951 ) 0 1
\tvert 1 ( 0.004951 0.99505 ) 1 1
\tvert 2 ( 0.995049 0.004951 ) 2 1
\tvert 3 ( 0.995049 0.99505 ) 3 1
\tvert 4 ( 0.004951 0.004951 ) 4 3
\tvert 5 ( 0.004951 0.99505 ) 7 2
\tvert 6 ( 0.995049 0.004951 ) 9 5
\tvert 7 ( 0.995049 0.99505 ) 14 3

\tnumtris 4
\ttri 0 2 1 0
\ttri 1 3 1 2
\ttri 2 6 5 4
\ttri 3 7 5 6

\tnumweights 17
\tweight 0 48 1.0 ( 2.455065 5.21452 0.565574 )
\tweight 1 48 1.0 ( 2.455065 5.409174 -0.528822 )
\tweight 2 48 1.0 ( 1.471064 5.723574 0.656117 )
\tweight 3 48 1.0 ( 1.471064 5.918229 -0.438279 )
\tweight 4 48 0.456828 ( -1.314141 5.837293 0.676343 )
\tweight 5 59 0.456828 ( -1.314141 -0.625642 0.259328 )
\tweight 6 52 0.086345 ( -0.386919 2.187816 -0.30181 )
\tweight 7 48 0.5 ( -1.314141 6.031948 -0.418053 )
\tweight 8 59 0.5 ( -1.314141 0.470846 0.076829 )
\tweight 9 48 0.331448 ( -2.280067 5.295721 0.580016 )
\tweight 10 59 0.302748 ( -2.280067 -0.715953 -0.28328 )
\tweight 11 54 0.065639 ( 2.837125 1.447748 2.811902 )
\tweight 12 53 0.089493 ( -2.234747 1.989634 -1.303629 )
\tweight 13 52 0.210672 ( -1.352844 2.097505 -0.844418 )
\tweight 14 48 0.467367 ( -2.280067 5.490375 -0.51438 )
\tweight 15 59 0.451175 ( -2.280067 0.380535 -0.465779 )
\tweight 16 52 0.081458 ( -1.352844 3.193994 -1.026917 )
}'''
        mesh = md5mesh.Mesh.parse(text)
        assert mesh.comment == 'meshes: com1_eye'
        assert mesh.shader == 'models/monsters/zombie/commando/com1_eye'
        assert len(mesh.verts) == 8
        assert len(mesh.tris) == 4
        assert len(mesh.weights) == 17

    def test_tostring(self):
        verts = [
            md5mesh.Vert.parse('vert 0 ( 0.004951 0.004951 ) 0 1'),
            md5mesh.Vert.parse('vert 1 ( 0.004951 0.99505 ) 1 1'),
            md5mesh.Vert.parse('vert 2 ( 0.995049 0.004951 ) 2 1')
        ]
        tris = [
            md5mesh.Tri.parse('tri 0 2 1 0'),
            md5mesh.Tri.parse('tri 1 3 1 2')
        ]
        weights = [
            md5mesh.Weight.parse('weight 0 48 1.0 ( 2.455065 5.21452 0.565574 )'),
            md5mesh.Weight.parse('weight 1 48 1.0 ( 2.455065 5.409174 -0.528822 )'),
            md5mesh.Weight.parse('weight 2 48 1.0 ( 1.471064 5.723574 0.656117 )'),
            md5mesh.Weight.parse('weight 3 48 1.0 ( 1.471064 5.918229 -0.438279 )')
        ]
        mesh = md5mesh.Mesh(comment='meshes: com1_eye',
                            shader='models/monsters/zombie/commando/com1_eye', verts=verts, tris=tris, weights=weights)
        assert mesh.to_string() == '''mesh {
\t// meshes: com1_eye
\tshader "models/monsters/zombie/commando/com1_eye"

\tnumverts 3
\tvert 0 ( 0.004951 0.004951 ) 0 1
\tvert 1 ( 0.004951 0.99505 ) 1 1
\tvert 2 ( 0.995049 0.004951 ) 2 1

\tnumtris 2
\ttri 0 2 1 0
\ttri 1 3 1 2

\tnumweights 4
\tweight 0 48 1.0 ( 2.455065 5.21452 0.565574 )
\tweight 1 48 1.0 ( 2.455065 5.409174 -0.528822 )
\tweight 2 48 1.0 ( 1.471064 5.723574 0.656117 )
\tweight 3 48 1.0 ( 1.471064 5.918229 -0.438279 )
}
'''

class TestMd5Mesh:
    def test_parse_match(self):
        text = '''MD5Version 10
commandline "mesh maps/fred/e3/chain/chain.mb -parent chaingunbone Lhand"

numJoints 3
numMeshes 2

joints {
\t"origin"\t-1 ( 0 0 0 ) ( 0 0 -0.7071067812 )\t\t// 
\t"target"\t0 ( 0 0 0 ) ( 0 0 -0.7071067812 )\t\t// origin
\t"waist"\t0 ( -0.465389 0 51.328655 ) ( -0.5394861067 -0.5394861067 -0.4571156754 )\t\t// origin
}

mesh {
\t// meshes: com1_d
\tshader "models/monsters/zombie/commando/com1_d"

\tnumverts 3
\tvert 0 ( 0.53591 0.438716 ) 0 1
\tvert 1 ( 0.50751 0.473978 ) 3 1
\tvert 2 ( 0.511314 0.50808 ) 1 2

\tnumtris 1
\ttri 0 2 1 0

\tnumweights 2
\tweight 0 61 1.0 ( -3.078593 3.522633 -5.625685 )
\tweight 1 61 0.8 ( -7.45092 1.8983 4.288566 )
}

mesh {
\t// meshes: cgun
\tshader "models/monsters/zombie/commando/cgun"

\tnumverts 2
\tvert 0 ( 0.738746 0.175496 ) 0 1
\tvert 1 ( 0.728951 0.141262 ) 1 1

\tnumtris 3
\ttri 0 2 1 0
\ttri 1 0 1 3
\ttri 2 4 0 3

\tnumweights 1
\tweight 0 39 1.0 ( 0.319793 2.069755 -3.67824 )
}
'''
        mesh = md5mesh.Md5Mesh.parse(text)
        assert mesh.version == 10
        assert mesh.commandline == 'mesh maps/fred/e3/chain/chain.mb -parent chaingunbone Lhand'
        assert len(mesh.joints) == 3
        assert len(mesh.meshes) == 2
