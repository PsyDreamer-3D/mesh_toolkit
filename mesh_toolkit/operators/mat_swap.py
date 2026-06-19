# SPDX-License-Identifier: GPL-2.0-or-later

import re

import bpy
from bpy.types import Operator

_BLENDER_SUFFIX_RE = re.compile(r'\.\d{3}$')


class MATERIAL_OT_fill_prefix_from_object(Operator):
    """Fill the Target Prefix field from the active object's name"""

    bl_idname = "material.fill_prefix_from_object"
    bl_label = "Fill Target Prefix from Object Name"
    bl_options = {'INTERNAL', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        props = context.scene.mat_swap
        name = context.active_object.name
        if props.strip_blender_suffix:
            name = _BLENDER_SUFFIX_RE.sub('', name)
        if name and not name.endswith('_'):
            name += '_'
        props.target_prefix = name
        return {'FINISHED'}


class MATERIAL_OT_swap_by_prefix(Operator):
    """Swap material slots whose names start with the source prefix,
replacing that prefix with the target prefix"""

    bl_idname = "material.swap_by_prefix"
    bl_label = "Swap Materials"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (
            obj is not None
            and obj.type == 'MESH'
            and context.mode == 'OBJECT'
            and len(obj.material_slots) > 0
        )

    def execute(self, context):
        props = context.scene.mat_swap
        src = props.src_prefix
        tgt = props.target_prefix

        if not src:
            self.report({'ERROR'}, "Source prefix is empty.")
            return {'CANCELLED'}
        if not tgt:
            self.report({'ERROR'}, "Target prefix is empty.")
            return {'CANCELLED'}

        obj = context.active_object
        swapped = not_found = skipped = 0

        for slot in obj.material_slots:
            mat = slot.material
            if mat is None or not mat.name.startswith(src):
                skipped += 1
                continue

            suffix = mat.name[len(src):]
            target_name = tgt + suffix
            new_mat = bpy.data.materials.get(target_name)

            if new_mat is None:
                not_found += 1
                continue

            slot.material = new_mat
            swapped += 1

        self.report(
            {'INFO'},
            f"Swapped {swapped}, not found {not_found}, skipped {skipped}.",
        )
        return {'FINISHED'}
