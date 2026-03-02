"""
mesh_analysis_ui — Maya UI for WGLL mesh analysis comparison tool.
Relationship-editor style: load high-res and low-res meshes, run analysis,
output a text report.
"""

import maya.cmds as cmds
import os
import sys

_WGLL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _WGLL_ROOT not in sys.path:
    sys.path.insert(0, _WGLL_ROOT)
import site
_USER_SITE = site.getusersitepackages()
if _USER_SITE not in sys.path:
    sys.path.insert(0, _USER_SITE)

WINDOW_NAME = "wgllMeshAnalysisWindow"


def show_analysis_ui():
    """Open the WGLL Mesh Analysis comparison UI."""

    if cmds.window(WINDOW_NAME, exists=True):
        cmds.deleteUI(WINDOW_NAME)

    state = {
        "high_res": None,
        "low_res": None,
        "last_report": None,
    }

    win = cmds.window(
        WINDOW_NAME,
        title="WGLL Mesh Analysis",
        widthHeight=(400, 420),
    )

    main = cmds.columnLayout(
        adjustableColumn=True, rowSpacing=6,
        columnOffset=("both", 10),
    )

    cmds.text(label="WGLL Mesh Analysis", font="boldLabelFont", height=28)
    cmds.text(label="Compare high-res sculpt to low-res retopo",
              font="smallPlainLabelFont")

    # === HIGH-RES SLOT ===
    cmds.separator(height=8, style="in")
    cmds.text(label="High-Res Mesh", font="boldLabelFont", align="left")
    hi_row = cmds.rowLayout(numberOfColumns=2, columnWidth2=(300, 90))
    hi_field = cmds.textField(editable=False, placeholderText="(select and load)")
    hi_btn = cmds.button(label="< Load Selected", height=24)
    cmds.setParent(main)
    hi_info = cmds.text(label="", align="left", height=16)

    # === LOW-RES SLOT ===
    cmds.separator(height=8, style="in")
    cmds.text(label="Low-Res Mesh", font="boldLabelFont", align="left")
    lo_row = cmds.rowLayout(numberOfColumns=2, columnWidth2=(300, 90))
    lo_field = cmds.textField(editable=False, placeholderText="(select and load)")
    lo_btn = cmds.button(label="< Load Selected", height=24)
    cmds.setParent(main)
    lo_info = cmds.text(label="", align="left", height=16)

    # === ANALYSIS ===
    cmds.separator(height=8, style="in")
    status_text = cmds.text(label="  Load both meshes, then click Analyze.",
                            align="left", height=20)

    analyze_btn = cmds.button(
        label="Run Analysis",
        height=40,
        backgroundColor=(0.3, 0.5, 0.7),
        enable=False,
    )

    # === OUTPUT ===
    cmds.separator(height=8, style="in")
    output_label = cmds.text(
        label=f"  Output: WGLL_Retopo/analysis/",
        align="left", font="smallPlainLabelFont",
    )
    open_btn = cmds.button(
        label="Open Last Report",
        height=28,
        enable=False,
    )
    report_path_text = cmds.text(label="", align="left", font="smallPlainLabelFont")

    # === CALLBACKS ===

    def _update_status(msg):
        cmds.text(status_text, edit=True, label=f"  {msg}")

    def _check_ready():
        ready = state["high_res"] is not None and state["low_res"] is not None
        cmds.button(analyze_btn, edit=True, enable=ready)
        if ready:
            _update_status("Ready. Click Run Analysis.")

    def _load_mesh(slot):
        """Load selected mesh into a slot ('high_res' or 'low_res')."""
        sel = cmds.ls(selection=True, long=True)
        if not sel:
            _update_status("Nothing selected.")
            return
        obj = sel[0]
        shapes = cmds.listRelatives(obj, shapes=True, type='mesh')
        if not shapes:
            _update_status(f"'{obj}' is not a polygon mesh.")
            return

        fc = cmds.polyEvaluate(obj, face=True) or 0
        vc = cmds.polyEvaluate(obj, vertex=True) or 0
        short = obj.split('|')[-1].split(':')[-1]

        state[slot] = obj

        field = hi_field if slot == "high_res" else lo_field
        info = hi_info if slot == "high_res" else lo_info

        cmds.textField(field, edit=True, text=short)
        cmds.text(info, edit=True, label=f"  {vc:,} verts, {fc:,} faces")

        _check_ready()

    def _on_load_hi(*args):
        _load_mesh("high_res")

    def _on_load_lo(*args):
        _load_mesh("low_res")

    def _on_analyze(*args):
        if not state["high_res"] or not state["low_res"]:
            _update_status("Load both meshes first.")
            return

        # Validate high > low
        hi_fc = cmds.polyEvaluate(state["high_res"], face=True) or 0
        lo_fc = cmds.polyEvaluate(state["low_res"], face=True) or 0
        if hi_fc <= lo_fc:
            _update_status(
                f"High-res ({hi_fc:,}) must have more faces than low-res ({lo_fc:,}). "
                f"Swap them."
            )
            return

        _update_status("Running analysis...")

        from maya_bridge.mesh_analysis_report import analyze_meshes, save_report

        # Progress window
        cmds.progressWindow(
            title="WGLL Analysis",
            progress=0, status="Analyzing...",
            isInterruptable=False, minValue=0, maxValue=100,
        )

        def _prog(msg, pct):
            cmds.progressWindow(edit=True, progress=int(pct), status=msg)

        try:
            report = analyze_meshes(
                state["high_res"], state["low_res"],
                progress_fn=_prog,
            )

            filepath = save_report(report)
            state["last_report"] = filepath

            cmds.button(open_btn, edit=True, enable=True)
            cmds.text(report_path_text, edit=True,
                      label=f"  Saved: {os.path.basename(filepath)}")
            _update_status("Analysis complete! Report saved.")

            print(f"\nWGLL Analysis saved to: {filepath}")
            print(f"\n{report}")

        except Exception as e:
            _update_status(f"Analysis failed: {e}")
            import traceback
            traceback.print_exc()
        finally:
            cmds.progressWindow(endProgress=True)

    def _on_open_report(*args):
        if state["last_report"] and os.path.exists(state["last_report"]):
            # Open in system text editor
            import subprocess
            subprocess.Popen(['open', state["last_report"]])

    # Wire callbacks
    cmds.button(hi_btn, edit=True, command=_on_load_hi)
    cmds.button(lo_btn, edit=True, command=_on_load_lo)
    cmds.button(analyze_btn, edit=True, command=_on_analyze)
    cmds.button(open_btn, edit=True, command=_on_open_report)

    cmds.showWindow(win)
