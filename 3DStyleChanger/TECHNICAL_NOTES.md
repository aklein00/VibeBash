# Technical Notes & Design Decisions

Key technical considerations, research findings, and design decisions for 3D Style Changer development.

## Design Decisions

### Why Single-View First?

**Decision:** Start with single screenshot approach, add multi-view later (Milestone 6)

**Reasoning:**
- Simpler implementation = faster iteration
- Validates core concept with minimal complexity
- User understands limitations and prefers speed to perfection
- Multi-view adds 2-4x processing time without guaranteed quality improvement
- Can assess when multi-view is worth the cost after testing single-view

**Trade-offs Accepted:**
- Lower quality 3D reconstruction (unseen surfaces will be hallucinated)
- Less accurate geometry on hidden sides
- May need manual cleanup for complex objects

**When to reconsider:** If single-view quality is unacceptable for simple objects, accelerate multi-view development.

---

### Why Hunyuan3D Over Alternatives?

**Decision:** Use Hunyuan3D as primary image-to-3D model

**Alternatives Considered:**
- **TripoSR**: Rejected - "quality is too low" (user feedback)
- **InstantMesh**: Requires multi-view input (Milestone 6)
- **LGM**: Requires multi-view input
- **Shap-E / Point-E**: Lower quality than image-based methods
- **CSM (Common Sense Machines)**: May be worth exploring if Hunyuan3D insufficient

**Hunyuan3D Advantages:**
- Better single-view quality than TripoSR
- Open-source and free to use
- Reasonable generation speed
- Active development and community

**Risks:**
- If Hunyuan3D doesn't support multi-view, need InstantMesh integration for Milestone 6
- Potential API changes or model updates breaking compatibility

---

### Why ComfyUI?

**Decision:** Build as ComfyUI custom nodes rather than standalone app

**Reasoning:**
- Visual workflow = easy to understand and modify
- Existing infrastructure for image processing
- Large user base familiar with ComfyUI
- Easy to integrate with other AI workflows
- Node-based = modular and extensible

**Alternatives Considered:**
- **Standalone Python script**: Less user-friendly, harder to visualize
- **Blender add-on**: Limited to Blender users, steeper learning curve
- **Web app**: Requires hosting, more complex infrastructure

---

### 3D Rendering Backend

**Decision:** TBD in Milestone 2 - evaluate options

**Options:**

#### Option A: PyTorch3D
**Pros:**
- Native Python
- Good integration with AI workflows
- GPU-accelerated rendering
- Supports differentiable rendering (future use)

**Cons:**
- Heavyweight dependency
- Steeper learning curve
- May be overkill for simple screenshots

#### Option B: Three.js (via Node.js subprocess)
**Pros:**
- Mature 3D rendering library
- Excellent file format support
- Easy to control camera and lighting
- Fast rendering

**Cons:**
- Requires Node.js installation
- Inter-process communication overhead
- More moving parts

#### Option C: Blender Headless
**Pros:**
- Industry-standard rendering quality
- Excellent 3D file support
- Powerful material and lighting systems
- Users may already have it installed

**Cons:**
- Blender dependency (large install)
- Slower startup time
- Python API can be complex

**Recommendation:** Start with **PyTorch3D** for tighter Python integration. If performance or complexity issues arise, switch to Three.js.

---

## Image Editing Strategy

### Primary: Recraft Banana API

**Pros:**
- Purpose-built for style transfer while preserving structure
- Fast API response times
- Good quality results

**Cons:**
- Requires API key and internet connection
- Potential cost per API call
- Dependency on external service

**Fallback Plan:** If Banana API unavailable or too expensive, use local Flux Dev or SD3 with ControlNet.

### Alternative: Flux Dev with Image Conditioning

**Pros:**
- Can run locally (no API costs)
- Good style control with prompts
- Fast inference on modern GPUs

**Cons:**
- Requires local GPU (VRAM requirements)
- May not preserve structure as well as Banana
- Need to tune conditioning strength

### Alternative: SD3 + IP-Adapter + ControlNet

**Pros:**
- Excellent structure preservation with ControlNet
- IP-Adapter maintains visual similarity
- Full local control

**Cons:**
- More complex node setup in ComfyUI
- Slower than API solutions
- Requires multiple models loaded in memory

---

## File Format Considerations

### Input Formats

**Must Support:**
- **OBJ** - Most common, simple text-based format
- **GLB** - glTF binary, standard for game engines
- **FBX** - Common in Unity/Unreal workflows

**Nice to Have:**
- **STL** - 3D printing community
- **DAE** (Collada) - Some game engines
- **BLEND** - Blender native

**Implementation Notes:**
- Use `trimesh` library for loading (supports OBJ, GLB, STL, OFF, PLY)
- For FBX, may need `pyfbx` or Blender Python API
- Prioritize OBJ and GLB for Milestone 2

### Output Formats

