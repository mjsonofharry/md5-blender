import bpy
from .. import md5mesh


def save(operator, context, path):
    collection = bpy.context.active_object.users_collection[0]

    armature_object = [
        obj for obj in collection.objects
        if obj.data in bpy.data.armatures[:]
    ][0]

    joints = [
        md5mesh.Joint.from_bone(bone, armature_object)
        for bone in armature_object.data.bones
    ]

    mesh_objects = [
        obj for obj in collection.objects
        if obj.data in bpy.data.meshes[:]
    ]

    md5_mesh: md5mesh.Md5Mesh = md5mesh.Md5Mesh(
        version=10,
        commandline=armature_object.get('commandline', ''),
        joints=joints,
        meshes=[]
    )

    f = open(path, 'w', encoding='utf-8')
    f.write(md5_mesh.to_string)
    f.close()

    return set()
