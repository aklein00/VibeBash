# WGLL Retopo

**What Good Looks Like** — Curvature-guided retopology toolkit for mobile game characters.

## The Problem

Automatic retopology tools (QuadRemesh, Maya's `polyRetopo`) distribute polygons uniformly across a mesh. But animated characters need edge loops concentrated around eyes, mouths, and joints — not evenly everywhere. The result: auto-retopo output looks okay statically but deforms terribly during animation.

## The Solution

WGLL Retopo provides three strategies, each progressively smarter:

### Strategy 1: Guided polyRetopo (Phase 1 — Available Now)
Analyzes your sculpt's curvature to find feature regions (eyes, nostrils, joints), marks those as hard edges, then runs `polyRetopo` with `preserveHardEdges=True`. The result follows feature lines far better than blind auto-retopo.

### Strategy 2: External Remesher (Phase 2 — Planned)
Integrates Instant Meshes (field-aligned quad meshing) for dramatically better quad flow than polyRetopo.

### Strategy 3: Template Projection (Phase 3 — Planned)
Pre-built topology templates for stylized characters that deform onto your sculpt via landmark fitting + shrinkwrap. Guarantees proper edge loops by construction.

## Quick Start

### Prerequisites
Install dependencies into Maya's Python:
```bash
/Applications/Autodesk/maya2025/Maya.app/Contents/bin/mayapy -m pip install scipy trimesh
```

### Usage in Maya

**Option A — Shelf button:**
Run `rebuild_ak_shelf.py` in Maya Script Editor to add the "Retopo" button, then click it.

**Option B — Script Editor:**
```python
import sys
sys.path.append('/Users/arthurklein/Documents/Work/Side/VibeBash/MayaScripts')
sys.path.append('/Users/arthurklein/Documents/Work/Side/VibeBash/WGLL_Retopo')
import WGLLRetopo
WGLLRetopo.run_with_ui()    # Full UI with presets
# or
WGLLRetopo.run()            # Quick retopo with defaults
```

### Presets

| Preset | Target Faces | Best For |
|--------|-------------|----------|
| Hero Character | 6,000 quads | Main character, close to camera |
| Background NPC | 2,000 quads | Distant characters, crowds |
| Prop | 500 quads | Objects, accessories |

## Architecture

```
WGLL_Retopo/
├── core/                   # Pure Python (no Maya dependency)
│   ├── mesh_io.py          # OBJ read/write, WGLLMesh dataclass
│   ├── mesh_analysis.py    # Curvature, feature detection, topology stats
│   └── guide_generation.py # Generate retopo guides from analysis
├── maya_bridge/            # Maya-specific integration
│   ├── maya_mesh_adapter.py       # Maya mesh <-> WGLLMesh
│   └── maya_polyretopo_tuned.py   # Guided polyRetopo wrapper
├── templates/              # Pre-built topology template OBJs (Phase 3)
├── references/             # User-provided WGLL reference models (Phase 4)
└── presets/                # Parameter presets (hero, npc, prop)
```

The core library has zero Maya imports — it can be tested standalone and extended to other DCC tools.

## Roadmap

- [x] Phase 1: Guided polyRetopo (curvature analysis + hard edge guides)
- [ ] Phase 2: Instant Meshes integration (external quad remesher)
- [ ] Phase 3: Template projection system (stylized head, body templates)
- [ ] Phase 4: WGLL reference system (quality scoring against reference models)
- [ ] Phase 5: UI polish, density painting, LOD tiers
