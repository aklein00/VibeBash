# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## BMad Game Dev Studio

BMad Method v6 is installed in this workspace (`_bmad/` folder) with three modules: Core, BMM (v6.0.0-Beta.7), and GDS (v0.1.5). All games are **HTML5 for mobile** (Venus/run.game platform) — not Unity, Unreal, or Godot.

**Start here:** `/project:bmad-help` — shows available workflows and recommends next steps based on project state.

**Key GDS commands:**

| Phase | Command | What it does |
|-------|---------|-------------|
| Quick Start | `/project:bmad-gds-quick-dev` | Solo dev rapid prototyping |
| Quick Start | `/project:bmad-gds-quick-spec` | Fast tech spec + stories |
| Pre-production | `/project:bmad-gds-brainstorm-game` | Brainstorm game concepts |
| Pre-production | `/project:bmad-gds-game-brief` | Create game vision/brief |
| Design | `/project:bmad-gds-gdd` | Full Game Design Document |
| Design | `/project:bmad-gds-narrative` | Story & world-building |
| Technical | `/project:bmad-gds-game-architecture` | Technical architecture |
| Production | `/project:bmad-gds-sprint-planning` | Plan sprints from GDD |
| Production | `/project:bmad-gds-create-story` | Prepare individual stories |
| Production | `/project:bmad-gds-dev-story` | Implement a story |
| Production | `/project:bmad-gds-code-review` | Code review |

**Agent commands** (load specialized personas): `/project:bmad-agent-gds-game-designer` (Samus Shepard), `/project:bmad-agent-gds-game-architect` (Cloud Dragonborn), `/project:bmad-agent-gds-game-dev` (Link Freeman), `/project:bmad-agent-gds-game-solo-dev` (Indie), `/project:bmad-agent-gds-game-qa` (GLaDOS), `/project:bmad-agent-gds-game-scrum-master` (Max).

**Other:** `/project:bmad-party-mode` (multi-agent discussion), `/project:bmad-brainstorming` (creative ideation).

**Output directories:** `bmad-output/planning-artifacts/`, `bmad-output/implementation-artifacts/`, `docs/`.

Full guide: `Brainstorming/BMAD_GUIDE.md`. All 72 commands (including BMM module) are available — see `.claude/commands/` for the full list.

## Game Manager

`GameManager/` is the centralized dashboard for tracking all game and app projects in the Side folder.

**View the dashboard:**
```bash
cd GameManager && python3 -m http.server 8080
# Open http://localhost:8080
```

**Update project status:** Edit `GameManager/catalog.json` directly. Key fields: `status`, `completion`, `completedMilestones`, `currentMilestone`, `notes`, `lastReviewed`.

**Check for drift:** Run `python3 GameManager/scanner.py` to compare the catalog against actual project files (milestones, GDD, git status, etc.).

**Tracked projects:** Dirtbagz, Ultraviolet, RetroStrikers, SugarRushDelivery, CoralQuest, Gateaux, ForestOfFools, BizzyDad, HelloWhirled, Agincort.

See `GameManager/README.md` for full schema, future milestones, and automation plans.

## Repository Overview

VibeBash is a multi-project workspace containing:

1. **GameManager** - Dashboard and catalog for tracking all Side folder projects
2. **ImageGenerator** - Python scripts for batch generating images (prefer `generate_images_google.py` for Google Imagen)
3. **Interface_Royale** - Design documentation system for F2P mobile game UI/UX templates
4. **MayaScripts** - Maya automation scripts collection

**Note**: For creating new Venus (run.game) games, use the `/new-venus-game` skill. Venus templates are stored separately at `/Users/arthurklein/Documents/Work/SeriesAI/Venus/venus_templates` and include Phaser (2D), React, Three.js (3D), and TypeScript (minimal) options. See the global `~/.claude/CLAUDE.md` for full Venus publishing instructions.

## Image Generation

**USER PREFERENCE: Use Google Imagen for all image generation unless explicitly stated otherwise.**

### Global Skill: /generate-image

A **global Claude Code skill** available in all projects for quick image generation.

**Usage:**
```bash
/generate-image "prompt" [width] [height] [output-path]
```

**Examples:**
```bash
# Quick test
/generate-image "a red apple on wooden table"

# Specific dimensions
/generate-image "sunset mountains" 1920 1080

# Custom output path
/generate-image "logo design" 512 512 ./assets/logo.png
```

**Backends supported:**
- Google Imagen (recommended - requires Google Cloud API key)
- RunComfy (requires RunComfy account)
- OpenAI DALL-E 3 (requires OpenAI API key)

**Configuration:** Edit `~/.claude/skills/generate-image/generate.py` line 13 to set backend.

See `~/.claude/skills/generate-image/README.md` for full setup instructions.

### Batch Image Generator (ImageGenerator/)

For bulk image generation from JSON prompts with opt-in cropping.

**USER PREFERENCE: Use Google Imagen version unless explicitly stated otherwise.**

