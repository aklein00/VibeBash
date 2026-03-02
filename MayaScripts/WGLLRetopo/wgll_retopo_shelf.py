"""
WGLLRetopo — WGLL Retopo shelf entry point for Maya.
Curvature-guided retopology for mobile game characters.
Author: Arthur Klein
Version: 0.2.0

Usage:
    import WGLLRetopo
    WGLLRetopo.run()            # Quick retopo (select mesh first)
    WGLLRetopo.run_with_ui()    # Open UI with parameter controls
"""

import maya.cmds as cmds
import os
import sys

# --- Configuration ---
TOOL_NAME = "WGLLRetopo"
TOOL_LABEL = "Retopo"
TOOL_ANNOTATION = "WGLL Retopo — Curvature-guided retopology"
TOOL_ICON = "polyRetopo.png"
SHELF_NAME = "AK_Shelf"

WGLL_ROOT = '/Users/arthurklein/Documents/Work/Side/VibeBash/WGLL_Retopo'

# Safety thresholds for mesh complexity
_THRESHOLD_FAST = 50000       # < 50K faces: fast, no warning
_THRESHOLD_MODERATE = 200000  # < 200K: moderate, warn
_THRESHOLD_SLOW = 500000      # < 500K: slow, recommend reduce
                              # >= 500K: very slow, require reduce


def _ensure_paths():
    """Add WGLL_Retopo and user site-packages to sys.path."""
    import site
    user_site = site.getusersitepackages()
    paths = [WGLL_ROOT, os.path.join(WGLL_ROOT, 'maya_bridge'), user_site]
    for p in paths:
        if p not in sys.path:
            sys.path.insert(0, p)


def _reload_modules():
    """Force-reload all WGLL modules so code changes take effect."""
    import importlib
    import core.mesh_io, core.mesh_analysis, core.guide_generation
    importlib.reload(core.mesh_io)
    importlib.reload(core.mesh_analysis)
    importlib.reload(core.guide_generation)
    import maya_bridge.maya_mesh_adapter, maya_bridge.maya_polyretopo_tuned
    importlib.reload(maya_bridge.maya_mesh_adapter)
    importlib.reload(maya_bridge.maya_polyretopo_tuned)


def run(target_face_count=5000):
    """Quick-run: guided retopo on selected mesh with default settings."""
    _ensure_paths()
    from maya_bridge.maya_polyretopo_tuned import quick_retopo
    return quick_retopo(target_face_count=target_face_count)


