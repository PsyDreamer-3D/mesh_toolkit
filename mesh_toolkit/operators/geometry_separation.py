# SPDX-License-Identifier: GPL-2.0-or-later

import json
import os

import bmesh
import bpy
from bpy.props import StringProperty
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper

from ..core.utils import _write_report


class MESH_OT_separate_by_json(Operator, ImportHelper):
    """Separate the active mesh into child objects whose geometry is
defined by vertex groups and/or materials in a JSON config file"""

    bl_idname = "mesh.separate_by_json"
    bl_label = "Separate by JSON…"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = ".json"
    filter_glob: StringProperty(default="*.json", options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (
            obj is not None
            and obj.type == 'MESH'
            and context.mode == 'OBJECT'
        )

    def execute(self, context):
        try:
            with open(self.filepath, 'r') as fh:
                config = json.load(fh)
        except Exception as exc:
            self.report({'ERROR'}, f"Could not load JSON: {exc}")
            return {'CANCELLED'}

        groups = {k: v for k, v in config.items() if not k.startswith('_')}

        if not groups:
            self.report({'ERROR'}, "JSON contains no valid group definitions.")
            return {'CANCELLED'}

        original_obj  = context.active_object
        original_mesh = original_obj.data
        original_name = original_obj.name
        warnings: list[str] = []
        created_objects: list[str] = []

        all_separated_face_indices: set[int] = set()

        for group_name, group_data in groups.items():
            vertex_group_names: list[str] = group_data.get("vertex_groups", [])
            material_names: list[str]     = group_data.get("materials", [])

            if not vertex_group_names and not material_names:
                warnings.append(
                    f"'{group_name}': no vertex_groups or materials defined — skipped."
                )
                continue

            vg_indices = {
                vg.index
                for vg in original_obj.vertex_groups
                if vg.name in vertex_group_names
            }

            verts_in_groups: set[int] = set()
            for v in original_mesh.vertices:
                for g in v.groups:
                    if g.group in vg_indices and g.weight >= 1.0:
                        verts_in_groups.add(v.index)
                        break

            mat_name_set = set(material_names)

            group_face_indices: set[int] = set()
            for poly in original_mesh.polygons:
                if any(vi in verts_in_groups for vi in poly.vertices):
                    group_face_indices.add(poly.index)
                    continue
                mat_name = None
                if poly.material_index < len(original_obj.material_slots):
                    slot_mat = original_obj.material_slots[poly.material_index].material
                    if slot_mat:
                        mat_name = slot_mat.name
                if mat_name is not None and any(req in mat_name for req in mat_name_set):
                    group_face_indices.add(poly.index)

            if not group_face_indices:
                found_mats = {
                    s.material.name
                    for s in original_obj.material_slots
                    if s.material
                }
                found_vgs = {vg.name for vg in original_obj.vertex_groups}
                missing_mats = {
                    req for req in mat_name_set
                    if not any(req in m for m in found_mats)
                }
                missing_vgs = set(vertex_group_names) - found_vgs
                detail_parts = []
                if missing_mats:
                    detail_parts.append("materials not found: " + ", ".join(sorted(missing_mats)))
                if missing_vgs:
                    detail_parts.append("vertex groups not found: " + ", ".join(sorted(missing_vgs)))
                if not missing_mats and not missing_vgs:
                    detail_parts.append(
                        "names exist on mesh but no faces matched "
                        "(check weight threshold or empty slots)"
                    )
                warnings.append(
                    f"'{group_name}': no matching geometry — "
                    + "; ".join(detail_parts)
                )
                continue

            child_vert_indices: set[int] = set()
            for fi in group_face_indices:
                for vi in original_mesh.polygons[fi].vertices:
                    child_vert_indices.add(vi)

            child_mesh = original_mesh.copy()
            bm = bmesh.new()
            bm.from_mesh(child_mesh)
            bm.verts.ensure_lookup_table()

            drop = [v for v in bm.verts if v.index not in child_vert_indices]
            if drop:
                bmesh.ops.delete(bm, geom=drop, context='VERTS')

            loose = [e for e in bm.edges if not e.link_faces]
            if loose:
                bmesh.ops.delete(bm, geom=loose, context='EDGES')

            bm.to_mesh(child_mesh)
            bm.free()
            child_mesh.update()

            child_name = f"{original_name}_{group_name}"
            child_mesh.name = child_name
            child_obj = bpy.data.objects.new(child_name, child_mesh)
            child_obj.matrix_world = original_obj.matrix_world.copy()

            for vg in original_obj.vertex_groups:
                child_obj.vertex_groups.new(name=vg.name)

            for col in original_obj.users_collection:
                col.objects.link(child_obj)

            child_obj.parent = original_obj
            child_obj.matrix_parent_inverse = original_obj.matrix_world.inverted()

            all_separated_face_indices.update(group_face_indices)
            created_objects.append(child_name)

        if all_separated_face_indices:
            all_poly_indices = set(range(len(original_mesh.polygons)))
            remaining_face_indices = all_poly_indices - all_separated_face_indices

            parent_keep_verts: set[int] = set()
            for fi in remaining_face_indices:
                for vi in original_mesh.polygons[fi].vertices:
                    parent_keep_verts.add(vi)

            bm = bmesh.new()
            bm.from_mesh(original_mesh)
            bm.verts.ensure_lookup_table()

            drop = [v for v in bm.verts if v.index not in parent_keep_verts]
            if drop:
                bmesh.ops.delete(bm, geom=drop, context='VERTS')

            loose = [e for e in bm.edges if not e.link_faces]
            if loose:
                bmesh.ops.delete(bm, geom=loose, context='EDGES')

            bm.to_mesh(original_mesh)
            bm.free()
            original_mesh.update()

        context.view_layer.objects.active = original_obj

        for w in warnings:
            self.report({'WARNING'}, w)

        if created_objects:
            self.report(
                {'INFO'},
                f"Created {len(created_objects)} child object(s): "
                + ", ".join(created_objects),
            )
        else:
            all_mats = sorted(
                s.material.name
                for s in original_obj.material_slots
                if s.material
            )
            all_vgs = sorted(vg.name for vg in original_obj.vertex_groups)
            lines = [
                "=== Separate by JSON: nothing created ===",
                f"  Object         : {original_name}",
                f"  Material slots ({len(all_mats)}):",
            ]
            lines += [f"    {m}" for m in all_mats] or ["    (none)"]
            lines += [f"  Vertex groups ({len(all_vgs)}):"]
            lines += [f"    {v}" for v in all_vgs] or ["    (none)"]
            lines += ["", "  Run 'Check JSON vs Mesh' for a full per-group report."]
            _write_report(context, "Mesh Toolkit — Separate Log", lines)
            self.report(
                {'WARNING'},
                f"Nothing created — mesh has {len(all_mats)} material(s) and "
                f"{len(all_vgs)} VG(s). See Text Editor → "
                f"'Mesh Toolkit — Separate Log'.",
            )

        return {'FINISHED'}


class MESH_OT_check_separation_json(Operator, ImportHelper):
    """Compare a separation JSON against the active mesh.
Reports which material and vertex group names match and which are missing.
Results are written to a text block readable in Blender's Text Editor."""

    bl_idname = "mesh.check_separation_json"
    bl_label = "Check JSON vs Mesh…"
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
        )

    def execute(self, context):
        obj = context.active_object

        try:
            with open(self.filepath, 'r') as fh:
                config = json.load(fh)
        except Exception as exc:
            self.report({'ERROR'}, f"Could not load JSON: {exc}")
            return {'CANCELLED'}

        groups = {k: v for k, v in config.items() if not k.startswith('_')}

        mesh_mats: set[str] = {
            s.material.name for s in obj.material_slots if s.material
        }
        mesh_vgs: set[str] = {vg.name for vg in obj.vertex_groups}

        lines: list[str] = [
            "=== Check JSON vs Mesh ===",
            f"  Object  : {obj.name}",
            f"  File    : {os.path.basename(self.filepath)}",
            "",
            f"  Material slots on mesh ({len(mesh_mats)}):",
        ]
        lines += [f"    {n}" for n in sorted(mesh_mats)] or ["    (none)"]
        lines += ["", f"  Vertex groups on mesh ({len(mesh_vgs)}):"]
        lines += [f"    {n}" for n in sorted(mesh_vgs)] or ["    (none)"]

        total_issues = 0
        lines += ["", f"  --- Per-group ({len(groups)} groups) ---"]

        for group_name, group_data in groups.items():
            vg_names:  list[str] = group_data.get("vertex_groups", [])
            mat_names: list[str] = group_data.get("materials", [])
            lines.append(f"\n  [{group_name}]")

            for vg in vg_names:
                ok = vg in mesh_vgs
                lines.append(f"    VG  {'OK ' if ok else 'MISS'}: {vg!r}")
                if not ok:
                    close = [
                        n for n in mesh_vgs
                        if vg.lower() in n.lower() or n.lower() in vg.lower()
                    ]
                    if close:
                        lines.append(f"         ^ similar on mesh: {close}")
                    total_issues += 1

            for mat in mat_names:
                matched = [m for m in mesh_mats if mat in m]
                ok = bool(matched)
                lines.append(f"    Mat {'OK ' if ok else 'MISS'}: {mat!r}")
                if ok:
                    lines.append(f"         ^ resolves to: {matched}")
                else:
                    close = [
                        n for n in mesh_mats
                        if mat.lower() in n.lower() or n.lower() in mat.lower()
                    ]
                    if close:
                        lines.append(f"         ^ similar on mesh: {close}")
                    total_issues += 1

        lines += ["", "========================="]

        text_name = "Mesh Toolkit — JSON Check"
        _write_report(context, text_name, lines)

        if total_issues:
            self.report(
                {'WARNING'},
                f"{total_issues} name(s) not found — see Text Editor "
                f"→ '{text_name}'.",
            )
        else:
            self.report(
                {'INFO'},
                f"All names matched — see Text Editor → '{text_name}'.",
            )

        return {'FINISHED'}