**Running:**
```bash
cd ImageGenerator
python3 generate_images_google.py  # Google Imagen version (PREFERRED)
# or
python3 generate_images.py  # DALL-E 3 version (use only if specifically requested)
```

**Prerequisites:**
- Python 3 with appropriate SDK (`openai`, `google-cloud-aiplatform`, or `requests`)
- API key configured

### How It Works

1. Reads prompts from `image_prompts.json` (array of objects with `id`, `prompt`, `size`, `image`)
2. Generates images via DALL-E 3 API at optimal resolution (1024x1024, 1792x1024, or 1024x1792 based on aspect ratio)
3. Saves raw high-resolution images to `generated_images_raw/`
4. **By default, keeps full DALL-E resolution** (no cropping) and copies to final folder
5. Optionally center-crops to exact dimensions if `"crop": true` is specified in JSON
6. Saves final images to `generated_images_final_cropped/` (full-size or cropped depending on setting)
7. Skips images that already exist (both raw and cropped)

### Image Prompts JSON Schema

```json
[
  {
    "id": "unique-identifier",
    "prompt": "Short description for reference",
    "size": "WIDTHxHEIGHT",
    "reasoning": "Why this size/format",
    "image": "Full DALL-E prompt text"
  }
]
```

**Field descriptions:**
- `id`: Used as filename (without extension)
- `size`: Target dimensions as "WIDTHxHEIGHT" (e.g., "300x200") or just "WIDTH" for square
- `image` or `prompt`: The subject to generate (style is added automatically if style_config present)
- `crop`: Optional boolean (default: `false`) - set to `true` to crop to exact dimensions
- `base_style`: Style keywords applied to all images in batch
- `seed`: Seed for reproducible generation (same seed = similar aesthetic)
- `style_override`: Per-image style override (optional)

### Asset Type Detection

The batch generator automatically detects asset type from prompts:

- **Characters**: Prompts containing "character", "sprite", "avatar", "animal", "creature", "person"
- **Environment**: Prompts with "landscape", "scene", "background", "facility", "terrain"
- **UI**: Prompts with "button", "icon", "menu", "interface", "navigation"
- **Objects**: Prompts with "item", "object", "prop", "material", "resource"

This enables future integration with `.image-style.json` reference images.

### Dry Run Mode

Preview enhanced prompts before generating:

```bash
python3 generate_images.py --dry-run
```

Output shows:
- Detected asset type
- Base style applied
- Final enhanced prompt
- No API calls made, no images generated

### Output Directories

- `generated_images_raw/` - Original DALL-E 3 outputs (1024-1792px)
- `generated_images_final_cropped/` - Final images (full-size or cropped depending on `crop` setting)
- `testImages/` - Manual test images
- `image_prompts_with_style_example.json` - Example of style-aware format
- `image_prompts_crop_example.json` - Example showing crop behavior

### Image Cropping Behavior

**Default:** Batch generator keeps full DALL-E resolution (no cropping)

- DALL-E only generates 3 sizes: 1024x1024, 1792x1024, 1024x1792
- By default, full-size images are saved to both folders (may be larger than requested)
- To get exact dimensions, add `"crop": true` to the image entry in JSON

**When to enable cropping (`"crop": true`):**
- UI elements (buttons, icons) that need exact pixel dimensions
- Splash screens with specific aspect ratio requirements
- Assets that must fit exact layout specifications

**When to keep full size (default, `"crop": false` or omit field):**
- Characters, environments, objects (composition matters)
- Artistic images where full frame is important
- Most general use cases

**Why this matters:**
- Cropping can discard up to 47.7% of the generated image area
- DALL-E generates at fixed resolutions, so requesting 300x400 actually generates 1024x1792
- Center-cropping assumes the subject is centered (often not true)
- Keeping full resolution preserves the entire AI-generated composition

### Example: Style-Consistent Batch

**image_prompts.json:**
```json
{
  "style_config": {
    "base_style": "cottagecore aesthetic with soft pastel colors, warm natural lighting, hand-painted watercolor textures",
    "seed": 100,
    "project": "cozy-farm-game"
  },
  "images": [
    {
      "id": "cute-chickens",
      "prompt": "Cute farm chickens",
      "size": "300x400",
      "crop": false
    },
    {
      "id": "cozy-barn",
      "prompt": "Cozy red barn with stone foundation",
      "size": "600x400",
      "crop": false
    },
    {
      "id": "ui-button",
      "prompt": "Wooden button with text 'Start'",
      "size": "256x128",
      "crop": true
    }
  ]
}
```

**Result:**
- All images share cottagecore style
- All use seed=100 (related aesthetic)
- Asset types detected: characters, environment, ui
- Final prompts combine base_style + subject
- Chickens and barn keep full DALL-E resolution (1024x1792 and 1792x1024)
- UI button crops to exact 256x128 dimensions

### API Key Security

