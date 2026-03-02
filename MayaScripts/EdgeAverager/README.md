# EdgeAverager

A Maya Python script that averages parallel edges while preserving mesh volume through surface-constrained vertex sliding.

## Overview

EdgeAverager is a topology optimization tool that smooths selected parallel edges by calculating an optimal path through them and moving vertices toward that path while maintaining the mesh's volume and surface continuity.

### Key Features

- **Parallel Edge Smoothing**: Averages 3 or more parallel edges to create cleaner topology
- **Volume Preservation**: Maintains mesh volume by sliding vertices along the surface (not linear interpolation)
- **Smart Filtering**: Automatically filters out disconnected edges and validates parallelism
- **Face Selection Support**: Can extract and process parallel edges from selected faces
- **Smooth Falloff**: Distance-based influence prevents abrupt changes in topology
- **Undo Support**: Single undo operation for the entire process

## Installation

### Method 1: Copy to Maya Scripts Directory

1. Copy the entire `EdgeAverager` folder to your Maya scripts directory:
   - **Windows**: `Documents/maya/scripts/`
   - **Mac**: `~/Library/Preferences/Autodesk/maya/scripts/`
   - **Linux**: `~/maya/scripts/`

2. Restart Maya or run:
   ```python
   import sys
   sys.path.append('/path/to/EdgeAverager')
   ```

### Method 2: Add to PYTHONPATH

Add the parent directory of `EdgeAverager` to your `MAYA_SCRIPT_PATH` or `PYTHONPATH`.

## Usage

### Basic Usage

1. Select 3 or more parallel edges (or faces to extract edges from)
2. Run the script:

```python
import edge_averager
edge_averager.run()
```

### With UI

Launch the UI for parameter control:

```python
import edge_averager
edge_averager.run_with_ui()
```

The UI provides:
- **Parallelism Tolerance**: Angle threshold for edge parallelism (1-30 degrees)
- **Influence Distance Multiplier**: Scale the automatic influence distance (0.1-3.0x)

### Custom Parameters

```python
import edge_averager

# Custom angle threshold (default: 5.0 degrees)
edge_averager.run(angle_threshold=10.0)

# Custom influence multiplier (default: 1.0)
edge_averager.run(influence_multiplier=1.5)

# Both
edge_averager.run(angle_threshold=10.0, influence_multiplier=1.5)
```

### Quick Test

Test the script on automatically generated geometry:

```python
import edge_averager
edge_averager.quick_test()
```

This creates a test cube, selects parallel edges, and runs EdgeAverager.

## How It Works

### Algorithm Overview

1. **Input Validation**
   - Check selection (edges or faces)
   - Extract edge indices
   - Validate minimum count (3+ edges)

2. **Connectivity Filtering**
   - Build connectivity graph (edges connected via shared vertices)
   - Find largest connected component
   - Filter out disconnected/orphan edges

3. **Parallelism Validation**
   - Calculate edge direction vectors
   - Compare angles between vectors
   - Accept edges within threshold (default: 5 degrees)
   - Support both parallel and anti-parallel edges

4. **Optimal Path Calculation**
   - Extract edge midpoints, directions, and lengths
   - Calculate weighted centroid (weighted by edge length)
   - Calculate weighted average direction
   - Define optimal path as line through centroid in average direction

5. **Volume-Preserving Vertex Sliding**
   - For each vertex in selection:
     - Project onto optimal path (target position)
     - Calculate surface normal from connected faces
     - Project displacement onto tangent plane (perpendicular to normal)
     - Apply smooth distance-based falloff
     - Move vertex along surface (not straight line)

### Mathematical Details

**Optimal Path Calculation:**
```
weighted_center = Σ(midpoint_i × length_i) / Σ(length_i)
avg_direction = normalize(Σ(direction_i × length_i) / Σ(length_i))
```

**Surface Sliding:**
```
displacement = target_position - current_position
tangent_displacement = displacement - (displacement · normal) × normal
falloff = smoothstep(distance / max_distance)
new_position = current_position + tangent_displacement × falloff
```

**Smooth Falloff (Hermite):**
```
t = distance / max_distance
smoothstep(t) = 1 - (3t² - 2t³)
```

## Parameters

### angle_threshold (float, default: 5.0)
Maximum angle deviation for edges to be considered parallel. Lower values are stricter.

- **1-3 degrees**: Very strict (nearly perfect parallel edges only)
- **5-10 degrees**: Moderate (recommended range)
- **15-30 degrees**: Loose (accepts edges with noticeable angle differences)

### influence_multiplier (float, default: 1.0)
Scales the automatic influence distance. Higher values affect vertices farther from edges.

- **0.1-0.5**: Tight influence (only vertices very close to edges)
- **1.0**: Default (2x average edge length)
- **1.5-3.0**: Extended influence (broader smoothing area)

The base influence distance is automatically calculated as 2× the average edge length.

## Examples

### Example 1: Simple Cube Edges

```python
# Create cube
cube = cmds.polyCube(width=2, height=2, depth=2)[0]

# Select 3 parallel edges
cmds.select(f'{cube}.e[0]', f'{cube}.e[2]', f'{cube}.e[8]')

# Run EdgeAverager
import edge_averager
edge_averager.run()
```

### Example 2: Face Selection

```python
# Select faces on cylinder
cylinder = cmds.polyCylinder(radius=1, height=2, subdivisionsAxis=20)[0]
cmds.select(f'{cylinder}.f[0:9]')  # Top faces

# EdgeAverager extracts parallel edges automatically
import edge_averager
edge_averager.run()
```

