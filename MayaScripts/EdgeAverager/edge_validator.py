"""
Edge Validator for EdgeAverager
Handles edge selection validation, connectivity filtering, and parallelism detection.
"""

from maya import OpenMaya
from maya import cmds
import geometry_utils


def get_selected_mesh_components():
    """
    Get selected mesh components from Maya selection

    Returns:
        tuple: (selection_list, component_type)
            - selection_list: OpenMaya.MSelectionList
            - component_type: 'edges', 'faces', or None
    """
    selection = OpenMaya.MSelectionList()
    OpenMaya.MGlobal.getActiveSelectionList(selection)

    if selection.isEmpty():
        return None, None

    # Check what type of components are selected
    dag_path = OpenMaya.MDagPath()
    component = OpenMaya.MObject()

    try:
        selection.getDagPath(0, dag_path, component)
    except:
        return None, None

    if component.isNull():
        return None, None

    # Determine component type
    if component.apiType() == OpenMaya.MFn.kMeshEdgeComponent:
        return selection, 'edges'
    elif component.apiType() == OpenMaya.MFn.kMeshPolygonComponent:
        return selection, 'faces'
    else:
        return None, None


def extract_edges_from_selection(selection_list, component_type):
    """
    Extract edge indices from selection (either direct edges or faces)

    Args:
        selection_list (OpenMaya.MSelectionList): Selection list
        component_type (str): 'edges' or 'faces'

    Returns:
        tuple: (dag_path, edge_indices)
            - dag_path: OpenMaya.MDagPath to mesh
            - edge_indices: list of int (edge indices)
    """
    dag_path = OpenMaya.MDagPath()
    component = OpenMaya.MObject()

    selection_list.getDagPath(0, dag_path, component)

    edge_indices = []

    if component_type == 'edges':
        # Direct edge selection
        edge_iter = OpenMaya.MItMeshEdge(dag_path, component)
        while not edge_iter.isDone():
            edge_indices.append(edge_iter.index())
            edge_iter.next()

    elif component_type == 'faces':
        # Extract edges from faces
        # For parallel edge detection, we want boundary edges of the face selection
        edge_set = set()

        face_iter = OpenMaya.MItMeshPolygon(dag_path, component)
        while not face_iter.isDone():
            edges = OpenMaya.MIntArray()
            face_iter.getEdges(edges)

            for i in range(edges.length()):
                edge_set.add(edges[i])

            face_iter.next()

        edge_indices = list(edge_set)

    return dag_path, edge_indices


def build_edge_connectivity_graph(dag_path, edge_indices):
    """
    Build connectivity graph for edges (edges are connected if they share a vertex)

    Args:
        dag_path (OpenMaya.MDagPath): Path to mesh
        edge_indices (list of int): Edge indices

    Returns:
        dict: Mapping of edge_index -> set of connected edge indices
    """
    connectivity = {idx: set() for idx in edge_indices}
    edge_set = set(edge_indices)

    edge_iter = OpenMaya.MItMeshEdge(dag_path)
    vertex_iter = OpenMaya.MItMeshVertex(dag_path)

    for edge_idx in edge_indices:
        # Fresh MScriptUtil for each edge setIndex call
        edge_su = OpenMaya.MScriptUtil()
        edge_prev = edge_su.asIntPtr()
        edge_iter.setIndex(edge_idx, edge_prev)

        for vertex_idx in [0, 1]:
            vertex_id = edge_iter.index(vertex_idx)

            # Fresh MScriptUtil for vertex setIndex call
            vert_su = OpenMaya.MScriptUtil()
            vert_prev = vert_su.asIntPtr()
            vertex_iter.setIndex(vertex_id, vert_prev)

            connected_edges = OpenMaya.MIntArray()
            vertex_iter.getConnectedEdges(connected_edges)

            for i in range(connected_edges.length()):
                connected_edge_idx = connected_edges[i]
                if connected_edge_idx in edge_set and connected_edge_idx != edge_idx:
                    connectivity[edge_idx].add(connected_edge_idx)

    return connectivity


def find_largest_connected_component(connectivity):
    """
    Find largest connected component using BFS

    Args:
        connectivity (dict): Edge connectivity graph

    Returns:
        list: Edge indices in largest component
    """
    if not connectivity:
        return []

    visited = set()
    components = []

    for start_edge in connectivity.keys():
        if start_edge in visited:
            continue

        # BFS from this edge
        component = []
        queue = [start_edge]

        while queue:
            current = queue.pop(0)

            if current in visited:
                continue

            visited.add(current)
            component.append(current)

            # Add unvisited neighbors to queue
            for neighbor in connectivity[current]:
                if neighbor not in visited:
                    queue.append(neighbor)

        components.append(component)

    # Return largest component
    if not components:
        return []

    return max(components, key=len)


