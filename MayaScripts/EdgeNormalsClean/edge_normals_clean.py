"""
EdgeNormalsClean — Harden selected edges, soften all others
Author: Arthur Klein
Version: 1.0.0

Select the edges you want hard, run this script. It hardens those edges
and softens every other edge on the mesh.

Usage:
    from EdgeNormalsClean import edge_normals_clean
    edge_normals_clean.run()
"""

import maya.cmds as cmds
import os

TOOL_NAME = "EdgeNormalsClean"
TOOL_LABEL = "ENClean"
TOOL_ANNOTATION = "Harden selected edges, soften all others"
SHELF_NAME = "AK_Shelf"


def run():
    """Harden selected edges, invert selection, soften the rest."""
    sel = cmds.ls(selection=True)
    if not sel:
        cmds.warning(f"{TOOL_NAME}: Nothing selected.")
        return

    hard_edges = cmds.filterExpand(sel, selectionMask=32, expand=True)
    if not hard_edges:
        cmds.warning(f"{TOOL_NAME}: Please select edges.")
        return

    mesh = hard_edges[0].split('.e[')[0]

    cmds.undoInfo(openChunk=True, chunkName=TOOL_NAME)
    try:
        # Clear history to avoid polySoftEdge warnings
        cmds.delete(mesh, constructionHistory=True)

        # 1. Harden the selected edges
        cmds.polySoftEdge(hard_edges, angle=0, constructionHistory=False)

        # 2. Select all edges, then deselect the hard ones to get the inverse
        cmds.select(mesh + '.e[*]')
        cmds.select(hard_edges, deselect=True)
        soft_edges = cmds.ls(selection=True, flatten=True)

        # 3. Soften the inverse edges
        if soft_edges:
            cmds.polySoftEdge(soft_edges, angle=180, constructionHistory=False)

        # 4. Restore original selection
        cmds.select(hard_edges)

        print(f"{TOOL_NAME}: Hardened {len(hard_edges)} edge(s), "
              f"softened {len(soft_edges)} edge(s) on '{mesh}'.")

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
        f"from EdgeNormalsClean import edge_normals_clean\n"
        f"edge_normals_clean.run()"
    )
    cmds.shelfButton(
        parent=SHELF_NAME, image="polySoftEdge.png", command=command,
        annotation=TOOL_ANNOTATION, label=TOOL_LABEL,
        imageOverlayLabel=TOOL_LABEL,
        overlayLabelColor=(0.8, 0.8, 0.8),
        overlayLabelBackColor=(0, 0, 0, 0.5),
        sourceType="python", width=35, height=35,
    )
    print(f"{TOOL_NAME}: Added to {SHELF_NAME}.")
