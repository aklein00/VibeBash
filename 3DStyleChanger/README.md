# 3D Style Changer

**AI-powered 3D model style transfer workflow for ComfyUI**

Transform 3D game assets with text prompts. Input a 3D model, describe the style change you want, and generate a new stylized 3D model automatically.

## Overview

3D Style Changer is a ComfyUI workflow that bridges 3D modeling and AI image generation to enable rapid style iteration for game assets. Perfect for indie developers who need quick visual variations without manual remodeling.

### What It Does

```
Input: 3D Model (.obj, .glb, .fbx)
       + Text Prompt ("make it cyberpunk", "wooden texture", "low-poly voxel style")
       ↓
Output: New 3D Model with applied style
```

### How It Works

1. **Load**: Import your 3D model into ComfyUI
2. **Render**: Generate a screenshot of the model
3. **Style**: AI image editor applies your text prompt to the screenshot
4. **Generate**: Hunyuan3D converts the styled image back to a 3D model
5. **Export**: Save the new 3D model for use in your game engine

## Project Status

**Current Milestone:** 🏗️ Milestone 1 - Foundation & Research (In Progress)

See [MILESTONES.md](MILESTONES.md) for the complete development roadmap.

## Key Features (Planned)

- ✅ Simple single-view workflow (Milestone 1-5)
- 🔄 Multi-view rendering for better quality (Milestone 6)
- 🎨 Style preset library for common game art styles
- 📦 Batch processing for multiple models
- 🚀 Optimized for fast iteration and game development

## Technology Stack

- **ComfyUI** - Visual workflow engine
- **Hunyuan3D** - Image-to-3D generation (chosen for quality over TripoSR)
- **Recraft Banana / Flux Dev** - AI image style editing
- **PyTorch3D / Three.js** - 3D rendering backend
- **Python** - Custom node development

## Design Philosophy

This tool is built with pragmatic constraints in mind:

- **Simple over perfect**: First pass doesn't need AAA quality
- **Speed over detail**: Fast iteration is more valuable than high poly counts
- **Game-focused**: Optimized for game assets, not film/product viz
- **AI-aware**: Embraces current AI limitations rather than fighting them

We know AI can't replace 3D artists—but it can help iterate faster.

## Use Cases

Perfect for:
- 🎮 **Indie game developers**: Rapid prototyping of asset variations
- 🎨 **Concept artists**: Exploring style directions quickly
- 🔄 **Asset iteration**: Testing different art styles before committing
- 📦 **Placeholder art**: Generating temp assets for game prototypes

Not suitable for:
- ❌ AAA production-ready assets
- ❌ Animation-rigged characters
- ❌ Complex CAD models or engineering assets
- ❌ Photo-realistic human faces

## Installation (When Available)

```bash
# Clone into ComfyUI custom nodes directory
cd ComfyUI/custom_nodes/
git clone https://github.com/yourusername/3DStyleChanger.git

# Install dependencies
cd 3DStyleChanger
pip install -r requirements.txt

# Download Hunyuan3D model (instructions in docs/HUNYUAN_SETUP.md)
python scripts/download_models.py

# Restart ComfyUI
```

## Quick Start (When Available)

1. Load the workflow: `workflows/single_view_style_transfer.json`
2. Click the `Load3DModel` node and select your 3D file
3. Enter your style prompt in the `StyleEdit3DScreenshot` node
4. Click "Queue Prompt" and wait for generation
5. Find your new 3D model in `output/3d_models/`

## Documentation

- [MILESTONES.md](MILESTONES.md) - Development roadmap and progress tracking
- [TECH_RESEARCH.md](TECH_RESEARCH.md) - Technical research and design decisions *(coming soon)*
- [WORKFLOW_GUIDE.md](docs/WORKFLOW_GUIDE.md) - Step-by-step usage guide *(coming soon)*
- [HUNYUAN_SETUP.md](docs/HUNYUAN_SETUP.md) - Hunyuan3D installation guide *(coming soon)*

## Project Structure

```
3DStyleChanger/
├── nodes/                      # Custom ComfyUI nodes
│   ├── load_3d_model.py       # 3D file loader
│   ├── render_3d_screenshot.py # Screenshot renderer
│   ├── style_edit_image.py    # AI style editor
│   └── hunyuan3d_generate.py  # Image-to-3D generator
├── workflows/                  # ComfyUI workflow JSONs
│   ├── single_view_style_transfer.json
│   └── multi_view_style_transfer.json
├── presets/                    # Style prompt presets
│   └── style_prompts.json
├── docs/                       # Documentation
├── examples/                   # Example inputs and outputs
├── scripts/                    # Utility scripts
├── requirements.txt            # Python dependencies
├── README.md                   # This file
└── MILESTONES.md              # Development roadmap
```

## Development Status

### ✅ Completed
- [x] Project planning and milestone definition

### 🔄 In Progress
- [ ] Milestone 1: Foundation & Research

### 📋 Upcoming
- [ ] Milestone 2: 3D Model Loading & Rendering
- [ ] Milestone 3: Image Style Editing Integration
- [ ] Milestone 4: Hunyuan3D Integration
- [ ] Milestone 5: End-to-End Workflow Assembly
- [ ] Milestone 6: Multi-View Enhancement
- [ ] Milestone 7: Polish & Optimization
- [ ] Milestone 8: Advanced Features (Optional)

## Contributing

This is currently a personal project. Once Milestone 5 is complete, contributions will be welcome!

## Known Limitations

- **Single-view reconstruction**: Initial version only captures one angle, so unseen surfaces may be incorrect
- **Quality ceiling**: AI-generated 3D models are approximate, not production-perfect
- **No animation preservation**: Rigging and animations are lost in conversion
- **Material limitations**: PBR materials may not transfer accurately
- **Processing time**: 1-2 minutes per model (depending on hardware/API)

These are inherent to current AI technology, not bugs. Multi-view rendering (Milestone 6) will improve quality significantly.

## Future Vision

Once core workflow is stable:
- Texture-only editing mode (preserve geometry perfectly)
- Integration with Blender, Unity, Godot
- Material/PBR map generation
- Animation rig preservation
- Real-time style preview

## License

*To be determined*

## Acknowledgments

- **Hunyuan3D Team** - For excellent image-to-3D model
- **ComfyUI** - For flexible visual workflow framework
- **Recraft** - For Banana image editing API
- Inspired by the needs of indie game developers who want to move fast

---

**Status:** 🏗️ **In Development** - Not yet functional

Follow [MILESTONES.md](MILESTONES.md) for progress updates.
