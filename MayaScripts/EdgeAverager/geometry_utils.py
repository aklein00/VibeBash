"""
Geometry Utilities for EdgeAverager
Provides math utilities for vector operations, projections, and smooth falloff calculations.
"""

from maya import OpenMaya
import math


class PathDefinition:
    """Defines an optimal path through edges with center and direction"""
    def __init__(self, center, direction):
        """
        Args:
            center (OpenMaya.MPoint): Weighted centroid of path
            direction (OpenMaya.MVector): Normalized average direction
        """
        self.center = center
        self.direction = direction

    def __repr__(self):
        return f"PathDefinition(center={self.center}, direction={self.direction})"


def calculate_distance_point_to_line(point, line_point, line_direction):
    """
    Calculate perpendicular distance from point to infinite line

    Args:
        point (OpenMaya.MPoint): Point to measure from
        line_point (OpenMaya.MPoint): Any point on the line
        line_direction (OpenMaya.MVector): Direction vector of line (should be normalized)

    Returns:
        float: Distance from point to line
    """
    # Vector from line point to target point
    point_vector = OpenMaya.MVector(point - line_point)

    # Project onto line direction
    projection_length = point_vector * line_direction

    # Calculate perpendicular component
    projection = line_direction * projection_length
    perpendicular = point_vector - projection

    return perpendicular.length()


def project_point_onto_line(point, line_point, line_direction):
    """
    Project a point onto an infinite line

    Args:
        point (OpenMaya.MPoint): Point to project
        line_point (OpenMaya.MPoint): Any point on the line
        line_direction (OpenMaya.MVector): Direction vector of line (should be normalized)

    Returns:
        OpenMaya.MPoint: Projected point on the line
    """
    # Vector from line point to target point
    point_vector = OpenMaya.MVector(point - line_point)

    # Project onto line direction
    projection_length = point_vector * line_direction
    projection = line_direction * projection_length

    # Projected point
    projected = line_point + projection
    return projected


def project_vector_onto_plane(vector, plane_normal):
    """
    Project a vector onto a plane defined by its normal
    (Removes the component parallel to the normal)

    Args:
        vector (OpenMaya.MVector): Vector to project
        plane_normal (OpenMaya.MVector): Normal of the plane (should be normalized)

    Returns:
        OpenMaya.MVector: Projected vector on the plane
    """
    # Component parallel to normal
    parallel_component = (vector * plane_normal) * plane_normal

    # Remove parallel component
    tangent_component = vector - parallel_component

    return tangent_component


def smooth_falloff(distance, max_distance):
    """
    Calculate smooth hermite falloff (0 to 1) based on distance
    Uses smoothstep interpolation: 3t² - 2t³

    Args:
        distance (float): Distance from source
        max_distance (float): Maximum influence distance

    Returns:
        float: Falloff value [0, 1] where 0=no influence, 1=full influence
    """
    if max_distance <= 0:
        return 1.0
    if distance <= 0:
        return 1.0
    if distance >= max_distance:
        return 0.0

    # Normalize distance to [0, 1]
    t = distance / max_distance

    # Smoothstep interpolation (inverted so 0=full influence)
    smooth_t = 3.0 * t * t - 2.0 * t * t * t

    return 1.0 - smooth_t


def calculate_weighted_center(points, weights):
    """
    Calculate weighted centroid of points

    Args:
        points (list of OpenMaya.MPoint): Points to average
        weights (list of float): Weight for each point

    Returns:
        OpenMaya.MPoint: Weighted center point
    """
    if not points or not weights or len(points) != len(weights):
        raise ValueError("Points and weights must be non-empty and same length")

    total_weight = sum(weights)
    if total_weight == 0:
        raise ValueError("Total weight cannot be zero")

    weighted_sum = OpenMaya.MPoint(0, 0, 0)
    for point, weight in zip(points, weights):
        weighted_sum += OpenMaya.MVector(point) * weight

    center = OpenMaya.MPoint(weighted_sum / total_weight)
    return center


def calculate_weighted_average_vector(vectors, weights):
    """
    Calculate weighted average of vectors

    Args:
        vectors (list of OpenMaya.MVector): Vectors to average
        weights (list of float): Weight for each vector

    Returns:
        OpenMaya.MVector: Weighted average vector (normalized)
    """
    if not vectors or not weights or len(vectors) != len(weights):
        raise ValueError("Vectors and weights must be non-empty and same length")

    total_weight = sum(weights)
    if total_weight == 0:
        raise ValueError("Total weight cannot be zero")

    weighted_sum = OpenMaya.MVector(0, 0, 0)
    for vector, weight in zip(vectors, weights):
        weighted_sum += vector * weight

    avg_vector = weighted_sum / total_weight
    avg_vector.normalize()

    return avg_vector


