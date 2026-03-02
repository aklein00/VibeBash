# Style-Consistent Image Generation - Quick Start Guide

## 🎨 What Is This?

A system for generating batches of images that look visually consistent - same art style, colors, lighting, and mood across all assets.

## 🚀 Quick Start (3 Steps)

### Step 1: Set Up Style Config

```bash
/setup-image-style
```

Claude will guide you through:
- Analyzing existing project art (if any)
- Choosing reference images
- Setting up exploration mode (for new projects)

**Result:** Creates `.image-style.json` in your project root

### Step 2: Generate Images

```bash
/generate-image "character sprite - warrior"
```

Claude automatically:
- Detects asset type ("character")
- Loads reference images
- Applies your project style
- Generates matching image

### Step 3: Batch Generate (Optional)

For bulk generation, use `ImageGenerator/`:

**image_prompts.json:**
```json
{
  "style_config": {
    "base_style": "cottagecore aesthetic, soft watercolor",
    "seed": 42
  },
  "images": [
    {"id": "chicken", "prompt": "Cute farm chicken", "size": "300x400"},
    {"id": "barn", "prompt": "Red barn", "size": "600x400"}
  ]
}
```

**Run:**
```bash
cd ImageGenerator
python3 generate_images.py --dry-run  # Preview first
python3 generate_images.py            # Generate
```

## 📋 Style Config Structure

**.image-style.json (in project root):**

```json
{
  "style_name": "my-game-style",
  "style_description": "Watercolor style with pastel colors",
  "asset_types": {
    "characters": {
      "reference_images": ["assets/char1.png", "assets/char2.png"],
      "style_notes": "Consistent proportions and expressions"
    },
    "environment": {
      "reference_images": ["assets/bg1.png"],
      "style_notes": "Warm lighting and soft shadows"
    }
  },
  "seed": 42,
  "exploration_mode": false
}
```

## 🎯 Asset Types

Claude auto-detects from your prompt:

| Type | Keywords |
|------|----------|
| **Characters** | character, sprite, avatar, person, animal |
| **Environment** | background, landscape, scene, level |
| **UI** | button, icon, menu, panel, interface |
| **Objects** | item, object, prop, weapon, tool |

## 🔍 Exploration Mode

**For new projects without existing art:**

1. **Enable exploration mode:**
   ```json
   {"exploration_mode": true, "seed": 100}
   ```

2. **Generate variations:**
   ```bash
   /generate-image "character sprite"
   ```
   Creates 3 variations: `_v1.png`, `_v2.png`, `_v3.png`

3. **Pick favorite and add to config:**
   ```json
   {
     "asset_types": {
       "characters": {
         "reference_images": ["generated_art/character_v2.png"]
       }
     }
   }
   ```

4. **Disable exploration mode:**
   ```json
   {"exploration_mode": false}
   ```

5. **Future generations match your chosen style!**

## ⚙️ How It Works

1. **Reference images** loaded into Claude's context (NOT uploaded to image API)
2. **Claude analyzes** visual style (colors, lighting, art style)
3. **Enhanced prompt** generated combining style + your request
4. **Google Imagen** generates image from enhanced prompt

**Important:** Reference images guide Claude's prompt writing, they don't directly control the image API. This is why consistency is ~70-80%, not pixel-perfect.

## 📊 Optimal Reference Counts

| Asset Type | Count | Why |
|-----------|-------|-----|
| Characters | 4-5 | Capture variety of poses, expressions |
| Environment | 2-3 | Lighting and palette are simpler |
| UI | 3-4 | Brand consistency across elements |
| Objects | 2-3 | Material and lighting are key |

**Rule of thumb:** 2-5 references per type. More ≠ better!

## 🎲 Seed Parameter

**For consistency:**
```bash
/generate-image "forest" 1024 768 "" 42
/generate-image "mountain" 1024 768 "" 42
# Both use seed 42 = similar aesthetic
```

**In style config:**
```json
{"seed": 42}  // Consistent generation
{"seed": null}  // Random variation
```

