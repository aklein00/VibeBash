"""
mesh_io — Lightweight mesh I/O using trimesh.
Reads/writes OBJ files and provides the WGLLMesh dataclass used throughout the core.
No Maya dependency.
"""

import numpy as np
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

try:
    import trimesh
except ImportError:
    trimesh = None


@dataclass
class WGLLMesh:
    """Lightweight mesh representation for WGLL Retopo core."""
    vertices: np.ndarray           # (N, 3) float64
    faces: list                    # list of arrays/lists, each with 3+ vertex indices
    normals: Optional[np.ndarray] = None   # (N, 3) vertex normals
    uvs: Optional[np.ndarray] = None       # (N, 2)
    metadata: dict = field(default_factory=dict)

    @property
    def vertex_count(self) -> int:
        return len(self.vertices)

    @property
    def face_count(self) -> int:
        return len(self.faces)

    @property
    def tri_count(self) -> int:
        """Approximate triangle count (quads = 2 tris each)."""
        count = 0
        for f in self.faces:
            count += max(1, len(f) - 2)
        return count

    @property
    def quad_ratio(self) -> float:
        """Fraction of faces that are quads (4 vertices)."""
        if len(self.faces) == 0:
            return 0.0
        quad_count = sum(1 for f in self.faces if len(f) == 4)
        return quad_count / len(self.faces)

    def compute_normals(self):
        """Compute per-vertex normals from face geometry."""
        normals = np.zeros_like(self.vertices)
        for face in self.faces:
            if len(face) < 3:
                continue
            v0, v1, v2 = self.vertices[face[0]], self.vertices[face[1]], self.vertices[face[2]]
            face_normal = np.cross(v1 - v0, v2 - v0)
            norm = np.linalg.norm(face_normal)
            if norm > 1e-10:
                face_normal /= norm
            for vi in face:
                normals[vi] += face_normal
        lengths = np.linalg.norm(normals, axis=1, keepdims=True)
        lengths = np.maximum(lengths, 1e-10)
        self.normals = normals / lengths


def _require_trimesh():
    if trimesh is None:
        raise ImportError(
            "trimesh is required for mesh I/O. Install with: pip install trimesh"
        )


def load_obj(filepath: str) -> WGLLMesh:
    """Load an OBJ file and return a WGLLMesh."""
    _require_trimesh()
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"OBJ file not found: {filepath}")

    scene_or_mesh = trimesh.load(str(filepath), process=False, force='mesh')

    if isinstance(scene_or_mesh, trimesh.Scene):
        geometries = list(scene_or_mesh.geometry.values())
        if not geometries:
            raise ValueError(f"No geometry found in {filepath}")
        mesh = geometries[0]
    else:
        mesh = scene_or_mesh

    vertices = np.array(mesh.vertices, dtype=np.float64)
    faces = _extract_faces(mesh)
    normals = np.array(mesh.vertex_normals, dtype=np.float64) if mesh.vertex_normals is not None else None

    wgll = WGLLMesh(
        vertices=vertices,
        faces=faces,
        normals=normals,
        metadata={"source": str(filepath), "name": filepath.stem}
    )

    if wgll.normals is None or len(wgll.normals) == 0:
        wgll.compute_normals()

    return wgll


def _extract_faces(mesh) -> list:
    """Extract face arrays from a trimesh mesh as list of arrays."""
    # trimesh triangulates by default, so faces are always tris
    if hasattr(mesh, 'faces') and mesh.faces is not None:
        return [np.array(f, dtype=np.int32) for f in mesh.faces]
    return []


def save_obj(mesh: WGLLMesh, filepath: str):
    """Save a WGLLMesh to OBJ format."""
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, 'w') as f:
        f.write(f"# WGLL Retopo output\n")
        f.write(f"# Vertices: {mesh.vertex_count}, Faces: {mesh.face_count}\n\n")

        for v in mesh.vertices:
            f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")

        if mesh.normals is not None:
            f.write("\n")
            for n in mesh.normals:
                f.write(f"vn {n[0]:.6f} {n[1]:.6f} {n[2]:.6f}\n")

        f.write("\n")
        for face in mesh.faces:
            indices = " ".join(str(vi + 1) for vi in face)  # OBJ is 1-indexed
            f.write(f"f {indices}\n")


def load_obj_raw(filepath: str) -> WGLLMesh:
    """
    Load an OBJ file directly (no trimesh), preserving quads.
    Useful when trimesh triangulates quads.
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"OBJ file not found: {filepath}")

    vertices = []
    faces = []
    normals_raw = []

    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            if parts[0] == 'v' and len(parts) >= 4:
                vertices.append([float(parts[1]), float(parts[2]), float(parts[3])])
            elif parts[0] == 'vn' and len(parts) >= 4:
                normals_raw.append([float(parts[1]), float(parts[2]), float(parts[3])])
            elif parts[0] == 'f':
                face_verts = []
                for p in parts[1:]:
                    # Handle f v, f v/vt, f v/vt/vn, f v//vn
                    vi = int(p.split('/')[0]) - 1  # OBJ is 1-indexed
                    face_verts.append(vi)
                faces.append(face_verts)

    verts_array = np.array(vertices, dtype=np.float64)
    normals_array = np.array(normals_raw, dtype=np.float64) if normals_raw else None

    # Convert faces to numpy — variable length faces stored as list of arrays
    face_arrays = [np.array(f, dtype=np.int32) for f in faces]

    mesh = WGLLMesh(
        vertices=verts_array,
        faces=face_arrays,
        normals=normals_array,
        metadata={"source": str(filepath), "name": filepath.stem}
    )

    if mesh.normals is None or len(mesh.normals) == 0:
        mesh.compute_normals()

    return mesh
