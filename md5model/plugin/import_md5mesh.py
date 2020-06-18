import bpy
import bmesh
import functools
import math
import mathutils
import os
from typing import Tuple, List
from ..md5mesh import Md5Mesh, Joint, Mesh, Vert, Tri, Weight


BONE_HEAD = (0.0, 0.0, 0.0)
BONE_TAIL = (0.0, 1.0, 0.0)
BONE_LENGTH = 5.0


@functools.lru_cache(maxsize=256)
def compute_joint_matrix(joint: Joint) -> mathutils.Matrix:
    '''Get the translation matrix for the joint (returns `mathutils.Matrix`)'''
    (qx, qy, qz) = joint.orientation

    t = 1.0 - (qx * qx) - (qy * qy) - (qz * qz)
    qw = 0.0 if t < 0.0 else -math.sqrt(t)

    q = -mathutils.Quaternion((qw, qx, qy, qz))
    translation = mathutils.Matrix.Translation(joint.position)
    return translation @ q.to_matrix().to_4x4()


def load(operator, context, path):
    name = os.path.splitext(os.path.basename(path))[0]
    f = open(path, 'r', encoding='utf-8')
    data = f.read()
    f.close()

    md5_mesh: Md5Mesh = Md5Mesh.parse(data)

    collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)

    armature_name = name.strip()
    armature_data = bpy.data.armatures.new(armature_name)
    armature_object = bpy.data.objects.new(
        armature_name,
        object_data=armature_data)
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
        bone.matrix = compute_joint_matrix(joint)
        bone.length = BONE_LENGTH

    for bone in armature_data.bones:
        bone.layers[1] = True

    for mesh in md5_mesh.meshes:
        mesh_name = mesh.comment.strip()
        verts = []
        for vert in mesh.verts:
            weights = mesh.weights[vert.weightStart:vert.weightEnd]
            global_vert_position = mathutils.Vector((0.0, 0.0, 0.0))
            for weight in weights:
                joint = md5_mesh.joints[weight.jointIndex]
                joint_matrix = compute_joint_matrix(joint)
                weight_position = mathutils.Vector(weight.position)
                adjust = (joint_matrix @ weight_position) * weight.bias
                global_vert_position += adjust
            verts.append(global_vert_position)
        edges = []
        faces = [x.verts for x in mesh.tris]

        mesh_data = bpy.data.meshes.new(mesh_name)
        mesh_data.from_pydata(verts, edges, faces)
        mesh_data.flip_normals()
        mesh_object = bpy.data.objects.new(mesh_name, object_data=mesh_data)
        mesh_object['shader'] = mesh.shader
        mesh_object['comment'] = mesh.comment

        for i, joint in enumerate(md5_mesh.joints):
            if i in (weight.jointIndex for weight in mesh.weights):
                vertex_group = mesh_object.vertex_groups.new(name=joint.name)

        for vert in mesh.verts:
            for weight in mesh.weights[vert.weightStart:vert.weightEnd]:
                joint = md5_mesh.joints[weight.jointIndex]
                vertex_group = next(
                    group for group in mesh_object.vertex_groups
                    if group.name == joint.name
                )
                vertex_group.add(
                    index=[vert.index],
                    weight=weight.bias,
                    type='ADD')

        bm = bmesh.new()
        bm.from_mesh(mesh_object.data)

        uv_layer = bm.loops.layers.uv.verify()
        deform_layer = bm.verts.layers.deform.verify()

        for i, (vert, bm_vert) in enumerate(zip(mesh.verts, bm.verts)):
            for loop in bm_vert.link_loops:
                loop[uv_layer].uv = mesh.verts[i].uv
            # for weight in mesh.weights[vert.weightStart:vert.weightEnd]:
            #     bm_vert[deform_layer][weight.jointIndex] = weight.bias

        bm.to_mesh(mesh_object.data)
        bm.free()

        modifier = mesh_object.modifiers.new(name=mesh_name, type='ARMATURE')
        modifier.object = armature_object
        collection.objects.link(mesh_object)

    bpy.ops.object.mode_set()

    return set()