### Example 3: Loose Tolerance

```python
# For edges that aren't perfectly parallel
import edge_averager
edge_averager.run(angle_threshold=15.0, influence_multiplier=2.0)
```

## Limitations

### Version 1.0 Constraints

- **Parallel Edges Only**: First iteration requires edges to be parallel within threshold
- **Connected Components**: Only processes largest connected edge group
- **No Live Preview**: Changes are applied immediately (use undo if needed)

### Common Issues

**"Need at least 3 edges"**
- Ensure you have 3+ edges selected
- Check that edges are connected (not isolated)

**"Only X parallel edges found"**
- Selected edges may not be parallel enough
- Increase `angle_threshold` parameter
- Check edge directions visually

**"Filtered out X disconnected edges"**
- Script automatically removes edges not connected to main group
- This is expected behavior for multi-component selections

## Advanced Usage

### Scripting Integration

```python
import edge_averager

def batch_smooth_edges(edge_groups, angle=5.0, influence=1.0):
    """Process multiple edge groups"""
    for edges in edge_groups:
        cmds.select(edges)
        edge_averager.run(
            angle_threshold=angle,
            influence_multiplier=influence,
            verbose=False  # Suppress output
        )

# Usage
edge_groups = [
    ['pCube1.e[0]', 'pCube1.e[2]', 'pCube1.e[8]'],
    ['pCube1.e[1]', 'pCube1.e[3]', 'pCube1.e[9]'],
]
batch_smooth_edges(edge_groups)
```

### Custom Influence Distance

```python
import edge_averager
import surface_slider

# Get validated selection
is_valid, dag_path, edge_data_list, message = edge_validator.validate_and_process_selection()

if is_valid:
    # Calculate optimal path
    optimal_path = geometry_utils.calculate_optimal_path(edge_data_list)

    # Apply with custom influence distance
    results = surface_slider.apply_vertex_sliding(
        dag_path=dag_path,
        edge_data_list=edge_data_list,
        optimal_path=optimal_path,
        influence_distance=5.0,  # Custom fixed distance
        influence_multiplier=1.0
    )
```

## File Structure

```
EdgeAverager/
├── __init__.py           # Package initialization
├── edge_averager.py      # Main script (run, run_with_ui, quick_test)
├── geometry_utils.py     # Math utilities (vectors, projections, falloff)
├── edge_validator.py     # Selection validation and connectivity
├── surface_slider.py     # Volume-preserving vertex sliding
└── README.md             # This file
```

## Future Enhancements

Planned features for future versions:

- **Non-Parallel Edge Support**: Detect edge loops and use spline fitting
- **Symmetry Preservation**: Auto-detect and mirror operations
- **Live Preview**: Ghost preview before applying changes
- **Edge Flow Detection**: Suggest edges to include automatically
- **Batch Processing**: Process multiple edge groups at once
- **Custom Influence Curves**: User-defined falloff functions

## Technical Details

### Dependencies

- Maya 2018+ (uses OpenMaya API 1.0)
- Python 2.7 or 3.x (Maya compatible)

### Maya API Usage

- `OpenMaya.MItMeshEdge` - Edge iteration and queries
- `OpenMaya.MItMeshVertex` - Vertex manipulation
- `OpenMaya.MItMeshPolygon` - Face queries
- `OpenMaya.MFnMesh` - Mesh modifications
- `OpenMaya.MVector` - Vector operations
- `OpenMaya.MPoint` - 3D point operations

### Performance

- **Edge Count**: Efficiently handles 3-100 edges
- **Vertex Updates**: Batch updates for performance
- **Undo**: Single undo chunk for entire operation
- **Memory**: Minimal overhead (processes only selected vertices)

## Testing

### Manual Testing

1. **Simple parallel edges:**
   ```python
   edge_averager.quick_test()
   ```

2. **Face selection:**
   - Select faces on cylinder
   - Run `edge_averager.run()`
   - Verify parallel edges extracted

3. **Non-parallel edges:**
   - Select non-parallel edges
   - Verify error message appears

4. **Disconnected geometry:**
   - Select edges from separate meshes
   - Verify filtering message

### Volume Validation

```python
# Before
mesh_fn = OpenMaya.MFnMesh(dag_path)
# Calculate volume (custom implementation needed)

# Run EdgeAverager
edge_averager.run()

# After
# Calculate volume again
# Assert: volume_after ≈ volume_before (within 1-2%)
```

## Troubleshooting

### Import Errors

If you get import errors:

```python
import sys
sys.path.append('/full/path/to/EdgeAverager')
import edge_averager
```

### Maya Version Compatibility

If using Maya 2022+, consider updating to OpenMaya 2.0:
- Replace `OpenMaya.MVector` with `om2.MVector`
- Replace iterators with Maya Python API 2.0 equivalents

### Mesh Artifacts

If you see inverted faces or strange topology:
- Check that input edges are actually parallel
- Reduce `influence_multiplier` to affect fewer vertices
- Try lower `angle_threshold` for stricter parallelism

## License

This script is provided as-is for educational and production use.

## Author

Arthur Klein

## Version

1.0.0 - Initial Release

---

## Quick Reference

```python
# Import
import edge_averager

# Basic usage
edge_averager.run()

# With UI
edge_averager.run_with_ui()

# Custom parameters
edge_averager.run(angle_threshold=10.0, influence_multiplier=1.5)

# Quick test
edge_averager.quick_test()
```

**Select 3+ parallel edges or faces → Run script → Enjoy cleaner topology!**
