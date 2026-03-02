"""
BatchImport — Import multiple files from a single file dialog
Author: Arthur Klein
Version: 1.0.0

Usage:
    import BatchImport.batch_import as tool
    tool.run()
"""

import maya.cmds as cmds
import os

TOOL_NAME = "BatchImport"
TOOL_LABEL = "BImp"
TOOL_ANNOTATION = "Import multiple files at once"
SHELF_NAME = "AK_Shelf"

# Supported file types for the dialog filter
FILE_FILTER = (
    "All Supported (*.fbx *.obj *.ma *.mb *.abc *.usd *.usda *.usdc);;"
    "FBX (*.fbx);;"
    "OBJ (*.obj);;"
    "Maya ASCII (*.ma);;"
    "Maya Binary (*.mb);;"
    "Alembic (*.abc);;"
    "USD (*.usd *.usda *.usdc);;"
    "All Files (*.*)"
)


def run():
    """Open a multi-select file dialog and import all chosen files."""
    files = cmds.fileDialog2(
        fileMode=4,  # 4 = select multiple existing files
        caption="Select Files to Import",
        fileFilter=FILE_FILTER,
        dialogStyle=2,
    )

    if not files:
        return

    cmds.undoInfo(openChunk=True, chunkName=TOOL_NAME)
    try:
        imported = []
        for filepath in files:
            ext = os.path.splitext(filepath)[1].lower()
            file_type = _detect_type(ext)
            if file_type:
                cmds.file(filepath, i=True, type=file_type,
                          ignoreVersion=True, mergeNamespacesOnClash=True,
                          namespace=":", options="v=0;")
                imported.append(os.path.basename(filepath))
                print(f"  Imported: {filepath}")
            else:
                cmds.warning(f"{TOOL_NAME}: Unsupported format '{ext}' — skipped {filepath}")

        print(f"{TOOL_NAME}: Imported {len(imported)} file(s).")
    except Exception as e:
        cmds.warning(f"{TOOL_NAME}: {e}")
    finally:
        cmds.undoInfo(closeChunk=True)


def _detect_type(ext):
    """Map file extension to Maya file type string."""
    type_map = {
        '.fbx': 'FBX',
        '.obj': 'OBJ',
        '.ma': 'mayaAscii',
        '.mb': 'mayaBinary',
        '.abc': 'Alembic',
        '.usd': 'USD Import',
        '.usda': 'USD Import',
        '.usdc': 'USD Import',
    }
    return type_map.get(ext)


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
        f"from BatchImport import batch_import\n"
        f"batch_import.run()"
    )
    cmds.shelfButton(
        parent=SHELF_NAME, image="fileOpen.png", command=command,
        annotation=TOOL_ANNOTATION, label=TOOL_LABEL,
        imageOverlayLabel=TOOL_LABEL,
        overlayLabelColor=(0.8, 0.8, 0.8),
        overlayLabelBackColor=(0, 0, 0, 0.5),
        sourceType="python", width=35, height=35,
    )
    print(f"{TOOL_NAME}: Added to {SHELF_NAME}.")