def validate_parallel_edges(dag_path, edge_indices, angle_threshold=5.0):
    """
    Validate that edges are parallel within tolerance

    Args:
        dag_path (OpenMaya.MDagPath): Path to mesh
        edge_indices (list of int): Edge indices to validate
        angle_threshold (float): Maximum angle deviation in degrees

    Returns:
        tuple: (is_valid, parallel_edge_indices, message)
            - is_valid: bool
            - parallel_edge_indices: list of int (edges that are parallel)
            - message: str (error/info message)
    """
    if len(edge_indices) < 3:
        return False, [], "Need at least 3 edges for averaging"

    # Get direction vectors for all edges
    edge_directions = []
    edge_iter = OpenMaya.MItMeshEdge(dag_path)

    for edge_idx in edge_indices:
        su = OpenMaya.MScriptUtil()
        edge_iter.setIndex(edge_idx, su.asIntPtr())
        direction = geometry_utils.calculate_edge_direction(edge_iter)
        edge_directions.append((edge_idx, direction))

    # Use first edge as reference
    reference_idx, reference_dir = edge_directions[0]

    parallel_edges = [reference_idx]
    non_parallel_edges = []

    for edge_idx, direction in edge_directions[1:]:
        angle = geometry_utils.angle_between_vectors_degrees(reference_dir, direction)

        # Check if parallel (angle ~0°) or anti-parallel (angle ~180°)
        is_parallel = (angle < angle_threshold) or (angle > (180 - angle_threshold))

        if is_parallel:
            parallel_edges.append(edge_idx)
        else:
            non_parallel_edges.append((edge_idx, angle))

    # Need at least 3 parallel edges
    if len(parallel_edges) < 3:
        message = f"Only {len(parallel_edges)} parallel edges found (need 3+). "
        if non_parallel_edges:
            angles = [f"{idx}: {angle:.1f}°" for idx, angle in non_parallel_edges[:3]]
            message += f"Non-parallel angles: {', '.join(angles)}"
        return False, [], message

    # Success
    if non_parallel_edges:
        message = f"Found {len(parallel_edges)} parallel edges. Filtered out {len(non_parallel_edges)} non-parallel edges."
    else:
        message = f"All {len(parallel_edges)} edges are parallel."

    return True, parallel_edges, message


def extract_edge_data(dag_path, edge_indices):
    """
    Extract geometric data from edges for path calculation

    Args:
        dag_path (OpenMaya.MDagPath): Path to mesh
        edge_indices (list of int): Edge indices

    Returns:
        list of dict: Edge data with keys 'index', 'midpoint', 'direction', 'length'
    """
    edge_data_list = []
    edge_iter = OpenMaya.MItMeshEdge(dag_path)

    for edge_idx in edge_indices:
        su = OpenMaya.MScriptUtil()
        edge_iter.setIndex(edge_idx, su.asIntPtr())

        midpoint = geometry_utils.calculate_edge_midpoint(edge_iter)
        direction = geometry_utils.calculate_edge_direction(edge_iter)
        length = geometry_utils.calculate_edge_length(edge_iter)

        edge_data_list.append({
            'index': edge_idx,
            'midpoint': midpoint,
            'direction': direction,
            'length': length
        })

    return edge_data_list


def validate_and_process_selection(angle_threshold=5.0):
    """
    Main validation function: get selection, filter, and validate

    Args:
        angle_threshold (float): Parallelism tolerance in degrees

    Returns:
        tuple: (is_valid, dag_path, edge_data_list, message)
            - is_valid: bool
            - dag_path: OpenMaya.MDagPath (or None)
            - edge_data_list: list of dict (or None)
            - message: str (error/info message)
    """
    # Step 1: Get selection
    selection, component_type = get_selected_mesh_components()

    if not selection or not component_type:
        return False, None, None, "Please select mesh edges or faces"

    # Step 2: Extract edges
    dag_path, edge_indices = extract_edges_from_selection(selection, component_type)

    if not edge_indices:
        return False, None, None, "No edges found in selection"

    if len(edge_indices) < 3:
        return False, None, None, f"Need at least 3 edges (found {len(edge_indices)})"

    # Step 3: Build connectivity and filter largest component
    connectivity = build_edge_connectivity_graph(dag_path, edge_indices)
    filtered_edges = find_largest_connected_component(connectivity)

    if len(filtered_edges) < len(edge_indices):
        filtered_count = len(edge_indices) - len(filtered_edges)
        cmds.warning(f"Filtered out {filtered_count} disconnected edges")

    if len(filtered_edges) < 3:
        return False, None, None, f"After filtering, only {len(filtered_edges)} connected edges remain (need 3+)"

    # Step 4: Validate parallelism
    is_valid, parallel_edges, message = validate_parallel_edges(dag_path, filtered_edges, angle_threshold)

    if not is_valid:
        return False, None, None, message

    # Step 5: Extract edge data
    edge_data_list = extract_edge_data(dag_path, parallel_edges)

    return True, dag_path, edge_data_list, message
