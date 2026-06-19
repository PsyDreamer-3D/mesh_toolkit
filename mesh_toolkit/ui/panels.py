# SPDX-License-Identifier: GPL-2.0-or-later

import bpy
from bpy.types import Panel, UIList

from ..core.utils import _TAB


# ---------------------------------------------------------------------------
# Shape Key Export — UIList
# ---------------------------------------------------------------------------

class SKX_UL_ShapeKeys(UIList):
    """Checkbox list of shape keys available for export."""

    bl_idname = "SKX_UL_ShapeKeys"

    def draw_item(
        self, context, layout, data, item, icon,
        active_data, active_propname, index,
    ):
        row = layout.row(align=True)
        row.prop(item, "include", text="")
        label_icon = 'LAYER_ACTIVE' if item.is_basis else 'SHAPEKEY_DATA'
        row.label(text=item.name, icon=label_icon)
        if item.is_basis:
            row.label(text="Basis")


# ---------------------------------------------------------------------------
# Geometry Separation panel
# ---------------------------------------------------------------------------

class MESH_PT_separate(Panel):
    bl_label = "Geometry Separation"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = _TAB
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        is_valid = (
            obj is not None
            and obj.type == 'MESH'
            and context.mode == 'OBJECT'
        )

        col = layout.column(align=True)
        col.enabled = is_valid
        col.scale_y = 1.2
        col.operator("mesh.separate_by_json", icon='MOD_EXPLODE')
        col.operator("mesh.check_separation_json", icon='VIEWZOOM')

        if not is_valid:
            layout.label(text="Select a mesh in Object Mode", icon='INFO')


# ---------------------------------------------------------------------------
# Color Attributes panel
# ---------------------------------------------------------------------------

class COLORATTR_PT_panel(Panel):
    bl_label = "Color Attributes"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = _TAB
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def draw(self, context):
        layout = self.layout
        obj = context.active_object

        if obj is None or obj.type != 'MESH':
            layout.label(text="Select a mesh object", icon='INFO')
            return

        mesh = obj.data

        info_box = layout.box()
        col = info_box.column(align=True)
        col.label(text=f"Vertices : {len(mesh.vertices)}")
        col.label(text=f"Loops    : {len(mesh.loops)}")

        layout.separator(factor=0.5)
        attrs = list(mesh.color_attributes)
        if attrs:
            active_name = (
                mesh.color_attributes.active_color.name
                if mesh.color_attributes.active_color
                else ""
            )
            box = layout.box()
            for attr in attrs:
                row = box.row(align=True)
                icon = 'LAYER_ACTIVE' if attr.name == active_name else 'LAYER_USED'
                row.label(text=attr.name, icon=icon)
                sub = row.row(align=True)
                sub.alignment = 'RIGHT'
                sub.label(text=attr.domain)
                sub.label(text=attr.data_type)
        else:
            layout.label(text="No color attributes", icon='INFO')

        layout.separator()
        col = layout.column(align=True)
        col.scale_y = 1.2
        col.operator("color_attr.export", icon='EXPORT', text="Export to JSON")
        col.operator("color_attr.import", icon='IMPORT', text="Import from JSON")

        layout.separator(factor=0.5)
        col2 = layout.column(align=True)
        col2.operator("color_attr.inspect", icon='ZOOM_IN', text="Inspect JSON…")
        col2.operator("color_attr.clear_all", icon='TRASH', text="Clear All Attributes")


# ---------------------------------------------------------------------------
# Material Swap panel
# ---------------------------------------------------------------------------

class MATSWAP_PT_panel(Panel):
    bl_label = "Material Swap"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = _TAB
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        props = context.scene.mat_swap
        obj = context.active_object
        is_valid = (
            obj is not None
            and obj.type == 'MESH'
            and context.mode == 'OBJECT'
        )

        layout.prop(props, "src_prefix")

        row = layout.row(align=True)
        row.prop(props, "target_prefix")
        row.operator(
            "material.fill_prefix_from_object",
            text="",
            icon='EYEDROPPER',
        )

        layout.prop(props, "strip_blender_suffix")

        src = props.src_prefix
        tgt = props.target_prefix
        if is_valid and src and tgt:
            matching_slots = [
                s for s in obj.material_slots
                if s.material and s.material.name.startswith(src)
            ]
            if matching_slots:
                layout.separator(factor=0.5)
                box = layout.box()
                box.label(text="Preview:", icon='HIDE_OFF')
                for i, slot in enumerate(matching_slots[:6]):
                    suffix = slot.material.name[len(src):]
                    target_name = tgt + suffix
                    exists = target_name in bpy.data.materials
                    icon = 'CHECKMARK' if exists else 'ERROR'
                    box.label(text=f"{slot.material.name}  →  {target_name}", icon=icon)
                overflow = len(matching_slots) - 6
                if overflow > 0:
                    box.label(text=f"… and {overflow} more", icon='DOT')

        layout.separator()
        row = layout.row()
        row.scale_y = 1.2
        row.enabled = is_valid
        row.operator("material.swap_by_prefix", icon='MATERIAL')

        if not is_valid:
            layout.label(text="Select a mesh in Object Mode", icon='INFO')


# ---------------------------------------------------------------------------
# Shape Key Export panel
# ---------------------------------------------------------------------------

class SKX_PT_panel(Panel):
    bl_label = "Shape Key Export"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = _TAB
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.type == 'MESH'

    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        settings = context.scene.skx_settings

        if not obj.data.shape_keys:
            layout.label(text="Active mesh has no shape keys", icon='INFO')
            return

        is_valid = context.mode == 'OBJECT'

        header = layout.row()
        header.label(text="Shape Keys:", icon='SHAPEKEY_DATA')
        btns = header.row(align=True)
        btns.operator("skx.populate_list", text="", icon='FILE_REFRESH')
        btns.operator("skx.select_all",    text="", icon='CHECKBOX_HLT')
        btns.operator("skx.select_none",   text="", icon='CHECKBOX_DEHLT')

        layout.template_list(
            "SKX_UL_ShapeKeys", "",
            settings, "key_items",
            settings, "key_items_index",
            rows=4,
        )

        layout.separator()
        name_col = layout.column(align=True)
        name_col.label(text="Naming:", icon='SORTALPHA')
        name_col.prop(settings, "obj_prefix")
        name_col.prop(settings, "obj_suffix")

        marked_non_basis = [
            i for i in settings.key_items if i.include and not i.is_basis
        ]
        if marked_non_basis:
            first = marked_non_basis[0]
            preview = (
                f"{settings.obj_prefix}"
                f"{obj.name}_{first.name}"
                f"{settings.obj_suffix}"
            )
            name_col.label(text=f"e.g. {preview}")

        layout.separator()
        place = layout.column(align=True)
        place.label(text="Placement:", icon='OUTLINER_COLLECTION')
        place.prop(settings, "use_collection")
        coll_row = place.row()
        coll_row.enabled = settings.use_collection
        coll_row.prop(settings, "collection_name")

        layout.separator()
        opts = layout.column(align=True)
        opts.label(text="Options:", icon='PREFERENCES')
        opts.prop(settings, "copy_transform")
        opts.prop(settings, "copy_materials")

        layout.separator()
        export_row = layout.row()
        export_row.scale_y = 1.6
        export_row.enabled = is_valid
        export_row.operator(
            "skx.export_shape_keys",
            text="Export Shape Keys",
            icon='EXPORT',
        )

        if not is_valid:
            layout.label(text="Switch to Object Mode to export", icon='INFO')
