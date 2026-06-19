# SPDX-License-Identifier: GPL-2.0-or-later

import json
import os

import bpy
from bpy.props import BoolProperty, EnumProperty, StringProperty
from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper, ImportHelper

_COLOR_FORMAT_VERSION = "1.0"
_FLOAT_PRECISION = 6


def _round_color(color):
    return [round(c, _FLOAT_PRECISION) for c in color]


def _collect_attributes(mesh, mode):
    if mode == 'ACTIVE':
        active = mesh.color_attributes.active_color
        return [active] if active else []
    return list(mesh.color_attributes)


def _is_mesh_obj(context):
    obj = context.active_object
    return obj is not None and obj.type == 'MESH' and context.mode == 'OBJECT'


class COLORATTR_OT_export(Operator, ExportHelper):
    """Export mesh color attributes to a JSON file"""

    bl_idname = "color_attr.export"
    bl_label = "Export Color Attributes"
    bl_options = {'REGISTER'}

    filename_ext = ".json"
    filter_glob: StringProperty(default="*.json", options={'HIDDEN'})

    export_mode: EnumProperty(
        name="Export",
        items=[
            ('ALL', "All Attributes", "Export every color attribute on the mesh"),
            ('ACTIVE', "Active Only", "Export only the active render color attribute"),
        ],
        default='ALL',
    )

    @classmethod
    def poll(cls, context):
        return _is_mesh_obj(context)

    def execute(self, context):
        obj = context.active_object
        mesh = obj.data

        attrs = _collect_attributes(mesh, self.export_mode)
        if not attrs:
            self.report({'WARNING'}, "No color attributes to export.")
            return {'CANCELLED'}

        payload = {
            "format_version": _COLOR_FORMAT_VERSION,
            "source_object": obj.name,
            "source_mesh": mesh.name,
            "vertex_count": len(mesh.vertices),
            "loop_count": len(mesh.loops),
            "color_attributes": [
                {
                    "name": attr.name,
                    "domain": attr.domain,
                    "data_type": attr.data_type,
                    "colors": [_round_color(d.color) for d in attr.data],
                }
                for attr in attrs
            ],
        }

        try:
            with open(self.filepath, 'w') as fh:
                json.dump(payload, fh, indent=2)
        except Exception as exc:
            self.report({'ERROR'}, f"Could not write file: {exc}")
            return {'CANCELLED'}

        self.report(
            {'INFO'},
            f"Exported {len(attrs)} attribute(s) → {os.path.basename(self.filepath)}",
        )
        return {'FINISHED'}


class COLORATTR_OT_import(Operator, ImportHelper):
    """Import color attributes from a JSON file onto the active mesh"""

    bl_idname = "color_attr.import"
    bl_label = "Import Color Attributes"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = ".json"
    filter_glob: StringProperty(default="*.json", options={'HIDDEN'})

    on_conflict: EnumProperty(
        name="On Conflict",
        items=[
            ('REPLACE', "Replace", "Overwrite an existing attribute of the same name"),
            ('SKIP', "Skip", "Leave the existing attribute untouched"),
            ('RENAME', "Rename", "Import under a new name (e.g. Col.001)"),
        ],
        default='REPLACE',
    )

    validate_topology: BoolProperty(
        name="Validate Topology",
        description="Abort if vertex/loop counts do not match the export source",
        default=True,
    )

    @classmethod
    def poll(cls, context):
        return _is_mesh_obj(context)

    def execute(self, context):
        obj = context.active_object
        mesh = obj.data

        try:
            with open(self.filepath, 'r') as fh:
                data = json.load(fh)
        except Exception as exc:
            self.report({'ERROR'}, f"Could not read file: {exc}")
            return {'CANCELLED'}

        if self.validate_topology:
            file_verts = data.get("vertex_count")
            file_loops = data.get("loop_count")
            if file_verts != len(mesh.vertices) or file_loops != len(mesh.loops):
                self.report(
                    {'ERROR'},
                    f"Topology mismatch: file has {file_verts}v/{file_loops}l, "
                    f"mesh has {len(mesh.vertices)}v/{len(mesh.loops)}l.",
                )
                return {'CANCELLED'}

        imported = skipped = 0

        for attr_data in data.get("color_attributes", []):
            name = attr_data["name"]
            domain = attr_data["domain"]
            data_type = attr_data["data_type"]
            colors = attr_data["colors"]

            existing = mesh.color_attributes.get(name)

            if existing is not None:
                if self.on_conflict == 'SKIP':
                    skipped += 1
                    continue
                elif self.on_conflict == 'REPLACE':
                    mesh.color_attributes.remove(existing)
                elif self.on_conflict == 'RENAME':
                    base = name
                    i = 1
                    while mesh.color_attributes.get(name):
                        name = f"{base}.{i:03d}"
                        i += 1

            attr = mesh.color_attributes.new(name=name, type=data_type, domain=domain)
            for i, entry in enumerate(attr.data):
                entry.color = colors[i]

            imported += 1

        self.report({'INFO'}, f"Imported {imported} attribute(s), skipped {skipped}.")
        return {'FINISHED'}


class COLORATTR_OT_inspect(Operator, ImportHelper):
    """Preview a color attribute JSON file without applying it to the mesh"""

    bl_idname = "color_attr.inspect"
    bl_label = "Inspect JSON File…"
    bl_options = {'REGISTER'}

    filename_ext = ".json"
    filter_glob: StringProperty(default="*.json", options={'HIDDEN'})

    def execute(self, context):
        try:
            with open(self.filepath, 'r') as fh:
                data = json.load(fh)
        except Exception as exc:
            self.report({'ERROR'}, f"Could not read file: {exc}")
            return {'CANCELLED'}

        print("\n--- Color Attribute JSON Inspect ---")
        print(f"  File        : {os.path.basename(self.filepath)}")
        print(f"  Source obj  : {data.get('source_object', '?')}")
        print(f"  Vertex count: {data.get('vertex_count', '?')}")
        print(f"  Loop count  : {data.get('loop_count', '?')}")

        attrs = data.get("color_attributes", [])
        print(f"  Attributes  : {len(attrs)}")
        for a in attrs:
            print(
                f"    · {a['name']}  "
                f"[{a['domain']} / {a['data_type']}]  "
                f"{len(a['colors'])} samples"
            )
        print("------------------------------------\n")

        self.report(
            {'INFO'},
            f"{os.path.basename(self.filepath)}: "
            f"{len(attrs)} attribute(s) — see System Console for details.",
        )
        return {'FINISHED'}


class COLORATTR_OT_clear_all(Operator):
    """Remove all color attributes from the active mesh"""

    bl_idname = "color_attr.clear_all"
    bl_label = "Clear All Color Attributes"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (
            obj is not None
            and obj.type == 'MESH'
            and context.mode == 'OBJECT'
            and len(obj.data.color_attributes) > 0
        )

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        mesh = context.active_object.data
        count = len(mesh.color_attributes)
        while mesh.color_attributes:
            mesh.color_attributes.remove(mesh.color_attributes[0])
        self.report({'INFO'}, f"Removed {count} color attribute(s).")
        return {'FINISHED'}
