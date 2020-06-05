import bpy
import bmesh
from .. import md5mesh


def save(operator, context, path):
    collection = bpy.context.active_object.users_collection[0]

    armature_object = [
        obj for obj in collection.objects
        if obj.data in bpy.data.armatures[:]
    ][0]

    joints = [
        md5mesh.Joint.from_blender(bone, armature_object)
        for bone in armature_object.data.bones
    ]

    meshes = [
        md5mesh.Mesh.from_blender(mesh_object, armature_object)
        for mesh_object in collection.objects
        if mesh_object.data in bpy.data.meshes[:]
    ]

    md5_mesh: md5mesh.Md5Mesh = md5mesh.Md5Mesh(
        version=10,
        commandline=armature_object.get('commandline', ''),
        joints=joints,
        meshes=meshes
    )

    f = open(path, 'w', encoding='utf-8')
    f.write(md5_mesh.to_string)
    f.close()

    return set()