def calculate_edge_midpoint(edge_iter):
    """
    Calculate midpoint of an edge

    Args:
        edge_iter (OpenMaya.MItMeshEdge): Edge iterator positioned at edge

    Returns:
        OpenMaya.MPoint: Midpoint of edge
    """
    point0 = edge_iter.point(0)
    point1 = edge_iter.point(1)

    midpoint = OpenMaya.MPoint(
        (point0.x + point1.x) / 2.0,
        (point0.y + point1.y) / 2.0,
        (point0.z + point1.z) / 2.0
    )

    return midpoint


def calculate_edge_direction(edge_iter):
    """
    Calculate direction vector of an edge

    Args:
        edge_iter (OpenMaya.MItMeshEdge): Edge iterator positioned at edge

    Returns:
        OpenMaya.MVector: Normalized direction vector
    """
    point0 = edge_iter.point(0)
    point1 = edge_iter.point(1)

    direction = OpenMaya.MVector(point1 - point0)
    direction.normalize()

    return direction


def calculate_edge_length(edge_iter):
    """
    Calculate length of an edge

    Args:
        edge_iter (OpenMaya.MItMeshEdge): Edge iterator positioned at edge

    Returns:
        float: Length of edge
    """
    point0 = edge_iter.point(0)
    point1 = edge_iter.point(1)

    direction = OpenMaya.MVector(point1 - point0)
    return direction.length()


def calculate_optimal_path(edge_data_list):
    """
    Calculate optimal path through parallel edges using weighted centroid and average direction

    Args:
        edge_data_list (list of dict): List of edge data with keys:
            - 'midpoint': OpenMaya.MPoint
            - 'direction': OpenMaya.MVector
            - 'length': float

    Returns:
        PathDefinition: Optimal path with center and direction
    """
    if not edge_data_list:
        raise ValueError("Edge data list cannot be empty")

    # Extract data
    midpoints = [data['midpoint'] for data in edge_data_list]
    directions = [data['direction'] for data in edge_data_list]
    lengths = [data['length'] for data in edge_data_list]

    # Calculate weighted center
    weighted_center = calculate_weighted_center(midpoints, lengths)

    # Calculate weighted average direction
    avg_direction = calculate_weighted_average_vector(directions, lengths)

    return PathDefinition(weighted_center, avg_direction)


def calculate_vertex_normal_from_faces(vertex_iter):
    """
    Calculate average normal at a vertex from its connected faces

    Args:
        vertex_iter (OpenMaya.MItMeshVertex): Vertex iterator positioned at vertex

    Returns:
        OpenMaya.MVector: Averaged normal vector (normalized)
    """
    # Get connected face indices
    face_indices = OpenMaya.MIntArray()
    vertex_iter.getConnectedFaces(face_indices)

    if face_indices.length() == 0:
        # Fallback to world up if no faces
        return OpenMaya.MVector(0, 1, 0)

    # Sum normals from all connected faces
    normal_sum = OpenMaya.MVector(0, 0, 0)
    num_faces = face_indices.length()

    for i in range(num_faces):
        face_normal = OpenMaya.MVector()
        vertex_iter.getNormal(face_normal, i)
        normal_sum += face_normal

    # Average and normalize
    avg_normal = normal_sum / float(num_faces)
    avg_normal.normalize()

    return avg_normal


def is_zero_vector(vector, epsilon=1e-6):
    """
    Check if a vector is approximately zero

    Args:
        vector (OpenMaya.MVector): Vector to check
        epsilon (float): Tolerance for zero comparison

    Returns:
        bool: True if vector length is less than epsilon
    """
    return vector.length() < epsilon


def angle_between_vectors_degrees(v1, v2):
    """
    Calculate angle between two vectors in degrees

    Args:
        v1 (OpenMaya.MVector): First vector
        v2 (OpenMaya.MVector): Second vector

    Returns:
        float: Angle in degrees [0, 180]
    """
    angle_radians = v1.angle(v2)
    return math.degrees(angle_radians)
