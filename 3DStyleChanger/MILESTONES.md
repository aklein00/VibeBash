 want # 3D Style Changer - Milestone Plan

**Project Goal:** Create a ComfyUI workflow that takes an input 3D model, applies style changes via text prompts, and generates a new stylized 3D model using AI. Optimized for simple game asset creation.

**Core Technology Stack:**
- ComfyUI as the workflow engine
- Hunyuan3D for image-to-3D generation (preferred over TripoSR)
- Image editing AI (Recraft Banana, Flux, or SD3 with ControlNet)
- Custom nodes for 3D model I/O

**Design Philosophy:**
- Start simple: Single-view screenshot approach first
- Iterate towards quality: Multi-view comes later
- Practical for game dev: Simple assets, fast iteration
- Accept AI limitations: First pass doesn't need perfection

---

## Milestone 1: Foundation & Research ⏳

**Goal:** Establish technical foundation and validate core workflow components.

### Tasks:
- [x] Define project scope and milestone plan
- [ ] Research Hunyuan3D implementation options:
  - [ ] Official Hunyuan3D repository capabilities
  - [ ] ComfyUI integration status (existing nodes or custom needed)
  - [ ] Input/output formats supported
  - [ ] API requirements and rate limits
- [ ] Test Hunyuan3D locally with sample images:
  - [ ] Single-view image-to-3D generation
  - [ ] Quality assessment with simple objects
  - [ ] Export format compatibility (.glb, .obj, .fbx)
- [ ] Identify image editing solution:
  - [ ] Recraft Banana API availability
  - [ ] Alternative: Flux Dev with image conditioning
  - [ ] Alternative: SD3 with IP-Adapter + ControlNet
- [ ] Set up development environment:
  - [ ] ComfyUI installation and configuration
  - [ ] Python dependencies for 3D processing
  - [ ] Test 3D model loading libraries (trimesh, PyTorch3D, or Three.js)

**Success Criteria:**
- Hunyuan3D successfully generates 3D model from a test image
- Image editing tool produces style-modified images from prompts
- 3D file formats confirmed compatible with target game engines

**Deliverables:**
- Technical research document (`TECH_RESEARCH.md`)
- Working Hunyuan3D test script
- List of required Python packages (`requirements.txt`)

---

## Milestone 2: 3D Model Loading & Rendering 📦

**Goal:** Create custom ComfyUI node to load 3D models and render screenshots.

### Tasks:
- [ ] Choose 3D rendering backend:
  - [ ] Option A: PyTorch3D (native Python, good for AI workflows)
  - [ ] Option B: Three.js via Node.js subprocess
  - [ ] Option C: Blender headless rendering
- [ ] Develop `Load3DModel` custom node:
  - [ ] Input: File path to 3D model (.obj, .glb, .fbx)
  - [ ] Output: 3D model data structure (mesh, textures, metadata)
  - [ ] Supported formats: OBJ, GLB minimum
- [ ] Develop `Render3DScreenshot` custom node:
  - [ ] Input: 3D model data, camera parameters
  - [ ] Output: Rendered image (PNG, 1024x1024 default)
  - [ ] Features:
    - [ ] Adjustable camera angle (front view default)
    - [ ] Lighting setup (3-point lighting)
    - [ ] Background options (white, transparent, gradient)
    - [ ] Resolution control
- [ ] Test with sample 3D models:
  - [ ] Simple objects (cube, sphere, teapot)
  - [ ] Game-style low-poly assets (character, prop)
  - [ ] Verify clean renders without artifacts

**Success Criteria:**
- Load common 3D file formats in ComfyUI
- Render clean screenshots suitable for image-to-3D input
- Fast rendering (< 2 seconds per screenshot)

**Deliverables:**
- `nodes/load_3d_model.py` - Custom ComfyUI node
- `nodes/render_3d_screenshot.py` - Custom ComfyUI node
- `examples/test_models/` - Sample 3D models for testing
- Node documentation in README

---

## Milestone 3: Image Style Editing Integration 🎨

**Goal:** Integrate AI image editing for style transfer based on text prompts.

### Tasks:
- [ ] Implement image editing node:
  - [ ] Primary: Recraft Banana API integration
  - [ ] Fallback: Flux Dev with image conditioning
  - [ ] Fallback: ComfyUI native SD3 workflow
- [ ] Develop `StyleEdit3DScreenshot` custom node:
  - [ ] Input: Screenshot image, text prompt (style description)
  - [ ] Output: Style-modified image
  - [ ] Parameters:
    - [ ] Style strength (0.0-1.0)
    - [ ] Preserve structure toggle
    - [ ] Seed for reproducibility
