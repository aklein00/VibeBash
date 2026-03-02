"""
MirrorWeld — ZBrush-style auto-detect mirror across X axis
Author: Arthur Klein
Version: 1.1.0

Auto-detects which side of X=0 has more geometry, mirrors to the other side,
combines, welds center verts, smooths normals on merged edges.
Deletes history, freezes transforms, moves pivot to origin.

If vertices are found near (but not on) X=0, prompts to snap them first
so the center seam welds cleanly.

Usage:
    from MirrorWeld import mirror_weld
    mirror_weld.run()
"""

import maya.cmds as cmds
import os

TOOL_NAME = "MirrorWeld"
TOOL_LABEL = "MirWld"
TOOL_ANNOTATION = "Mirror across X, combine, weld center verts, smooth normals"
SHELF_NAME = "AK_Shelf"

WELD_THRESHOLD = 0.001
SNAP_THRESHOLD = 0.1


def _find_near_x_verts(obj, threshold):
    """Return verts that are close to X=0 but not exactly on it."""
    all_verts = cmds.ls(obj + ".vtx[*]", flatten=True)
    near_verts = []
    for vtx in all_verts:
        pos = cmds.pointPosition(vtx, world=True)
        x = abs(pos[0])
        if 0 < x <= threshold:
            near_verts.append(vtx)
    return near_verts


def _snap_verts_to_x(verts):
    """Snap the given verts to X=0, preserving Y and Z."""
    for vtx in verts:
        pos = cmds.pointPosition(vtx, world=True)
        cmds.xform(vtx, worldSpace=True, translation=(0, pos[1], pos[2]))


def run(weld_threshold=WELD_THRESHOLD, snap_threshold=SNAP_THRESHOLD):
    """Mirror across X, combine, weld center verts, clean up."""
    selection = cmds.ls(selection=True, type='transform')
    if not selection:
        cmds.warning(f"{TOOL_NAME}: Select a mesh.")
        return

    obj = selection[0]
    obj_name = obj.split('|')[-1].split(':')[-1]

    # --- Pre-check: verts near X=0 ---
    near_x_verts = _find_near_x_verts(obj, snap_threshold)
    snap = False
    if near_x_verts:
        answer = cmds.confirmDialog(
            title=TOOL_NAME,
            message=(
                f"Found {len(near_x_verts)} vert(s) near X=0 "
                f"(within +/-{snap_threshold}).\n"
                f"Snap them to X=0 before mirroring?\n\n"
                f"This ensures the center seam welds cleanly."
            ),
            button=['Snap', 'Skip', 'Cancel'],
            defaultButton='Snap',
            cancelButton='Cancel',
            dismissString='Cancel',
        )
        if answer == 'Cancel':
            return
        snap = (answer == 'Snap')

    cmds.undoInfo(openChunk=True, chunkName=TOOL_NAME)
    try:
        # 1. Snap near-X verts if user opted in
        if snap:
            _snap_verts_to_x(near_x_verts)
            print(f"{TOOL_NAME}: Snapped {len(near_x_verts)} vert(s) to X=0.")

        # 2. Duplicate and mirror across X=0
        dupe = cmds.duplicate(obj, returnRootsOnly=True)[0]
        cmds.xform(dupe, worldSpace=True, pivots=(0, 0, 0))
        cmds.scale(-1, 1, 1, dupe, worldSpace=True)

        # 3. Reverse normals on the mirror (scaling by -1 flips face winding)
        cmds.polyNormal(dupe, normalMode=0, userNormalMode=0)

        # 4. Combine original + mirror
        combined = cmds.polyUnite(obj, dupe, constructionHistory=False)[0]

        # 4b. Delete leftover source transforms (polyUnite can leave empty groups)
        for src in [obj, dupe]:
            if cmds.objExists(src):
                cmds.delete(src)

        # 5. Merge verts near X=0
        all_verts = cmds.ls(combined + ".vtx[*]", flatten=True)
        center_verts = []
        for vtx in all_verts:
            pos = cmds.pointPosition(vtx, world=True)
            if abs(pos[0]) < weld_threshold * 10:
                center_verts.append(vtx)

        if center_verts:
            cmds.select(center_verts)
            cmds.polyMergeVertex(distance=weld_threshold,
                                 alwaysMergeTwoVertices=False,
                                 constructionHistory=False)

        # 6. Soften normals
        cmds.select(combined)
        cmds.polySoftEdge(combined, angle=180, constructionHistory=False)

        # 7. Delete history
        cmds.delete(combined, constructionHistory=True)

        # 8. Freeze transforms
        cmds.makeIdentity(combined, apply=True, translate=True,
                          rotate=True, scale=True, normal=False)

        # 9. Pivot to origin
        cmds.xform(combined, worldSpace=True, rotatePivot=(0, 0, 0))
        cmds.xform(combined, worldSpace=True, scalePivot=(0, 0, 0))

        # 10. Rename and select
        combined = cmds.rename(combined, obj_name)
        cmds.select(combined)

        print(f"{TOOL_NAME}: Mirrored and welded '{combined}'.")

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
        f"from MirrorWeld import mirror_weld\n"
        f"mirror_weld.run()"
    )
    cmds.shelfButton(
        parent=SHELF_NAME, image="polyMirrorGeometry.png", command=command,
        annotation=TOOL_ANNOTATION, label=TOOL_LABEL,
        imageOverlayLabel=TOOL_LABEL,
        overlayLabelColor=(0.8, 0.8, 0.8),
        overlayLabelBackColor=(0, 0, 0, 0.5),
        sourceType="python", width=35, height=35,
    )
    print(f"{TOOL_NAME}: Added to {SHELF_NAME}.")
