"""
CollapseEdgeVerts — Convert selected edges to vertices and merge to center
Author: Arthur Klein
Version: 1.0.0

Usage:
    from CollapseEdgeVerts import collapse_edge_verts
    collapse_edge_verts.run()
"""

import maya.cmds as cmds
import os

# --- Configuration ---
TOOL_NAME = "CollapseEdgeVerts"
TOOL_LABEL = "CEVrt"
TOOL_ANNOTATION = "Convert selected edges to verts, merge to center"
TOOL_ICON = "collapse_edge_verts.png"
SHELF_NAME = "AK_Shelf"


def run():
    """Convert selected edges to vertices, then merge those vertices to center."""
    sel = cmds.ls(selection=True)
    if not sel:
        cmds.warning(f"{TOOL_NAME}: Nothing selected.")
        return

    edges = cmds.filterExpand(sel, selectionMask=32, expand=True)
    if not edges:
        cmds.warning(f"{TOOL_NAME}: Please select edges.")
        return

    cmds.undoInfo(openChunk=True, chunkName=TOOL_NAME)
    try:
        # Convert edges to vertices
        verts = cmds.polyListComponentConversion(edges, fromEdge=True, toVertex=True)
        verts = cmds.ls(verts, flatten=True)

        if not verts:
            cmds.warning(f"{TOOL_NAME}: No vertices found from edge selection.")
            return

        n = len(verts)

        # Calculate centroid
        cx, cy, cz = 0.0, 0.0, 0.0
        for v in verts:
            pos = cmds.pointPosition(v, world=True)
            cx += pos[0]
            cy += pos[1]
            cz += pos[2]
        cx /= n
        cy /= n
        cz /= n

        # Move ALL verts to centroid — symmetry modeling mirrors this automatically
        cmds.select(verts)
        cmds.move(cx, cy, cz, absolute=True, worldSpace=True)

        # Weld overlapping vertices into one
        cmds.polyMergeVertex(distance=0.001, constructionHistory=True)

        print(f"{TOOL_NAME}: Collapsed {n} verts to ({cx:.3f}, {cy:.3f}, {cz:.3f})")
    except Exception as e:
        cmds.warning(f"{TOOL_NAME}: {e}")
    finally:
        cmds.undoInfo(closeChunk=True)


# --- Shelf Installation (safe, append-only) ---

def _button_exists_on_shelf(shelf, label):
    buttons = cmds.shelfLayout(shelf, query=True, childArray=True) or []
    for btn in buttons:
        if cmds.shelfButton(btn, query=True, exists=True):
            if cmds.shelfButton(btn, query=True, label=True) == label:
                return True
    return False


def install_to_shelf():
    if not cmds.shelfLayout(SHELF_NAME, exists=True):
        cmds.shelfLayout(SHELF_NAME, parent="ShelfLayout")

    if _button_exists_on_shelf(SHELF_NAME, TOOL_LABEL):
        print(f"{TOOL_NAME}: Already on {SHELF_NAME}, skipping.")
        return

    try:
        scripts_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        scripts_root = '/Users/arthurklein/Documents/Work/Side/VibeBash/MayaScripts'

    command = (
        f"import sys\n"
        f"if '{scripts_root}' not in sys.path:\n"
        f"    sys.path.append('{scripts_root}')\n"
        f"from CollapseEdgeVerts import collapse_edge_verts\n"
        f"collapse_edge_verts.run()"
    )

    icons_dir = os.path.join(scripts_root, 'icons')
    icon_path = os.path.join(icons_dir, TOOL_ICON)
    icon = icon_path if os.path.exists(icon_path) else "polyCollapseEdge.png"

    cmds.shelfButton(
        parent=SHELF_NAME, image=icon, command=command,
        annotation=TOOL_ANNOTATION, label=TOOL_LABEL,
        imageOverlayLabel=TOOL_LABEL,
        overlayLabelColor=(0.8, 0.8, 0.8),
        overlayLabelBackColor=(0, 0, 0, 0.5),
        sourceType="python", width=35, height=35,
    )
    print(f"{TOOL_NAME}: Added to {SHELF_NAME}.")
