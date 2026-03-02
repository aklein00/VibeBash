"""
EdgeAverager - Main Script
Maya Python script for averaging parallel edges while preserving mesh volume.

Usage:
    1. Select 3+ parallel edges (or faces to extract edges from)
    2. Run: edge_averager.run()
    3. Optional parameters:
       - angle_threshold: Parallelism tolerance in degrees (default: 5.0)
       - influence_multiplier: Scale influence distance (default: 1.0)

Example:
    import edge_averager
    edge_averager.run()

    # With custom parameters
    edge_averager.run(angle_threshold=10.0, influence_multiplier=1.5)
"""

from maya import cmds
from maya import OpenMaya
import sys
import os

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import geometry_utils
import edge_validator
import surface_slider


def run(angle_threshold=5.0, influence_multiplier=1.0, verbose=True):
    """
    Main entry point for EdgeAverager script

    Args:
        angle_threshold (float): Maximum angle deviation for parallel edges (degrees)
        influence_multiplier (float): Multiplier for automatic influence distance
        verbose (bool): Print detailed feedback

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Open undo chunk
        cmds.undoInfo(openChunk=True)

        if verbose:
            print("\n" + "="*60)
            print("EdgeAverager - Parallel Edge Smoothing")
            print("="*60)

        # Step 1: Validate and process selection
        if verbose:
            print("\n[1/4] Validating selection...")

        is_valid, dag_path, edge_data_list, message = edge_validator.validate_and_process_selection(
            angle_threshold=angle_threshold
        )

        if not is_valid:
            cmds.error(f"Validation failed: {message}")
            return False

        if verbose:
            print(f"  ✓ {message}")
            print(f"  ✓ Processing {len(edge_data_list)} edges")

        # Step 2: Calculate optimal path
        if verbose:
            print("\n[2/4] Calculating optimal path...")

        optimal_path = geometry_utils.calculate_optimal_path(edge_data_list)

        if verbose:
            print(f"  ✓ Path center: ({optimal_path.center.x:.3f}, "
                  f"{optimal_path.center.y:.3f}, {optimal_path.center.z:.3f})")
            print(f"  ✓ Path direction: ({optimal_path.direction.x:.3f}, "
                  f"{optimal_path.direction.y:.3f}, {optimal_path.direction.z:.3f})")

        # Step 3: Apply vertex sliding
        if verbose:
            print("\n[3/4] Applying volume-preserving vertex sliding...")

        results = surface_slider.apply_vertex_sliding(
            dag_path=dag_path,
            edge_data_list=edge_data_list,
            optimal_path=optimal_path,
            influence_distance=None,  # Auto-calculate
            influence_multiplier=influence_multiplier
        )

        if verbose:
            print(f"  ✓ Vertices moved: {results['vertices_moved']}")
            print(f"  ✓ Influence distance: {results['influence_distance']:.3f}")
            print(f"  ✓ Max displacement: {results['max_displacement']:.3f}")
            print(f"  ✓ Avg displacement: {results['avg_displacement']:.3f}")

        # Step 4: Finalize
        if verbose:
            print("\n[4/4] Finalizing...")
            print("  ✓ Operation complete!")
            print("\n" + "="*60)
            print("Success! Edges have been averaged.")
            print("="*60 + "\n")

        return True

    except Exception as e:
        cmds.error(f"EdgeAverager failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Close undo chunk
        cmds.undoInfo(closeChunk=True)


def run_with_ui():
    """
    Launch UI for EdgeAverager with parameter controls
    """
    window_name = "edgeAveragerWindow"

    # Delete existing window if it exists
    if cmds.window(window_name, exists=True):
        cmds.deleteUI(window_name)

    # Create window
    window = cmds.window(window_name, title="EdgeAverager", widthHeight=(400, 200))

    cmds.columnLayout(adjustableColumn=True, rowSpacing=10, columnOffset=("both", 10))

    cmds.text(label="EdgeAverager - Parallel Edge Smoothing", font="boldLabelFont")
    cmds.separator(height=10)

    # Angle threshold slider
    cmds.text(label="Parallelism Tolerance (degrees):", align="left")
    angle_slider = cmds.floatSliderGrp(
        field=True,
        minValue=1.0,
        maxValue=30.0,
        value=5.0,
        step=0.5,
        columnWidth=[(1, 80), (2, 250)]
    )

    # Influence multiplier slider
    cmds.text(label="Influence Distance Multiplier:", align="left")
    influence_slider = cmds.floatSliderGrp(
        field=True,
        minValue=0.1,
        maxValue=3.0,
        value=1.0,
        step=0.1,
        columnWidth=[(1, 80), (2, 250)]
    )

    cmds.separator(height=10)

    # Apply button
    def apply_callback(*args):
        angle = cmds.floatSliderGrp(angle_slider, query=True, value=True)
        influence = cmds.floatSliderGrp(influence_slider, query=True, value=True)
        run(angle_threshold=angle, influence_multiplier=influence, verbose=True)

    cmds.button(label="Apply EdgeAverager", command=apply_callback, height=40)

    cmds.separator(height=5)
    cmds.text(label="Select 3+ parallel edges or faces", font="smallPlainLabelFont")

    cmds.showWindow(window)


def quick_test():
    """
    Quick test function to verify script functionality
    Creates test geometry and runs EdgeAverager
    """
    print("\n" + "="*60)
    print("EdgeAverager Quick Test")
    print("="*60)

    # Create test cube
    cube = cmds.polyCube(name='edgeAverager_test_cube', width=2, height=2, depth=2)[0]
    print(f"\n✓ Created test cube: {cube}")

    # Select 3 parallel edges on top face
    cmds.select(f'{cube}.e[0]', f'{cube}.e[2]', f'{cube}.e[8]', replace=True)
    print("✓ Selected 3 parallel edges")

    # Run EdgeAverager
    print("\n" + "-"*60)
    success = run(verbose=True)

    if success:
        print("\n✓ Test completed successfully!")
    else:
        print("\n✗ Test failed")

    return success


# Auto-run for command line execution
if __name__ == "__main__":
    # If running from Maya script editor or command line
    print("EdgeAverager loaded successfully!")
    print("\nUsage:")
    print("  edge_averager.run()           - Run with selection")
    print("  edge_averager.run_with_ui()   - Launch UI")
    print("  edge_averager.quick_test()    - Run test\n")
