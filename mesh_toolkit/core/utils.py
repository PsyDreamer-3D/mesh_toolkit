# SPDX-License-Identifier: GPL-2.0-or-later

import bpy

_TAB = "Mesh Tools"


def _resolve_vertex_indices(obj, vg_names: list, mat_names: list) -> frozenset:
    """Return vertex indices (weight ≥ 1.0 in vg_names OR on faces using mat_names)."""
    mesh = obj.data

    vg_indices = {vg.index for vg in obj.vertex_groups if vg.name in vg_names}
    verts_in_groups: set = set()
    for v in mesh.vertices:
        for g in v.groups:
            if g.group in vg_indices and g.weight >= 1.0:
                verts_in_groups.add(v.index)
                break

    mat_name_set = set(mat_names)
    face_verts: set = set()
    for poly in mesh.polygons:
        if any(vi in verts_in_groups for vi in poly.vertices):
            for vi in poly.vertices:
                face_verts.add(vi)
            continue
        mat_name = None
        if poly.material_index < len(obj.material_slots):
            slot_mat = obj.material_slots[poly.material_index].material
            if slot_mat:
                mat_name = slot_mat.name
        if mat_name is not None and any(req in mat_name for req in mat_name_set):
            for vi in poly.vertices:
                face_verts.add(vi)

    return frozenset(face_verts)


def _write_report(context, text_name: str, lines: list[str]) -> None:
    """Write *lines* to a bpy.data.texts block and focus any open Text Editor on it."""
    if text_name in bpy.data.texts:
        tb = bpy.data.texts[text_name]
        tb.clear()
    else:
        tb = bpy.data.texts.new(text_name)
    tb.write("\n".join(lines))
    for area in context.screen.areas:
        if area.type == 'TEXT_EDITOR':
            area.spaces.active.text = tb
            break
