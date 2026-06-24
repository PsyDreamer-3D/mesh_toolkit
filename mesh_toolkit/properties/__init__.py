# SPDX-License-Identifier: GPL-2.0-or-later

from .geometry_separation_builder import (
    GSB_MaterialItem,
    GSB_VertexGroupItem,
    GSB_ObjectEntry,
    GSB_Settings,
)
from .mat_swap import MatSwapProperties
from .shape_key_export import SKX_ShapeKeyItem, SKX_Settings
from .vgroup_transfer import VGT_GroupItem, VGT_Settings

classes = (
    # inner before outer (CollectionProperty references)
    GSB_MaterialItem,
    GSB_VertexGroupItem,
    GSB_ObjectEntry,
    GSB_Settings,
    MatSwapProperties,
    SKX_ShapeKeyItem,
    SKX_Settings,
    VGT_GroupItem,
    VGT_Settings,
)


def register():
    import bpy
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.gsb_settings = bpy.props.PointerProperty(type=GSB_Settings)
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
    if hasattr(bpy.types.Scene, "gsb_settings"):
        del bpy.types.Scene.gsb_settings
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
