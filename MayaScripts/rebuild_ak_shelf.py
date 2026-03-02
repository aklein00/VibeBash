"""
Rebuild AK_Shelf — Master shelf builder for all MayaScripts tools.

Run in Maya Script Editor (Python tab):
    exec(open('/Users/arthurklein/Documents/Work/Side/VibeBash/MayaScripts/rebuild_ak_shelf.py').read())

Clears and rebuilds from scratch each time to ensure correct order and separators.
Comment out any tools you don't want on the shelf.
"""

import maya.cmds as cmds
import sys
import os

SHELF_NAME = "AK_Shelf"

# Hardcoded — do NOT use __file__ (undefined when run via exec in Maya)
SCRIPTS_ROOT = '/Users/arthurklein/Documents/Work/Side/VibeBash/MayaScripts'
ICONS_DIR = os.path.join(SCRIPTS_ROOT, 'icons')

# Add MayaScripts to Python path if needed
if SCRIPTS_ROOT not in sys.path:
    sys.path.append(SCRIPTS_ROOT)


def _button_exists(label):
    """Check if a button with this label is already on the shelf."""
    if not cmds.shelfLayout(SHELF_NAME, exists=True):
        return False
    buttons = cmds.shelfLayout(SHELF_NAME, query=True, childArray=True) or []
    for btn in buttons:
        if cmds.shelfButton(btn, query=True, exists=True):
            if cmds.shelfButton(btn, query=True, label=True) == label:
                return True
    return False


def _icon(name):
    """Return full path to custom icon, or the name itself for Maya built-ins."""
    custom = os.path.join(ICONS_DIR, name)
    if os.path.exists(custom):
        return custom
    return name  # Fall back to Maya built-in icon name


def _add_button(label, annotation, icon, import_line, run_line,
                overlay_color=(0.8, 0.8, 0.8),
                overlay_bg=(0, 0, 0, 0.5)):
    """Add a single tool button to AK_Shelf."""
    command = (
        f"import sys\n"
        f"if '{SCRIPTS_ROOT}' not in sys.path:\n"
        f"    sys.path.append('{SCRIPTS_ROOT}')\n"
        f"{import_line}\n"
        f"{run_line}"
    )

    cmds.shelfButton(
        parent=SHELF_NAME,
        image=_icon(icon),
        command=command,
        annotation=annotation,
        label=label,
        imageOverlayLabel=label,
        overlayLabelColor=overlay_color,
        overlayLabelBackColor=overlay_bg,
        sourceType="python",
        width=35,
        height=35,
    )
    print(f"  [{label}] added.")


def _sep():
    """Add a visual separator on the shelf."""
    cmds.separator(parent=SHELF_NAME, style="shelf", horizontal=False, width=12, height=35)


def _clear_shelf():
    """Remove all buttons and separators from AK_Shelf for a clean rebuild."""
    if not cmds.shelfLayout(SHELF_NAME, exists=True):
        return
    children = cmds.shelfLayout(SHELF_NAME, query=True, childArray=True) or []
    for child in children:
        cmds.deleteUI(child)
    print(f"  Cleared {len(children)} items from {SHELF_NAME}")


def save_shelves():
    """Save all shelves to disk."""
    try:
        import maya.mel as mel
        mel.eval('saveAllShelves $gShelfTopLevel')
        print("All shelves saved to disk.")
    except Exception as e:
        print(f"Warning: Could not save shelves - {e}")


