# WGLL Retopo — Milestones

## Current Focus
Clothing geometry (t-shirt torso, tubular shapes) for mobile game characters.
Hair analysis planned for later. Head/face topology deferred.

---

## M1: Analysis Tool Foundation
- [x] Maya UI: two mesh input slots with load-from-selection
- [x] Validation: high-res must have more faces than low-res
- [x] Basic per-mesh stats (verts, faces, tri/quad/ngon, bounding box)
- [x] Text file output to `WGLL_Retopo/analysis/`
- [x] Entry point: `WGLLRetopo.analyze()`

## M2: Topology Quality Metrics (Low-Res)
- [x] Face area uniformity (std dev, min/max ratio, score)
- [x] Edge length uniformity (std dev, min/max ratio, score)
- [x] Valence distribution (3/4/5/6+ edge counts per vertex)
- [x] Quad ratio and tri/ngon counts
- [x] Pole detection with world-space positions
- [x] Vertex spacing (nearest-neighbor distances, uniformity score)

## M3: High-Res to Low-Res Relationship
- [x] Surface deviation (mean/max/median/95th percentile distance)
- [x] Normal deviation (angle between low-res and high-res normals)
- [x] Bounding box comparison (world space, sizes)
- [x] Transform comparison (position, rotation, scale)
- [x] Summary scores (A-F grading)

## M4: polyRetopo Fix
- [ ] Fix polyRetopo deferred evaluation bug (node not computing before history delete)
- [ ] Match exact MEL command that works manually in Maya
- [ ] Verify face count actually changes after retopo

## M5: Curvature-Aware Analysis
- [ ] High-res curvature map vs low-res vertex density correlation
- [ ] Feature preservation score
- [ ] Are high-curvature areas getting more verts?

## M6: External Tool Integration (Instant Meshes)
- [ ] Download/install Instant Meshes macOS binary
- [ ] Subprocess wrapper: export OBJ, run IM, import result
- [ ] Field-aligned quad meshing as alternative to polyRetopo

## M7: Template Projection System
- [ ] Pre-built OBJ templates (stylized head, body, clothing)
- [ ] Landmark alignment (Procrustes + RBF deformation)
- [ ] Closest-point projection (shrinkwrap)
- [ ] Constrained Laplacian relaxation

## M8: WGLL Reference System
- [ ] Analyze user-provided "good topology" examples
- [ ] Build topology quality profiles (JSON)
- [ ] Score retopo results against reference profiles
- [ ] Comparison mode: two retopo attempts vs same high-res

## M9: Retopo on Screen
- [ ] One-click retopo of whatever is visible in viewport
- [ ] Auto-detect clothing vs head vs hair geometry
- [ ] Apply appropriate strategy per piece

---

## Change Log
- 2026-02-09: Project created. M1-M3 implemented (analysis tool). M4 in progress (polyRetopo fix).
