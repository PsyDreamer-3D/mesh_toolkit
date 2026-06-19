# SPDX-License-Identifier: GPL-2.0-or-later

from bpy.props import BoolProperty, CollectionProperty, IntProperty, StringProperty
from bpy.types import PropertyGroup


class SKX_ShapeKeyItem(PropertyGroup):
    """One row in the shape-key selection UIList."""
    # 'name' is inherited from PropertyGroup; it stores the key-block name.
    include: BoolProperty(
        name="Include",
        description="Mark this shape key for export",
        default=True,
    )
    is_basis: BoolProperty(
        name="Is Basis",
        description="This entry is the reference (Basis) key",
        default=False,
    )


class SKX_Settings(PropertyGroup):
    """Scene-level settings for the Shape Key Exporter."""

    obj_prefix: StringProperty(
        name="Prefix",
        description="Prepend this string to every exported object name",
        default="",
    )
    obj_suffix: StringProperty(
        name="Suffix",
        description="Append this string to every exported object name",
        default="",
    )

    use_collection: BoolProperty(
        name="Group in Collection",
        description="Place all exported objects into a dedicated collection",
        default=True,
    )
    collection_name: StringProperty(
        name="Collection Name",
        description=(
            "Name for the destination collection. "
            "Defaults to '<source_object>_shape_keys' when left blank"
        ),
        default="",
    )

    copy_transform: BoolProperty(
        name="Match Source Transform",
        description="Apply the source object's world matrix to each exported object",
        default=True,
    )
    copy_materials: BoolProperty(
        name="Copy Materials",
        description="Reference the same materials as the source object",
        default=True,
    )

    key_items: CollectionProperty(type=SKX_ShapeKeyItem)
    key_items_index: IntProperty(default=0)