def rebuild():
    """Clear and rebuild all tool buttons on AK_Shelf with proper grouping."""
    print(f"\n--- Rebuilding {SHELF_NAME} ---\n")

    # Create shelf if it doesn't exist
    if not cmds.shelfLayout(SHELF_NAME, exists=True):
        cmds.shelfLayout(SHELF_NAME, parent="ShelfLayout")
        print(f"Created shelf: {SHELF_NAME}")

    # Clear existing buttons for a fresh rebuild with correct order/separators
    _clear_shelf()

    # ==========================================
    # IMPORT / EXPORT
    # ==========================================

    _add_button(
        label="FBatch",
        annotation="Batch Group Exporter UI",
        icon="batch_group_exporter.png",
        import_line=(
            "import sys as _s\\n"
            "for k in list(_s.modules.keys()):\\n"
            "    if k.startswith('maya_batch_group_exporter'): del _s.modules[k]\\n"
            "from maya_batch_group_exporter import show_batch_exporter"
        ),
        run_line="show_batch_exporter()",
    )

    _add_button(
        label="XFBX",
        annotation="Export selected objects as individual FBX files",
        icon="batch_export_fbx.png",
        import_line="from BatchExportFBX import batch_export_fbx",
        run_line="batch_export_fbx.run()",
        overlay_color=(0.1178, 0.03, 0.1129),
        overlay_bg=(0.5783, 0.4912, 0.136, 0.2),
    )

    _add_button(
        label="BImp",
        annotation="Import multiple files at once",
        icon="batch_import.png",
        import_line="from BatchImport import batch_import",
        run_line="batch_import.run()",
    )

    _sep()

    # ==========================================
    # PIVOT TOOLS
    # ==========================================

    _add_button(
        label="CtrPvt",
        annotation="Center pivot on selected objects",
        icon="center_pivot.png",
        import_line="from CenterPivot import center_pivot",
        run_line="center_pivot.run()",
    )

    _add_button(
        label="Pvt0",
        annotation="Move pivot to world origin (0, 0, 0)",
        icon="pivot_to_origin.png",
        import_line="from PivotToOrigin import pivot_to_origin",
        run_line="pivot_to_origin.run()",
    )

    _sep()

    # ==========================================
    # MODELING TOOLS
    # ==========================================

    _add_button(
        label="Comb+",
        annotation="Combine, merge verts, delete history, freeze transforms",
        icon="combine_plus.png",
        import_line="from CombinePlus import combine_plus",
        run_line="combine_plus.run()",
    )

    _add_button(
        label="DupEx",
        annotation="Duplicate selected faces to new geometry",
        icon="dupe_extract.png",
        import_line="from DupeExtract import dupe_extract",
        run_line="dupe_extract.run()",
        overlay_color=(0.2, 0.9, 0.9),
    )

    _add_button(
        label="MirWld",
        annotation="Mirror across X, combine, weld center verts, smooth normals",
        icon="mirror_weld.png",
        import_line="from MirrorWeld import mirror_weld",
        run_line="mirror_weld.run()",
        overlay_color=(0.9, 0.2, 0.6),
    )

    _add_button(
        label="MirX",
        annotation="Mirror over X axis (scale -1, freeze)",
        icon="mirror_x.png",
        import_line="from MirrorX import mirror_x",
        run_line="mirror_x.run()",
        overlay_color=(0.9, 0.2, 0.2),
    )

    _add_button(
        label="Merge",
        annotation="Merge selected vertices (threshold 0.001)",
        icon="merge.png",
        import_line="import maya.cmds as cmds",
        run_line="cmds.polyMergeVertex(distance=0.001, constructionHistory=True)",
    )

    _add_button(
        label="MrgCtr",
        annotation="Merge vertices to center",
        icon="merge_center.png",
        import_line="import maya.cmds as cmds",
        run_line="cmds.polyMergeVertex(alwaysMergeTwoVertices=True, constructionHistory=True)",
    )

    _add_button(
        label="CEVrt",
        annotation="Convert selected edges to verts, merge to center",
        icon="collapse_edge_verts.png",
        import_line="from CollapseEdgeVerts import collapse_edge_verts",
        run_line="collapse_edge_verts.run()",
    )

    _add_button(
        label="Collps",
        annotation="Collapse selected edges/faces",
        icon="collapse.png",
        import_line="import maya.cmds as cmds",
        run_line="cmds.polyCollapseEdge(constructionHistory=True)",
    )

    _add_button(
        label="FNScl",
        annotation="Move selected faces along their normals",
        icon="face_normal_scale.png",
        import_line="from FaceNormalScale import face_normal_scale",
        run_line="face_normal_scale.run_with_ui()",
        overlay_color=(0.9, 0.7, 0.2),
    )

    _add_button(
        label="AsMat",
        annotation="Assign most common material to entire mesh",
        icon="assign_common_material.png",
        import_line="from AssignCommonMaterial import assign_common_material",
        run_line="assign_common_material.run()",
        overlay_color=(0.8, 0.4, 0.9),
    )

    _sep()

    # ==========================================
    # EDGE / NORMAL TOOLS
    # ==========================================

    _add_button(
        label="EdgeAvg",
        annotation="EdgeAverager - Average parallel edges with volume preservation",
        icon="edge_averager.png",
        import_line="import importlib, EdgeAverager; importlib.reload(EdgeAverager)",
        run_line="EdgeAverager.run()",
        overlay_color=(0.8, 0.5, 0.2),
    )

    _add_button(
        label="ENClean",
        annotation="Harden selected edges, soften all others",
        icon="edge_normals_clean.png",
        import_line="from EdgeNormalsClean import edge_normals_clean",
        run_line="edge_normals_clean.run()",
        overlay_color=(0.2, 0.8, 0.6),
    )

    _add_button(
        label="Hard",
        annotation="Harden selected edges",
        icon="harden_edge.png",
        import_line="import maya.cmds as cmds",
        run_line="cmds.polySoftEdge(angle=0, constructionHistory=True)",
    )

    _add_button(
        label="Soft",
        annotation="Soften selected edges",
        icon="soften_edge.png",
        import_line="import maya.cmds as cmds",
        run_line="cmds.polySoftEdge(angle=180, constructionHistory=True)",
    )

    _sep()

    # ==========================================
    # RETOPOLOGY
    # ==========================================

    _add_button(
        label="Retopo",
        annotation="WGLL Retopo — Curvature-guided retopology",
        icon="polyRetopo.png",
        import_line=(
            "wgll_root = '/Users/arthurklein/Documents/Work/Side/VibeBash/WGLL_Retopo'\\n"
            "for p in [wgll_root]:\\n"
            "    if p not in sys.path: sys.path.insert(0, p)\\n"
            "import importlib, WGLLRetopo; importlib.reload(WGLLRetopo)"
        ),
        run_line="WGLLRetopo.run_with_ui()",
        overlay_color=(0.2, 0.9, 0.4),
    )

    _sep()

    # ==========================================
    # UV / TEXTURE TOOLS
    # ==========================================

    _add_button(
        label="RldTx",
        annotation="Reload textures on selected mesh from disk",
        icon="reload_texture.png",
        import_line="from ReloadTexture import reload_texture",
        run_line="reload_texture.run()",
        overlay_color=(0.4, 0.8, 0.9),
    )

    _add_button(
        label="UVNav",
        annotation="Move UV shells on 16x16 color atlas",
        icon="uv_atlas_nav.png",
        import_line="import importlib; from UVAtlasNav import uv_atlas_nav; importlib.reload(uv_atlas_nav)",
        run_line="uv_atlas_nav.run()",
        overlay_color=(1.0, 0.8, 0.2),
    )

    _add_button(
        label="UVx",
        annotation="Planar UV projection along X axis",
        icon="uv_project_x.png",
        import_line="from UVProject import uv_project",
        run_line="uv_project.run(axis='x')",
        overlay_color=(1.0, 0.3, 0.3),
    )

    _add_button(
        label="UVy",
        annotation="Planar UV projection along Y axis",
        icon="uv_project_y.png",
        import_line="from UVProject import uv_project",
        run_line="uv_project.run(axis='y')",
        overlay_color=(0.3, 1.0, 0.3),
    )

    _add_button(
        label="UVz",
        annotation="Planar UV projection along Z axis",
        icon="uv_project_z.png",
        import_line="from UVProject import uv_project",
        run_line="uv_project.run(axis='z')",
        overlay_color=(0.3, 0.5, 1.0),
    )

    _add_button(
        label="FaceUV",
        annotation="Face UV Manager - Expression atlas control",
        icon="face_uv_manager.png",
        import_line="from FaceUVManager import face_uv_manager",
        run_line="mgr = face_uv_manager.FaceUVManager(); mgr.show()",
    )

    print(f"\n--- {SHELF_NAME} rebuild complete ---\n")

    # Save all shelves to disk
    save_shelves()


# Auto-run when exec'd
rebuild()
