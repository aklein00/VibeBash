"""
FaceUVManager — Facial expression UV atlas control (8x8 grid)
Author: Arthur Klein
Version: 1.0.0

Manages facial expression UV offsets on an 8x8 texture atlas.
Supports separate eye L/R control, linking, presets.

Usage:
    from FaceUVManager import face_uv_manager
    mgr = face_uv_manager.FaceUVManager()
    mgr.show()
"""

import maya.cmds as cmds
import json
import os

TOOL_NAME = "FaceUVManager"
TOOL_LABEL = "FaceUV"
TOOL_ANNOTATION = "Face UV Manager - Expression atlas control"
SHELF_NAME = "AK_Shelf"


class FaceUVManager:

    # Constants
    ATLAS_ROWS = 8
    ATLAS_COLS = 8
    UV_CELL_SIZE = 1.0 / 8.0
    PRESET_FILE_NAME = "presets.json"

    def __init__(self):
        self.window_name = "face_uv_manager_window"
        self.dock_name = "face_uv_manager_dock"

        # Default settings
        self.mouth_mesh = "mouth_expressions"
        self.left_eye_mesh = "eye_left_expressions"
        self.right_eye_mesh = "eye_right_expressions"

        # Default Positions (0-indexed coordinates)
        self.default_eye_pos = {'col': 0, 'row': 7}   # A, 7
        self.default_mouth_pos = {'col': 0, 'row': 0}  # A, 0

        # Current State
        self.left_eye_pos = self.default_eye_pos.copy()
        self.right_eye_pos = self.default_eye_pos.copy()
        self.mouth_pos = self.default_mouth_pos.copy()

        # UI Selection State
        self.active_mode = 'eye_linked'  # 'eye_linked', 'eye_left', 'eye_right', 'mouth'

        try:
            self.script_dir = os.path.dirname(os.path.abspath(__file__))
        except NameError:
            self.script_dir = '/Users/arthurklein/Documents/Work/Side/VibeBash/MayaScripts/FaceUVManager'

        self.presets_path = os.path.join(self.script_dir, self.PRESET_FILE_NAME)
        self.presets = self.load_presets()

        # Column mapping (A=0, B=1, etc.)
        self.cols = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

    def show(self):
        if cmds.window(self.window_name, exists=True):
            cmds.deleteUI(self.window_name)

        self.window = cmds.window(self.window_name, title="Face UV Manager", widthHeight=(400, 700))

        main_layout = cmds.columnLayout(adjustableColumn=True)

        # --- Settings Section ---
        cmds.frameLayout(label="Settings", collapsable=True, parent=main_layout)
        cmds.rowLayout(numberOfColumns=2, adjustableColumn=2)
        cmds.text(label="Mouth Mesh:")
        self.mouth_mesh_field = cmds.textField(text=self.mouth_mesh, changeCommand=self.update_settings)
        cmds.setParent('..')
        cmds.rowLayout(numberOfColumns=2, adjustableColumn=2)
        cmds.text(label="Left Eye Mesh:")
        self.left_eye_mesh_field = cmds.textField(text=self.left_eye_mesh, changeCommand=self.update_settings)
        cmds.setParent('..')
        cmds.rowLayout(numberOfColumns=2, adjustableColumn=2)
        cmds.text(label="Right Eye Mesh:")
        self.right_eye_mesh_field = cmds.textField(text=self.right_eye_mesh, changeCommand=self.update_settings)
        cmds.setParent('..')
        cmds.setParent('..')  # End Settings Frame

        # --- Controls Section ---
        cmds.frameLayout(label="Controls", parent=main_layout)

        # Mode Selection
        cmds.rowLayout(numberOfColumns=2, adjustableColumn=2)
        cmds.text(label="Target: ", align='right', width=50)
        self.selection_collection = cmds.radioCollection()
        cmds.rowLayout(numberOfColumns=3)
        self.rb_eyes = cmds.radioButton(label='Eyes', select=True, onCommand=self.on_mode_change)
        self.rb_mouth = cmds.radioButton(label='Mouth', onCommand=self.on_mode_change)
        cmds.setParent('..')
        cmds.setParent('..')

        # Eye Linking Controls
        self.eye_options_layout = cmds.rowLayout(numberOfColumns=3, adjustableColumn=2)
        cmds.text(label="", width=50)  # spacer

        cmds.columnLayout(adjustableColumn=True)
        self.chk_link_eyes = cmds.checkBox(label="Link L/R", value=True, changeCommand=self.on_mode_change)

        cmds.rowLayout(numberOfColumns=2)
        self.eye_side_collection = cmds.radioCollection()
        self.rb_eye_left = cmds.radioButton(label="Left", onCommand=self.on_mode_change)
        self.rb_eye_right = cmds.radioButton(label="Right", onCommand=self.on_mode_change)
        cmds.setParent('..')
        cmds.setParent('..')

        # Gather Button
        self.btn_gather = cmds.button(label="Gather (L->R)", width=80, command=self.gather_eyes)

        cmds.setParent('..')

        # Grid Position Display
        cmds.separator(style='none', height=5)
        cmds.rowLayout(numberOfColumns=6)
        cmds.text(label="  L Eye:")
        self.lbl_eye_l = cmds.text(label=self.get_coord_str(self.left_eye_pos), font="boldLabelFont")
        cmds.text(label="  R Eye:")
        self.lbl_eye_r = cmds.text(label=self.get_coord_str(self.right_eye_pos), font="boldLabelFont")
        cmds.text(label="  Mouth:")
        self.lbl_mouth = cmds.text(label=self.get_coord_str(self.mouth_pos), font="boldLabelFont")
        cmds.setParent('..')

        # Navigation Buttons (D-Pad Style)
        cmds.columnLayout(adjustableColumn=True)
        cmds.separator(style='none', height=10)

        cmds.rowLayout(numberOfColumns=2, adjustableColumn=2)

        cmds.gridLayout(numberOfColumns=3, cellWidthHeight=(60, 40))
        cmds.separator(style='none')
        cmds.button(label="UP", command=lambda x: self.nudge_selection(0, 1))
        cmds.separator(style='none')
        cmds.button(label="LEFT", command=lambda x: self.nudge_selection(-1, 0))
        cmds.separator(style='none')
        cmds.button(label="RIGHT", command=lambda x: self.nudge_selection(1, 0))
        cmds.separator(style='none')
        cmds.button(label="DOWN", command=lambda x: self.nudge_selection(0, -1))
        cmds.separator(style='none')
        cmds.setParent('..')

        cmds.separator(style='none')
        cmds.setParent('..')

        # Back to Default Button
        cmds.separator(height=10, style='none')
        cmds.button(label="Back to Default", command=self.reset_to_defaults)
        cmds.separator(height=10, style='none')

        cmds.setParent('..')
        cmds.setParent('..')  # End Controls Frame

        # --- Preset Section ---
        cmds.frameLayout(label="Expressions / Presets", parent=main_layout)

        self.preset_list = cmds.textScrollList(numberOfRows=8, allowMultiSelection=False,
                                               selectCommand=self.on_preset_select,
                                               doubleClickCommand=self.apply_current_preset)
        self.refresh_preset_list()

        cmds.rowLayout(numberOfColumns=3, adjustableColumn=1)
        self.preset_name_field = cmds.textField(placeholderText="New Expression Name")
        cmds.button(label="Save New", command=self.save_new_preset)
        cmds.button(label="Rename", command=self.rename_preset)
        cmds.setParent('..')

        cmds.button(label="Delete Selected", command=self.delete_preset)
        cmds.button(label="Apply Selected", command=self.apply_current_preset)

        cmds.setParent('..')  # End Preset Frame

        cmds.showWindow(self.window)

        # Initial state update
        cmds.radioCollection(self.eye_side_collection, edit=True, select=self.rb_eye_left)
        self.on_mode_change()
        self.update_ui_labels()

    def update_settings(self, *args):
        self.mouth_mesh = cmds.textField(self.mouth_mesh_field, query=True, text=True)
        self.left_eye_mesh = cmds.textField(self.left_eye_mesh_field, query=True, text=True)
        self.right_eye_mesh = cmds.textField(self.right_eye_mesh_field, query=True, text=True)

    def on_mode_change(self, *args):
        is_mouth = cmds.radioButton(self.rb_mouth, query=True, select=True)

        if is_mouth:
            self.active_mode = 'mouth'
            cmds.control(self.chk_link_eyes, edit=True, enable=False)
            cmds.control(self.rb_eye_left, edit=True, enable=False)
            cmds.control(self.rb_eye_right, edit=True, enable=False)
            cmds.control(self.btn_gather, edit=True, enable=False)
        else:
            cmds.control(self.chk_link_eyes, edit=True, enable=True)
            is_linked = cmds.checkBox(self.chk_link_eyes, query=True, value=True)
            cmds.control(self.btn_gather, edit=True, enable=True)

            if is_linked:
                self.active_mode = 'eye_linked'
                cmds.control(self.rb_eye_left, edit=True, enable=False)
                cmds.control(self.rb_eye_right, edit=True, enable=False)
            else:
                cmds.control(self.rb_eye_left, edit=True, enable=True)
                cmds.control(self.rb_eye_right, edit=True, enable=True)
                if cmds.radioButton(self.rb_eye_left, query=True, select=True):
                    self.active_mode = 'eye_left'
                else:
                    self.active_mode = 'eye_right'

    def get_coord_str(self, pos_dict):
        col_char = self.cols[pos_dict['col']]
        return "({}, {})".format(col_char, pos_dict['row'])

    def gather_eyes(self, *args):
        self.left_eye_pos = self.right_eye_pos.copy()
        self.apply_uv_offset(self.left_eye_mesh, self.left_eye_pos['col'], self.left_eye_pos['row'])
        self.update_ui_labels()
        print("Gathered Left Eye to Right Eye Position.")

    def nudge_selection(self, d_col, d_row):
        targets = []
        min_row, max_row = 0, 7

        if self.active_mode == 'mouth':
            targets.append((self.mouth_mesh, self.mouth_pos))
            min_row, max_row = 0, 3
        elif self.active_mode == 'eye_linked':
            targets.append((self.left_eye_mesh, self.left_eye_pos))
            targets.append((self.right_eye_mesh, self.right_eye_pos))
            min_row, max_row = 4, 7
        elif self.active_mode == 'eye_left':
            targets.append((self.left_eye_mesh, self.left_eye_pos))
            min_row, max_row = 4, 7
        elif self.active_mode == 'eye_right':
            targets.append((self.right_eye_mesh, self.right_eye_pos))
            min_row, max_row = 4, 7

        for mesh_name, pos in targets:
            new_col = max(0, min(self.ATLAS_COLS - 1, pos['col'] + d_col))
            new_row = max(min_row, min(max_row, pos['row'] + d_row))
            pos['col'] = new_col
            pos['row'] = new_row
            self.apply_uv_offset(mesh_name, new_col, new_row)

        self.update_ui_labels()

    def reset_to_defaults(self, *args):
        self.left_eye_pos = self.default_eye_pos.copy()
        self.right_eye_pos = self.default_eye_pos.copy()
        self.mouth_pos = self.default_mouth_pos.copy()
        self.update_ui_labels()
        self.apply_uv_offset(self.mouth_mesh, self.mouth_pos['col'], self.mouth_pos['row'])
        self.apply_uv_offset(self.left_eye_mesh, self.left_eye_pos['col'], self.left_eye_pos['row'])
        self.apply_uv_offset(self.right_eye_mesh, self.right_eye_pos['col'], self.right_eye_pos['row'])
        print("Reset to defaults.")

    def apply_uv_offset(self, mesh_name, col, row):
        if not cmds.objExists(mesh_name):
            return

        u_min = col * self.UV_CELL_SIZE
        v_min = row * self.UV_CELL_SIZE

        uvs = cmds.polyListComponentConversion(mesh_name, toUV=True)
        if not uvs:
            return

        vals = cmds.polyEditUV(uvs, query=True)
        if not vals:
            return

        us = vals[0::2]
        vs = vals[1::2]

        curr_center_u = (min(us) + max(us)) / 2.0
        curr_center_v = (min(vs) + max(vs)) / 2.0

        target_center_u = u_min + (self.UV_CELL_SIZE / 2.0)
        target_center_v = v_min + (self.UV_CELL_SIZE / 2.0)

        offset_u = target_center_u - curr_center_u
        offset_v = target_center_v - curr_center_v

        cmds.polyEditUV(uvs, u=offset_u, v=offset_v, relative=True)

    def update_ui_labels(self):
        cmds.text(self.lbl_eye_l, edit=True, label=self.get_coord_str(self.left_eye_pos))
        cmds.text(self.lbl_eye_r, edit=True, label=self.get_coord_str(self.right_eye_pos))
        cmds.text(self.lbl_mouth, edit=True, label=self.get_coord_str(self.mouth_pos))

    # --- Preset Handling ---

    def load_presets(self):
        if os.path.exists(self.presets_path):
            try:
                with open(self.presets_path, 'r') as f:
                    data = json.load(f)
                    return self.migrate_presets(data)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def migrate_presets(self, data):
        clean_data = {}
        for name, val in data.items():
            if 'eye' in val and 'left_eye' not in val:
                new_val = {
                    'left_eye': val['eye'].copy(),
                    'right_eye': val['eye'].copy(),
                    'mouth': val['mouth'].copy()
                }
                clean_data[name] = new_val
            else:
                clean_data[name] = val
        return clean_data

    def save_presets(self):
        with open(self.presets_path, 'w') as f:
            json.dump(self.presets, f, indent=4)

    def refresh_preset_list(self):
        cmds.textScrollList(self.preset_list, edit=True, removeAll=True)
        for name in sorted(self.presets.keys()):
            cmds.textScrollList(self.preset_list, edit=True, append=name)

    def on_preset_select(self, *args):
        pass

    def save_new_preset(self, *args):
        name = cmds.textField(self.preset_name_field, query=True, text=True)
        if not name:
            cmds.warning("Please enter a name.")
            return
        self.presets[name] = {
            'left_eye': self.left_eye_pos.copy(),
            'right_eye': self.right_eye_pos.copy(),
            'mouth': self.mouth_pos.copy()
        }
        self.save_presets()
        self.refresh_preset_list()
        print("Saved preset: {}".format(name))

    def rename_preset(self, *args):
        selected = cmds.textScrollList(self.preset_list, query=True, selectItem=True)
        if not selected:
            return
        old_name = selected[0]
        new_name = cmds.textField(self.preset_name_field, query=True, text=True)
        if not new_name:
            return
        if new_name in self.presets:
            cmds.warning("Name already exists.")
            return
        self.presets[new_name] = self.presets.pop(old_name)
        self.save_presets()
        self.refresh_preset_list()

    def delete_preset(self, *args):
        selected = cmds.textScrollList(self.preset_list, query=True, selectItem=True)
        if not selected:
            return
        name = selected[0]
        del self.presets[name]
        self.save_presets()
        self.refresh_preset_list()

    def apply_current_preset(self, *args):
        selected = cmds.textScrollList(self.preset_list, query=True, selectItem=True)
        if not selected:
            return
        name = selected[0]
        data = self.presets.get(name)
        if not data:
            return
        self.left_eye_pos = data.get('left_eye', self.default_eye_pos).copy()
        self.right_eye_pos = data.get('right_eye', self.default_eye_pos).copy()
        self.mouth_pos = data.get('mouth', self.default_mouth_pos).copy()
        self.update_ui_labels()
        self.apply_uv_offset(self.left_eye_mesh, self.left_eye_pos['col'], self.left_eye_pos['row'])
        self.apply_uv_offset(self.right_eye_mesh, self.right_eye_pos['col'], self.right_eye_pos['row'])
        self.apply_uv_offset(self.mouth_mesh, self.mouth_pos['col'], self.mouth_pos['row'])
        print("Applied preset: {}".format(name))


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
        f"from FaceUVManager import face_uv_manager\n"
        f"mgr = face_uv_manager.FaceUVManager(); mgr.show()"
    )
    cmds.shelfButton(
        parent=SHELF_NAME, image="polyEditUV.png", command=command,
        annotation=TOOL_ANNOTATION, label=TOOL_LABEL,
        imageOverlayLabel=TOOL_LABEL,
        overlayLabelColor=(0.8, 0.8, 0.8),
        overlayLabelBackColor=(0, 0, 0, 0.5),
        sourceType="python", width=35, height=35,
    )
    print(f"{TOOL_NAME}: Added to {SHELF_NAME}.")