def run_with_ui():
    """Launch WGLL Retopo UI with two-step analyze-then-retopo workflow."""
    _ensure_paths()

    window_name = "wgllRetopoWindow"
    if cmds.window(window_name, exists=True):
        cmds.deleteUI(window_name)

    # Shared state between callbacks
    state = {
        "analyzed": False,
        "guides": None,
        "mesh_name": None,
        "reduced_mesh": None,
    }

    window = cmds.window(
        window_name,
        title="WGLL Retopo — Guided Retopology",
        widthHeight=(430, 560),
    )

    main_layout = cmds.columnLayout(
        adjustableColumn=True, rowSpacing=6,
        columnOffset=("both", 10),
    )

    cmds.text(label="WGLL Retopo", font="boldLabelFont", height=28)
    cmds.text(
        label="Curvature-guided retopology for mobile characters",
        font="smallPlainLabelFont",
    )

    # =============================================
    # SECTION 1: Mesh info + Analyze
    # =============================================
    cmds.separator(height=8, style="in")
    cmds.text(label="Step 1: Analyze Mesh", font="boldLabelFont", align="left")

    # Status display
    status_text = cmds.text(
        label="  Select a mesh and click Analyze.",
        align="left", height=20,
    )
    mesh_info_text = cmds.text(label="", align="left", height=18)
    warning_text = cmds.text(label="", align="left", height=18)

    # Reduce section (hidden by default, shown for large meshes)
    reduce_frame = cmds.frameLayout(
        label="Reduce Mesh (polyReduce)",
        collapsable=True, collapse=True,
        visible=False,
        marginWidth=5, marginHeight=5,
    )
    cmds.text(
        label="Your mesh is too dense for Python analysis.\n"
             "Reduce it first — WGLL will analyze the reduced copy\n"
             "and apply guides to the original.",
        align="left", wordWrap=True, height=50,
    )
    cmds.text(label="Keep (% of original):", align="left")
    reduce_slider = cmds.floatSliderGrp(
        field=True, minValue=1.0, maxValue=100.0,
        value=50.0, step=1.0,
        columnWidth=[(1, 60), (2, 280)],
    )

    reduce_btn = cmds.button(
        label="polyReduce",
        height=32,
        backgroundColor=(0.6, 0.5, 0.2),
    )
    cmds.setParent(main_layout)

    # Analyze button
    analyze_btn = cmds.button(
        label="Analyze Selected Mesh",
        height=38,
        backgroundColor=(0.3, 0.5, 0.7),
    )

    # =============================================
    # SECTION 2: Retopo Parameters
    # =============================================
    cmds.separator(height=8, style="in")
    cmds.text(label="Step 2: Retopologize", font="boldLabelFont", align="left")

    # Target face count
    cmds.text(label="Target Face Count:", align="left")
    face_count_field = cmds.intSliderGrp(
        field=True, minValue=200, maxValue=20000,
        value=5000, step=100,
        columnWidth=[(1, 80), (2, 270)],
    )

    # Curvature percentile
    cmds.text(label="Feature Sensitivity (lower = more guides):", align="left")
    curvature_slider = cmds.floatSliderGrp(
        field=True, minValue=50.0, maxValue=95.0,
        value=75.0, step=1.0,
        columnWidth=[(1, 80), (2, 270)],
    )

    # Crease angle
    cmds.text(label="Crease Angle (degrees):", align="left")
    crease_slider = cmds.floatSliderGrp(
        field=True, minValue=10.0, maxValue=90.0,
        value=30.0, step=1.0,
        columnWidth=[(1, 80), (2, 270)],
    )

    # Face uniformity
    cmds.text(label="Face Uniformity (lower = more adaptive):", align="left")
    uniformity_slider = cmds.floatSliderGrp(
        field=True, minValue=0.0, maxValue=1.0,
        value=0.3, step=0.05,
        columnWidth=[(1, 80), (2, 270)],
    )

    # Preset buttons
    cmds.text(label="Presets:", align="left")
    cmds.rowLayout(numberOfColumns=3, columnWidth3=(130, 130, 130))

    def _preset_hero(*args):
        cmds.intSliderGrp(face_count_field, edit=True, value=6000)
        cmds.floatSliderGrp(curvature_slider, edit=True, value=70.0)
        cmds.floatSliderGrp(crease_slider, edit=True, value=25.0)
        cmds.floatSliderGrp(uniformity_slider, edit=True, value=0.3)

    def _preset_bg(*args):
        cmds.intSliderGrp(face_count_field, edit=True, value=2000)
        cmds.floatSliderGrp(curvature_slider, edit=True, value=80.0)
        cmds.floatSliderGrp(crease_slider, edit=True, value=35.0)
        cmds.floatSliderGrp(uniformity_slider, edit=True, value=0.5)

    def _preset_prop(*args):
        cmds.intSliderGrp(face_count_field, edit=True, value=500)
        cmds.floatSliderGrp(curvature_slider, edit=True, value=85.0)
        cmds.floatSliderGrp(crease_slider, edit=True, value=40.0)
        cmds.floatSliderGrp(uniformity_slider, edit=True, value=0.7)

    cmds.button(label="Hero Character", command=_preset_hero, height=28)
    cmds.button(label="Background NPC", command=_preset_bg, height=28)
    cmds.button(label="Prop", command=_preset_prop, height=28)
    cmds.setParent(main_layout)

    cmds.separator(height=6)

    # Retopo button (disabled until analysis passes)
    retopo_btn = cmds.button(
        label="Run Retopo (Analyze first)",
        height=42,
        backgroundColor=(0.35, 0.35, 0.35),
        enable=False,
    )

    # Fallback: plain polyRetopo without analysis
    cmds.separator(height=4)
    fallback_btn = cmds.button(
        label="Skip Analysis — Run Plain polyRetopo",
        height=28,
        backgroundColor=(0.4, 0.3, 0.3),
    )
    cmds.text(
        label="(No curvature guides — uses Maya defaults)",
        font="smallPlainLabelFont", align="center",
    )

    # =============================================
    # CALLBACKS
    # =============================================

    def _update_status(msg, color=None):
        cmds.text(status_text, edit=True, label=f"  {msg}")

    def _set_analyzed(success, guides=None, mesh=None):
        state["analyzed"] = success
        state["guides"] = guides
        state["mesh_name"] = mesh
        if success:
            cmds.button(retopo_btn, edit=True,
                        label="Run WGLL Guided Retopo",
                        backgroundColor=(0.3, 0.65, 0.3),
                        enable=True)
        else:
            cmds.button(retopo_btn, edit=True,
                        label="Run Retopo (Analyze first)",
                        backgroundColor=(0.35, 0.35, 0.35),
                        enable=False)

    def _get_selected_mesh():
        """Get selected mesh and its face count, or None."""
        sel = cmds.ls(selection=True, long=True)
        if not sel:
            return None, 0
        obj = sel[0]
        shapes = cmds.listRelatives(obj, shapes=True, type='mesh')
        if not shapes:
            return None, 0
        fc = cmds.polyEvaluate(obj, face=True)
        return obj, fc or 0

    def _classify_mesh(face_count):
        """Return safety tier and recommendation."""
        if face_count < _THRESHOLD_FAST:
            return "fast", f"Fast ({face_count:,} faces) — ready to analyze."
        elif face_count < _THRESHOLD_MODERATE:
            return "moderate", f"Moderate ({face_count:,} faces) — analysis will take ~10-30s."
        elif face_count < _THRESHOLD_SLOW:
            return "slow", f"Dense ({face_count:,} faces) — analysis will take 1-3 min."
        else:
            return "danger", f"Very dense ({face_count:,} faces) — may freeze Maya."

    def _on_analyze(*args):
        _ensure_paths()
        _reload_modules()
        _set_analyzed(False)

        mesh, fc = _get_selected_mesh()
        if not mesh:
            _update_status("Nothing selected. Select a polygon mesh.")
            cmds.text(mesh_info_text, edit=True, label="")
            cmds.text(warning_text, edit=True, label="")
            return

        tier, msg = _classify_mesh(fc)
        short = mesh.split('|')[-1].split(':')[-1]
        verts = cmds.polyEvaluate(mesh, vertex=True) or 0
        cmds.text(mesh_info_text, edit=True,
                  label=f"  {short}: {verts:,} verts, {fc:,} faces")

        if tier == "danger":
            _update_status("Too dense for direct analysis.")
            cmds.text(warning_text, edit=True,
                      label="  Reduce first, or use Skip Analysis below.")
            cmds.frameLayout(reduce_frame, edit=True, visible=True, collapse=False)
            return

        if tier == "slow":
            cmds.text(warning_text, edit=True,
                      label="  Consider reducing first for faster results.")
            cmds.frameLayout(reduce_frame, edit=True, visible=True, collapse=True)
        else:
            cmds.text(warning_text, edit=True, label="")
            cmds.frameLayout(reduce_frame, edit=True, visible=False)

        _update_status(msg + " Running analysis...")

        # Run the analysis
        from maya_bridge.maya_polyretopo_tuned import _make_progress_callback
        from maya_bridge.maya_mesh_adapter import maya_to_wgll_mesh
        from core.guide_generation import generate_guides, format_guide_summary

        cmds.progressWindow(
            title="WGLL Analyze",
            progress=0, status="Analyzing...",
            isInterruptable=True, minValue=0, maxValue=100,
        )
        try:
            wgll_mesh = maya_to_wgll_mesh(mesh)
            progress_cb = _make_progress_callback()

            curvature_pct = cmds.floatSliderGrp(
                curvature_slider, query=True, value=True)
            crease_ang = cmds.floatSliderGrp(
                crease_slider, query=True, value=True)

            guides = generate_guides(
                wgll_mesh,
                curvature_percentile=curvature_pct,
                crease_angle=crease_ang,
                progress_fn=progress_cb,
            )

            if cmds.progressWindow(query=True, isCancelled=True):
                _update_status("Analysis cancelled.")
                return

            summary = format_guide_summary(guides)
            print(f"\n{summary}")

            _update_status(
                f"Analysis complete — {guides.guide_edge_count} guide edges found."
            )
            _set_analyzed(True, guides=guides, mesh=mesh)

        except Exception as e:
            _update_status(f"Analysis failed: {e}")
            import traceback
            traceback.print_exc()
        finally:
            cmds.progressWindow(endProgress=True)

    def _parse_reduction_pct(name):
        """
        Parse the _redN suffix to get current % of original.
        Returns 100 if no suffix found (meaning it's the original mesh).
        e.g. 'myMesh_red20' -> 20, 'myMesh' -> 100
        """
        import re
        match = re.search(r'_red(\d+)$', name)
        if match:
            return int(match.group(1))
        return 100

    def _make_reduced_name(name, slider_pct):
        """
        Build a reduced mesh name with cumulative _redN suffix.
        - Strips any existing _redN suffix
        - Computes cumulative % of original
        - Appends _redN where N = total % of original remaining

        e.g. 'myMesh' slider=20 -> 'myMesh_red20'
             'myMesh_red20' slider=50 -> 'myMesh_red10'  (50% of 20% = 10%)
        """
        import re
        current_pct = _parse_reduction_pct(name)
        new_pct = max(1, int(current_pct * slider_pct / 100.0))
        base_name = re.sub(r'_red\d+$', '', name)
        return f"{base_name}_red{new_pct}", new_pct

    def _fix_nonmanifold(mesh_name):
        """
        Fix non-manifold geometry on a mesh so polyReduce can process it.
        Uses Maya's Mesh > Cleanup (polyCleanupArgList) which is the only
        reliable way to fix non-manifold in Maya.
        """
        import maya.mel as mel

        _update_status("Fixing non-manifold geometry (Mesh Cleanup)...")
        cmds.select(mesh_name, replace=True)

        # polyCleanupArgList 4 args (18 total):
        #  [0] "0" = all meshes in selection
        #  [1] "2" = CLEANUP mode (not "1" which is select-only)
        #  [2] "1" = 4-sided faces
        #  [3] "0" = n-sided faces
        #  [4] "1" = concave faces
        #  [5] "1" = faces with holes
        #  [6] "1" = non-planar faces
        #  [7] "1" = (tolerance flag)
        #  [8] "0" = zero area faces
        #  [9] "1e-05" = zero area tolerance
        # [10] "1" = zero length edges
        # [11] "1e-05" = zero length tolerance
        # [12] "0" = (unused)
        # [13] "1e-05" = tolerance
        # [14] "0" = (unused)
        # [15] "1" = non-manifold geometry (KEY flag)
        # [16] "1" = lamina faces
        # [17] "0" = (unused)
        mel.eval(
            'polyCleanupArgList 4 '
            '{ "0","2","1","0","1","1","1","1","0","1e-05",'
            '"1","1e-05","0","1e-05","0","1","1","0" }'
        )

        cmds.delete(mesh_name, constructionHistory=True)
        new_fc = cmds.polyEvaluate(mesh_name, face=True) or 0
        print(f"WGLL Retopo: Cleanup complete — {new_fc:,} faces")
        return mesh_name

    def _on_reduce(*args):
        """Reduce selected mesh using polyReduce with cumulative naming."""
        mesh, fc = _get_selected_mesh()
        if not mesh:
            _update_status("Nothing selected.")
            return

        slider_pct = cmds.floatSliderGrp(reduce_slider, query=True, value=True)
        short = mesh.split('|')[-1].split(':')[-1]
        new_name, total_pct = _make_reduced_name(short, slider_pct)

        _update_status(f"Reducing to {total_pct}% of original...")

        cmds.undoInfo(openChunk=True, chunkName="WGLL_Reduce")
        try:
            # Duplicate
            dup = cmds.duplicate(mesh, name=new_name)[0]

            # Try polyReduce directly first
            _update_status("Running polyReduce...")
            reduce_ok = False
            try:
                cmds.polyReduce(
                    dup,
                    ver=1,
                    percentage=100.0 - slider_pct,
                    triangulate=False,
                    preserveTopology=True,
                    constructionHistory=True,
                )
                reduce_ok = True
            except RuntimeError as e:
                if "nonmanifold" in str(e).lower():
                    # Fix non-manifold via OBJ roundtrip, then retry
                    dup = _fix_nonmanifold(dup)
                    _update_status("Retrying polyReduce on cleaned mesh...")
                    cmds.polyReduce(
                        dup,
                        ver=1,
                        percentage=100.0 - slider_pct,
                        triangulate=False,
                        preserveTopology=True,
                        constructionHistory=True,
                    )
                    reduce_ok = True
                else:
                    raise

            cmds.delete(dup, constructionHistory=True)

            new_fc = cmds.polyEvaluate(dup, face=True) or 0
            state["reduced_mesh"] = dup

            cmds.select(dup, replace=True)

            _update_status(
                f"Reduced: {new_name} ({new_fc:,} faces, {total_pct}% of original). "
                f"Now click Analyze."
            )
            print(f"WGLL Retopo: Created {new_name} — {new_fc:,} faces "
                  f"({total_pct}% of original)")

        except Exception as e:
            _update_status(f"polyReduce failed: {e}")
            import traceback
            traceback.print_exc()
        finally:
            cmds.undoInfo(closeChunk=True)

    def _on_retopo(*args):
        if not state["analyzed"]:
            cmds.warning("WGLL Retopo: Run Analyze first.")
            return

        mesh = state["mesh_name"]
        if not mesh or not cmds.objExists(mesh):
            cmds.warning("WGLL Retopo: Analyzed mesh no longer exists.")
            _set_analyzed(False)
            return

        target_fc = cmds.intSliderGrp(face_count_field, query=True, value=True)
        uniformity = cmds.floatSliderGrp(uniformity_slider, query=True, value=True)
        short = mesh.split('|')[-1].split(':')[-1]

        _update_status(f"Running polyRetopo on {short}...")

        cmds.undoInfo(openChunk=True, chunkName="WGLL_Retopo")
        try:
            # Duplicate the analyzed mesh
            dup = cmds.duplicate(mesh, name=f"{short}_wgll_retopo")[0]
            cmds.select(dup, replace=True)

            before_fc = cmds.polyEvaluate(dup, face=True)

            # Mark cached guide edges as hard on the duplicate
            if state["guides"] and state["guides"].combined_edges:
                _ensure_paths()
                _reload_modules()
                from maya_bridge.maya_mesh_adapter import mark_edges_as_hard
                mark_edges_as_hard(dup, state["guides"].combined_edges)
                print(f"WGLL Retopo: Marked {state['guides'].guide_edge_count} guide edges")

            # Run polyRetopo
            retopo_node = cmds.polyRetopo(
                dup,
                targetFaceCount=target_fc,
                faceUniformity=uniformity,
                preserveHardEdges=True,
                constructionHistory=True,
            )

            # Force Maya to evaluate the node before baking
            cmds.refresh()
            if retopo_node:
                node_name = retopo_node[0] if isinstance(retopo_node, list) else retopo_node
                cmds.dgeval(node_name)

            after_fc = cmds.polyEvaluate(dup, face=True)
            cmds.delete(dup, constructionHistory=True)
            cmds.select(dup, replace=True)

            print(f"WGLL Retopo: {before_fc:,} -> {after_fc:,} faces "
                  f"(target was {target_fc:,})")

            if after_fc == before_fc:
                _update_status(
                    f"Warning: face count unchanged ({after_fc:,}). "
                    f"Try 'Skip Analysis' or reduce further."
                )
            else:
                _update_status(
                    f"Retopo complete: {dup} ({after_fc:,} faces)"
                )

        except Exception as e:
            _update_status(f"Retopo failed: {e}")
            import traceback
            traceback.print_exc()
        finally:
            cmds.undoInfo(closeChunk=True)

    def _on_fallback(*args):
        """Run plain polyRetopo without WGLL analysis."""
        mesh, fc = _get_selected_mesh()
        if not mesh:
            cmds.warning("WGLL Retopo: Nothing selected.")
            return

        target = cmds.intSliderGrp(face_count_field, query=True, value=True)
        uniformity = cmds.floatSliderGrp(
            uniformity_slider, query=True, value=True)
        short = mesh.split('|')[-1].split(':')[-1]

        cmds.undoInfo(openChunk=True, chunkName="WGLL_PlainRetopo")
        try:
            dup = cmds.duplicate(mesh, name=f"{short}_plain_retopo")[0]
            cmds.select(dup, replace=True)
            cmds.polyRetopo(
                dup,
                targetFaceCount=target,
                faceUniformity=uniformity,
            )
            result = cmds.rename(dup, f"{short}_retopo")
            cmds.delete(result, constructionHistory=True)
            cmds.select(result, replace=True)
            _update_status(f"Plain retopo done: {result}")
            print(f"WGLL Retopo: Plain polyRetopo result: {result}")
        except Exception as e:
            cmds.warning(f"Plain retopo failed: {e}")
        finally:
            cmds.undoInfo(closeChunk=True)

    # Wire up callbacks
    cmds.button(analyze_btn, edit=True, command=_on_analyze)
    cmds.button(reduce_btn, edit=True, command=_on_reduce)
    cmds.button(retopo_btn, edit=True, command=_on_retopo)
    cmds.button(fallback_btn, edit=True, command=_on_fallback)

    cmds.showWindow(window)


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
        module_name = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        scripts_root = '/Users/arthurklein/Documents/Work/Side/VibeBash/MayaScripts'
        module_name = TOOL_NAME

    command = (
        f"import sys\n"
        f"for p in ['{scripts_root}', '{WGLL_ROOT}']:\n"
        f"    if p not in sys.path: sys.path.insert(0, p)\n"
        f"import importlib, {module_name}\n"
        f"importlib.reload({module_name})\n"
        f"{module_name}.run_with_ui()"
    )

    cmds.shelfButton(
        parent=SHELF_NAME,
        image=TOOL_ICON,
        command=command,
        annotation=TOOL_ANNOTATION,
        label=TOOL_LABEL,
        imageOverlayLabel=TOOL_LABEL,
        overlayLabelColor=(0.2, 0.9, 0.4),
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
