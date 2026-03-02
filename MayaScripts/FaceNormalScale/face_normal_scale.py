"""
FaceNormalScale — Move selected faces along their normals
Author: Arthur Klein
Version: 1.0.0

Usage:
    import FaceNormalScale.face_normal_scale as tool
    tool.run(offset=0.1)       # Direct run
    tool.run_with_ui()         # Launch UI with slider
"""

import maya.cmds as cmds
import os
import sys

# --- Configuration ---
TOOL_NAME = "FaceNormalScale"
TOOL_LABEL = "FNScl"
TOOL_ANNOTATION = "Move selected faces along their normals"
TOOL_ICON = "face_normal_scale.png"
SHELF_NAME = "AK_Shelf"


def run(offset=0.1):
    """Move selected faces along their normals by offset distance.

    Args:
        offset (float): Distance to move. Positive = outward, negative = inward.
    """
    selection = cmds.ls(selection=True)
    faces = cmds.filterExpand(selection, selectionMask=34)  # 34 = polygon faces
    if not faces:
        cmds.warning(f"{TOOL_NAME}: Select polygon faces first.")
        return

    cmds.undoInfo(openChunk=True, chunkName=TOOL_NAME)
    try:
        cmds.select(faces)
        cmds.polyMoveFacet(localTranslateZ=offset)
        print(f"{TOOL_NAME}: Moved {len(faces)} face(s) by {offset}")
    except Exception as e:
        cmds.warning(f"{TOOL_NAME}: {e}")
    finally:
        cmds.undoInfo(closeChunk=True)


def run_with_ui():
    """Launch popup with slider for offset distance."""
    window_name = "faceNormalScaleWindow"
    if cmds.window(window_name, exists=True):
        cmds.deleteUI(window_name)

    window = cmds.window(window_name, title="FaceNormalScale", widthHeight=(350, 160))
    cmds.columnLayout(adjustableColumn=True, rowSpacing=8, columnOffset=("both", 10))

    cmds.text(label="Face Normal Scale", font="boldLabelFont")
    cmds.separator(height=5)
    cmds.text(label="Offset Distance:", align="left")

    offset_slider = cmds.floatSliderGrp(
        field=True,
        minValue=-2.0,
        maxValue=2.0,
        value=0.1,
        step=0.01,
        columnWidth=[(1, 60), (2, 230)]
    )

    cmds.separator(height=5)

    def confirm_callback(*args):
        val = cmds.floatSliderGrp(offset_slider, query=True, value=True)
        run(offset=val)

    cmds.button(label="Confirm", command=confirm_callback, height=35)
    cmds.text(
        label="Select faces first. Positive = outward, negative = inward.",
        font="smallPlainLabelFont",
    )

    cmds.showWindow(window)


# --- Shelf Installation (safe, append-only) ---

def _button_exists_on_shelf(shelf, label):
    """Check if a button with this label already exists on the shelf."""
    buttons = cmds.shelfLayout(shelf, query=True, childArray=True) or []
    for btn in buttons:
        if cmds.shelfButton(btn, query=True, exists=True):
            if cmds.shelfButton(btn, query=True, label=True) == label:
                return True
    return False


def _save_shelves():
    """Save all shelves to disk."""
    try:
        import maya.mel as mel
        mel.eval('saveAllShelves $gShelfTopLevel')
        print("All shelves saved.")
    except Exception as e:
        print(f"Warning: Could not save shelves - {e}")


def install_to_shelf():
    """Add this tool's button to AK_Shelf. Safe to run multiple times."""
    if not cmds.shelfLayout(SHELF_NAME, exists=True):
        cmds.shelfLayout(SHELF_NAME, parent="ShelfLayout")
        print(f"Created shelf: {SHELF_NAME}")

    if _button_exists_on_shelf(SHELF_NAME, TOOL_LABEL):
        print(f"{TOOL_NAME}: Button already on {SHELF_NAME}, skipping.")
        return

    try:
        scripts_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        scripts_root = '/Users/arthurklein/Documents/Work/Side/VibeBash/MayaScripts'

    command = (
        f"import sys\n"
        f"if '{scripts_root}' not in sys.path:\n"
        f"    sys.path.append('{scripts_root}')\n"
        f"from FaceNormalScale import face_normal_scale\n"
        f"face_normal_scale.run_with_ui()"
    )

    icons_dir = os.path.join(scripts_root, 'icons')
    icon_path = os.path.join(icons_dir, TOOL_ICON)
    icon = icon_path if os.path.exists(icon_path) else "polyNormal.png"

    cmds.shelfButton(
        parent=SHELF_NAME,
        image=icon,
        command=command,
        annotation=TOOL_ANNOTATION,
        label=TOOL_LABEL,
        imageOverlayLabel=TOOL_LABEL,
        overlayLabelColor=(0.9, 0.7, 0.2),
        overlayLabelBackColor=(0, 0, 0, 0.5),
        sourceType="python",
        width=35,
        height=35,
    )
    print(f"{TOOL_NAME}: Added to {SHELF_NAME}.")
    _save_shelves()


def remove_from_shelf():
    """Remove this tool's button from AK_Shelf."""
    if not cmds.shelfLayout(SHELF_NAME, exists=True):
        return
    buttons = cmds.shelfLayout(SHELF_NAME, query=True, childArray=True) or []
    for btn in buttons:
        if cmds.shelfButton(btn, query=True, exists=True):
            if cmds.shelfButton(btn, query=True, label=True) == TOOL_LABEL:
                cmds.deleteUI(btn)
                print(f"{TOOL_NAME}: Removed from {SHELF_NAME}.")
                _save_shelves()
                return