- [ ] Test style editing quality:
  - [ ] Simple prompts: "make it wooden", "cyberpunk style", "cartoon style"
  - [ ] Complex prompts: "low-poly voxel art with bright colors"
  - [ ] Verify geometry preservation in edited images
- [ ] Create style presets:
  - [ ] Common game art styles (voxel, low-poly, cartoon, realistic)
  - [ ] Material changes (wood, metal, stone, plastic)
  - [ ] Color palette shifts (warm, cool, monochrome)

**Success Criteria:**
- Text prompt successfully modifies image style
- Original object silhouette and structure mostly preserved
- Style changes are visually clear and match prompts

**Deliverables:**
- `nodes/style_edit_image.py` - Custom ComfyUI node
- `presets/style_prompts.json` - Curated style prompt library
- Comparison images showing before/after edits

---

## Milestone 4: Hunyuan3D Integration 🏗️

**Goal:** Integrate Hunyuan3D for image-to-3D generation within ComfyUI.

### Tasks:
- [ ] Develop `Hunyuan3D_Generate` custom node:
  - [ ] Input: Styled image
  - [ ] Output: 3D model file path
  - [ ] Parameters:
    - [ ] Output format (.glb, .obj)
    - [ ] Quality settings (if available)
    - [ ] Generation seed
- [ ] Handle Hunyuan3D API or local inference:
  - [ ] If API: Authentication, rate limiting, error handling
  - [ ] If local: Model download, CUDA/CPU setup, memory management
- [ ] Implement output saving:
  - [ ] Save to `/output/3d_models/` directory
  - [ ] Filename: `{timestamp}_{prompt_hash}.glb`
  - [ ] Metadata JSON with generation parameters
- [ ] Test generation quality:
  - [ ] Simple objects (props, furniture)
  - [ ] Characters (humanoid, creature)
  - [ ] Vehicles and hard-surface objects
  - [ ] Document quality by category

**Success Criteria:**
- Styled image successfully generates 3D model via Hunyuan3D
- Output models are valid and importable in Blender/Unity/Godot
- Generation time acceptable (< 2 minutes per model)

**Deliverables:**
- `nodes/hunyuan3d_generate.py` - Custom ComfyUI node
- `docs/HUNYUAN_SETUP.md` - Installation and API setup guide
- Test outputs in `/output/3d_models/examples/`

---

## Milestone 5: End-to-End Workflow Assembly 🔗

**Goal:** Connect all nodes into a functional single-view workflow in ComfyUI.

### Tasks:
- [ ] Create base workflow JSON:
  - [ ] Node chain: Load3DModel → Render → StyleEdit → Hunyuan3D → Save
  - [ ] Default parameters optimized for game assets
  - [ ] Clear node labels and organization
- [ ] Add workflow controls:
  - [ ] Text input node for style prompt
  - [ ] File picker for input 3D model
  - [ ] Output path configuration
  - [ ] Preview nodes at each stage
- [ ] Implement batch processing:
  - [ ] Process multiple 3D models with same style
  - [ ] Queue system for sequential generation
  - [ ] Progress tracking and ETA
- [ ] Error handling and validation:
  - [ ] Check for invalid 3D file formats
  - [ ] Validate image quality before Hunyuan3D
  - [ ] Graceful failure with error messages
- [ ] Create example workflows:
  - [ ] `workflow_simple.json` - Minimal single-model conversion
  - [ ] `workflow_batch.json` - Batch style transfer
  - [ ] `workflow_variations.json` - Generate multiple style variants

**Success Criteria:**
- Complete workflow runs from 3D input to 3D output without manual intervention
- All intermediate results viewable in ComfyUI interface
- Workflow saveable and shareable as JSON

**Deliverables:**
- `workflows/single_view_style_transfer.json` - Main workflow
- `workflows/examples/` - Example workflow variations
- `docs/WORKFLOW_GUIDE.md` - User guide with screenshots

---

## Milestone 6: Multi-View Enhancement 📸

**Goal:** Upgrade to multi-view rendering for improved 3D reconstruction quality.

### Tasks:
- [ ] Develop `Render3DMultiView` node:
  - [ ] Generate 6-8 views (front, back, left, right, top, bottom, 45° angles)
  - [ ] Consistent camera distance and lighting across views
  - [ ] Output: Image batch + camera parameters
- [ ] Extend style editing for batches:
  - [ ] Apply same style edits to all views consistently
  - [ ] Preserve spatial relationships between views
  - [ ] Optional: Slightly vary style per view for richness
