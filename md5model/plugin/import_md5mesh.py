import bpy
import functools
import math
import mathutils
import os
from typing import Tuple, List
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

    armature_name = name.strip()
    armature_data = bpy.data.armatures.new(armature_name)
    armature_object = bpy.data.objects.new(
        armature_name, object_data=armature_data)
    armature_object['commandline'] = md5_mesh.commandline
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
        mesh_name = mesh.comment.strip()
        verts = [
            md5_mesh.compute_global_vert_position(vert, mesh)
            for vert in mesh.verts
        ]
        edges = []
        faces = [x.verts for x in mesh.tris]
        mesh_data = bpy.data.meshes.new(mesh_name)
        mesh_data.from_pydata(verts, edges, faces)
        mesh_data.flip_normals()
        mesh_object = bpy.data.objects.new(mesh_name, object_data=mesh_data)
        mesh_object['shader'] = mesh.shader

        for joint in md5_mesh.joints:
            indices = [
                i for i, vert in enumerate(mesh.verts)
                if md5_mesh.vert_belongs_to_group(vert, mesh, joint)
            ]
            vertex_group = mesh_object.vertex_groups.new(name=joint.name)
            vertex_group.add(index=indices, weight=1.0, type='REPLACE')

        modifier = mesh_object.modifiers.new(name=mesh_name, type='ARMATURE')
        modifier.object = armature_object

        collection.objects.link(mesh_object)

    bpy.ops.object.mode_set()

    return set()
