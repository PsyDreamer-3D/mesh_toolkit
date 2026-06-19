# SPDX-License-Identifier: GPL-2.0-or-later

from .mat_swap import MatSwapProperties
from .shape_key_export import SKX_ShapeKeyItem, SKX_Settings

classes = (
    MatSwapProperties,
    SKX_ShapeKeyItem,
    SKX_Settings,
)


def register():
    import bpy
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.mat_swap = bpy.props.PointerProperty(type=MatSwapProperties)
    bpy.types.Scene.skx_settings = bpy.props.PointerProperty(type=SKX_Settings)


def unregister():
    import bpy
    if hasattr(bpy.types.Scene, "skx_settings"):
        del bpy.types.Scene.skx_settings
    if hasattr(bpy.types.Scene, "mat_swap"):
        del bpy.types.Scene.mat_swap
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
