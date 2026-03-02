"""
maya_polyretopo_tuned — Guided polyRetopo wrapper with WGLL-tuned defaults.
Analyzes a sculpt mesh, marks feature edges as hard, then runs polyRetopo
with preserveHardEdges=True for dramatically better edge flow.
"""

import maya.cmds as cmds
import sys
import os

_WGLL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _WGLL_ROOT not in sys.path:
    sys.path.insert(0, _WGLL_ROOT)
import site
_USER_SITE = site.getusersitepackages()
if _USER_SITE not in sys.path:
    sys.path.insert(0, _USER_SITE)

from maya_bridge.maya_mesh_adapter import (
    maya_to_wgll_mesh,
    mark_edges_as_hard,
)
from core.guide_generation import generate_guides, format_guide_summary
from core.mesh_analysis import compute_topology_stats


def _safe_short_name(maya_obj):
    """Strip DAG path and namespace to get a safe name for suffixing."""
    short = maya_obj.split('|')[-1]
    short = short.split(':')[-1]
    return short


# -- Progress window helpers --
# The analysis has 5 internal steps mapped to 0-60% of the overall bar.
# Steps 2-5 (duplicate, mark edges, polyRetopo, report) are 60-100%.

_ANALYSIS_STEPS = {
    "Building adjacency map...":       (0, 10),
    "Computing vertex curvature...":   (10, 25),
    "Smoothing curvature field...":    (25, 35),
    "Finding feature edges...":        (35, 40),
    "Detecting crease edges...":       (40, 55),
    "Combining guide edges...":        (55, 58),
    "Analysis complete.":              (58, 60),
}


def _make_progress_callback():
    """
    Create a progress callback for generate_guides that drives
    Maya's progressWindow. Returns the callback function.
    """
    def progress_fn(step_name, sub_pct=0.0):
        if cmds.progressWindow(query=True, isCancelled=True):
            return
        if step_name in _ANALYSIS_STEPS:
            lo, hi = _ANALYSIS_STEPS[step_name]
            overall = lo + (hi - lo) * min(sub_pct, 1.0)
        else:
            overall = 60
        cmds.progressWindow(
            edit=True,
            progress=int(overall),
            status=f"[1/5] {step_name}",
        )
    return progress_fn


def _progress_update(step_num, total_steps, message, pct):
    """Update the progress window for major pipeline steps."""
    if cmds.progressWindow(query=True, isCancelled=True):
        return
    cmds.progressWindow(
        edit=True,
        progress=int(pct),
        status=f"[{step_num}/{total_steps}] {message}",
    )


