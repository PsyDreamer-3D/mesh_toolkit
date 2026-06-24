# SPDX-License-Identifier: GPL-2.0-or-later

from .panels import (
    GSB_UL_Entries,
    GSB_UL_Items,
    SKX_UL_ShapeKeys,
    VGT_UL_Groups,
    MESH_PT_separate,
    MESH_PT_json_builder,
    COLORATTR_PT_panel,
    MATSWAP_PT_panel,
    SKX_PT_panel,
    VGT_PT_panel,
)

classes = (
    # UILists before panels
    GSB_UL_Entries,
    GSB_UL_Items,
    SKX_UL_ShapeKeys,
    VGT_UL_Groups,
    # parent panel before child
    MESH_PT_separate,
    MESH_PT_json_builder,
    COLORATTR_PT_panel,
    MATSWAP_PT_panel,
    SKX_PT_panel,
    VGT_PT_panel,
)


def register():
    import bpy
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    import bpy
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
