import bpy
import bmesh
from typing import List
from ..md5mesh import Md5Mesh, Joint, Mesh, Vert, Tri, Weight


def save(operator, context, path):
    collection = bpy.context.active_object.users_collection[0]

    armature_object = next(
        obj for obj in collection.objects
        if obj.data in bpy.data.armatures[:]
    )

    commandline = armature_object.get('commandline', '')

    joints: List[md5mesh.Joint] = []
    for bone in armature_object.data.bones:
        parent = bone.parent
        parent_name = parent.name if parent else ''
        parent_index = next(
            i for i, other in enumerate(armature_object.data.bones)
            if other == parent
        ) if parent else -1
        location, rotation, scale = bone.matrix_local.decompose()
        joints.append(Joint(
            name=bone.name,
            parentIndex=parent_index,
            position=location[:],
            orientation=(-rotation.normalized())[1:],
            comment=f' {parent_name}'))

    mesh_objects = [
        obj for obj in collection.objects
        if obj.data in bpy.data.meshes[:]
    ]

    meshes: List[Mesh] = []
    for mesh_object in mesh_objects:
        shader = mesh_object.get('shader', '')
        comment = mesh_object.get('comment', '')
        tris = [
            Tri(index=i, verts=poly.vertices)
            for i, poly in enumerate(mesh_object.data.polygons)
        ]

        bm = bmesh.new()
        bm.from_mesh(mesh_object.data)

        uv_layer = bm.loops.layers.uv.active

        verts: List[Vert] = []
        weights: List[Weight] = []
        weight_count = 0
        for i, (vert, bm_vert) in enumerate(zip(mesh_object.data.vertices, bm.verts)):
            uv = bm_vert.link_loops[0][uv_layer].uv
            verts.append(Vert(
                index=i,
                uv=(uv.x, uv.y),
                weightStart=weight_count,
                weightCount=len(vert.groups)))
            for vert_group in vert.groups:
                bone = armature_object.data.bones[vert_group.group]
                x, y, z = (
                    bone.matrix_local.inverted() @
                    armature_object.matrix_world.inverted() @
                    vert.co.to_4d()
                )[:3]
                weights.append(Weight(
                    index=weight_count,
                    jointIndex=vert_group.group,
                    bias=vert_group.weight,
                    position=(x, y, z)))
                weight_count += 1

        bm.free()

        meshes.append(Mesh(
            comment=comment,
            shader=shader,
            verts=verts,
            tris=tris,
            weights=weights))

    md5_mesh = Md5Mesh(
        version=10,
        commandline=commandline,
        joints=joints,
        meshes=meshes
    )

    f = open(path, 'w', encoding='utf-8')
    f.write(md5_mesh.to_string)
    f.close()

    return set()