def guided_retopo(
    target_mesh=None,
    target_face_count=5000,
    curvature_percentile=75.0,
    crease_angle=30.0,
    face_uniformity=0.3,
    smooth_iterations=3,
    verbose=True,
):
    """
    Run curvature-guided polyRetopo on a Maya mesh.

    Workflow:
    1. Analyze the sculpt mesh for curvature and crease features
    2. Duplicate the mesh
    3. Mark detected feature edges as hard edges on the duplicate
    4. Run polyRetopo with preserveHardEdges=True
    5. Report topology quality stats
    """
    # Resolve target
    if target_mesh is None:
        sel = cmds.ls(selection=True, long=True)
        if not sel:
            cmds.warning("WGLL Retopo: Nothing selected. Select a mesh first.")
            return None
        target_mesh = sel[0]

    # Validate it's a mesh
    shapes = cmds.listRelatives(target_mesh, shapes=True, type='mesh')
    if not shapes:
        cmds.warning(f"WGLL Retopo: '{target_mesh}' is not a polygon mesh.")
        return None

    # Guard against empty meshes
    face_count = cmds.polyEvaluate(target_mesh, face=True)
    if not face_count or face_count == 0:
        cmds.warning("WGLL Retopo: Mesh has no faces.")
        return None

    original_selection = cmds.ls(selection=True, long=True)
    short_name = _safe_short_name(target_mesh)

    # Open progress window
    cmds.progressWindow(
        title="WGLL Retopo",
        progress=0,
        status="Starting...",
        isInterruptable=True,
        minValue=0,
        maxValue=100,
    )

    cmds.undoInfo(openChunk=True, chunkName="WGLL_GuidedRetopo")
    try:
        if verbose:
            print("\n" + "=" * 60)
            print("WGLL Retopo — Guided polyRetopo")
            print("=" * 60)

        # --- Step 1: Convert to WGLLMesh and analyze (0-60%) ---
        _progress_update(1, 5, f"Extracting mesh data ({face_count} faces)...", 0)

        if verbose:
            print(f"\n[1/5] Analyzing mesh ({short_name}, {face_count} faces)...")

        wgll_mesh = maya_to_wgll_mesh(target_mesh)

        if verbose:
            print(f"  Converted: {wgll_mesh.vertex_count} verts, {wgll_mesh.face_count} faces")

        # Generate guides with live progress
        analysis_progress = _make_progress_callback()
        guides = generate_guides(
            wgll_mesh,
            curvature_percentile=curvature_percentile,
            crease_angle=crease_angle,
            smooth_iterations=smooth_iterations,
            progress_fn=analysis_progress,
        )

        if verbose:
            print(f"\n{format_guide_summary(guides)}")

        # Check if user cancelled
        if cmds.progressWindow(query=True, isCancelled=True):
            cmds.warning("WGLL Retopo: Cancelled by user.")
            return None

        # --- Step 2: Duplicate (60-65%) ---
        _progress_update(2, 5, "Duplicating mesh...", 60)

        if verbose:
            print(f"\n[2/5] Duplicating mesh...")

        dup = cmds.duplicate(target_mesh, name=f"{short_name}_wgll_guides")[0]

        # --- Step 3: Mark hard edges (65-75%) ---
        _progress_update(3, 5, f"Marking {guides.guide_edge_count} guide edges as hard...", 65)

        if verbose:
            print(f"\n[3/5] Marking {guides.guide_edge_count} guide edges as hard...")

        if guides.combined_edges:
            mark_edges_as_hard(dup, guides.combined_edges)
        else:
            if verbose:
                print("  No guide edges found (mesh may be very smooth).")

        # --- Step 4: polyRetopo (75-95%) ---
        _progress_update(4, 5, f"Running polyRetopo (target: {target_face_count} faces)...", 75)

        if verbose:
            print(f"\n[4/5] Running polyRetopo (target: {target_face_count} faces)...")

        cmds.select(dup, replace=True)

        before_fc = cmds.polyEvaluate(dup, face=True)

        retopo_node = cmds.polyRetopo(
            dup,
            targetFaceCount=target_face_count,
            faceUniformity=face_uniformity,
            preserveHardEdges=True,
            constructionHistory=True,
        )

        # Force Maya to evaluate the polyRetopo node before baking
        # Without this, delete(ch=True) removes the unevaluated node
        cmds.refresh()
        if retopo_node:
            node_name = retopo_node[0] if isinstance(retopo_node, list) else retopo_node
            cmds.dgeval(node_name)

        after_fc = cmds.polyEvaluate(dup, face=True)
        if verbose:
            print(f"  polyRetopo: {before_fc} -> {after_fc} faces")

        if after_fc == before_fc:
            cmds.warning(
                f"WGLL Retopo: polyRetopo did not change face count "
                f"({before_fc} -> {after_fc}). The mesh may need preprocessing."
            )

        result_name = f"{short_name}_wgll_retopo"
        result_mesh = cmds.rename(dup, result_name)
        cmds.delete(result_mesh, constructionHistory=True)

        # --- Step 5: Report (95-100%) ---
        _progress_update(5, 5, "Analyzing result...", 95)

        if verbose:
            print(f"\n[5/5] Analyzing result topology...")

            result_wgll = maya_to_wgll_mesh(result_mesh)
            stats = compute_topology_stats(result_wgll)

            print(f"\n  Result: {result_name}")
            print(f"  Vertices: {stats['vertex_count']}")
            print(f"  Faces: {stats['face_count']} (target was {target_face_count})")
            print(f"  Quad ratio: {stats['quad_ratio']:.1%}")
            print(f"  Tri %: {stats['tri_percentage']:.1f}%")
            print(f"  Avg valence: {stats['avg_valence']:.2f} (ideal: 4.0)")
            print(f"  Valence distribution: {stats['valence_distribution']}")
            print(f"\n{'=' * 60}")
            print(f"Done! Result mesh: {result_name}")
            print(f"{'=' * 60}\n")

        _progress_update(5, 5, "Done!", 100)
        cmds.select(result_mesh, replace=True)

        return result_mesh

    except Exception as e:
        cmds.warning(f"WGLL Retopo failed: {e}")
        import traceback
        traceback.print_exc()
        if original_selection:
            try:
                cmds.select(original_selection, replace=True)
            except Exception:
                pass
        return None

    finally:
        cmds.undoInfo(closeChunk=True)
        cmds.progressWindow(endProgress=True)


def quick_retopo(target_face_count=5000):
    """One-click guided retopo with sensible defaults."""
    return guided_retopo(target_face_count=target_face_count)


def retopo_hero(target_mesh=None):
    """Guided retopo tuned for mobile hero characters (8K-15K tris)."""
    return guided_retopo(
        target_mesh=target_mesh,
        target_face_count=6000,
        curvature_percentile=70.0,
        crease_angle=25.0,
        face_uniformity=0.3,
    )


def retopo_background(target_mesh=None):
    """Guided retopo tuned for mobile background NPCs (3K-5K tris)."""
    return guided_retopo(
        target_mesh=target_mesh,
        target_face_count=2000,
        curvature_percentile=80.0,
        crease_angle=35.0,
        face_uniformity=0.5,
    )


def retopo_prop(target_mesh=None):
    """Guided retopo tuned for mobile props (500-2K tris)."""
    return guided_retopo(
        target_mesh=target_mesh,
        target_face_count=500,
        curvature_percentile=85.0,
        crease_angle=40.0,
        face_uniformity=0.7,
    )
