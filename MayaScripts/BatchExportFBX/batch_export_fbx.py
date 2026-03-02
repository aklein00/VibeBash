"""
BatchExportFBX — Export selected objects as individual FBX files
Author: Arthur Klein
Version: 1.0.0

Usage:
    import BatchExportFBX.batch_export_fbx as tool
    tool.run()
"""

import maya.cmds as cmds
import maya.mel as mel
import os

TOOL_NAME = "BatchExportFBX"
TOOL_LABEL = "XFBX"
TOOL_ANNOTATION = "Export selected objects as individual FBX files"
SHELF_NAME = "AK_Shelf"

EXPORT_DIR = os.path.expanduser("~/Downloads/Exports from Maya")


def run():
    """Export each selected transform as a separate FBX to ~/Downloads/Exports from Maya/."""
    selected_objects = cmds.ls(selection=True)
    if not selected_objects:
        cmds.warning(f"{TOOL_NAME}: No objects selected.")
        return

    if not os.path.exists(EXPORT_DIR):
        os.makedirs(EXPORT_DIR)

    cmds.undoInfo(openChunk=True, chunkName=TOOL_NAME)
    try:
        # Configure FBX export settings
        mel.eval('FBXResetExport')
        mel.eval('FBXExportBakeComplexAnimation -v false;')
        mel.eval('FBXExportCameras -v false;')
        mel.eval('FBXExportLights -v false;')
        mel.eval('FBXExportEmbeddedTextures -v true;')
        mel.eval('FBXExportFileVersion -v FBX202000;')

        exported = []
        for obj in selected_objects:
            simple_name = obj.split('|')[-1].split(':')[-1]
            if cmds.objectType(obj, isType='transform'):
                cmds.select(obj, replace=True)
                export_path = os.path.join(EXPORT_DIR, f"{simple_name}.fbx")
                mel.eval(f'FBXExport -f "{export_path}" -s;')
                exported.append(simple_name)
                print(f"  Exported: {export_path}")

        # Restore original selection
        cmds.select(selected_objects, replace=True)
        print(f"{TOOL_NAME}: Exported {len(exported)} object(s) to {EXPORT_DIR}")
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
        f"from BatchExportFBX import batch_export_fbx\n"
        f"batch_export_fbx.run()"
    )
    cmds.shelfButton(
        parent=SHELF_NAME, image="pythonFamily.png", command=command,
        annotation=TOOL_ANNOTATION, label=TOOL_LABEL,
        imageOverlayLabel=TOOL_LABEL,
        overlayLabelColor=(0.1178, 0.03, 0.1129),
        overlayLabelBackColor=(0.5783, 0.4912, 0.136, 0.2),
        sourceType="python", width=35, height=35,
    )
    print(f"{TOOL_NAME}: Added to {SHELF_NAME}.")
