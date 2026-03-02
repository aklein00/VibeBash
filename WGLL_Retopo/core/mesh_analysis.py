"""
mesh_analysis — Curvature computation, feature detection, and topology statistics.
Analyzes a high-resolution sculpt to identify where edge loops should be placed.
No Maya dependency.
"""

import numpy as np
from typing import Optional
from .mesh_io import WGLLMesh


def build_adjacency(mesh, progress_fn=None):
    """
    Build vertex adjacency map from face data.
    Returns dict mapping vertex_index -> set of neighbor vertex indices.
    """
    adj = {}
    total = len(mesh.faces)
    for fi, face in enumerate(mesh.faces):
        face_list = list(face) if isinstance(face, np.ndarray) else face
        n = len(face_list)
        for i in range(n):
            vi = face_list[i]
            vj = face_list[(i + 1) % n]
            adj.setdefault(vi, set()).add(vj)
            adj.setdefault(vj, set()).add(vi)
        if progress_fn and fi % 20000 == 0:
            progress_fn(fi / max(total, 1))
    return adj


def compute_vertex_curvature(mesh, adjacency=None, progress_fn=None):
    """
    Compute approximate mean curvature at each vertex using the discrete Laplacian.

    Method: For each vertex, compute the mean of (neighbor - vertex) vectors.
    The magnitude of this "Laplacian vector" approximates mean curvature.
    High values = high curvature (feature areas like eyes, nostrils, joints).
    Low values = flat areas (torso, forehead).

    Returns:
        np.ndarray of shape (N,) with curvature magnitude per vertex.
    """
    if adjacency is None:
        adjacency = build_adjacency(mesh)

    if mesh.normals is None:
        mesh.compute_normals()

    n_verts = mesh.vertex_count
    curvature = np.zeros(n_verts, dtype=np.float64)

    for vi in range(n_verts):
        neighbors = adjacency.get(vi, set())
        if not neighbors:
            continue
        neighbor_positions = mesh.vertices[list(neighbors)]
        laplacian = np.mean(neighbor_positions - mesh.vertices[vi], axis=0)
        curvature[vi] = np.linalg.norm(laplacian)
        if progress_fn and vi % 10000 == 0:
            progress_fn(vi / max(n_verts, 1))

    return curvature


def detect_feature_vertices(mesh, curvature, threshold_percentile=75.0):
    """
    Find vertices in high-curvature regions (likely feature areas).

    Returns:
        Boolean array of shape (N,) — True for feature vertices.
    """
    threshold = np.percentile(curvature, threshold_percentile)
    return curvature >= threshold


def find_feature_edges(mesh, curvature, threshold_percentile=75.0,
                       adjacency=None):
    """
    Find edges where both endpoints are high-curvature (feature edges).
    These edges should be preserved during retopology.

    Returns:
        List of (vi, vj) tuples representing feature edges.
    """
    if adjacency is None:
        adjacency = build_adjacency(mesh)

    feature_mask = detect_feature_vertices(mesh, curvature, threshold_percentile)
    feature_edges = []
    seen = set()

    for vi in range(mesh.vertex_count):
        if not feature_mask[vi]:
            continue
        for vj in adjacency.get(vi, set()):
            if not feature_mask[vj]:
                continue
            edge = (min(vi, vj), max(vi, vj))
            if edge not in seen:
                seen.add(edge)
                feature_edges.append(edge)

    return feature_edges


def compute_edge_angles(mesh, progress_fn=None):
    """
    Compute dihedral angle at each edge (angle between adjacent face normals).
    High angles indicate creases/sharp features.

    Returns:
        Dict mapping (vi, vj) -> angle in degrees.
    """
    if mesh.normals is None:
        mesh.compute_normals()

    # Build edge-to-faces map
    edge_faces = {}
    face_normals = []
    total_faces = len(mesh.faces)

    for fi, face in enumerate(mesh.faces):
        face_list = list(face) if isinstance(face, np.ndarray) else face
        if len(face_list) < 3:
            face_normals.append(np.zeros(3))
            continue
        v0, v1, v2 = mesh.vertices[face_list[0]], mesh.vertices[face_list[1]], mesh.vertices[face_list[2]]
        fn = np.cross(v1 - v0, v2 - v0)
        norm = np.linalg.norm(fn)
        if norm > 1e-10:
            fn /= norm
        face_normals.append(fn)

        n = len(face_list)
        for i in range(n):
            edge = (min(face_list[i], face_list[(i + 1) % n]),
                    max(face_list[i], face_list[(i + 1) % n]))
            edge_faces.setdefault(edge, []).append(fi)

        if progress_fn and fi % 20000 == 0:
            progress_fn(fi / max(total_faces, 1))

    face_normals = np.array(face_normals)
    edge_angles = {}

    for edge, fis in edge_faces.items():
        if len(fis) == 2:
            dot = np.clip(np.dot(face_normals[fis[0]], face_normals[fis[1]]), -1.0, 1.0)
            angle = np.degrees(np.arccos(dot))
            edge_angles[edge] = angle
        elif len(fis) == 1:
            edge_angles[edge] = 180.0  # Boundary edge

    return edge_angles


def find_crease_edges(mesh, crease_angle=30.0, progress_fn=None):
    """
    Find edges with dihedral angle above the crease threshold.

    Returns:
        List of (vi, vj) edge tuples.
    """
    edge_angles = compute_edge_angles(mesh, progress_fn=progress_fn)
    return [edge for edge, angle in edge_angles.items() if angle >= crease_angle]


def compute_topology_stats(mesh, adjacency=None):
    """
    Compute topology quality statistics for a mesh.
    Used by the WGLL reference system to profile "good" topology.
    """
    if adjacency is None:
        adjacency = build_adjacency(mesh)

    # Valence distribution
    valences = [len(adjacency.get(vi, set())) for vi in range(mesh.vertex_count)]
    valence_counts = {}
    for v in valences:
        valence_counts[v] = valence_counts.get(v, 0) + 1

    # Edge lengths
    edge_lengths = []
    seen = set()
    for vi in range(mesh.vertex_count):
        for vj in adjacency.get(vi, set()):
            edge = (min(vi, vj), max(vi, vj))
            if edge not in seen:
                seen.add(edge)
                length = np.linalg.norm(mesh.vertices[vi] - mesh.vertices[vj])
                edge_lengths.append(length)

    edge_lengths = np.array(edge_lengths) if edge_lengths else np.array([0.0])

    # Face type counts
    tri_count = 0
    quad_count = 0
    ngon_count = 0
    for face in mesh.faces:
        n = len(face) if isinstance(face, (list, np.ndarray)) else 0
        if n == 3:
            tri_count += 1
        elif n == 4:
            quad_count += 1
        elif n > 4:
            ngon_count += 1

    total_faces = tri_count + quad_count + ngon_count

    return {
        "vertex_count": mesh.vertex_count,
        "face_count": total_faces,
        "tri_count": tri_count,
        "quad_count": quad_count,
        "ngon_count": ngon_count,
        "quad_ratio": quad_count / max(total_faces, 1),
        "tri_percentage": tri_count / max(total_faces, 1) * 100,
        "valence_distribution": valence_counts,
        "avg_valence": np.mean(valences) if valences else 0,
        "avg_edge_length": float(np.mean(edge_lengths)),
        "edge_length_std": float(np.std(edge_lengths)),
        "edge_count": len(edge_lengths),
    }
