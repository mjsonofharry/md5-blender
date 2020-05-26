import bpy
import math
import mathutils as mu
import os
from typing import Tuple
from .. import md5mesh


BONE_HEAD = (0.0, 0.0, 0.0)
BONE_TAIL = (0.0, 1.0, 0.0)
BONE_LENGTH = 5.0


def compute_w(qx: float, qy: float, qz: float) -> float:
    '''Compute `w` from  the `x`, `y`, and `z` components of a unit quaternion (reference: http://tfc.duke.free.fr/coding/md5-specs-en.html).'''
    t = 1.0 - (qx * qx) - (qy * qy) - (qz * qz)
    if t < 0.0:
        return 0.0
    else:
        return -math.sqrt(t)


def load(operator, context, path):
    name = os.path.splitext(os.path.basename(path))[0]
    f = open(path, 'r', encoding='utf-8')
    data = f.read()
    f.close()

    md5_mesh: md5mesh.Md5Mesh = md5mesh.Md5Mesh.parse(data)

    collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)

    armature_name = f'{name} Armature'
    armature_data = bpy.data.armatures.new(armature_name)
    armature = bpy.data.objects.new(armature_name, object_data=armature_data)
    collection.objects.link(armature)

    bpy.ops.object.mode_set()
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='EDIT')

    for joint in md5_mesh.joints:
        bone = armature_data.edit_bones.new(joint.name)

        translation = mu.Matrix.Translation(joint.position)
        (qx, qy, qz) = joint.orientation
        qw = compute_w(qx, qy, qz)
        orientation = -mu.Quaternion((qw, qx, qy, qz))

        if joint.parentIndex >= 0:
            parentName = md5_mesh.joints[joint.parentIndex].name
            bone.parent = armature_data.edit_bones[parentName]
        # order of assignments matters here
        bone.head = BONE_HEAD
        bone.tail = BONE_TAIL
        bone.matrix = translation @ orientation.to_matrix().to_4x4()
        bone.length = BONE_LENGTH

    for bone in armature_data.bones:
        bone.layers[1] = True

    bpy.ops.object.mode_set()

    return set()
