"""
UVAtlasNav — Move UV shells on a 16x16 color atlas grid
Author: Arthur Klein
Version: 1.0.0

Navigate selected UV shells between swatches on a 16x16 color palette texture.
Supports directional movement with wrapping and random placement.

Usage:
    from UVAtlasNav import uv_atlas_nav
    uv_atlas_nav.run()
"""

import maya.cmds as cmds
import os
import random
import math

# --- Configuration ---
TOOL_NAME = "UVAtlasNav"
TOOL_LABEL = "UVNav"
TOOL_ANNOTATION = "Move UV shells on 16x16 color atlas"
TOOL_ICON = "uv_atlas_nav.png"
SHELF_NAME = "AK_Shelf"

GRID_SIZE = 16
CELL_SIZE = 1.0 / GRID_SIZE


# --- Core UV functions ---

def _get_selected_uvs():
    """Get UVs from current selection, converting if needed.

    Returns:
        list or None: Flattened UV component list, or None if nothing usable.
    """
    sel = cmds.ls(selection=True)
    if not sel:
        return None

    # Try direct UV selection first
    uvs = cmds.filterExpand(sel, selectionMask=35, expand=True)
    if uvs:
        return uvs

    # Convert whatever is selected (faces, edges, verts, objects) to UVs
    converted = cmds.polyListComponentConversion(sel, toUV=True)
    if converted:
        uvs = cmds.ls(converted, flatten=True)
        if uvs:
            return uvs

    return None


def _get_uv_center(uvs):
    """Calculate average U and V of the given UV components.

    Returns:
        tuple: (center_u, center_v)
    """
    vals = cmds.polyEditUV(uvs, query=True)
    if not vals:
        return 0.0, 0.0

    us = vals[0::2]
    vs = vals[1::2]
    center_u = sum(us) / len(us)
    center_v = sum(vs) / len(vs)
    return center_u, center_v


def _get_current_cell(uvs):
    """Determine which grid cell the UV shell center falls in.

    Returns:
        tuple: (col, row) each 0-15
    """
    center_u, center_v = _get_uv_center(uvs)
    col = int(center_u / CELL_SIZE)
    row = int(center_v / CELL_SIZE)
    col = max(0, min(GRID_SIZE - 1, col))
    row = max(0, min(GRID_SIZE - 1, row))
    return col, row


def _move_to_cell(uvs, target_col, target_row):
    """Move UV shell so its center lands on the target cell.

    Args:
        uvs: UV component list
        target_col: Target column (0-15)
        target_row: Target row (0-15)
    """
    target_u = (target_col + 0.5) * CELL_SIZE
    target_v = (target_row + 0.5) * CELL_SIZE

    current_u, current_v = _get_uv_center(uvs)

    delta_u = target_u - current_u
    delta_v = target_v - current_v

    cmds.polyEditUV(uvs, u=delta_u, v=delta_v, relative=True)


def _nudge(du, dv):
    """Move selected UVs by du/dv cells with wrapping.

    Args:
        du: Column delta (-1, 0, or 1)
        dv: Row delta (-1, 0, or 1)

    Returns:
        tuple or None: (new_col, new_row) if successful
    """
    uvs = _get_selected_uvs()
    if not uvs:
        cmds.warning(f"{TOOL_NAME}: Select faces, edges, or UVs first.")
        return None

    cmds.undoInfo(openChunk=True, chunkName=TOOL_NAME)
    try:
        col, row = _get_current_cell(uvs)
        new_col = (col + du) % GRID_SIZE
        new_row = (row + dv) % GRID_SIZE
        _move_to_cell(uvs, new_col, new_row)
        return new_col, new_row
    except Exception as e:
        cmds.warning(f"{TOOL_NAME}: {e}")
        return None
    finally:
        cmds.undoInfo(closeChunk=True)


def _random_cell():
    """Move selected UVs to a random cell.

    Returns:
        tuple or None: (col, row) if successful
    """
    uvs = _get_selected_uvs()
    if not uvs:
        cmds.warning(f"{TOOL_NAME}: Select faces, edges, or UVs first.")
        return None

    cmds.undoInfo(openChunk=True, chunkName=TOOL_NAME)
    try:
        col = random.randint(0, GRID_SIZE - 1)
        row = random.randint(0, GRID_SIZE - 1)
        _move_to_cell(uvs, col, row)
        return col, row
    except Exception as e:
        cmds.warning(f"{TOOL_NAME}: {e}")
        return None
    finally:
        cmds.undoInfo(closeChunk=True)


# --- UI ---

def run():
    """Launch the UV Atlas Navigator window and open the UV Editor."""
    # Open Maya's UV Editor
    import maya.mel as mel
    mel.eval('TextureViewWindow')

    window_name = "uvAtlasNavWindow"
    if cmds.window(window_name, exists=True):
        cmds.deleteUI(window_name)

    window = cmds.window(window_name, title="UV Atlas Navigator", widthHeight=(220, 300))
    cmds.columnLayout(adjustableColumn=True, rowSpacing=6, columnOffset=("both", 10))

    cell_label = cmds.text(label="Cell: --", font="boldLabelFont")
    cmds.separator(height=5)

    def _update_label(result):
        if result:
            col, row = result
            cmds.text(cell_label, edit=True, label=f"Cell: ({col}, {row})")

    def _refresh_cell():
        uvs = _get_selected_uvs()
        if uvs:
            col, row = _get_current_cell(uvs)
            cmds.text(cell_label, edit=True, label=f"Cell: ({col}, {row})")

    # D-pad navigation
    cmds.gridLayout(numberOfColumns=3, cellWidthHeight=(63, 35))
    cmds.separator(style='none')
    cmds.button(label="UP", command=lambda *a: _update_label(_nudge(0, 1)))
    cmds.separator(style='none')
    cmds.button(label="LEFT", command=lambda *a: _update_label(_nudge(-1, 0)))
    cmds.separator(style='none')
    cmds.button(label="RIGHT", command=lambda *a: _update_label(_nudge(1, 0)))
    cmds.separator(style='none')
    cmds.button(label="DOWN", command=lambda *a: _update_label(_nudge(0, -1)))
    cmds.separator(style='none')
    cmds.setParent('..')

    cmds.separator(height=5)
    cmds.button(label="Random", command=lambda *a: _update_label(_random_cell()), height=30)
    cmds.separator(height=5)
    cmds.text(label="Select faces, edges, or UVs first.", font="smallPlainLabelFont")

    cmds.showWindow(window)

    # Show current cell if something is already selected
    _refresh_cell()


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
        f"from UVAtlasNav import uv_atlas_nav\n"
        f"uv_atlas_nav.run()"
    )

    icons_dir = os.path.join(scripts_root, 'icons')
    icon_path = os.path.join(icons_dir, TOOL_ICON)
    icon = icon_path if os.path.exists(icon_path) else "polyEditUV.png"

    cmds.shelfButton(
        parent=SHELF_NAME, image=icon, command=command,
        annotation=TOOL_ANNOTATION, label=TOOL_LABEL,
        imageOverlayLabel=TOOL_LABEL,
        overlayLabelColor=(1.0, 0.8, 0.2),
        overlayLabelBackColor=(0, 0, 0, 0.5),
        sourceType="python", width=35, height=35,
    )
    print(f"{TOOL_NAME}: Added to {SHELF_NAME}.")
