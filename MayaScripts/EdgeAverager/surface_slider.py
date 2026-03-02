"""
Surface Slider for EdgeAverager
Implements volume-preserving vertex sliding algorithm that moves vertices
toward optimal path while maintaining mesh surface continuity.
"""

from maya import OpenMaya
import geometry_utils


def get_vertices_from_edges(dag_path, edge_data_list):
    """
    Extract all unique vertices from edge list

    Args:
        dag_path (OpenMaya.MDagPath): Path to mesh
        edge_data_list (list of dict): Edge data with 'index' key

    Returns:
        set: Set of vertex indices
    """
    vertex_indices = set()
    edge_iter = OpenMaya.MItMeshEdge(dag_path)

    for edge_data in edge_data_list:
        su = OpenMaya.MScriptUtil()
        edge_iter.setIndex(edge_data['index'], su.asIntPtr())

        # Add both vertices of edge
        vertex_indices.add(edge_iter.index(0))
        vertex_indices.add(edge_iter.index(1))

    return vertex_indices


def calculate_vertex_target_position(vertex_position, optimal_path):
    """
    Calculate target position for vertex (projection onto optimal path)

    Args:
        vertex_position (OpenMaya.MPoint): Current vertex position
        optimal_path (geometry_utils.PathDefinition): Optimal path definition

    Returns:
        OpenMaya.MPoint: Target position on path
    """
    return geometry_utils.project_point_onto_line(
        vertex_position,
        optimal_path.center,
        optimal_path.direction
    )


def calculate_vertex_surface_normal(dag_path, vertex_index):
    """
    Calculate average surface normal at vertex from connected faces

    Args:
        dag_path (OpenMaya.MDagPath): Path to mesh
        vertex_index (int): Vertex index

    Returns:
        OpenMaya.MVector: Averaged surface normal
    """
    vertex_iter = OpenMaya.MItMeshVertex(dag_path)
    su = OpenMaya.MScriptUtil()
    vertex_iter.setIndex(vertex_index, su.asIntPtr())

    return geometry_utils.calculate_vertex_normal_from_faces(vertex_iter)


def calculate_distance_to_path(vertex_position, optimal_path):
    """
    Calculate perpendicular distance from vertex to optimal path

    Args:
        vertex_position (OpenMaya.MPoint): Vertex position
        optimal_path (geometry_utils.PathDefinition): Optimal path

    Returns:
        float: Distance to path
    """
    return geometry_utils.calculate_distance_point_to_line(
        vertex_position,
        optimal_path.center,
        optimal_path.direction
    )


def slide_vertex_on_surface(current_position, target_position, surface_normal,
                           distance_to_path, max_influence_distance):
    """
    Calculate new vertex position with surface-constrained sliding

    Args:
        current_position (OpenMaya.MPoint): Current vertex position
        target_position (OpenMaya.MPoint): Target position on path
        surface_normal (OpenMaya.MVector): Surface normal at vertex
        distance_to_path (float): Distance from vertex to path
        max_influence_distance (float): Maximum distance for influence falloff

    Returns:
        OpenMaya.MPoint: New vertex position
    """
    # Calculate displacement vector
    displacement = OpenMaya.MVector(target_position - current_position)

    # Check if displacement is significant
    if geometry_utils.is_zero_vector(displacement):
        return current_position

    # Project displacement onto tangent plane (perpendicular to surface normal)
    tangent_displacement = geometry_utils.project_vector_onto_plane(
        displacement,
        surface_normal
    )

    # Apply smooth falloff based on distance to path
    falloff = geometry_utils.smooth_falloff(distance_to_path, max_influence_distance)

    # Calculate final position
    final_displacement = tangent_displacement * falloff
    new_position = current_position + final_displacement

    return new_position


def calculate_automatic_influence_distance(edge_data_list):
    """
    Automatically calculate influence distance based on edge lengths
    Uses average edge length as base influence distance

    Args:
        edge_data_list (list of dict): Edge data with 'length' key

    Returns:
        float: Influence distance
    """
    if not edge_data_list:
        return 1.0  # Default fallback

    total_length = sum(data['length'] for data in edge_data_list)
    avg_length = total_length / len(edge_data_list)

    # Use 2x average edge length as influence distance
    # This ensures smooth falloff extends beyond immediate edge area
    return avg_length * 2.0


