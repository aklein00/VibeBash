# MayaScripts

Custom Maya shelf tools for the AK_Shelf. Each tool is a standalone Python module with a `run()` entry point.

## Quick Start

**Rebuild entire shelf** — paste in Maya Script Editor (Python tab):
```python
exec(open('/Users/arthurklein/Documents/Work/Side/VibeBash/MayaScripts/rebuild_ak_shelf.py').read())
```

**Run any tool manually** (without shelf):
```python
import sys
sys.path.append('/Users/arthurklein/Documents/Work/Side/VibeBash/MayaScripts')

from CombinePlus import combine_plus
combine_plus.run()
```

---

## Import / Export

| Label | Tool | Description |
|-------|------|-------------|
| `FBatch` | **BatchGroupExporter** | Full UI for managing export groups and batch FBX exporting. Lives in Maya scripts directory (external). |
| `XFBX` | **BatchExportFBX** | Export each selected transform as an individual FBX to `~/Downloads/Exports from Maya/`. FBX 2020, embeds textures. |
| `BImp` | **BatchImport** | Multi-select file dialog to import multiple files (FBX, OBJ, MA, MB, ABC, USD) at once. |

```python
from maya_batch_group_exporter import show_batch_exporter; show_batch_exporter()
from BatchExportFBX import batch_export_fbx; batch_export_fbx.run()
from BatchImport import batch_import; batch_import.run()
```

## Pivot

| Label | Tool | Description |
|-------|------|-------------|
| `CtrPvt` | **CenterPivot** | Center pivot on each selected object. |
| `Pvt0` | **PivotToOrigin** | Move pivot to world origin (0,0,0) without moving geometry. |

```python
from CenterPivot import center_pivot; center_pivot.run()
from PivotToOrigin import pivot_to_origin; pivot_to_origin.run()
```

## Modeling

| Label | Tool | Description |
|-------|------|-------------|
| `Comb+` | **CombinePlus** | Combine 2+ meshes, merge verts (0.001), delete history, freeze transforms. Names result after first selection. |
| `DupEx` | **DupeExtract** | Duplicate selected faces as a new separate mesh. Deletes history, freezes transforms. |
| `MirWld` | **MirrorWeld** | Auto-detect mirror direction, mirror across X, combine, weld center verts, soften normals. Deletes history, freezes, pivots to origin. |
| `MirX` | **MirrorX** | Mirror object over X axis. Verifies pivot at origin, scales X by -1, fixes normals, deletes history, freezes transforms. |
| `Merge` | *(built-in)* | Merge selected vertices (0.001 threshold). |
| `MrgCtr` | *(built-in)* | Merge selected vertices to their center point. |
| `CEVrt` | **CollapseEdgeVerts** | Convert selected edges to vertices, merge them to center. |
| `Collps` | *(built-in)* | Collapse selected edges/faces. |
| `FNScl` | **FaceNormalScale** | Move selected faces along their normals. Popup with slider (-2.0 to 2.0, default 0.1). |
| `AsMat` | **AssignCommonMaterial** | Find the most-used material on a mesh and assign it to the entire mesh. |

```python
from CombinePlus import combine_plus; combine_plus.run()
from DupeExtract import dupe_extract; dupe_extract.run()
from MirrorWeld import mirror_weld; mirror_weld.run()
from FaceNormalScale import face_normal_scale
face_normal_scale.run(offset=0.1)   # Direct
face_normal_scale.run_with_ui()     # Slider popup
from AssignCommonMaterial import assign_common_material; assign_common_material.run()
from CollapseEdgeVerts import collapse_edge_verts; collapse_edge_verts.run()
from MirrorX import mirror_x; mirror_x.run()
```

## Edge / Normals

| Label | Tool | Description |
|-------|------|-------------|
| `EdgeAvg` | **EdgeAverager** | Average 3+ parallel edges with volume-preserving surface sliding. Has UI mode for angle threshold and influence distance. |
| `ENClean` | **EdgeNormalsClean** | Harden selected edges, soften all others on the mesh. |
| `Hard` | *(built-in)* | Harden selected edges (angle 0). |
| `Soft` | *(built-in)* | Soften selected edges (angle 180). |

```python
import EdgeAverager
EdgeAverager.run()          # Direct
EdgeAverager.run_with_ui()  # With sliders
from EdgeNormalsClean import edge_normals_clean; edge_normals_clean.run()
```

## Retopology

| Label | Tool | Description |
|-------|------|-------------|
| `Retopo` | **WGLLRetopo** | Curvature-guided retopology. Analyzes sculpt curvature, marks hard edge guides, runs polyRetopo. Presets for hero, NPC, props. |

```python
import WGLLRetopo
WGLLRetopo.run()            # Quick retopo
WGLLRetopo.run_with_ui()    # UI with sliders and presets
```
> Core library lives in `VibeBash/WGLL_Retopo/`. Requires `scipy` and `trimesh`: `mayapy -m pip install scipy trimesh`

## UV / Texture

| Label | Tool | Description |
|-------|------|-------------|
| `RldTx` | **ReloadTexture** | Force-reload all file textures on selected mesh from disk. Useful after editing in Photoshop/Substance. |
| `UVNav` | **UVAtlasNav** | Move UV shells on a 16x16 color atlas. D-pad navigation with wrapping + random placement. |
| `UVx` | **UVProject** | Planar UV projection along X axis. Stacks shells, fits inside one 16x16 atlas cell at (8,8). |
| `UVy` | **UVProject** | Planar UV projection along Y axis. Same atlas cell placement. |
| `UVz` | **UVProject** | Planar UV projection along Z axis. Same atlas cell placement. |
| `FaceUV` | **FaceUVManager** | Expression atlas UV management on 8x8 grid. D-pad navigation, eye L/R linking, presets. |

```python
from ReloadTexture import reload_texture; reload_texture.run()
from UVAtlasNav import uv_atlas_nav; uv_atlas_nav.run()  # Opens navigator window
from UVProject import uv_project; uv_project.run(axis='x')  # or 'y' or 'z'
from FaceUVManager import face_uv_manager; mgr = face_uv_manager.FaceUVManager(); mgr.show()
```

---

## Adding New Tools

1. Copy `_template/tool_template.py` to `MayaScripts/YourTool/your_tool.py`
2. Edit constants: `TOOL_NAME`, `TOOL_LABEL`, `TOOL_ICON`
3. Implement logic in `run()`
4. Add entry to `rebuild_ak_shelf.py`
5. Update this README

## Project Structure

```
MayaScripts/
├── README.md                  <- This file
├── _template/
│   └── tool_template.py       <- Copy this for new tools
├── rebuild_ak_shelf.py        <- Run in Maya to rebuild shelf
├── icons/                     <- Custom shelf icons (256x256 PNG)
├── AssignCommonMaterial/
├── CollapseEdgeVerts/
├── MirrorX/
├── UVAtlasNav/
├── BatchExportFBX/
├── BatchImport/
├── CenterPivot/
├── CombinePlus/
├── DupeExtract/
├── EdgeAverager/
├── EdgeNormalsClean/
├── FaceNormalScale/
├── FaceUVManager/
├── MirrorWeld/
├── PivotToOrigin/
├── ReloadTexture/
├── UVProject/
└── WGLLRetopo/                <- Shelf entry (core in ../WGLL_Retopo/)
```