**CRITICAL**: The API key in `generate_images.py` line 9 should be removed before committing. Never commit API keys to version control.

## Interface_Royale

### Purpose
Design documentation system for creating reusable F2P mobile game UI/UX templates based on patterns from top-grossing games (Clash Royale, etc.).

### Core Documents

1. **Interface_Royale_Design_Document.md** - Master template defining:
   - Core UI principles ("Secret UI Sauce")
   - 13 essential screen templates (Home, Battle, Collection, Shop, etc.)
   - Monetization surfaces and retention loops
   - Component library hierarchy (Atoms → Molecules → Organisms)

2. **Interface_Royale_Automation_Plan.md** - Pipeline automation spec:
   - Input schemas (`idea.json`, `template.json`)
   - Generation steps from concept to asset list
   - Output structure (design docs, wireframes, stub assets)

3. **Use_Case_Idle_Clicker_Design.md** - Example implementation:
   - "Tap Tycoon: Factory Frenzy" idle clicker game design
   - Shows how template adapts to specific genres

4. **Competitive_Analysis_One_Pager.md** - Market research reference

5. **Idle_Clicker_Asset_List.csv** - Comprehensive asset inventory with specs

### Asset List CSV Structure

```
category,screen,component,asset_name,variant,dimensions,format,notes
```

- **category**: UI, VFX, Audio, UX
- **screen**: Home, Play, Collection, Shop, etc.
- **component**: Button, Icon, Banner, Canvas, etc.
- **dimensions**: Pixel dimensions or "9-slice WxH"
- **format**: png, svg, json, wav

### Design Philosophy

Interface Royale templates optimize for:
- **Monetization**: ARPDAU, payer conversion, pay depth
- **Retention**: D1/D7/D30 metrics
- **Accessibility**: One-handed ergonomics, WCAG AA compliance
- **LiveOps**: Events calendar, rotating modes, season pass backbone

### Key Patterns

- Navigation max depth: 2 levels
- Persistent 4-5 tab bar with central primary CTA
- Red-dot hygiene: badges only on resolvable actions
- Appointment loops: time-gated rewards (chests, quests)
- Smart scarcity: limited slots, time-limited offers

## MayaScripts

Collection of custom Maya shelf tools for the AK_Shelf. See `MayaScripts/README.md` for the full tool list, code snippets, and project structure.

### MayaScripts Documentation Rule

**IMPORTANT:** When making significant changes to any script in `MayaScripts/` (adding a tool, renaming, changing behavior, adding parameters, or removing a tool), you MUST update these files before finishing:

1. **`MayaScripts/README.md`** — Update the tool table and code snippets for the affected group
2. **`MayaScripts/rebuild_ak_shelf.py`** — Update shelf button if label/annotation/icon changed

This does NOT apply to minor bug fixes or internal refactors that don't change the tool's name, purpose, or interface.

## Development Workflow

This is primarily a design and automation tooling workspace, not a live application codebase.

### Typical Tasks

**Testing Image Prompts:**
1. Test a single prompt quickly: `/generate-image "your prompt here" 1024 768`
2. If satisfied, add to `ImageGenerator/image_prompts.json`
3. Run batch generation: `cd ImageGenerator && python3 generate_images.py`
4. Review outputs in `generated_images_final_cropped/`

**Adding New Image Prompts:**
1. Edit `ImageGenerator/image_prompts.json`
2. Add new entry with unique `id`, target `size`, and prompt `image` text
3. Run batch script to generate all missing images
4. Script automatically skips existing images to save API costs

**Creating New Game Design:**
1. Use `Interface_Royale_Design_Document.md` as template reference
2. Create genre-specific design doc (see `Use_Case_Idle_Clicker_Design.md`)
3. Generate asset list CSV based on required screens and components
4. Optional: Use ImageGenerator to create placeholder art

**Extending the Automation Pipeline:**
- Follow architecture in `Interface_Royale_Automation_Plan.md`
- Inputs: `idea.json` and `template.json` schemas
- Outputs: design docs, wireframes.json, assets.csv, stub assets

## File Organization

```
VibeBash/
├── ImageGenerator/
│   ├── generate_images.py          # Main batch generation script
│   ├── image_prompts.json          # Prompt definitions
│   ├── generated_images_raw/       # Original DALL-E outputs
│   ├── generated_images_final_cropped/  # Cropped finals
│   └── testImages/                 # Manual test images
├── Interface_Royale/
│   ├── Interface_Royale_Design_Document.md
│   ├── Interface_Royale_Automation_Plan.md
│   ├── Use_Case_Idle_Clicker_Design.md
│   ├── Competitive_Analysis_One_Pager.md
│   └── Idle_Clicker_Asset_List.csv
└── MayaScripts/                    # Reserved for future use
```

## Notes

- No build system, package managers, or runtime environment beyond Python 3
- Not a git repository currently
- Primary use case: design documentation and batch asset generation for game prototyping
- ImageGenerator script skips existing files to save API costs on reruns
