# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.0] - 2026-06-19

### Added
- **Geometry Separation** — separate the active mesh into named child objects
  driven by a JSON config file mapping group names to vertex groups and/or
  material substrings; faces are removed from the parent after separation.
- **Check JSON vs Mesh** — dry-run validation operator that writes a per-group
  match/miss report (with near-miss suggestions) to a Text Editor block.
- **Color Attribute I/O** — export all or the active color attribute to JSON
  with vertex/loop topology metadata; import back with Replace / Skip / Rename
  conflict resolution and optional topology validation.
- **Color Attribute Inspect** — preview a color attribute JSON file in the
  System Console without modifying the mesh.
- **Clear All Color Attributes** — batch-remove every color attribute from the
  active mesh (with confirmation dialog).
- **Material Swap** — batch-swap material slots by source/target prefix with a
  live preview of each pairing and an eyedropper to fill the target prefix from
  the active object name.
- **Shape Key Export** — export selected shape keys as standalone mesh objects
  using `bmesh` (no `bpy.ops`); supports prefix/suffix naming, destination
  collection, and optional transform/material copying.
- `blender_manifest.toml` for Blender 5.x Extensions compatibility.

[Unreleased]: https://github.com/psydreamer-3d/mesh_toolkit/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/psydreamer-3d/mesh_toolkit/releases/tag/v1.1.0
