import bpy
import functools
import math
import mathutils
import os
from typing import Tuple, List, Optional
from .. import md5mesh


BONE_HEAD = (0.0, 0.0, 0.0)
BONE_TAIL = (0.0, 1.0, 0.0)
BONE_LENGTH = 5.0


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
    armature_object = bpy.data.objects.new(
        armature_name, object_data=armature_data)
    collection.objects.link(armature_object)

    bpy.context.view_layer.objects.active = armature_object
    bpy.ops.object.mode_set()
    bpy.ops.object.mode_set(mode='EDIT')

    for joint in md5_mesh.joints:
        bone = armature_data.edit_bones.new(joint.name)
        if joint.parentIndex >= 0:
            parentName = md5_mesh.joints[joint.parentIndex].name
            bone.parent = armature_data.edit_bones[parentName]
        bone.head = BONE_HEAD
        bone.tail = BONE_TAIL
        bone.matrix = joint.matrix
        bone.length = BONE_LENGTH

    for bone in armature_data.bones:
        bone.layers[1] = True

    for mesh in md5_mesh.meshes:
        def compute_vert_position(vert: md5mesh.Vert):
            '''Compute the absolute position of a single vertex (reference: http://tfc.duke.free.fr/coding/md5-specs-en.html)'''
            def apply_weight_to_position(acc: mathutils.Vector, weight: md5mesh.Weight):
                '''Adjust a position vector using a single weight (reference: http://tfc.duke.free.fr/coding/md5-specs-en.html'''
                joint = md5_mesh.joints[weight.jointIndex]
                return acc + ((joint.matrix @ mathutils.Vector(weight.position)) * weight.bias)
            weights = mesh.weights[vert.weightStart:vert.weightEnd]
            weighted_position = functools.reduce(apply_weight_to_position, [mathutils.Vector((0.0, 0.0, 0.0)), *weights])
            return weighted_position
        verts = [compute_vert_position(vert) for vert in mesh.verts]

        edges = []
        faces = [x.verts for x in mesh.tris]

        mesh_name = f'{mesh.comment}'.strip()
        mesh_data = bpy.data.meshes.new(mesh_name)
        mesh_data.from_pydata(verts, edges, faces)
        mesh_object = bpy.data.objects.new(mesh_name, object_data=mesh_data)
        collection.objects.link(mesh_object)

        # ???
        # modifier = mesh.modifiers.new(name=mesh_name, type='ARMATURE')
        # modifier.object = armature_object

    bpy.ops.object.mode_set()

    return set()
