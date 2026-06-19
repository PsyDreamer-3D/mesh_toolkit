# SPDX-License-Identifier: GPL-2.0-or-later

from .mat_swap import MatSwapProperties
from .shape_key_export import SKX_ShapeKeyItem, SKX_Settings
from .vgroup_transfer import VGT_GroupItem, VGT_Settings

classes = (
    MatSwapProperties,
    SKX_ShapeKeyItem,
    SKX_Settings,
    VGT_GroupItem,   # must precede VGT_Settings (CollectionProperty reference)
    VGT_Settings,
)


def register():
    import bpy
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.mat_swap     = bpy.props.PointerProperty(type=MatSwapProperties)
    bpy.types.Scene.skx_settings = bpy.props.PointerProperty(type=SKX_Settings)
    bpy.types.Scene.vgt_settings = bpy.props.PointerProperty(type=VGT_Settings)


def unregister():
    import bpy
    if hasattr(bpy.types.Scene, "vgt_settings"):
        del bpy.types.Scene.vgt_settings
    if hasattr(bpy.types.Scene, "skx_settings"):
        del bpy.types.Scene.skx_settings
    if hasattr(bpy.types.Scene, "mat_swap"):
        del bpy.types.Scene.mat_swap
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