**What seeds do:**
- ✅ Make generation reproducible
- ✅ Create similar (not identical) images
- ✅ Work best with same style description
- ❌ Don't guarantee pixel-perfect consistency

## 📝 Realistic Expectations

### What You Get: ~70-80% Consistency

✅ Similar color palettes
✅ Matching art style (watercolor, vector, etc.)
✅ Consistent lighting approach
✅ Related mood/atmosphere

### What You Don't Get: 100% Identical

❌ Pixel-perfect matching
❌ Identical lighting in every image
❌ Guaranteed style adherence
❌ Same composition across subjects

### Why Not 100%?

- Image APIs have inherent randomness
- Different subjects affect interpretation
- Reference images guide Claude, not the API
- Text prompts are the final interface to the model

## ✅ Best Practices

**Do:**
- Keep style description under 400 tokens
- Use 2-5 cohesive reference images per type
- Use exploration mode for new projects
- Use consistent seed for related batches
- Edit `.image-style.json` manually for quick tweaks

**Avoid:**
- More than 5 references per type
- Mixing conflicting styles (pixel art + photorealism)
- Overly verbose style descriptions (> 500 tokens)
- Low-quality or inconsistent references
- Expecting pixel-perfect consistency

## 🔧 Dry Run Mode

**Preview prompts before generating:**

```bash
cd ImageGenerator
python3 generate_images.py --dry-run
```

Shows:
- Detected asset type
- Style applied
- Final enhanced prompt
- No API calls, no images generated

## 💡 Common Workflows

### Workflow 1: Brand New Game Project

1. `/setup-image-style` → Enable exploration mode
2. Generate 3 character variations
3. Pick favorite, add to references
4. Generate 3 environment variations
5. Pick favorite, add to references
6. Disable exploration mode
7. Generate production assets (all match style!)

### Workflow 2: Existing Game with Art

1. `/setup-image-style` → Claude finds existing images
2. Claude analyzes art and suggests style description
3. Confirm or refine description
4. Generate new assets (match existing style!)

### Workflow 3: Quick Batch Generation

1. Create `image_prompts.json` with `style_config`
2. `python3 generate_images.py --dry-run`
3. Review enhanced prompts
4. `python3 generate_images.py`
5. All images share consistent style

## 🆘 Troubleshooting

### "Style isn't consistent enough"

- **Check references:** Are they visually cohesive?
- **Simplify style description:** Try < 300 tokens
- **Use same seed:** Add seed to config
- **Reduce reference count:** Try 3 instead of 5

### "Images look too similar"

- **Remove seed:** Set to `null` for variation
- **Use different seeds:** Increment seed per image
- **Vary prompts more:** Add specific details

### "Setup skill isn't working"

- **Check for existing config:** `.image-style.json` might exist
- **Verify working directory:** Must be in project root
- **Use absolute paths:** For reference images

## 📚 Full Documentation

- **Implementation details:** `STYLE_CONSISTENCY_IMPLEMENTATION.md`
- **Global instructions:** `~/.claude/CLAUDE.md` (Image Style Consistency section)
- **Project instructions:** `CLAUDE.md` (Batch Image Generator section)
- **Setup skill:** `~/.claude/skills/setup-image-style/SKILL.md`
- **Generate skill:** `~/.claude/skills/generate-image/SKILL.md`

## 🎯 Key Takeaways

1. **Style consistency is ~70-80%, not 100%** - manage expectations
2. **Reference images go to Claude, not image API** - Claude writes better prompts
3. **2-5 references per type is optimal** - more isn't better
4. **Seed helps but isn't magic** - provides similarity, not identical results
5. **Exploration mode for new projects** - discover your style first
6. **Edit `.image-style.json` manually** - fastest way to tweak style

---

**Quick Command Reference:**

```bash
# Setup
/setup-image-style

# Generate single image
/generate-image "character sprite - warrior"

# Generate with seed
/generate-image "forest scene" 1024 768 "" 42

# Batch generate
cd ImageGenerator
python3 generate_images.py --dry-run
python3 generate_images.py
```

That's it! Start with `/setup-image-style` and you're ready to generate style-consistent images. 🎨
