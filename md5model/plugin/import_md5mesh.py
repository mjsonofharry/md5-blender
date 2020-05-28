import bpy
import bmesh
import math
import mathutils as mu
import os
from typing import Tuple, List, Optional
from .. import md5mesh


BONE_HEAD = (0.0, 0.0, 0.0)
BONE_TAIL = (0.0, 1.0, 0.0)
BONE_LENGTH = 5.0


def compute_w(qx: float, qy: float, qz: float) -> float:
    '''Compute `w` for a unit quaternion (reference: http://tfc.duke.free.fr/coding/md5-specs-en.html)'''
    t = 1.0 - (qx * qx) - (qy * qy) - (qz * qz)
    if t < 0.0:
        return 0.0
    else:
        return -math.sqrt(t)


def compute_bone_matrix(
    position: Tuple[float, float, float],
    orientation: Tuple[float, float, float]
) -> Tuple[md5mesh.Joint, mu.Matrix]:
    '''Combine position and orientation vectors into a transformation matrix'''
    translation = mu.Matrix.Translation(position)
    (qx, qy, qz) = orientation
    qw = compute_w(qx, qy, qz)
    orientation = -mu.Quaternion((qw, qx, qy, qz))
    return translation @ orientation.to_matrix().to_4x4()


def load(operator, context, path):
    name = os.path.splitext(os.path.basename(path))[0]
    f = open(path, 'r', encoding='utf-8')
    data = f.read()
    f.close()

    md5_mesh: md5mesh.Md5Mesh = md5mesh.Md5Mesh.parse(data)

    collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)

    armature_name = f'{name} Armature'.strip()
    armature_data = bpy.data.armatures.new(armature_name)
    armature_object = bpy.data.objects.new(armature_name, object_data=armature_data)
    collection.objects.link(armature_object)

    bpy.context.view_layer.objects.active = armature_object
    bpy.ops.object.mode_set()
    bpy.ops.object.mode_set(mode='EDIT')

    joint_matrices = [
        (joint, compute_bone_matrix(joint.position, joint.orientation))
        for joint in md5_mesh.joints
    ]

    for joint, matrix in joint_matrices:
        bone = armature_data.edit_bones.new(joint.name)
        if joint.parentIndex >= 0:
            parentName = md5_mesh.joints[joint.parentIndex].name
            bone.parent = armature_data.edit_bones[parentName]
        bone.head = BONE_HEAD
        bone.tail = BONE_TAIL
        bone.matrix = matrix
        bone.length = BONE_LENGTH

    for bone in armature_data.bones:
        bone.layers[1] = True

    for mesh in md5_mesh.meshes:
        bm = bmesh.new()
        # do stuff with bm here
        mesh_name = f'{mesh.comment} Mesh'.strip()
        mesh_data = bpy.data.objects.new(mesh_name)
        bm.to_mesh(mesh_data)
        bm.free()
        mesh_object = bpy.data.objects.new(mesh_name, object_data=mesh_data)

        # ???
        modifier = mesh.modifiers.new(name=mesh_name, type='ARMATURE')
        modifier.object = armature_object

    bpy.ops.object.mode_set()

    return set()
