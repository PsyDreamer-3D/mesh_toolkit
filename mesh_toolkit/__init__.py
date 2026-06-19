# SPDX-License-Identifier: GPL-2.0-or-later

# START — workflow remove
_needs_reload = "bpy" in locals()
# END — workflow remove

import bpy
from . import properties, operators, ui

# START — workflow remove
if _needs_reload:
    import sys, importlib

    all_modules = dict(sorted(sys.modules.items(), key=lambda x: x[0]))

    for k, v in all_modules.items():
        if v is not None and (k == __name__ or k.startswith(__name__ + ".")):
            importlib.reload(v)

del _needs_reload
# END — workflow remove

bl_info = {
    "name": "Mesh Toolkit",
    "author": "PsyDreamer-3D",
    "version": (1, 1, 0),
    "blender": (5, 1, 0),
    "location": "View3D > Sidebar > Mesh Tools",
    "description": (
        "Combined mesh utilities: geometry separation by JSON, "
        "color attribute I/O, material prefix swapping, "
        "and shape key export."
    ),
    "category": "Mesh",
}


def register():
    properties.register()
    operators.register()
    ui.register()


def unregister():
    ui.unregister()
    operators.unregister()
    properties.unregister()


if __name__ == "__main__":
    register()
