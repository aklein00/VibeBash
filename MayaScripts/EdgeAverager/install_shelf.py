"""
Install EdgeAverager to Maya Shelf (safe, append-only)
Run this script in Maya to add EdgeAverager button to AK_Shelf.
Safe to run multiple times — won't create duplicates.
"""

from maya import cmds
import os

TOOL_NAME = "EdgeAverager"
TOOL_LABEL = "EdgeAvg"
TOOL_ANNOTATION = "EdgeAverager - Average parallel edges with volume preservation"
TOOL_ICON = "polyEdgeToCurve.png"
SHELF_NAME = "AK_Shelf"


def _button_exists_on_shelf(shelf, label):
    """Check if a button with this label already exists on the shelf."""
    buttons = cmds.shelfLayout(shelf, query=True, childArray=True) or []
    for btn in buttons:
        if cmds.shelfButton(btn, query=True, exists=True):
            if cmds.shelfButton(btn, query=True, label=True) == label:
                return True
    return False


def install_to_shelf():
    """Add EdgeAverager button to AK_Shelf. Safe to run multiple times."""
    if not cmds.shelfLayout(SHELF_NAME, exists=True):
        cmds.shelfLayout(SHELF_NAME, parent="ShelfLayout")
        print(f"Created shelf: {SHELF_NAME}")

    if _button_exists_on_shelf(SHELF_NAME, TOOL_LABEL):
        print(f"{TOOL_NAME}: Already on {SHELF_NAME}, skipping.")
        return True

    # Detect path dynamically from this file's location
    try:
        scripts_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        scripts_root = '/Users/arthurklein/Documents/Work/Side/VibeBash/MayaScripts'
    command = (
        f"import sys\n"
        f"if '{scripts_root}' not in sys.path:\n"
        f"    sys.path.append('{scripts_root}')\n"
        f"import importlib, EdgeAverager\n"
        f"importlib.reload(EdgeAverager)\n"
        f"EdgeAverager.run()"
    )

    cmds.shelfButton(
        parent=SHELF_NAME,
        image=TOOL_ICON,
        command=command,
        annotation=TOOL_ANNOTATION,
        label=TOOL_LABEL,
        imageOverlayLabel=TOOL_LABEL,
        overlayLabelColor=(0.8, 0.5, 0.2),
        overlayLabelBackColor=(0, 0, 0, 0.5),
        sourceType="python",
        width=35,
        height=35,
    )

    print(f"{TOOL_NAME}: Added to {SHELF_NAME}.")
    return True


def remove_from_shelf():
    """Remove EdgeAverager button from AK_Shelf."""
    if not cmds.shelfLayout(SHELF_NAME, exists=True):
        return
    buttons = cmds.shelfLayout(SHELF_NAME, query=True, childArray=True) or []
    for btn in buttons:
        if cmds.shelfButton(btn, query=True, exists=True):
            if cmds.shelfButton(btn, query=True, label=True) == TOOL_LABEL:
                cmds.deleteUI(btn)
                print(f"{TOOL_NAME}: Removed from {SHELF_NAME}.")
                return


if __name__ == "__main__":
    install_to_shelf()
