import importlib
from . import wgll_retopo_shelf
importlib.reload(wgll_retopo_shelf)
from .wgll_retopo_shelf import run, run_with_ui


def analyze():
    """Open the WGLL Mesh Analysis comparison UI."""
    import sys, os, site
    wgll_root = '/Users/arthurklein/Documents/Work/Side/VibeBash/WGLL_Retopo'
    user_site = site.getusersitepackages()
    for p in [wgll_root, os.path.join(wgll_root, 'maya_bridge'), user_site]:
        if p not in sys.path:
            sys.path.insert(0, p)
    import maya_bridge.mesh_analysis_ui
    importlib.reload(maya_bridge.mesh_analysis_ui)
    import maya_bridge.mesh_analysis_report
    importlib.reload(maya_bridge.mesh_analysis_report)
    maya_bridge.mesh_analysis_ui.show_analysis_ui()