def apply_vertex_sliding(dag_path, edge_data_list, optimal_path,
                        influence_distance=None, influence_multiplier=1.0):
    """
    Apply volume-preserving vertex sliding to all vertices in edge selection

    Args:
        dag_path (OpenMaya.MDagPath): Path to mesh
        edge_data_list (list of dict): Edge data
        optimal_path (geometry_utils.PathDefinition): Optimal path to slide toward
        influence_distance (float or None): Max influence distance (None = auto-calculate)
        influence_multiplier (float): Multiplier for influence distance (default 1.0)

    Returns:
        dict: Results with keys 'vertices_moved', 'max_displacement', 'avg_displacement'
    """
    # Auto-calculate influence distance if not provided
    if influence_distance is None:
        influence_distance = calculate_automatic_influence_distance(edge_data_list)

    # Apply multiplier
    influence_distance *= influence_multiplier

    # Get all vertices from edges
    vertex_indices = get_vertices_from_edges(dag_path, edge_data_list)

    # Get mesh function set for vertex modifications
    mesh_fn = OpenMaya.MFnMesh(dag_path)

    # Calculate new positions for all vertices
    vertex_iter = OpenMaya.MItMeshVertex(dag_path)
    new_positions = {}
    displacements = []

    for vertex_index in vertex_indices:
        su = OpenMaya.MScriptUtil()
        vertex_iter.setIndex(vertex_index, su.asIntPtr())

        current_position = vertex_iter.position(OpenMaya.MSpace.kWorld)
        target_position = calculate_vertex_target_position(current_position, optimal_path)
        surface_normal = calculate_vertex_surface_normal(dag_path, vertex_index)
        distance_to_path = calculate_distance_to_path(current_position, optimal_path)

        new_position = slide_vertex_on_surface(
            current_position,
            target_position,
            surface_normal,
            distance_to_path,
            influence_distance
        )

        new_positions[vertex_index] = new_position

        displacement_vector = OpenMaya.MVector(new_position - current_position)
        displacements.append(displacement_vector.length())

    # Apply all vertex position changes (fresh iterator for write pass)
    write_iter = OpenMaya.MItMeshVertex(dag_path)
    for vertex_index, new_position in new_positions.items():
        su = OpenMaya.MScriptUtil()
        write_iter.setIndex(vertex_index, su.asIntPtr())
        write_iter.setPosition(new_position, OpenMaya.MSpace.kWorld)

    # Calculate statistics
    results = {
        'vertices_moved': len(new_positions),
        'max_displacement': max(displacements) if displacements else 0.0,
        'avg_displacement': sum(displacements) / len(displacements) if displacements else 0.0,
        'influence_distance': influence_distance
    }

    return results


def estimate_volume_change(dag_path, vertex_indices, old_positions, new_positions):
    """
    Estimate volume change caused by vertex sliding (optional validation)
    This is an approximation based on local volume displacement

    Args:
        dag_path (OpenMaya.MDagPath): Path to mesh
        vertex_indices (list): Vertex indices that moved
        old_positions (dict): Mapping vertex_index -> old MPoint
        new_positions (dict): Mapping vertex_index -> new MPoint

    Returns:
        float: Estimated volume change (positive = volume increase)
    """
    # Simplified volume estimation:
    # Sum of (displacement * area of connected faces)
    volume_change = 0.0

    vertex_iter = OpenMaya.MItMeshVertex(dag_path)
    face_iter = OpenMaya.MItMeshPolygon(dag_path)

    for vertex_index in vertex_indices:
        if vertex_index not in old_positions or vertex_index not in new_positions:
            continue

        vert_su = OpenMaya.MScriptUtil()
        vertex_iter.setIndex(vertex_index, vert_su.asIntPtr())

        surface_normal = calculate_vertex_surface_normal(dag_path, vertex_index)

        old_pos = old_positions[vertex_index]
        new_pos = new_positions[vertex_index]
        displacement = OpenMaya.MVector(new_pos - old_pos)
        normal_displacement = displacement * surface_normal

        face_indices = OpenMaya.MIntArray()
        vertex_iter.getConnectedFaces(face_indices)

        num_faces = face_indices.length()
        if num_faces == 0:
            continue

        total_face_area = 0.0
        for i in range(num_faces):
            # Fresh MScriptUtil for each face setIndex — must stay in scope through getArea
            face_su = OpenMaya.MScriptUtil()
            face_iter.setIndex(face_indices[i], face_su.asIntPtr())
            # area_util must persist until getDouble completes
            area_util = OpenMaya.MScriptUtil(0.0)
            area_ptr = area_util.asDoublePtr()
            face_iter.getArea(area_ptr, OpenMaya.MSpace.kWorld)
            total_face_area += OpenMaya.MScriptUtil.getDouble(area_ptr)

        vertex_volume_change = normal_displacement * (total_face_area / num_faces)
        volume_change += vertex_volume_change

    return volume_change
