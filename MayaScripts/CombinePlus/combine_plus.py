"""
CombinePlus — Combine meshes, merge close verts, delete history, freeze transforms
Author: Arthur Klein
Version: 1.0.0

Usage:
    import CombinePlus.combine_plus as tool
    tool.run()
"""

import maya.cmds as cmds
import os

TOOL_NAME = "CombinePlus"
TOOL_LABEL = "Comb+"
TOOL_ANNOTATION = "Combine, merge verts, delete history, freeze transforms"
TOOL_ICON = "polyUnite.png"
SHELF_NAME = "AK_Shelf"

MERGE_THRESHOLD = 0.001  # Distance in scene units for merging close verts


def run(merge_threshold=MERGE_THRESHOLD):
    """Combine selected meshes, merge close verts, delete history, freeze."""
    selection = cmds.ls(selection=True, type='transform')
    if len(selection) < 2:
        cmds.warning(f"{TOOL_NAME}: Select 2 or more meshes to combine.")
        return

    # Use the first object's name as the base for the result
    base_name = selection[0].split('|')[-1].split(':')[-1]

    cmds.undoInfo(openChunk=True, chunkName=TOOL_NAME)
    try:
        # 1. Combine
        result = cmds.polyUnite(selection, constructionHistory=False)
        combined = result[0]

        # 2. Merge close vertices
        cmds.select(combined)
        cmds.polyMergeVertex(combined, distance=merge_threshold,
                             alwaysMergeTwoVertices=False,
                             constructionHistory=False)

        # 3. Delete history
        cmds.delete(combined, constructionHistory=True)

        # 4. Freeze transformations
        cmds.makeIdentity(combined, apply=True, translate=True,
                          rotate=True, scale=True, normal=False)

        # 5. Rename
        combined = cmds.rename(combined, base_name)
        cmds.select(combined)

        vert_count = cmds.polyEvaluate(combined, vertex=True)
        print(f"{TOOL_NAME}: Combined into '{combined}' ({vert_count} verts).")

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
        f"from CombinePlus import combine_plus\n"
        f"combine_plus.run()"
    )
    cmds.shelfButton(
        parent=SHELF_NAME, image=TOOL_ICON, command=command,
        annotation=TOOL_ANNOTATION, label=TOOL_LABEL,
        imageOverlayLabel=TOOL_LABEL,
        overlayLabelColor=(0.8, 0.8, 0.8),
        overlayLabelBackColor=(0, 0, 0, 0.5),
        sourceType="python", width=35, height=35,
    )
    print(f"{TOOL_NAME}: Added to {SHELF_NAME}.")
