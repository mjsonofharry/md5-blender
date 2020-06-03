if 'bpy' in locals():
    import importlib
    if 'import_m5mesh' in locals():
        importlib.reload(import_m5mesh)
    if 'import_md5anim' in locals():
        importlib.reload(import_md5anim)
    if 'export_m5mesh' in locals():
        importlib.reload(export_m5mesh)
    if 'export_md5anim' in locals():
        importlib.reload(export_md5anim)


import bpy
import bpy_extras.io_utils


class ImportMd5Mesh(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """Load an id Tech 4 md5mesh file"""
    bl_idname = "import_scene.md5mesh"
    bl_label = "Import MD5 Mesh"
    bl_options = {'UNDO', 'PRESET'}

    filename_ext = ".md5mesh"
    filter_glob: bpy.props.StringProperty(
        default="*.md5mesh", options={'HIDDEN'})

    def draw(self, context):
        pass

    def execute(self, context):
        from . import import_md5mesh
        return import_md5mesh.load(self, context, self.filepath)


class ImportMd5Anim(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """Load an id Tech 4 md5anim file"""
    bl_idname = "import_scene.md5anim"
    bl_label = "Import MD5 Animation"
    bl_options = {'UNDO', 'PRESET'}

    filename_ext = ".md5anim"
    filter_glob: bpy.props.StringProperty(
        default="*.md5anim", options={'HIDDEN'})

    def draw(self, context):
        pass

    def execute(self, context):
        pass


class ExportMd5Mesh(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """Save id Tech 4 md5mesh file"""
    bl_idname = "export_scene.md5mesh"
    bl_label = "Export MD5 Mesh"
    bl_options = {'UNDO', 'PRESET'}

    filename_ext = ".md5mesh"
    filter_glob: bpy.props.StringProperty(
        default="*.md5mesh", options={'HIDDEN'})

    def draw(self, context):
        pass

    def execute(self, context):
        from . import export_md5mesh
        return export_md5mesh.save(self, context, self.filepath)


class ExportMd5Anim(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """Save id Tech 4 md5anim file"""
    bl_idname = "export_scene.md5anim"
    bl_label = "Export MD5 Animation"
    bl_options = {'UNDO', 'PRESET'}

    filename_ext = ".md5anim"
    filter_glob: bpy.props.StringProperty(
        default="*.md5anim", options={'HIDDEN'})

    def draw(self, context):
        pass

    def execute(self, context):
        pass


def menu_func_import_mesh(self, context):
    self.layout.operator(
        ImportMd5Mesh.bl_idname, text="MD5 Mesh (.md5mesh)")


def menu_func_import_anim(self, context):
    self.layout.operator(
        ImportMd5Anim.bl_idname, text="MD5 Animation (.md5anim)")


def menu_func_export_mesh(self, context):
    self.layout.operator(
        ExportMd5Mesh.bl_idname, text="MD5 Mesh (.md5mesh)")


def menu_func_export_anim(self, context):
    self.layout.operator(
        ExportMd5Anim.bl_idname, text="MD5 Animation (.md5anim)")


classes = [
    ImportMd5Mesh,
    ImportMd5Anim,
    ExportMd5Mesh,
    ExportMd5Anim
]


def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import_mesh)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import_anim)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export_mesh)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export_anim)


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import_mesh)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import_anim)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export_mesh)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export_anim)
