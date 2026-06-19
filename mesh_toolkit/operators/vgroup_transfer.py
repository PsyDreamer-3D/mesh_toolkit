# SPDX-License-Identifier: GPL-2.0-or-later

import mathutils
import bpy
from bpy.types import Operator


class VGT_OT_PopulateList(Operator):
    """Rebuild the vertex-group list from the chosen source object"""

    bl_idname = "vgt.populate_list"
    bl_label = "Refresh List"
    bl_description = "Rebuild the vertex-group list from the source object"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        src = context.scene.vgt_settings.source_object
        return src is not None and src.type == 'MESH'

    def execute(self, context):
        settings = context.scene.vgt_settings
        settings.group_items.clear()
        for vg in settings.source_object.vertex_groups:
            item = settings.group_items.add()
            item.name = vg.name
            item.include = True
        return {'FINISHED'}


class VGT_OT_SelectAll(Operator):
    """Mark every vertex group in the list for transfer"""

    bl_idname = "vgt.select_all"
    bl_label = "Select All"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return len(context.scene.vgt_settings.group_items) > 0

    def execute(self, context):
        for item in context.scene.vgt_settings.group_items:
            item.include = True
        return {'FINISHED'}


class VGT_OT_SelectNone(Operator):
    """Unmark every vertex group in the list"""

    bl_idname = "vgt.select_none"
    bl_label = "Select None"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return len(context.scene.vgt_settings.group_items) > 0

    def execute(self, context):
        for item in context.scene.vgt_settings.group_items:
            item.include = False
        return {'FINISHED'}


class VGT_OT_Transfer(Operator):
    """Transfer selected vertex groups from the source object to the active object.
Nearest Vertex uses a KD-tree spatial lookup; Topology requires identical vertex counts."""

    bl_idname = "vgt.transfer"
    bl_label = "Transfer Vertex Groups"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        dst = context.active_object
        if dst is None or dst.type != 'MESH' or context.mode != 'OBJECT':
            return False
        src = context.scene.vgt_settings.source_object
        return src is not None and src.type == 'MESH' and src != dst

    def execute(self, context):
        settings = context.scene.vgt_settings
        dst_obj   = context.active_object
        src_obj   = settings.source_object
        src_mesh  = src_obj.data
        dst_mesh  = dst_obj.data

        # Decide which groups to transfer.
        if settings.group_items:
            names = [item.name for item in settings.group_items if item.include]
        else:
            names = [vg.name for vg in src_obj.vertex_groups]

        if not names:
            self.report({'WARNING'}, "No vertex groups selected for transfer.")
            return {'CANCELLED'}

        # ------------------------------------------------------------------
        # Build a per-destination-vertex → source-vertex index map.
        # ------------------------------------------------------------------
        if settings.vert_mapping == 'TOPOLOGY':
            if len(src_mesh.vertices) != len(dst_mesh.vertices):
                self.report(
                    {'ERROR'},
                    f"Topology mode requires identical vertex counts "
                    f"(source: {len(src_mesh.vertices)}, "
                    f"destination: {len(dst_mesh.vertices)}).",
                )
                return {'CANCELLED'}
            vert_map = list(range(len(dst_mesh.vertices)))
        else:
            # Nearest vertex via KD-tree, optionally in world space.
            if settings.use_object_transform:
                src_mat = src_obj.matrix_world
                dst_mat = dst_obj.matrix_world
            else:
                src_mat = dst_mat = mathutils.Matrix.Identity(4)

            kd = mathutils.kdtree.KDTree(len(src_mesh.vertices))
            for i, v in enumerate(src_mesh.vertices):
                kd.insert(src_mat @ v.co, i)
            kd.balance()

            vert_map = [
                kd.find(dst_mat @ v.co)[1]   # index of nearest source vertex
                for v in dst_mesh.vertices
            ]

        # ------------------------------------------------------------------
        # Pre-build a weight lookup for each requested group.
        # Iterating src_mesh.vertices once is far faster than calling
        # VertexGroup.weight() per vertex (which does a linear search each time).
        # Layout: src_weights[group_name][src_vert_index] = weight
        # ------------------------------------------------------------------
        group_name_set = set(names)
        src_weights: dict[str, dict[int, float]] = {n: {} for n in names
                                                     if src_obj.vertex_groups.get(n)}
        missing = [n for n in names if src_obj.vertex_groups.get(n) is None]

        # Build a fast index→name lookup for source groups.
        src_idx_to_name = {vg.index: vg.name for vg in src_obj.vertex_groups}

        for v in src_mesh.vertices:
            for ge in v.groups:
                gname = src_idx_to_name.get(ge.group)
                if gname in group_name_set and gname in src_weights:
                    src_weights[gname][v.index] = ge.weight

        # ------------------------------------------------------------------
        # Write weights onto the destination object.
        # For Replace semantics: remove any existing same-named group first
        # so old weights on vertices that map to unweighted source verts are
        # cleared, then recreate and populate.
        # ------------------------------------------------------------------
        transferred = 0

        for name, weight_map in src_weights.items():
            existing = dst_obj.vertex_groups.get(name)
            if existing is not None:
                dst_obj.vertex_groups.remove(existing)

            dst_vg = dst_obj.vertex_groups.new(name=name)

            for dst_idx, src_idx in enumerate(vert_map):
                weight = weight_map.get(src_idx, 0.0)
                if weight > 0.0:
                    dst_vg.add([dst_idx], weight, 'REPLACE')

            transferred += 1

        # ------------------------------------------------------------------
        # Report
        # ------------------------------------------------------------------
        msg = f"Transferred {transferred} vertex group(s)"
        if missing:
            msg += f"; {len(missing)} not found on source: {', '.join(missing)}"
        self.report({'INFO'}, msg + ".")
        return {'FINISHED'}
