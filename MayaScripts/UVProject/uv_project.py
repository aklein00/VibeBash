"""
UVProject — Planar UV projection along X, Y, or Z axis
Author: Arthur Klein
Version: 2.0.0

Supports face and object selections. Auto-sizes projection to bounding box,
stacks shells, fits inside one cell of a 16x16 atlas, and places at cell (8,8).

Usage:
    from UVProject import uv_project
    uv_project.run(axis='x')  # or 'y' or 'z'
"""

import maya.cmds as cmds
import os

TOOL_NAME = "UVProject"
SHELF_NAME = "AK_Shelf"

# 16x16 atlas grid settings
GRID_SIZE = 16
CELL_SIZE = 1.0 / GRID_SIZE  # 0.0625
TARGET_COL = 8
TARGET_ROW = 8
CELL_PADDING = 0.85  # fill 85% of cell, leaves a small margin


def run(axis='x'):
    """Apply planar UV projection along the given axis with auto-sizing."""
    axis = axis.lower()
    if axis not in ('x', 'y', 'z'):
        cmds.warning(f"{TOOL_NAME}: Invalid axis '{axis}'. Use 'x', 'y', or 'z'.")
        return

    sel = cmds.ls(selection=True, long=True)
    if not sel:
        cmds.warning(f"{TOOL_NAME}: Nothing selected.")
        return

    # Expand selection to faces
    faces_to_process = cmds.filterExpand(sel, selectionMask=34, expand=True)
    if not faces_to_process:
        # Try converting object selection to faces
        objects = cmds.ls(selection=True, transforms=True, long=True)
        if objects:
            faces_to_process = []
            for obj in objects:
                faces_to_process.extend(cmds.ls(obj + ".f[*]", flatten=True, long=True))

    if not faces_to_process:
        cmds.warning(f"{TOOL_NAME}: Could not define a valid face selection.")
        return

    # Sort faces by mesh for batch processing (keeps UV shells sewn)
    mesh_map = {}
    for f in faces_to_process:
        m = f.split('.f[')[0]
        if m not in mesh_map:
            mesh_map[m] = []
        mesh_map[m].append(f)

    cmds.undoInfo(openChunk=True, chunkName=f"{TOOL_NAME}_{axis.upper()}")
    try:
        for mesh, faces in mesh_map.items():
            bb = cmds.exactWorldBoundingBox(faces)

            cx = (bb[0] + bb[3]) / 2.0
            cy = (bb[1] + bb[4]) / 2.0
            cz = (bb[2] + bb[5]) / 2.0

            # Width and height depend on projection axis
            if axis == 'x':
                w = bb[5] - bb[2]  # Z range
                h = bb[4] - bb[1]  # Y range
            elif axis == 'y':
                w = bb[3] - bb[0]  # X range
                h = bb[5] - bb[2]  # Z range
            else:  # z
                w = bb[3] - bb[0]  # X range
                h = bb[4] - bb[1]  # Y range

            # Prevent division by zero for flat geometry
            if w <= 0.001:
                w = 1.0
            if h <= 0.001:
                h = 1.0

            # Project normalized to 0-1 (pw=w, ph=h fits UVs to bounding box)
            cmds.polyPlanarProjection(faces, md=axis, pc=(cx, cy, cz), pw=w, ph=h)

            # Get projected UVs
            uvs = cmds.polyListComponentConversion(faces, toUV=True)
            uvs = cmds.ls(uvs, flatten=True)
            if not uvs:
                continue

            vals = cmds.polyEditUV(uvs, query=True)
            us = vals[0::2]
            vs = vals[1::2]

            # Scale to fit inside one atlas cell
            uv_w = max(us) - min(us)
            uv_h = max(vs) - min(vs)
            max_dim = max(uv_w, uv_h)
            scale = (CELL_SIZE * CELL_PADDING) / max_dim if max_dim > 0 else 1.0

            cur_u = (min(us) + max(us)) / 2.0
            cur_v = (min(vs) + max(vs)) / 2.0
            cmds.polyEditUV(uvs, pivotU=cur_u, pivotV=cur_v, scaleU=scale, scaleV=scale)

            # Move to target cell center
            target_u = (TARGET_COL + 0.5) * CELL_SIZE
            target_v = (TARGET_ROW + 0.5) * CELL_SIZE
            cmds.polyEditUV(uvs, u=target_u - cur_u, v=target_v - cur_v, relative=True)

            print(f"{TOOL_NAME}: Projected '{mesh}' -> cell ({TARGET_COL}, {TARGET_ROW})")

        # Restore original selection
        cmds.select(sel)

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


def install_to_shelf(axis='x'):
    label = f"UV{axis.lower()}"
    colors = {'x': (1.0, 0.3, 0.3), 'y': (0.3, 1.0, 0.3), 'z': (0.3, 0.5, 1.0)}

    if not cmds.shelfLayout(SHELF_NAME, exists=True):
        cmds.shelfLayout(SHELF_NAME, parent="ShelfLayout")
    if _button_exists_on_shelf(SHELF_NAME, label):
        print(f"{TOOL_NAME}: [{label}] already on {SHELF_NAME}, skipping.")
        return

    try:
        scripts_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        scripts_root = '/Users/arthurklein/Documents/Work/Side/VibeBash/MayaScripts'

    command = (
        f"import sys\n"
        f"if '{scripts_root}' not in sys.path:\n"
        f"    sys.path.append('{scripts_root}')\n"
        f"from UVProject import uv_project\n"
        f"uv_project.run(axis='{axis}')"
    )
    cmds.shelfButton(
        parent=SHELF_NAME, image="polyPlanarProj.png", command=command,
        annotation=f"Planar UV projection along {axis.upper()} axis",
        label=label, imageOverlayLabel=label,
        overlayLabelColor=colors.get(axis, (0.8, 0.8, 0.8)),
        overlayLabelBackColor=(0, 0, 0, 0.5),
        sourceType="python", width=35, height=35,
    )
    print(f"{TOOL_NAME}: [{label}] added to {SHELF_NAME}.")
