# Mesh Toolkit

A Blender extension providing four mesh utilities in a single N-panel tab (**View3D › Sidebar › Mesh Tools**).

**Minimum requirements:** Blender 5.1 · Python 3.11

---

## Tools

### 1. Geometry Separation
Separate the active mesh into named child objects using a JSON config file that maps group names to vertex groups and/or material substrings.

- **Separate by JSON** — opens a file browser, then creates child objects and strips the assigned faces from the parent.
- **Check JSON vs Mesh** — dry-run validation; writes a per-group match/miss report to a Text Editor block.

JSON format:
```json
{
  "Head": { "vertex_groups": ["Head_VG"], "materials": ["Skin_Head"] },
  "Body": { "materials": ["Skin_Body", "Cloth"] }
}
```
Keys starting with `_` are treated as comments and ignored.

---

### 2. Color Attribute I/O
Export and import mesh color attributes as JSON so they can be transferred between blend files or backed up externally.

- **Export to JSON** — saves all attributes (or only the active one) with topology metadata for later validation.
- **Import from JSON** — restores attributes with configurable conflict resolution: Replace / Skip / Rename.
- **Inspect JSON** — prints a summary to the System Console without touching the mesh.
- **Clear All Attributes** — removes every color attribute from the active mesh (confirmation required).

---

### 3. Material Swap
Batch-swap material slots by prefix.

1. Set **Source Prefix** to the prefix currently on the mesh slots (e.g. `Figure_`).
2. Set **Target Prefix** to the replacement prefix (e.g. `Victoria_`), or click the eyedropper to fill it from the active object's name.
3. A live preview lists each `Figure_X → Victoria_X` pairing and highlights missing materials.
4. Click **Swap Materials** to apply.

---

### 4. Shape Key Export
Export selected shape keys as standalone mesh objects using the direct Python data API (no `bpy.ops`).

1. Click **Refresh** to populate the list from the active mesh.
2. Tick the keys to export (Basis is excluded by default).
3. Optionally set a prefix/suffix for the generated object names.
4. Choose a destination collection and whether to copy the source transform and materials.
5. Click **Export Shape Keys**.

---

## Installation

1. In Blender go to **Edit › Preferences › Get Extensions**.
2. Drag and drop the `mesh_toolkit` folder (or a `.zip` of it) onto the Blender window, or use **Install from Disk**.
3. The add-on will appear under **Mesh** in the Extensions list.

---

## License

GPL-2.0-or-later — see `SPDX-License-Identifier` headers in each source file.
