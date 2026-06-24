# SPDX-License-Identifier: GPL-2.0-or-later

import json

import bpy
from bpy.props import StringProperty
from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper

from ..core.utils import _resolve_vertex_indices


class GSB_OT_add_entry(Operator):
    """Add a new output-object entry and populate its material and vertex-group
lists from the active mesh"""

    bl_idname = "mesh.gsb_add_entry"
    bl_label = "Add Entry"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (
            obj is not None
            and obj.type == 'MESH'
            and context.mode == 'OBJECT'
        )

    def execute(self, context):
        settings = context.scene.gsb_settings
        name = settings.new_entry_name.strip()
        if not name:
            self.report({'WARNING'}, "Enter a name before adding an entry.")
            return {'CANCELLED'}

        obj = context.active_object
        entry = settings.entries.add()
        entry.entry_name = name

        for slot in obj.material_slots:
            if slot.material:
                item = entry.mat_items.add()
                item.name = slot.material.name

        for vg in obj.vertex_groups:
            item = entry.vg_items.add()
            item.name = vg.name

        settings.active_index = len(settings.entries) - 1
        settings.new_entry_name = ""
        return {'FINISHED'}


class GSB_OT_remove_entry(Operator):
    """Remove the active entry from the list"""

    bl_idname = "mesh.gsb_remove_entry"
    bl_label = "Remove Entry"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return len(context.scene.gsb_settings.entries) > 0

    def execute(self, context):
        settings = context.scene.gsb_settings
        idx = settings.active_index
        settings.entries.remove(idx)
        settings.active_index = max(0, idx - 1)
        return {'FINISHED'}


class GSB_OT_export_json(Operator, ExportHelper):
    """Export the current entry list as a Separate-by-JSON config file"""

    bl_idname = "mesh.gsb_export_json"
    bl_label = "Export Config JSON…"
    bl_options = {'REGISTER'}

    filename_ext = ".json"
    filter_glob: StringProperty(default="*.json", options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        return len(context.scene.gsb_settings.entries) > 0

    def execute(self, context):
        settings = context.scene.gsb_settings
        output = {}
        for entry in settings.entries:
            mats = [item.name for item in entry.mat_items if item.include]
            vgs  = [item.name for item in entry.vg_items  if item.include]
            group = {}
            if vgs:
                group["vertex_groups"] = vgs
            if mats:
                group["materials"] = mats
            output[entry.entry_name] = group

        try:
            with open(self.filepath, 'w', encoding='utf-8') as fh:
                json.dump(output, fh, indent=4, ensure_ascii=False)
        except Exception as exc:
            self.report({'ERROR'}, f"Could not write file: {exc}")
            return {'CANCELLED'}

        self.report({'INFO'}, f"Exported {len(output)} entries to {self.filepath}")
        return {'FINISHED'}


class GSB_OT_export_vertex_json(Operator, ExportHelper):
    """Export a JSON listing the resolved vertex indices for each entry on the
active mesh"""

    bl_idname = "mesh.gsb_export_vertex_json"
    bl_label = "Export Vertex JSON…"
    bl_options = {'REGISTER'}

    filename_ext = ".json"
    filter_glob: StringProperty(default="*.json", options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (
            obj is not None
            and obj.type == 'MESH'
            and context.mode == 'OBJECT'
            and len(context.scene.gsb_settings.entries) > 0
        )

    def execute(self, context):
        obj = context.active_object
        settings = context.scene.gsb_settings

        output = {"_meta": {"source_object": obj.name}}
        for entry in settings.entries:
            mats = [item.name for item in entry.mat_items if item.include]
            vgs  = [item.name for item in entry.vg_items  if item.include]
            indices = sorted(_resolve_vertex_indices(obj, vgs, mats))
            output[entry.entry_name] = {"vertex_indices": indices}

        try:
            with open(self.filepath, 'w', encoding='utf-8') as fh:
                json.dump(output, fh, indent=4, ensure_ascii=False)
        except Exception as exc:
            self.report({'ERROR'}, f"Could not write file: {exc}")
            return {'CANCELLED'}

        self.report({'INFO'}, f"Exported vertex indices for {len(settings.entries)} entries.")
        return {'FINISHED'}
