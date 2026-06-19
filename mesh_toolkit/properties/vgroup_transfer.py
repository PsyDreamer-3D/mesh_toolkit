# SPDX-License-Identifier: GPL-2.0-or-later

import bpy
from bpy.props import BoolProperty, CollectionProperty, EnumProperty, IntProperty, PointerProperty
from bpy.types import PropertyGroup


class VGT_GroupItem(PropertyGroup):
    """One row in the vertex-group selection UIList."""
    # 'name' is inherited from PropertyGroup; it stores the vertex group name.
    include: BoolProperty(
        name="Include",
        description="Transfer this vertex group",
        default=True,
    )


class VGT_Settings(PropertyGroup):
    """Scene-level settings for the Vertex Group Transfer operator."""

    source_object: PointerProperty(
        name="Source Object",
        description="Object to copy vertex groups from",
        type=bpy.types.Object,
    )

    vert_mapping: EnumProperty(
        name="Vertex Mapping",
        description="How source vertices are mapped onto the destination mesh",
        items=[
            ('NEAREST',   "Nearest Vertex", "Map each destination vertex to the closest source vertex (KD-tree)"),
            ('TOPOLOGY',  "Topology",       "1-to-1 index mapping — requires identical vertex counts"),
        ],
        default='NEAREST',
    )

    use_object_transform: BoolProperty(
        name="Use Object Transform",
        description="Account for each object's world-space transform when evaluating distances",
        default=True,
    )

    group_items: CollectionProperty(type=VGT_GroupItem)
    group_items_index: IntProperty(default=0)
