# SPDX-License-Identifier: GPL-2.0-or-later

import bmesh
import bpy
from bpy.types import Operator


class SKX_OT_PopulateList(Operator):
    """Rebuild the shape-key selection list from the active mesh object"""

    bl_idname = "skx.populate_list"
    bl_label = "Refresh List"
    bl_description = "Rebuild the shape-key list from the active object"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'MESH' and obj.data.shape_keys

    def execute(self, context):
        obj = context.active_object
        settings = context.scene.skx_settings
        settings.key_items.clear()

        reference_key = obj.data.shape_keys.reference_key

        for kb in obj.data.shape_keys.key_blocks:
            item = settings.key_items.add()
            item.name = kb.name
            item.is_basis = (kb == reference_key)
            item.include = not item.is_basis

        return {'FINISHED'}


class SKX_OT_SelectAll(Operator):
    """Mark every shape key in the list for export"""

    bl_idname = "skx.select_all"
    bl_label = "Select All"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return len(context.scene.skx_settings.key_items) > 0

    def execute(self, context):
        for item in context.scene.skx_settings.key_items:
            item.include = True
        return {'FINISHED'}


class SKX_OT_SelectNone(Operator):
    """Unmark every shape key in the list"""

    bl_idname = "skx.select_none"
    bl_label = "Select None"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return len(context.scene.skx_settings.key_items) > 0

    def execute(self, context):
        for item in context.scene.skx_settings.key_items:
            item.include = False
        return {'FINISHED'}


class SKX_OT_ExportShapeKeys(Operator):
    """Export marked shape keys as standalone mesh objects"""

    bl_idname = "skx.export_shape_keys"
    bl_label = "Export Shape Keys"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (
            obj is not None
            and obj.type == 'MESH'
            and obj.data.shape_keys is not None
            and context.mode == 'OBJECT'
        )

    def execute(self, context):
        source_obj = context.active_object
        src_mesh = source_obj.data
        settings = context.scene.skx_settings
        key_blocks = src_mesh.shape_keys.key_blocks

        if len(settings.key_items) == 0:
            reference_key = src_mesh.shape_keys.reference_key
            keys_to_export = [kb for kb in key_blocks if kb != reference_key]
        else:
            marked = {item.name for item in settings.key_items if item.include}
            keys_to_export = [kb for kb in key_blocks if kb.name in marked]

        if not keys_to_export:
            self.report({'WARNING'}, "No shape keys marked for export.")
            return {'CANCELLED'}

        target_collection = None
        if settings.use_collection:
            coll_name = (
                settings.collection_name.strip()
                or f"{source_obj.name}_shape_keys"
            )
            target_collection = bpy.data.collections.get(coll_name)
            if target_collection is None:
                target_collection = bpy.data.collections.new(coll_name)
                context.scene.collection.children.link(target_collection)

        created: list[str] = []
        for kb in keys_to_export:
            new_obj = self._shape_key_to_object(source_obj, kb, settings)

            if target_collection:
                target_collection.objects.link(new_obj)
            else:
                for coll in source_obj.users_collection:
                    coll.objects.link(new_obj)

            created.append(new_obj.name)

        self.report(
            {'INFO'},
            f"Exported {len(created)} shape key(s): {', '.join(created)}",
        )
        return {'FINISHED'}

    def _shape_key_to_object(self, source_obj, key_block, settings):
        """
        Return a new bpy.data.Object whose mesh holds the deformed vertex
        positions of *key_block*.  The object is NOT yet linked to any collection.

        bm.from_mesh(mesh, use_shape_key=True, shape_key_index=i) reads the
        absolute positions in key_blocks[i].data[] rather than Basis positions,
        giving us the correctly deformed geometry at value 1.0.  All custom
        data layers (UVs, vertex colours, face maps) transfer automatically.
        The resulting mesh has no shape keys.
        """
        src_mesh = source_obj.data
        key_index = list(src_mesh.shape_keys.key_blocks).index(key_block)

        new_name = (
            f"{settings.obj_prefix}"
            f"{source_obj.name}_{key_block.name}"
            f"{settings.obj_suffix}"
        )

        bm = bmesh.new()
        bm.from_mesh(src_mesh, use_shape_key=True, shape_key_index=key_index)
        new_mesh = bpy.data.meshes.new(new_name)
        bm.to_mesh(new_mesh)
        bm.free()
        new_mesh.update()

        if settings.copy_materials:
            for mat in src_mesh.materials:
                new_mesh.materials.append(mat)

        new_obj = bpy.data.objects.new(new_name, new_mesh)

        if settings.copy_transform:
            new_obj.matrix_world = source_obj.matrix_world.copy()

        return new_obj
