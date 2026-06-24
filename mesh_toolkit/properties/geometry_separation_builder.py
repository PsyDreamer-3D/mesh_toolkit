# SPDX-License-Identifier: GPL-2.0-or-later

import bpy
from bpy.props import BoolProperty, CollectionProperty, IntProperty, StringProperty
from bpy.types import PropertyGroup


class GSB_MaterialItem(PropertyGroup):
    include: BoolProperty(name="Include", default=False)


class GSB_VertexGroupItem(PropertyGroup):
    include: BoolProperty(name="Include", default=False)


class GSB_ObjectEntry(PropertyGroup):
    entry_name: StringProperty(name="Name", default="")
    mat_items:  CollectionProperty(type=GSB_MaterialItem)
    mat_index:  IntProperty(default=0)
    vg_items:   CollectionProperty(type=GSB_VertexGroupItem)
    vg_index:   IntProperty(default=0)


class GSB_Settings(PropertyGroup):
    entries:        CollectionProperty(type=GSB_ObjectEntry)
    active_index:   IntProperty(default=0)
    new_entry_name: StringProperty(name="Name", default="")
