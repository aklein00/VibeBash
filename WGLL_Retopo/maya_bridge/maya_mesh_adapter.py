"""
maya_mesh_adapter — Convert between Maya mesh objects and WGLL core WGLLMesh.
Requires Maya 2025+ Python environment.
"""

import maya.cmds as cmds
import maya.api.OpenMaya as om2
import numpy as np
import sys
import os

# Add core and user site-packages to path
_WGLL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _WGLL_ROOT not in sys.path:
    sys.path.insert(0, _WGLL_ROOT)
import site
_USER_SITE = site.getusersitepackages()
if _USER_SITE not in sys.path:
    sys.path.insert(0, _USER_SITE)

from core.mesh_io import WGLLMesh


def _get_mesh_dag_path(maya_obj):
    """
    Resolve a Maya object name to a dag path pointing at the mesh shape.
    Handles transforms, shape nodes, full DAG paths, and namespaces.
    """
    # If it's a transform, get its mesh shape
    if cmds.objectType(maya_obj) == 'transform':
        shapes = cmds.listRelatives(maya_obj, shapes=True, type='mesh', fullPath=True)
        if not shapes:
            raise ValueError(f"'{maya_obj}' has no mesh shape node.")
        shape = shapes[0]
    elif cmds.objectType(maya_obj) == 'mesh':
        shape = cmds.ls(maya_obj, long=True)[0]
    else:
        raise ValueError(f"'{maya_obj}' is not a mesh or transform.")

    sel = om2.MSelectionList()
    sel.add(shape)
    dag_path = sel.getDagPath(0)
    # Ensure we're pointing at the shape, not the transform
    if dag_path.apiType() == om2.MFn.kTransform:
        dag_path.extendToShape()
    return dag_path


def maya_to_wgll_mesh(maya_obj):
    """
    Extract mesh data from a Maya object into a WGLLMesh.

    Args:
        maya_obj: Maya object name (transform or mesh shape).

    Returns:
        WGLLMesh with vertices, faces, and normals.
    """
    dag_path = _get_mesh_dag_path(maya_obj)
    mesh_fn = om2.MFnMesh(dag_path)

    # Vertices
    points = mesh_fn.getPoints(om2.MSpace.kWorld)
    vertices = np.array([[p.x, p.y, p.z] for p in points], dtype=np.float64)

    # Faces (preserves quads — not triangulated)
    face_counts, face_connects = mesh_fn.getVertices()
    faces = []
    idx = 0
    for count in face_counts:
        face = [face_connects[idx + i] for i in range(count)]
        faces.append(np.array(face, dtype=np.int32))
        idx += count

    # Normals
    try:
        normals_raw = mesh_fn.getVertexNormals(False, om2.MSpace.kWorld)
        normals = np.array([[n.x, n.y, n.z] for n in normals_raw], dtype=np.float64)
    except Exception:
        normals = None

    short_name = maya_obj.split('|')[-1].split(':')[-1]
    wgll = WGLLMesh(
        vertices=vertices,
        faces=faces,
        normals=normals,
        metadata={
            "maya_object": maya_obj,
            "name": short_name,
        }
    )

    if wgll.normals is None:
        wgll.compute_normals()

    return wgll


def wgll_mesh_to_maya(mesh, name="wgll_retopo_result"):
    """
    Create a new Maya mesh from WGLLMesh data.

    Args:
        mesh: WGLLMesh to convert.
        name: Name for the new Maya object.

    Returns:
        Maya transform node name.
    """
    points = om2.MPointArray([om2.MPoint(v[0], v[1], v[2]) for v in mesh.vertices])

    face_counts = []
    face_connects = []
    for face in mesh.faces:
        face_list = list(face) if isinstance(face, np.ndarray) else face
        face_counts.append(len(face_list))
        face_connects.extend(int(v) for v in face_list)

    mesh_fn = om2.MFnMesh()
    new_obj = mesh_fn.create(
        points,
        face_counts,
        face_connects,
    )

    # Get the transform parent and rename
    dag_node = om2.MFnDagNode(new_obj)
    transform_path = dag_node.parent(0)
    transform_name = om2.MFnDagNode(transform_path).name()
    result = cmds.rename(transform_name, name)

    return result


def get_edge_vertex_pairs(maya_obj):
    """
    Get all edges as (vi, vj) vertex index pairs for a Maya mesh.

    Returns:
        List of (vi, vj) tuples.
    """
    dag_path = _get_mesh_dag_path(maya_obj)

    edge_pairs = []
    edge_iter = om2.MItMeshEdge(dag_path)
    while not edge_iter.isDone():
        vi = edge_iter.vertexId(0)
        vj = edge_iter.vertexId(1)
        edge_pairs.append((vi, vj))
        edge_iter.next()

    return edge_pairs


def mark_edges_as_hard(maya_obj, edge_vertex_pairs):
    """
    Mark specific edges as hard edges on a Maya mesh.
    Used to guide polyRetopo's preserveHardEdges feature.

    Args:
        maya_obj: Maya mesh object name.
        edge_vertex_pairs: List of (vi, vj) tuples identifying edges to harden.
    """
    # Build a lookup of vertex pairs to edge indices
    all_edges = get_edge_vertex_pairs(maya_obj)
    edge_index_map = {}
    for idx, (vi, vj) in enumerate(all_edges):
        edge_index_map[(min(vi, vj), max(vi, vj))] = idx

    # Find matching edge indices
    edge_indices = []
    for vi, vj in edge_vertex_pairs:
        key = (min(vi, vj), max(vi, vj))
        if key in edge_index_map:
            edge_indices.append(edge_index_map[key])

    if not edge_indices:
        cmds.warning("WGLL Retopo: No matching edges found to mark as hard.")
        return

    # Resolve the short name for edge component syntax
    short_name = cmds.ls(maya_obj, shortNames=True)[0]
    edge_components = [f"{short_name}.e[{idx}]" for idx in edge_indices]

    # Process in batches to avoid command line length limits
    batch_size = 500
    for i in range(0, len(edge_components), batch_size):
        batch = edge_components[i:i + batch_size]
        cmds.select(batch, replace=True)
        cmds.polySoftEdge(angle=0, constructionHistory=False)

    print(f"WGLL Retopo: Marked {len(edge_indices)} edges as hard.")
