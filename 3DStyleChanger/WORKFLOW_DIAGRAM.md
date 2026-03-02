# 3D Style Changer - Workflow Architecture

Visual representation of the data flow and processing stages.

## Single-View Workflow (Milestones 1-5)

```
┌─────────────────────────────────────────────────────────────────┐
│                      USER INPUTS                                │
│  • 3D Model File (.obj, .glb, .fbx)                            │
│  • Style Text Prompt ("make it cyberpunk metal")               │
│  • Render Settings (camera angle, lighting)                    │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 1: Load 3D Model                                          │
│  Node: Load3DModel                                              │
│  ├─ Parse file format (OBJ/GLB/FBX)                            │
│  ├─ Extract mesh data (vertices, faces, normals)               │
│  ├─ Extract textures (if present)                              │
│  └─ Output: 3D model data structure                            │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 2: Render Screenshot                                      │
│  Node: Render3DScreenshot                                       │
│  ├─ Position camera (front view, centered)                     │
│  ├─ Set up lighting (3-point default)                          │
│  ├─ Render to image (1024x1024 PNG)                            │
│  └─ Output: Screenshot image                                    │
│                                                                  │
│  Parameters:                                                     │
│  • Camera angle: Front (default), Side, Top, Custom            │
│  • Resolution: 512 / 1024 / 2048                                │
│  • Background: White / Transparent / Gradient                   │
│  • Lighting: Default / Bright / Studio / Outdoor               │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 3: AI Style Editing                                       │
│  Node: StyleEdit3DScreenshot                                    │
│  ├─ Load base image (screenshot from Stage 2)                  │
│  ├─ Apply text prompt via AI image editor:                     │
│  │   • Option A: Recraft Banana API                            │
│  │   • Option B: Flux Dev with image conditioning              │
│  │   • Option C: SD3 with IP-Adapter                           │
│  ├─ Preserve structure (keep silhouette and geometry cues)     │
│  └─ Output: Style-modified image                                │
│                                                                  │
│  Parameters:                                                     │
│  • Text prompt: User-defined style description                 │
│  • Style strength: 0.3 (subtle) to 1.0 (dramatic)              │
│  • Structure preservation: Low / Medium / High                 │
│  • Seed: For reproducible results                               │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 4: Image-to-3D Generation                                 │
│  Node: Hunyuan3D_Generate                                       │
│  ├─ Send styled image to Hunyuan3D                             │
│  ├─ Generate 3D mesh from single view                          │
│  ├─ Export to file format (.glb preferred)                     │
│  └─ Output: 3D model file path                                  │
│                                                                  │
│  Parameters:                                                     │
│  • Output format: GLB / OBJ / FBX                               │
│  • Quality: Draft / Standard / High                             │
│  • Seed: For reproducible generation                            │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 5: Save Output                                            │
│  Node: Save3DModel                                              │
│  ├─ Save to output directory                                   │
│  ├─ Filename: {timestamp}_{prompt_hash}.glb                    │
│  ├─ Generate metadata JSON:                                    │
│  │   • Original model name                                     │
│  │   • Style prompt used                                       │
│  │   • Generation parameters                                   │
│  │   • Timestamps                                               │
│  └─ Output: File path + metadata                                │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FINAL OUTPUT                                 │
│  • Styled 3D Model (.glb file)                                  │
│  • Metadata JSON                                                │
│  • Preview image (optional)                                     │
│  • Location: /output/3d_models/                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Multi-View Workflow (Milestone 6)

Enhances Stage 2 and Stage 4 for improved quality.

```
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 1: Load 3D Model                                          │
│  (Same as single-view)                                          │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 2: Render Multi-View Screenshots                          │
│  Node: Render3DMultiView                                        │
│  ├─ Generate 6-8 camera angles:                                │
│  │   • Front (0°)                                               │
│  │   • Back (180°)                                              │
│  │   • Left (90°)                                               │
│  │   • Right (270°)                                             │
│  │   • Top (90° elevation)                                      │
│  │   • Bottom (-90° elevation)                                  │
│  │   • Optional: 45° angles for more detail                    │
│  ├─ Consistent lighting across all views                       │
│  ├─ Same camera distance and framing                           │
│  └─ Output: Image batch (6-8 images) + camera metadata         │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 3: AI Style Editing (Batch)                               │
│  Node: StyleEdit3DScreenshot (Batch Mode)                       │
│  ├─ Apply same style to all views                              │
│  ├─ Maintain consistency across images                         │
│  ├─ Optional: Slight variation per view for richness           │
│  └─ Output: Batch of styled images                              │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 4: Multi-View to 3D Generation                            │
│  Node: MultiViewTo3D                                            │
│  ├─ Option A: Hunyuan3D multi-view mode (if supported)         │
│  ├─ Option B: InstantMesh integration                          │
│  ├─ Option C: LGM (Large Gaussian Model)                       │
│  ├─ Merge views into coherent 3D mesh                          │
│  └─ Output: Higher-quality 3D model                             │
│                                                                  │
│  Expected improvements vs. single-view:                         │
│  • Better geometry on hidden surfaces                           │
│  • Fewer hallucinated details                                   │
│  • More accurate proportions                                    │
│  • Smoother mesh topology                                       │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 5: Save Output                                            │
│  (Same as single-view)                                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Batch Processing Workflow

