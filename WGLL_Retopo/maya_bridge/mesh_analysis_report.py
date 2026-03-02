"""
mesh_analysis_report — Analyze mesh topology quality and high/low-res relationships.
Produces a detailed text report for review.
"""

import maya.cmds as cmds
import maya.api.OpenMaya as om2
import numpy as np
import os
import sys
from datetime import datetime

_WGLL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _WGLL_ROOT not in sys.path:
    sys.path.insert(0, _WGLL_ROOT)
import site
_USER_SITE = site.getusersitepackages()
if _USER_SITE not in sys.path:
    sys.path.insert(0, _USER_SITE)

ANALYSIS_DIR = os.path.join(_WGLL_ROOT, 'analysis')


def _get_dag_path(maya_obj):
    """Resolve Maya object to mesh dag path."""
    if cmds.objectType(maya_obj) == 'transform':
        shapes = cmds.listRelatives(maya_obj, shapes=True, type='mesh', fullPath=True)
        if not shapes:
            raise ValueError(f"'{maya_obj}' has no mesh shape.")
        shape = shapes[0]
    elif cmds.objectType(maya_obj) == 'mesh':
        shape = cmds.ls(maya_obj, long=True)[0]
    else:
        raise ValueError(f"'{maya_obj}' is not a mesh or transform.")
    sel = om2.MSelectionList()
    sel.add(shape)
    dag = sel.getDagPath(0)
    if dag.apiType() == om2.MFn.kTransform:
        dag.extendToShape()
    return dag


def _extract_mesh_data(maya_obj):
    """Extract vertices, faces, normals from Maya mesh using OpenMaya 2.0."""
    dag = _get_dag_path(maya_obj)
    fn = om2.MFnMesh(dag)

    # Vertices
    pts = fn.getPoints(om2.MSpace.kWorld)
    verts = np.array([[p.x, p.y, p.z] for p in pts], dtype=np.float64)

    # Faces
    counts, connects = fn.getVertices()
    faces = []
    idx = 0
    for c in counts:
        faces.append([connects[idx + i] for i in range(c)])
        idx += c

    # Normals
    try:
        norms = fn.getVertexNormals(False, om2.MSpace.kWorld)
        normals = np.array([[n.x, n.y, n.z] for n in norms], dtype=np.float64)
    except Exception:
        normals = None

    return verts, faces, normals, fn, dag


def _compute_face_areas(verts, faces):
    """Compute area of each face via cross product."""
    areas = []
    for face in faces:
        if len(face) < 3:
            areas.append(0.0)
            continue
        # Triangulate fan from first vertex
        area = 0.0
        v0 = verts[face[0]]
        for i in range(1, len(face) - 1):
            v1 = verts[face[i]]
            v2 = verts[face[i + 1]]
            area += 0.5 * np.linalg.norm(np.cross(v1 - v0, v2 - v0))
        areas.append(area)
    return np.array(areas)


def _compute_edge_lengths(verts, faces):
    """Compute length of each unique edge."""
    edges = set()
    lengths = []
    for face in faces:
        n = len(face)
        for i in range(n):
            e = (min(face[i], face[(i+1) % n]), max(face[i], face[(i+1) % n]))
            if e not in edges:
                edges.add(e)
                lengths.append(np.linalg.norm(verts[e[0]] - verts[e[1]]))
    return np.array(lengths), len(edges)


def _compute_valence(verts, faces):
    """Compute valence (edge count) per vertex."""
    adj = {}
    for face in faces:
        n = len(face)
        for i in range(n):
            vi, vj = face[i], face[(i+1) % n]
            adj.setdefault(vi, set()).add(vj)
            adj.setdefault(vj, set()).add(vi)
    valences = np.array([len(adj.get(i, set())) for i in range(len(verts))])
    return valences, adj


def _face_type_breakdown(faces):
    """Count tris, quads, ngons."""
    tris = quads = ngons = 0
    for f in faces:
        n = len(f)
        if n == 3: tris += 1
        elif n == 4: quads += 1
        elif n > 4: ngons += 1
    return tris, quads, ngons


def _bounding_box(verts):
    """Compute axis-aligned bounding box."""
    mn = verts.min(axis=0)
    mx = verts.max(axis=0)
    return mn, mx


def _uniformity_score(values):
    """Score 0-1 where 1 = perfectly uniform. Based on coefficient of variation."""
    if len(values) == 0:
        return 0.0
    mean = np.mean(values)
    if mean < 1e-10:
        return 0.0
    cv = np.std(values) / mean  # coefficient of variation
    return max(0.0, 1.0 - cv)


