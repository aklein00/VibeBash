"""
guide_generation — Generate retopology guide data from mesh analysis.
Produces guide edges and density maps that drive better polyRetopo results.
No Maya dependency.
"""

import numpy as np
from typing import Optional
from .mesh_io import WGLLMesh
from .mesh_analysis import (
    build_adjacency,
    compute_vertex_curvature,
    find_feature_edges,
    find_crease_edges,
)


class RetopologyGuides:
    """Container for retopology guide data generated from mesh analysis."""

    def __init__(self):
        self.feature_edges: list = []     # (vi, vj) tuples from curvature
        self.crease_edges: list = []      # (vi, vj) tuples from dihedral angles
        self.combined_edges: list = []    # Union of feature + crease edges
        self.curvature: Optional[np.ndarray] = None
        self.density_weights: Optional[np.ndarray] = None  # Per-vertex density suggestion

    @property
    def guide_edge_count(self) -> int:
        return len(self.combined_edges)


def generate_guides(
    mesh,
    curvature_percentile=75.0,
    crease_angle=30.0,
    smooth_iterations=3,
    progress_fn=None,
):
    """
    Analyze a sculpt mesh and generate retopology guides.

    Args:
        mesh: High-resolution sculpt mesh (WGLLMesh).
        curvature_percentile: Threshold for feature detection (higher = fewer features).
        crease_angle: Minimum dihedral angle for crease detection.
        smooth_iterations: Laplacian smoothing passes on the curvature field.
        progress_fn: Optional callback(step_name, sub_progress_0_to_1) for progress reporting.

    Returns:
        RetopologyGuides with all computed guide data.
    """
    guides = RetopologyGuides()

    def _report(step, pct=0.0):
        if progress_fn:
            progress_fn(step, pct)

    # Step 1: Build adjacency
    _report("Building adjacency map...")
    adjacency = build_adjacency(
        mesh,
        progress_fn=lambda p: _report("Building adjacency map...", p),
    )

    # Step 2: Compute curvature
    _report("Computing vertex curvature...")
    curvature = compute_vertex_curvature(
        mesh, adjacency,
        progress_fn=lambda p: _report("Computing vertex curvature...", p),
    )

    # Step 3: Smooth curvature
    _report("Smoothing curvature field...")
    curvature = _smooth_vertex_field(
        curvature, adjacency, smooth_iterations,
        progress_fn=lambda p: _report("Smoothing curvature field...", p),
    )
    guides.curvature = curvature

    # Step 4: Find feature edges
    _report("Finding feature edges...")
    guides.feature_edges = find_feature_edges(
        mesh, curvature, curvature_percentile, adjacency
    )

    # Step 5: Find crease edges
    _report("Detecting crease edges...")
    guides.crease_edges = find_crease_edges(
        mesh, crease_angle,
        progress_fn=lambda p: _report("Detecting crease edges...", p),
    )

    # Combine edge sets
    _report("Combining guide edges...")
    combined = set()
    for e in guides.feature_edges:
        combined.add((min(e[0], e[1]), max(e[0], e[1])))
    for e in guides.crease_edges:
        combined.add((min(e[0], e[1]), max(e[0], e[1])))
    guides.combined_edges = list(combined)

    # Compute density weights from curvature
    guides.density_weights = _curvature_to_density(curvature)

    _report("Analysis complete.", 1.0)
    return guides


def _smooth_vertex_field(values, adjacency, iterations, progress_fn=None):
    """Laplacian smooth a per-vertex scalar field."""
    smoothed = values.copy()
    n_verts = len(values)
    for it in range(iterations):
        new_values = smoothed.copy()
        for vi in range(n_verts):
            neighbors = adjacency.get(vi, set())
            if not neighbors:
                continue
            neighbor_vals = smoothed[list(neighbors)]
            new_values[vi] = 0.5 * smoothed[vi] + 0.5 * np.mean(neighbor_vals)
        smoothed = new_values
        if progress_fn:
            progress_fn((it + 1) / iterations)
    return smoothed


def _curvature_to_density(curvature):
    """
    Convert curvature values to density weights.
    Higher curvature -> higher density (more polygons wanted here).
    Normalized to range [0.3, 1.0] so flat areas still get some density.
    """
    if len(curvature) == 0:
        return np.array([])

    c_min = np.min(curvature)
    c_max = np.max(curvature)
    c_range = c_max - c_min

    if c_range < 1e-10:
        return np.full_like(curvature, 0.65)

    normalized = (curvature - c_min) / c_range
    return 0.3 + 0.7 * normalized


def guides_to_vertex_indices(guides):
    """Get the set of all vertex indices involved in guide edges."""
    indices = set()
    for vi, vj in guides.combined_edges:
        indices.add(vi)
        indices.add(vj)
    return indices


def format_guide_summary(guides):
    """Human-readable summary of generated guides."""
    lines = [
        "WGLL Retopo Guide Summary",
        "=" * 40,
        f"Feature edges (curvature): {len(guides.feature_edges)}",
        f"Crease edges (dihedral):   {len(guides.crease_edges)}",
        f"Combined guide edges:      {len(guides.combined_edges)}",
    ]
    if guides.curvature is not None:
        lines.extend([
            f"Curvature range: {np.min(guides.curvature):.4f} - {np.max(guides.curvature):.4f}",
            f"Mean curvature:  {np.mean(guides.curvature):.4f}",
        ])
    if guides.density_weights is not None:
        lines.extend([
            f"Density range:   {np.min(guides.density_weights):.2f} - {np.max(guides.density_weights):.2f}",
        ])
    return "\n".join(lines)
