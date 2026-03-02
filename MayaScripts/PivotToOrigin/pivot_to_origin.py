"""
PivotToOrigin — Move pivot point to world origin (0, 0, 0)
Author: Arthur Klein
Version: 1.0.0

Usage:
    import PivotToOrigin.pivot_to_origin as tool
    tool.run()
"""

import maya.cmds as cmds
import os

TOOL_NAME = "PivotToOrigin"
TOOL_LABEL = "Pvt0"
TOOL_ANNOTATION = "Move pivot to world origin (0, 0, 0)"
SHELF_NAME = "AK_Shelf"


def run():
    """Set the rotate and scale pivot to (0, 0, 0) for each selected object."""
    selection = cmds.ls(selection=True)
    if not selection:
        cmds.warning(f"{TOOL_NAME}: Nothing selected.")
        return

    cmds.undoInfo(openChunk=True, chunkName=TOOL_NAME)
    try:
        for obj in selection:
            cmds.xform(obj, worldSpace=True, rotatePivot=(0, 0, 0))
            cmds.xform(obj, worldSpace=True, scalePivot=(0, 0, 0))
        print(f"{TOOL_NAME}: Pivot set to origin on {len(selection)} object(s).")
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
        f"from PivotToOrigin import pivot_to_origin\n"
        f"pivot_to_origin.run()"
    )
    cmds.shelfButton(
        parent=SHELF_NAME, image="moveManip.png", command=command,
        annotation=TOOL_ANNOTATION, label=TOOL_LABEL,
        imageOverlayLabel=TOOL_LABEL,
        overlayLabelColor=(0.8, 0.8, 0.8),
        overlayLabelBackColor=(0, 0, 0, 0.5),
        sourceType="python", width=35, height=35,
    )
    print(f"{TOOL_NAME}: Added to {SHELF_NAME}.")