- [ ] Research multi-view 3D generation:
  - [ ] Check if Hunyuan3D supports multi-view input
  - [ ] Alternative: InstantMesh integration
  - [ ] Alternative: LGM (Large Gaussian Model)
- [ ] Implement multi-view to 3D node:
  - [ ] If Hunyuan3D supports: Use native multi-view mode
  - [ ] If not: Integrate alternative model (InstantMesh, etc.)
  - [ ] Merge multi-view results into single coherent mesh
- [ ] Quality comparison testing:
  - [ ] Single-view vs. multi-view output quality
  - [ ] Processing time comparison
  - [ ] Document when multi-view is worth the extra cost

**Success Criteria:**
- Multi-view rendering produces consistent, well-aligned images
- 3D reconstruction quality noticeably better than single-view
- Workflow allows user to choose single or multi-view mode

**Deliverables:**
- `nodes/render_3d_multiview.py` - Multi-view rendering node
- `nodes/multiview_to_3d.py` - Multi-view reconstruction node
- `workflows/multi_view_style_transfer.json` - Multi-view workflow
- Quality comparison report (`docs/SINGLE_VS_MULTI_VIEW.md`)

---

## Milestone 7: Polish & Optimization ✨

**Goal:** Refine UI/UX, optimize performance, and add quality-of-life features.

### Tasks:
- [ ] Performance optimization:
  - [ ] Cache rendered screenshots to avoid re-rendering
  - [ ] Batch API calls when possible
  - [ ] GPU memory management for large models
  - [ ] Parallel processing for batch workflows
- [ ] UI improvements:
  - [ ] Custom ComfyUI interface for 3D preview (if possible)
  - [ ] Better node icons and descriptions
  - [ ] Grouped nodes for cleaner workflows
  - [ ] Tooltips with parameter explanations
- [ ] Quality-of-life features:
  - [ ] Preset style library with thumbnails
  - [ ] Compare mode: Side-by-side original vs. styled model
  - [ ] Undo/variation system: Generate multiple versions from same input
  - [ ] Export metadata: Track generation parameters for each output
- [ ] Documentation and examples:
  - [ ] Video tutorial showing complete workflow
  - [ ] Gallery of example transformations
  - [ ] Troubleshooting guide (common errors and fixes)
  - [ ] Performance tips for large batches
- [ ] Testing and validation:
  - [ ] Test with 20+ diverse 3D models
  - [ ] Verify compatibility with Unity, Godot, Blender
  - [ ] Stress test batch processing (100+ models)
  - [ ] Cross-platform testing (Windows, Mac, Linux)

**Success Criteria:**
- Workflow is polished and user-friendly
- Performance is optimized for real-world use
- Documentation is comprehensive and clear

**Deliverables:**
- Optimized node code with performance improvements
- Complete documentation suite
- Example gallery with 20+ transformations
- Video tutorial (5-10 minutes)

---

## Milestone 8: Advanced Features (Optional) 🚀

**Goal:** Add advanced features for power users and specific use cases.

### Tasks:
- [ ] Texture-only editing mode:
  - [ ] Extract UV maps from input model
  - [ ] Edit textures without changing geometry
  - [ ] Reapply edited textures to original mesh
- [ ] ControlNet depth guidance:
  - [ ] Extract depth map from 3D model
  - [ ] Use depth ControlNet during style editing
  - [ ] Better geometry preservation
- [ ] Animation preservation:
  - [ ] Detect if input model has rigging/animations
  - [ ] Attempt to transfer rig to new geometry
  - [ ] Or: Only edit textures for animated models
- [ ] LOD generation:
  - [ ] Automatically generate multiple LOD levels
  - [ ] Simplify meshes for mobile/distant views
  - [ ] Export LOD bundles
- [ ] Material extraction:
  - [ ] Parse PBR materials from input model
  - [ ] Generate matching PBR maps for output
  - [ ] Albedo, normal, roughness, metallic maps
- [ ] Integration with 3D software:
  - [ ] Blender add-on for direct import/export
  - [ ] Unity editor plugin
  - [ ] Godot plugin
- [ ] API and CLI:
  - [ ] REST API for programmatic access
  - [ ] Command-line interface for scripting
  - [ ] Python SDK for integration

**Success Criteria:**
- Advanced features work reliably for their intended use cases
- Features are optional and don't complicate basic workflow

**Deliverables:**
- Advanced feature nodes and workflows
- Feature-specific documentation
- Integration plugins (if developed)

---

## Change Log

### 2026-01-30
- Initial milestone plan created
- 8 milestones defined from foundation to advanced features
- Prioritized single-view approach first, multi-view in Milestone 6
- Committed to Hunyuan3D as primary image-to-3D model
