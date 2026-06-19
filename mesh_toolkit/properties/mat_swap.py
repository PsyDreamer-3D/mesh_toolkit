# SPDX-License-Identifier: GPL-2.0-or-later

from bpy.props import BoolProperty, StringProperty
from bpy.types import PropertyGroup


class MatSwapProperties(PropertyGroup):
    src_prefix: StringProperty(
        name="Source Prefix",
        description="Prefix to match on existing material slots (e.g. 'Figure_')",
        default="Figure_",
    )
    target_prefix: StringProperty(
        name="Target Prefix",
        description="Replacement prefix to look up in the blend file (e.g. 'Victoria_')",
        default="",
    )
    strip_blender_suffix: BoolProperty(
        name="Strip .001 Suffix",
        description=(
            "When using the eyedropper, strip Blender's auto-appended .001-style "
            "suffix from the object name before writing it as the prefix"
        ),
        default=True,
    )