**Preferred: GLB**
- Single file (mesh + textures)
- Widely supported (Unity, Godot, Blender, web)
- Smaller file size than FBX

**Also Support:**
- **OBJ** + MTL - For simple compatibility
- **FBX** - If Unity/Unreal users request it

**Not Recommended:**
- **STL** - No texture support
- **PLY** - Less common in game engines

---

## Performance Optimization Strategies

### Caching

**What to Cache:**
- Rendered screenshots (Stage 2) - Avoid re-rendering same model+angle
- Style-edited images (Stage 3) - Avoid re-processing same prompt
- Generated 3D models (Stage 4) - Avoid regenerating if parameters unchanged

**Cache Key Format:**
```python
# Render cache
f"{model_hash}_{camera_angle}_{resolution}_{lighting_preset}.png"

# Style edit cache
f"{image_hash}_{prompt_hash}_{style_strength}.png"

# 3D generation cache
f"{styled_image_hash}_{model_name}_{seed}.glb"
```

**Cache Location:** `~/.cache/3d_style_changer/` or `ComfyUI/temp/3d_style_changer/`

**Cache Invalidation:** Time-based (7 days) or manual clear command

### Batch Processing

**Optimization:** Process multiple models in parallel when GPU allows

**Strategy:**
1. Load all 3D models into memory (if RAM permits)
2. Render all screenshots in batch
3. Send all images to style editor (batch API call if supported)
4. Queue Hunyuan3D generations (respect rate limits)

**Memory Management:**
- Monitor GPU VRAM usage
- Offload models from GPU after rendering
- Use disk swapping for large batches

### GPU Utilization

**Issue:** Hunyuan3D may saturate GPU, leaving other stages idle

**Solution:**
- Run rendering on CPU if GPU fully utilized
- Overlap CPU and GPU tasks where possible
- Consider dual-GPU setups for power users

---

## Error Handling Philosophy

### Fail Gracefully

**Principle:** Workflow should never crash without saving partial results

**Implementation:**
- Try/catch around each node's process() method
- Save intermediate results before risky operations
- Log errors to both console and file
- Return error message to ComfyUI UI

### Batch Processing Resilience

**Principle:** One failed model shouldn't stop entire batch

**Implementation:**
```python
for model in batch:
    try:
        result = process_model(model)
        results.append(result)
    except Exception as e:
        log_error(model, e)
        results.append({"status": "failed", "error": str(e)})
        continue  # Process next model

# Generate summary report
successful = [r for r in results if r["status"] == "success"]
failed = [r for r in results if r["status"] == "failed"]
print(f"Batch complete: {len(successful)}/{len(batch)} succeeded")
```

### User-Friendly Error Messages

**Bad:**
```
Error: KeyError 'vertices' at line 347 in load_3d_model.py
```

**Good:**
```
Failed to load 3D model: The file appears to be corrupt or in an unsupported format.
Supported formats: OBJ, GLB, FBX
Tip: Try opening the file in Blender to verify it's valid.
```

---

## Quality Assessment

### How to Measure Success

**Metrics to Track:**
- **Generation success rate**: % of models that complete without errors
- **Visual similarity**: How well does output match style prompt? (subjective, user testing)
- **Geometry preservation**: How much does output resemble input shape? (compare bounding boxes, silhouette overlap)
- **Processing time**: Seconds per model
- **User satisfaction**: Would users use this in their workflow?

### Testing Protocol

**Milestone 2 Testing:**
- 10 simple objects (cube, sphere, cylinder, teapot, etc.)
- Verify clean screenshots from all common angles
- Check for rendering artifacts or missing geometry

**Milestone 3 Testing:**
- 5 style prompts × 10 test objects = 50 style edits
- Styles: wooden, cyberpunk, cartoon, low-poly, stone
- Score each on 1-5 scale for quality and structure preservation

**Milestone 4 Testing:**
- 20 diverse styled images → 3D models
- Categories: Characters, props, vehicles, environment pieces
- Measure success rate and identify failure patterns

**Milestone 5 End-to-End Testing:**
- 50 real game assets (sourced from open asset packs)
- Full workflow: load → render → style → generate → save
- Document bugs, edge cases, and quality issues

**Milestone 6 Multi-View Testing:**
- A/B test: Single-view vs. Multi-view on same 20 models
- Blind user study: Which outputs look better?
- Time vs. quality trade-off analysis

---

## Known Limitations & Workarounds

### Limitation 1: Single-View Blind Spots

**Problem:** Back of object is hallucinated by Hunyuan3D

**Workarounds:**
- Milestone 6: Multi-view rendering
- User education: Best for objects with simple backs (characters facing forward, front-facing props)
- Manual touchup: User edits back in Blender after generation

### Limitation 2: Complex Topology

**Problem:** AI-generated meshes have poor topology (ngons, non-manifold geometry)

**Workarounds:**
- Post-processing: Auto-remesh output (quadify, decimate)
- User expectation: Communicate that this is "sketch quality" not "production ready"
- Milestone 8: Add automatic retopology step

