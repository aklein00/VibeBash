"""
DupeExtract — Duplicate selected faces to new geometry
Author: Arthur Klein
Version: 1.0.0

Select faces, run this to extract them as a new separate mesh.
Deletes history and freezes transforms on the result.

Usage:
    from DupeExtract import dupe_extract
    dupe_extract.run()
"""

import maya.cmds as cmds
import os

TOOL_NAME = "DupeExtract"
TOOL_LABEL = "DupEx"
TOOL_ANNOTATION = "Duplicate selected faces to new geometry"
SHELF_NAME = "AK_Shelf"


def run():
    """Extract selected faces as new geometry, delete history, freeze transforms."""
    sel = cmds.ls(selection=True, long=True)
    if not sel:
        cmds.warning(f"{TOOL_NAME}: Nothing selected.")
        return

    # Expand to faces
    faces = cmds.filterExpand(sel, selectionMask=34, expand=True)
    if not faces:
        cmds.warning(f"{TOOL_NAME}: Please select faces.")
        return

    # Get the parent mesh
    mesh = faces[0].split('.f[')[0]

    cmds.undoInfo(openChunk=True, chunkName=TOOL_NAME)
    try:
        # Duplicate the mesh
        dupe = cmds.duplicate(mesh, returnRootsOnly=True)[0]

        # Build matching face indices on the duplicate
        face_indices = []
        for f in faces:
            idx = f.split('.f[')[1].rstrip(']')
            face_indices.append(int(idx))

        # Get total face count on duplicate
        total_faces = cmds.polyEvaluate(dupe, face=True)

        # Select all faces on duplicate EXCEPT the ones we want to keep
        all_indices = set(range(total_faces))
        keep_indices = set(face_indices)
        delete_indices = all_indices - keep_indices

        if delete_indices:
            delete_faces = [f"{dupe}.f[{i}]" for i in sorted(delete_indices)]
            cmds.select(delete_faces)
            cmds.delete()

        # Select the duplicate
        cmds.select(dupe)

        # Delete history
        cmds.delete(dupe, constructionHistory=True)

        # Freeze transformations
        cmds.makeIdentity(dupe, apply=True, translate=True,
                          rotate=True, scale=True, normal=False)

        print(f"{TOOL_NAME}: Extracted {len(face_indices)} face(s) to '{dupe}'.")

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
        f"from DupeExtract import dupe_extract\n"
        f"dupe_extract.run()"
    )
    cmds.shelfButton(
        parent=SHELF_NAME, image="polyChipOff.png", command=command,
        annotation=TOOL_ANNOTATION, label=TOOL_LABEL,
        imageOverlayLabel=TOOL_LABEL,
        overlayLabelColor=(0.8, 0.8, 0.8),
        overlayLabelBackColor=(0, 0, 0, 0.5),
        sourceType="python", width=35, height=35,
    )
    print(f"{TOOL_NAME}: Added to {SHELF_NAME}.")
