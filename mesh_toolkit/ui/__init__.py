# SPDX-License-Identifier: GPL-2.0-or-later

from .panels import (
    SKX_UL_ShapeKeys,
    VGT_UL_Groups,
    MESH_PT_separate,
    COLORATTR_PT_panel,
    MATSWAP_PT_panel,
    SKX_PT_panel,
    VGT_PT_panel,
)

classes = (
    SKX_UL_ShapeKeys,
    VGT_UL_Groups,
    MESH_PT_separate,
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
