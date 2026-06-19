# SPDX-License-Identifier: GPL-2.0-or-later

from .geometry_separation import MESH_OT_separate_by_json, MESH_OT_check_separation_json
from .color_attributes import (
    COLORATTR_OT_export,
    COLORATTR_OT_import,
    COLORATTR_OT_inspect,
    COLORATTR_OT_clear_all,
)
from .mat_swap import MATERIAL_OT_fill_prefix_from_object, MATERIAL_OT_swap_by_prefix
from .shape_key_export import (
    SKX_OT_PopulateList,
    SKX_OT_SelectAll,
    SKX_OT_SelectNone,
    SKX_OT_ExportShapeKeys,
)
from .vgroup_transfer import (
    VGT_OT_PopulateList,
    VGT_OT_SelectAll,
    VGT_OT_SelectNone,
    VGT_OT_Transfer,
)

classes = (
    MESH_OT_separate_by_json,
    MESH_OT_check_separation_json,
    COLORATTR_OT_export,
    COLORATTR_OT_import,
    COLORATTR_OT_inspect,
    COLORATTR_OT_clear_all,
    MATERIAL_OT_fill_prefix_from_object,
    MATERIAL_OT_swap_by_prefix,
    SKX_OT_PopulateList,
    SKX_OT_SelectAll,
    SKX_OT_SelectNone,
    SKX_OT_ExportShapeKeys,
    VGT_OT_PopulateList,
    VGT_OT_SelectAll,
    VGT_OT_SelectNone,
    VGT_OT_Transfer,
)


def register():
    import bpy
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    import bpy
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