Process multiple 3D models with the same style in one run.

```
┌─────────────────────────────────────────────────────────────────┐
│ USER INPUTS                                                      │
│  • Directory of 3D models                                       │
│  • Single style prompt (applied to all)                         │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
                        ┌──────────┐
                        │ For each │
                        │  model   │
                        └─────┬────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
              ┌──────────┐        ┌──────────┐
              │ Model A  │        │ Model B  │  ...
              └────┬─────┘        └────┬─────┘
                   │                   │
                   ▼                   ▼
           Single-View Workflow   Single-View Workflow
                   │                   │
                   ▼                   ▼
              ┌──────────┐        ┌──────────┐
              │ Output A │        │ Output B │  ...
              └──────────┘        └──────────┘
                   │                   │
                   └─────────┬─────────┘
                             │
                             ▼
                   ┌──────────────────┐
                   │ Batch Complete   │
                   │ • Summary report │
                   │ • All outputs    │
                   └──────────────────┘
```

---

## Data Flow Summary

| Stage | Input | Process | Output |
|-------|-------|---------|--------|
| **1. Load** | 3D file path | Parse mesh data | 3D model object |
| **2. Render** | 3D model object + camera params | Render screenshot | PNG image |
| **3. Style** | Screenshot + text prompt | AI image editing | Styled image |
| **4. Generate** | Styled image | Image-to-3D (Hunyuan3D) | 3D model file |
| **5. Save** | 3D model file | Write to disk + metadata | File path |

---

## Node Communication Format

Nodes communicate via ComfyUI's standard output/input system:

```python
# Example: Render3DScreenshot node output
{
  "image": PIL.Image or torch.Tensor,
  "metadata": {
    "camera_angle": "front",
    "resolution": [1024, 1024],
    "model_name": "input_model.obj"
  }
}

# Example: Hunyuan3D_Generate node output
{
  "file_path": "/output/3d_models/20260130_abc123.glb",
  "metadata": {
    "prompt": "cyberpunk metal texture",
    "generation_time": 87.3,  # seconds
    "model": "hunyuan3d-v1.0"
  }
}
```

---

## Performance Characteristics

| Stage | Time (Estimated) | Bottleneck |
|-------|------------------|------------|
| Load 3D Model | < 1 sec | File I/O |
| Render Screenshot | 1-5 sec | GPU rendering |
| AI Style Edit | 5-15 sec | API latency or GPU inference |
| Hunyuan3D Generate | 30-120 sec | GPU inference (large model) |
| Save Output | < 1 sec | File I/O |
| **Total (Single)** | **40-140 sec** | Primarily Hunyuan3D |
| **Total (Multi-view)** | **90-300 sec** | Multiple renders + longer 3D gen |

Optimization opportunities:
- Cache rendered screenshots to avoid re-rendering
- Batch API calls when processing multiple models
- Use GPU efficiently (offload CPU tasks)
- Parallel processing for batch workflows

---

## Error Handling Flow

```
[User Input]
    ↓
[Validation] ──✗──→ [Error: Invalid file format]
    ↓ ✓
[Load 3D] ──✗──→ [Error: Corrupt file / unsupported features]
    ↓ ✓
[Render] ──✗──→ [Error: Rendering failed / out of memory]
    ↓ ✓
[Style Edit] ──✗──→ [Error: API failure / prompt rejected]
    ↓ ✓
[Hunyuan3D] ──✗──→ [Error: Generation failed / timeout]
    ↓ ✓
[Save] ──✗──→ [Error: Disk full / permission denied]
    ↓ ✓
[Success Output]
```

Each node should:
- Log errors with context
- Provide user-friendly error messages
- Allow workflow to continue if possible (skip failed items in batch)
- Save partial results before failure

---

## Future Workflow Extensions

### Texture-Only Mode (Milestone 8)
```
Load 3D → Extract UV Map → Edit Texture → Reapply → Save
(No image-to-3D generation - preserves geometry perfectly)
```

### ControlNet Depth Guidance (Milestone 8)
```
Load 3D → Render (RGB + Depth) → Style Edit with Depth ControlNet → Hunyuan3D
(Better geometry preservation during style editing)
```

### Animation Preservation (Milestone 8)
```
Load Rigged 3D → Render + Extract Rig → Style Edit → Hunyuan3D → Transfer Rig
(Attempt to preserve animations - complex and experimental)
```
