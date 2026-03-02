"""
EdgeAverager Package
Maya Python script for averaging parallel edges while preserving mesh volume.

Main Functions:
    - run(): Execute EdgeAverager on current selection
    - run_with_ui(): Launch UI for parameter control
    - quick_test(): Create test geometry and run script

Author: Arthur Klein
Version: 1.0.0
"""

from .edge_averager import run, run_with_ui, quick_test

__version__ = "1.0.0"
__author__ = "Arthur Klein"
__all__ = ["run", "run_with_ui", "quick_test"]
