"""
ToolName — Short description of what this tool does
Author: Arthur Klein
Version: 1.0.0

Usage:
    import ToolName.tool_name as tool
    tool.run()
"""

import maya.cmds as cmds
import os
import sys

# --- Configuration ---
TOOL_NAME = "ToolName"
TOOL_LABEL = "Tool"           # Short label for shelf button (max ~6 chars)
TOOL_ANNOTATION = "ToolName — What it does"
TOOL_ICON = "commandButton.png"  # Maya default icon (or path to custom .png)
SHELF_NAME = "AK_Shelf"


def run():
    """Main entry point. Select objects first, then call this."""
    selection = cmds.ls(selection=True)
    if not selection:
        cmds.warning(f"{TOOL_NAME}: Nothing selected.")
        return

    cmds.undoInfo(openChunk=True, chunkName=TOOL_NAME)
    try:
        # --- Your tool logic here ---
        for obj in selection:
            pass  # Replace with actual operations
        print(f"{TOOL_NAME}: Done.")
    except Exception as e:
        cmds.warning(f"{TOOL_NAME}: {e}")
    finally:
        cmds.undoInfo(closeChunk=True)


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

    # Detect the MayaScripts root from this file's location
    try:
        scripts_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        module_name = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        scripts_root = '/Users/arthurklein/Documents/Work/Side/VibeBash/MayaScripts'
        module_name = TOOL_NAME

    command = (
        f"import sys\n"
        f"if '{scripts_root}' not in sys.path:\n"
        f"    sys.path.append('{scripts_root}')\n"
        f"import importlib, {module_name}\n"
        f"importlib.reload({module_name})\n"
        f"{module_name}.run()"
    )

    cmds.shelfButton(
        parent=SHELF_NAME,
        image=TOOL_ICON,
        command=command,
        annotation=TOOL_ANNOTATION,
        label=TOOL_LABEL,
        imageOverlayLabel=TOOL_LABEL,
        overlayLabelColor=(0.8, 0.8, 0.8),
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
