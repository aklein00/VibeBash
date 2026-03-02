"""
MirrorX — Mirror selected object by scaling X to -1
Author: Arthur Klein
Version: 1.0.0

Verifies pivot is at origin, scales X by -1, deletes history, freezes transforms.

Usage:
    from MirrorX import mirror_x
    mirror_x.run()
"""

import maya.cmds as cmds
import os

# --- Configuration ---
TOOL_NAME = "MirrorX"
TOOL_LABEL = "MirX"
TOOL_ANNOTATION = "Mirror over X axis (scale -1, freeze)"
TOOL_ICON = "mirror_x.png"
SHELF_NAME = "AK_Shelf"

ORIGIN_TOLERANCE = 0.0001


def run():
    """Mirror selected object(s) over X by scaling -1, then clean up."""
    selection = cmds.ls(selection=True, type='transform')
    if not selection:
        cmds.warning(f"{TOOL_NAME}: Select one or more meshes.")
        return

    cmds.undoInfo(openChunk=True, chunkName=TOOL_NAME)
    try:
        for obj in selection:
            _mirror_object(obj)
    except Exception as e:
        cmds.warning(f"{TOOL_NAME}: {e}")
    finally:
        cmds.undoInfo(closeChunk=True)


def _mirror_object(obj):
    """Mirror a single object over X."""
    # Verify pivot is at origin
    pivot = cmds.xform(obj, query=True, worldSpace=True, rotatePivot=True)
    if abs(pivot[0]) > ORIGIN_TOLERANCE or abs(pivot[1]) > ORIGIN_TOLERANCE or abs(pivot[2]) > ORIGIN_TOLERANCE:
        cmds.warning(
            f"{TOOL_NAME}: '{obj}' pivot is at ({pivot[0]:.4f}, {pivot[1]:.4f}, {pivot[2]:.4f}), "
            f"not at origin. Moving pivot to origin first."
        )
        cmds.xform(obj, worldSpace=True, rotatePivot=(0, 0, 0), scalePivot=(0, 0, 0))

    # Scale X by -1
    cmds.setAttr(f"{obj}.scaleX", -1)

    # Delete history
    cmds.delete(obj, constructionHistory=True)

    # Freeze transforms
    cmds.makeIdentity(obj, apply=True, translate=True, rotate=True, scale=True, normal=False)

    # Reverse normals (scaling by -1 flips them)
    cmds.polyNormal(obj, normalMode=0, userNormalMode=0, constructionHistory=False)

    print(f"{TOOL_NAME}: Mirrored '{obj}' over X axis.")


# --- Shelf Installation ---

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
        f"from MirrorX import mirror_x\n"
        f"mirror_x.run()"
    )

    icons_dir = os.path.join(scripts_root, 'icons')
    icon_path = os.path.join(icons_dir, TOOL_ICON)
    icon = icon_path if os.path.exists(icon_path) else "polyMirrorGeometry.png"

    cmds.shelfButton(
        parent=SHELF_NAME, image=icon, command=command,
        annotation=TOOL_ANNOTATION, label=TOOL_LABEL,
        imageOverlayLabel=TOOL_LABEL,
        overlayLabelColor=(0.9, 0.2, 0.2),
        overlayLabelBackColor=(0, 0, 0, 0.5),
        sourceType="python", width=35, height=35,
    )
    print(f"{TOOL_NAME}: Added to {SHELF_NAME}.")
