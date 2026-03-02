"""
AssignCommonMaterial — Assign the most common material to the entire mesh
Author: Arthur Klein
Version: 1.0.0

Usage:
    import AssignCommonMaterial.assign_common_material as tool
    tool.run()
"""

import maya.cmds as cmds
import os
import sys

# --- Configuration ---
TOOL_NAME = "AssignCommonMaterial"
TOOL_LABEL = "AsMat"
TOOL_ANNOTATION = "Assign most common material to entire mesh"
TOOL_ICON = "assign_common_material.png"
SHELF_NAME = "AK_Shelf"


def run():
    """Find the most common non-default material in the scene and assign it to selected meshes."""
    selection = cmds.ls(selection=True, type='transform', long=True)
    if not selection:
        cmds.warning(f"{TOOL_NAME}: Select one or more meshes.")
        return

    # Find the most common non-default material across the ENTIRE scene
    best_sg = _find_most_common_material()
    if not best_sg:
        cmds.warning(f"{TOOL_NAME}: No non-default materials found in scene.")
        return

    materials = cmds.listConnections(best_sg + '.surfaceShader') or ['unknown']
    mat_name = materials[0]

    cmds.undoInfo(openChunk=True, chunkName=TOOL_NAME)
    try:
        for mesh in selection:
            cmds.sets(mesh, forceElement=best_sg)
        short_names = [m.split('|')[-1] for m in selection]
        print(f"{TOOL_NAME}: Assigned '{mat_name}' to {len(selection)} mesh(es): {', '.join(short_names)}")
    except Exception as e:
        cmds.warning(f"{TOOL_NAME}: {e}")
    finally:
        cmds.undoInfo(closeChunk=True)


def _find_most_common_material():
    """Scan all shading engines in the scene, return the non-default SG with the most members."""
    all_sgs = cmds.ls(type='shadingEngine') or []

    best_sg = None
    best_count = 0

    for sg in all_sgs:
        if sg == 'initialShadingGroup' or sg == 'initialParticleSE':
            continue

        members = cmds.sets(sg, query=True) or []
        count = 0
        for member in members:
            expanded = cmds.ls(member, flatten=True) or []
            count += len(expanded)

        if count > best_count:
            best_count = count
            best_sg = sg

    return best_sg


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
        f"from AssignCommonMaterial import assign_common_material\n"
        f"assign_common_material.run()"
    )

    icons_dir = os.path.join(scripts_root, 'icons')
    icon_path = os.path.join(icons_dir, TOOL_ICON)
    icon = icon_path if os.path.exists(icon_path) else "assignShadingGroup.png"

    cmds.shelfButton(
        parent=SHELF_NAME,
        image=icon,
        command=command,
        annotation=TOOL_ANNOTATION,
        label=TOOL_LABEL,
        imageOverlayLabel=TOOL_LABEL,
        overlayLabelColor=(0.8, 0.4, 0.9),
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