def _surface_deviation(low_verts, high_fn):
    """Compute distance from each low-res vert to closest point on high-res surface."""
    deviations = []
    for v in low_verts:
        pt = om2.MPoint(v[0], v[1], v[2])
        closest, _ = high_fn.getClosestPoint(pt, om2.MSpace.kWorld)
        dist = pt.distanceTo(closest)
        deviations.append(dist)
    return np.array(deviations)


def _nearest_neighbor_distances(verts):
    """Compute distance to nearest neighbor for each vertex (pure numpy, no scipy)."""
    n = len(verts)
    if n < 2:
        return np.array([0.0])
    # For low-res meshes this brute-force approach is fine
    # Compute pairwise distance matrix
    diffs = verts[:, np.newaxis, :] - verts[np.newaxis, :, :]  # (N, N, 3)
    dists = np.linalg.norm(diffs, axis=2)  # (N, N)
    np.fill_diagonal(dists, np.inf)  # exclude self-distance
    return np.min(dists, axis=1)


def analyze_meshes(high_res_obj, low_res_obj, progress_fn=None):
    """
    Run full analysis on a high-res / low-res mesh pair.
    Returns a formatted text report string.
    """
    def _prog(msg, pct):
        if progress_fn:
            progress_fn(msg, pct)

    _prog("Extracting high-res mesh data...", 0)
    hi_verts, hi_faces, hi_normals, hi_fn, hi_dag = _extract_mesh_data(high_res_obj)

    _prog("Extracting low-res mesh data...", 10)
    lo_verts, lo_faces, lo_normals, lo_fn, lo_dag = _extract_mesh_data(low_res_obj)

    hi_name = high_res_obj.split('|')[-1].split(':')[-1]
    lo_name = low_res_obj.split('|')[-1].split(':')[-1]
    hi_fc = len(hi_faces)
    lo_fc = len(lo_faces)

    # Validation
    if hi_fc <= lo_fc:
        return (f"ERROR: High-res ({hi_name}: {hi_fc} faces) has fewer/equal faces "
                f"than low-res ({lo_name}: {lo_fc} faces). Swap them.")

    lines = []
    lines.append("WGLL Mesh Analysis Report")
    lines.append("=" * 60)
    lines.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"High-Res: {hi_name} ({hi_fc:,} faces)")
    lines.append(f"Low-Res:  {lo_name} ({lo_fc:,} faces)")
    lines.append(f"Reduction ratio: {lo_fc/hi_fc*100:.2f}%")
    lines.append("")

    # === LOW-RES TOPOLOGY ===
    _prog("Analyzing low-res topology...", 20)
    lines.append("=" * 60)
    lines.append("LOW-RES TOPOLOGY")
    lines.append("=" * 60)

    lo_tris, lo_quads, lo_ngons = _face_type_breakdown(lo_faces)
    lines.append(f"Vertices: {len(lo_verts):,}")
    lines.append(f"Faces: {lo_fc:,} ({lo_quads:,} quads, {lo_tris:,} tris, {lo_ngons:,} ngons)")
    lines.append(f"Quad ratio: {lo_quads/max(lo_fc,1)*100:.1f}%")

    # Face areas
    _prog("Computing face areas...", 30)
    lo_areas = _compute_face_areas(lo_verts, lo_faces)
    area_score = _uniformity_score(lo_areas)
    lines.append("")
    lines.append("Face Area:")
    lines.append(f"  Mean: {np.mean(lo_areas):.6f} units^2")
    lines.append(f"  Std Dev: {np.std(lo_areas):.6f}")
    lines.append(f"  Min: {np.min(lo_areas):.6f}  Max: {np.max(lo_areas):.6f}")
    lines.append(f"  Min/Max ratio: {np.min(lo_areas)/max(np.max(lo_areas),1e-10):.3f}")
    lines.append(f"  Uniformity Score: {area_score:.3f} (1.0 = perfectly uniform)")

    # Edge lengths
    _prog("Computing edge lengths...", 40)
    lo_edges, lo_edge_count = _compute_edge_lengths(lo_verts, lo_faces)
    edge_score = _uniformity_score(lo_edges)
    lines.append("")
    lines.append(f"Edges: {lo_edge_count:,}")
    lines.append("Edge Length:")
    lines.append(f"  Mean: {np.mean(lo_edges):.6f} units")
    lines.append(f"  Std Dev: {np.std(lo_edges):.6f}")
    lines.append(f"  Min: {np.min(lo_edges):.6f}  Max: {np.max(lo_edges):.6f}")
    lines.append(f"  Min/Max ratio: {np.min(lo_edges)/max(np.max(lo_edges),1e-10):.3f}")
    lines.append(f"  Uniformity Score: {edge_score:.3f}")

    # Valence
    _prog("Computing vertex valence...", 50)
    lo_valences, lo_adj = _compute_valence(lo_verts, lo_faces)
    lines.append("")
    lines.append("Valence Distribution:")
    for val in sorted(set(lo_valences)):
        count = int(np.sum(lo_valences == val))
        pct = count / len(lo_valences) * 100
        label = ""
        if val < 4:
            label = " -- pole (under)"
        elif val == 4:
            label = " -- ideal"
        elif val > 4:
            label = " -- pole (over)"
        lines.append(f"  {val}-valence: {count:,} verts ({pct:.1f}%){label}")

    ideal_pct = int(np.sum(lo_valences == 4)) / max(len(lo_valences), 1)
    lines.append(f"  Regularity Score: {ideal_pct:.3f} (fraction with ideal valence 4)")

    # Pole locations
    pole_indices = np.where(lo_valences != 4)[0]
    if len(pole_indices) > 0 and len(pole_indices) <= 50:
        lines.append("")
        lines.append(f"Pole Locations ({len(pole_indices)} poles):")
        for pi in pole_indices:
            v = lo_verts[pi]
            lines.append(f"  vtx[{pi}] valence={lo_valences[pi]} at ({v[0]:.3f}, {v[1]:.3f}, {v[2]:.3f})")
    elif len(pole_indices) > 50:
        lines.append(f"\n  {len(pole_indices)} poles total (too many to list individually)")

    # Vertex spacing
    _prog("Computing vertex spacing...", 60)
    nn_dists = _nearest_neighbor_distances(lo_verts)
    spacing_score = _uniformity_score(nn_dists)
    lines.append("")
    lines.append("Vertex Spacing (nearest-neighbor):")
    lines.append(f"  Mean: {np.mean(nn_dists):.6f} units")
    lines.append(f"  Std Dev: {np.std(nn_dists):.6f}")
    lines.append(f"  Min: {np.min(nn_dists):.6f}  Max: {np.max(nn_dists):.6f}")
    lines.append(f"  Uniformity Score: {spacing_score:.3f}")

    # === HIGH-RES STATS ===
    lines.append("")
    lines.append("=" * 60)
    lines.append("HIGH-RES STATS")
    lines.append("=" * 60)
    hi_tris, hi_quads, hi_ngons = _face_type_breakdown(hi_faces)
    lines.append(f"Vertices: {len(hi_verts):,}")
    lines.append(f"Faces: {hi_fc:,} ({hi_quads:,} quads, {hi_tris:,} tris, {hi_ngons:,} ngons)")

    # === RELATIONSHIP ===
    _prog("Computing surface deviation...", 70)
    lines.append("")
    lines.append("=" * 60)
    lines.append("HIGH-RES / LOW-RES RELATIONSHIP")
    lines.append("=" * 60)

    # Surface deviation
    deviations = _surface_deviation(lo_verts, hi_fn)
    lines.append("")
    lines.append("Surface Deviation (low-res verts to high-res surface):")
    lines.append(f"  Mean: {np.mean(deviations):.6f} units")
    lines.append(f"  Max: {np.max(deviations):.6f} units")
    lines.append(f"  Median: {np.median(deviations):.6f} units")
    lines.append(f"  95th percentile: {np.percentile(deviations, 95):.6f} units")
    lines.append(f"  99th percentile: {np.percentile(deviations, 99):.6f} units")

    # Bounding boxes
    _prog("Computing bounding boxes...", 85)
    hi_mn, hi_mx = _bounding_box(hi_verts)
    lo_mn, lo_mx = _bounding_box(lo_verts)
    hi_size = hi_mx - hi_mn
    lo_size = lo_mx - lo_mn

    lines.append("")
    lines.append("Bounding Box (world space):")
    lines.append(f"  High-res: ({hi_mn[0]:.3f}, {hi_mn[1]:.3f}, {hi_mn[2]:.3f}) to "
                 f"({hi_mx[0]:.3f}, {hi_mx[1]:.3f}, {hi_mx[2]:.3f})")
    lines.append(f"  Low-res:  ({lo_mn[0]:.3f}, {lo_mn[1]:.3f}, {lo_mn[2]:.3f}) to "
                 f"({lo_mx[0]:.3f}, {lo_mx[1]:.3f}, {lo_mx[2]:.3f})")
    lines.append(f"  High-res size: {hi_size[0]:.3f} x {hi_size[1]:.3f} x {hi_size[2]:.3f}")
    lines.append(f"  Low-res size:  {lo_size[0]:.3f} x {lo_size[1]:.3f} x {lo_size[2]:.3f}")

    # Transform info
    lines.append("")
    lines.append("Transforms (world space):")
    for name, obj in [("High-res", high_res_obj), ("Low-res", low_res_obj)]:
        pos = cmds.xform(obj, query=True, worldSpace=True, translation=True)
        rot = cmds.xform(obj, query=True, worldSpace=True, rotation=True)
        scl = cmds.xform(obj, query=True, worldSpace=True, scale=True)
        lines.append(f"  {name}: pos=({pos[0]:.3f}, {pos[1]:.3f}, {pos[2]:.3f}) "
                     f"rot=({rot[0]:.1f}, {rot[1]:.1f}, {rot[2]:.1f}) "
                     f"scale=({scl[0]:.3f}, {scl[1]:.3f}, {scl[2]:.3f})")

    # Normal deviation
    _prog("Computing normal deviation...", 90)
    if lo_normals is not None and hi_normals is not None:
        # For each low-res vert, find closest point on high-res and compare normals
        normal_dots = []
        for i, v in enumerate(lo_verts):
            pt = om2.MPoint(v[0], v[1], v[2])
            closest, face_id = hi_fn.getClosestPoint(pt, om2.MSpace.kWorld)
            hi_normal = hi_fn.getClosestNormal(pt, om2.MSpace.kWorld)[0]
            hi_n = np.array([hi_normal.x, hi_normal.y, hi_normal.z])
            lo_n = lo_normals[i]
            dot = np.clip(np.dot(lo_n, hi_n), -1.0, 1.0)
            normal_dots.append(dot)
        normal_dots = np.array(normal_dots)
        angle_devs = np.degrees(np.arccos(normal_dots))

        lines.append("")
        lines.append("Normal Deviation (angle between low-res and high-res normals):")
        lines.append(f"  Mean: {np.mean(angle_devs):.2f} degrees")
        lines.append(f"  Max: {np.max(angle_devs):.2f} degrees")
        lines.append(f"  Median: {np.median(angle_devs):.2f} degrees")

    # === SUMMARY SCORES ===
    _prog("Generating summary...", 95)
    lines.append("")
    lines.append("=" * 60)
    lines.append("SUMMARY SCORES")
    lines.append("=" * 60)

    def _grade(score):
        if score >= 0.90: return "A"
        elif score >= 0.80: return "B"
        elif score >= 0.65: return "C"
        elif score >= 0.50: return "D"
        else: return "F"

    lines.append(f"  Face Area Uniformity:    {area_score:.3f} ({_grade(area_score)})")
    lines.append(f"  Edge Length Uniformity:   {edge_score:.3f} ({_grade(edge_score)})")
    lines.append(f"  Vertex Spacing Uniformity:{spacing_score:.3f} ({_grade(spacing_score)})")
    lines.append(f"  Valence Regularity:      {ideal_pct:.3f} ({_grade(ideal_pct)})")

    # Surface fit
    total_surface = np.sum(_compute_face_areas(hi_verts, hi_faces))
    mean_dev_ratio = np.mean(deviations) / max(np.max(hi_size), 1e-10)
    fit_score = max(0.0, 1.0 - mean_dev_ratio * 100)
    lines.append(f"  Surface Fit:             {fit_score:.3f} ({_grade(fit_score)})")

    lines.append("")
    lines.append("=" * 60)
    lines.append("END OF REPORT")
    lines.append("=" * 60)

    _prog("Done!", 100)
    return "\n".join(lines)


def save_report(report_text, prefix="analysis"):
    """Save report to WGLL_Retopo/analysis/ with timestamp."""
    os.makedirs(ANALYSIS_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.txt"
    filepath = os.path.join(ANALYSIS_DIR, filename)
    with open(filepath, 'w') as f:
        f.write(report_text)
    return filepath