### Limitation 3: Animation Loss

**Problem:** Input model's rig and animations are discarded

**Workarounds:**
- Texture-only mode (Milestone 8) preserves geometry and rig
- Document limitation clearly
- Future: Research rig transfer algorithms (very complex)

### Limitation 4: Material Loss

**Problem:** PBR materials (metallic, roughness maps) not preserved

**Workarounds:**
- Generate basic materials based on style prompt
- Milestone 8: Extract and regenerate PBR maps
- User touchup: Re-apply materials in game engine

### Limitation 5: Scale and Units

**Problem:** Output model may have incorrect scale

**Workarounds:**
- Store original bounding box dimensions
- Scale output to match input size
- Add scale parameter to Save3DModel node

---

## Security & Privacy Considerations

### API Keys

**Risk:** Hardcoded API keys in workflow JSON

**Mitigation:**
- Store keys in environment variables or secure config file
- Never commit keys to git
- Use ComfyUI's built-in credential manager if available

### User Data

**Risk:** User 3D models sent to external APIs (Recraft, Hunyuan3D if using API)

**Mitigation:**
- Clearly document what data is sent externally
- Offer local-only mode (use Flux/SD3 instead of Recraft)
- Don't log or cache user models without permission

### Model Licensing

**Risk:** Generated 3D models may have licensing restrictions from Hunyuan3D or Recraft

**Mitigation:**
- Review Hunyuan3D license terms
- Document any commercial use restrictions
- Provide disclaimer in README

---

## Development Tools & Environment

### Recommended Setup

**Hardware:**
- GPU: NVIDIA RTX 3060 or better (12GB+ VRAM)
- RAM: 16GB minimum, 32GB recommended
- Storage: 50GB free (for models and cache)

**Software:**
- Python 3.10 or 3.11
- ComfyUI (latest stable)
- CUDA 11.8 or 12.1
- Git for version control

**Libraries:**
- `torch` - PyTorch for neural networks
- `trimesh` - 3D model loading
- `pytorch3d` - 3D rendering (or alternative)
- `pillow` - Image processing
- `requests` - API calls
- `numpy` - Numerical operations

### Development Workflow

1. **Prototype in Jupyter Notebook** - Test individual components
2. **Convert to ComfyUI Nodes** - Package as custom nodes
3. **Test in ComfyUI** - Validate in full workflow
4. **Iterate** - Refine based on test results

### Debugging Tips

- Use ComfyUI's built-in node preview to inspect intermediate results
- Save debug images to disk for comparison
- Log timing information to identify bottlenecks
- Use `pdb` or `ipdb` for interactive debugging

---

## Future Research Directions

### Better 3D Generation Models

**Watch for:**
- Improved Hunyuan3D versions
- New image-to-3D models (research papers, Hugging Face)
- Text-to-3D models that accept reference images

### Advanced Style Transfer

**Explore:**
- ControlNet for 3D (depth + normal guidance)
- 3D-aware diffusion models
- Style transfer that modifies geometry, not just texture

### Automation

**Ideas:**
- Auto-detect optimal camera angle for rendering
- Auto-tune style strength based on input complexity
- Auto-generate multiple style variations
- Batch processing with intelligent queuing

---

## Open Questions (To Research in Milestone 1)

1. **Does Hunyuan3D have a multi-view mode?** If yes, simplifies Milestone 6.
2. **Can Hunyuan3D run locally or only via API?** Affects cost and privacy.
3. **What is Recraft Banana's pricing and rate limits?** May need fallback sooner than planned.
4. **How does Hunyuan3D handle transparent backgrounds?** Important for rendering setup.
5. **Can ComfyUI nodes display 3D previews?** Would improve UX significantly.

---

## References & Resources

### Hunyuan3D
- Repository: [github.com/Tencent/Hunyuan3D-1](https://github.com/Tencent/Hunyuan3D-1)
- Paper: *(link TBD after research)*

### ComfyUI
- Official Repo: [github.com/comfyanonymous/ComfyUI](https://github.com/comfyanonymous/ComfyUI)
- Custom Node Dev Guide: [comfyanonymous.github.io/ComfyUI_examples/](https://comfyanonymous.github.io/ComfyUI_examples/)

### 3D Libraries
- Trimesh: [trimsh.org](https://trimsh.org)
- PyTorch3D: [pytorch3d.org](https://pytorch3d.org)
- Three.js: [threejs.org](https://threejs.org)

### Image-to-3D Models
- TripoSR: [stability.ai/triposr](https://stability.ai/triposr)
- InstantMesh: [github.com/TencentARC/InstantMesh](https://github.com/TencentARC/InstantMesh)
- CSM: [csm.ai](https://csm.ai)

---

## Change Log

### 2026-01-30
- Initial technical notes document created
- Design decisions documented
- Open questions listed for Milestone 1 research
