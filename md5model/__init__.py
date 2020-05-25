bl_info = {
    "name": "MD5 format",
    "author": "Matthew James Harrison",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "File > Import-Export",
    "description": "MD5 meshes and animations",
    "warning": "",
    "doc_url": "https://github.com/mjsonofharry/md5-blender",
    "category": "Import-Export"
}


def register():
    from . import plugin
    plugin.register()


def unregister():
    from . import plugin
    plugin.unregister()


if __name__ == "__main__":
    register()
