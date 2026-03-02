"""
ReloadTexture — Reload file textures on selected meshes from disk
Author: Arthur Klein
Version: 1.0.0

Usage:
    import ReloadTexture.reload_texture as tool
    tool.run()
"""

import maya.cmds as cmds
import os
import sys

# --- Configuration ---
TOOL_NAME = "ReloadTexture"
TOOL_LABEL = "RldTx"
TOOL_ANNOTATION = "Reload textures on selected mesh from disk"
TOOL_ICON = "reload_texture.png"
SHELF_NAME = "AK_Shelf"


def run():
    """Reload all file textures connected to the selected mesh(es)."""
    selection = cmds.ls(selection=True)
    if not selection:
        cmds.warning(f"{TOOL_NAME}: Select one or more meshes.")
        return

    # Collect all file texture nodes connected to the selection
    file_nodes = set()

    for obj in selection:
        # Get shape nodes
        shapes = cmds.listRelatives(obj, shapes=True, fullPath=True) or [obj]

        for shape in shapes:
            # Get shading groups connected to this shape
            sgs = cmds.listConnections(shape, type='shadingEngine') or []
            for sg in sgs:
                # Walk all connections from the shading group to find file nodes
                history = cmds.listHistory(sg, pruneDagObjects=True) or []
                for node in history:
                    if cmds.nodeType(node) == 'file':
                        file_nodes.add(node)

    if not file_nodes:
        cmds.warning(f"{TOOL_NAME}: No file textures found on selection.")
        return

    reloaded = 0
    for file_node in sorted(file_nodes):
        tex_path = cmds.getAttr(file_node + '.fileTextureName') or ''
        if not tex_path:
            continue

        # Re-set the path to force Maya to reload from disk
        cmds.setAttr(file_node + '.fileTextureName', tex_path, type='string')
        reloaded += 1
        print(f"  Reloaded: {file_node} -> {os.path.basename(tex_path)}")

    print(f"{TOOL_NAME}: Reloaded {reloaded} texture(s).")


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
        f"from ReloadTexture import reload_texture\n"
        f"reload_texture.run()"
    )

    icons_dir = os.path.join(scripts_root, 'icons')
    icon_path = os.path.join(icons_dir, TOOL_ICON)
    icon = icon_path if os.path.exists(icon_path) else "refresh.png"

    cmds.shelfButton(
        parent=SHELF_NAME,
        image=icon,
        command=command,
        annotation=TOOL_ANNOTATION,
        label=TOOL_LABEL,
        imageOverlayLabel=TOOL_LABEL,
        overlayLabelColor=(0.4, 0.8, 0.9),
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
