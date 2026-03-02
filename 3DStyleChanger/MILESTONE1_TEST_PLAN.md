# Milestone 1 Test Plan

**Goal:** Validate Hunyuan3D quality and full pipeline feasibility using RunComfy.

## Test Workflows Created

### 1. `milestone1_test_hunyuan3d.json`
**Purpose:** Test Hunyuan3D image-to-3D generation in isolation

**Workflow:**
```
Load Image → Hunyuan3D → Save 3D Model
```

**What to test:**
- Raw Hunyuan3D quality without style editing
- Generation speed
- Output format quality (.glb)
- Geometry accuracy

### 2. `milestone1_test_full_pipeline.json`
**Purpose:** Test complete pipeline with style transfer

**Workflow:**
```
Load Image → Style Transfer (text prompt) → Hunyuan3D → Save 3D Model
```

**What to test:**
- Style transfer quality (does it preserve structure?)
- End-to-end pipeline success rate
- How well styled images convert to 3D
- Different style prompts effectiveness

---

## Test Images Needed

Please prepare **5 test images** with variety:

### Image Requirements:
- **Format:** PNG or JPG
- **Resolution:** 1024x1024 (or 512x512 minimum)
- **Background:** Clean, preferably white or transparent
- **Subject:** Centered, front-facing view
- **Lighting:** Even, no harsh shadows

### Suggested Test Cases:

1. **Simple Object** (cube, sphere, or basic shape)
   - Tests: Basic 3D generation capability

2. **Character** (humanoid figure or creature)
   - Tests: Complex geometry handling

3. **Prop** (weapon, tool, furniture)
   - Tests: Mid-complexity objects

4. **Vehicle** (car, spaceship, drone)
   - Tests: Hard-surface modeling

5. **Organic Object** (tree, rock, plant)
   - Tests: Irregular geometry

**Where to get test images:**
- Screenshot 3D models from Blender/Maya
- Download from Sketchfab (front-view screenshots)
- Use existing game assets
- AI-generate with DALL-E/Midjourney if needed

---

## Test Protocol

### Test 1: Hunyuan3D Only (No Style Transfer)

**Steps:**
1. Import `milestone1_test_hunyuan3d.json` into RunComfy
2. Upload a test image (start with simple object)
3. Run workflow
4. Download generated .glb file
5. Open in Blender or online viewer (https://gltf-viewer.donmccurdy.com/)
6. Repeat for all 5 test images

**Record for each:**
- ✅ Success / ❌ Failure
- Generation time (seconds)
- Quality score (1-5): How accurate is the geometry?
- Notes: What worked? What failed?

**Example Results Table:**
```
| Image | Success | Time | Quality | Notes |
|-------|---------|------|---------|-------|
| Cube  | ✅      | 45s  | 4/5     | Clean, slight edge smoothing |
| Character | ✅  | 67s  | 3/5     | Back side hallucinated |
| Prop  | ✅      | 52s  | 4/5     | Good detail |
| Vehicle | ❌    | -    | -       | Failed: too complex |
| Organic | ✅    | 58s  | 2/5     | Messy geometry |
```

### Test 2: Full Pipeline with Style Transfer

**Steps:**
1. Import `milestone1_test_full_pipeline.json` into RunComfy
2. Upload a test image
3. Edit style prompt (try each prompt below)
4. Run workflow
5. Compare: Original → Styled Image → 3D Output
6. Assess if style is preserved in 3D conversion

**Style Prompts to Test:**
- `"cyberpunk metal texture, futuristic style, neon accents"`
- `"wooden toy style, smooth polished wood texture"`
- `"low-poly voxel art, blocky minecraft style"`
- `"cartoon character style, cel-shaded, simple colors"`

**Record for each:**
- Does style transfer preserve object structure? (Yes/No)
- Does 3D output reflect the style? (Yes/No/Partially)
- Quality degradation vs. Test 1? (Better/Same/Worse)

---

## Key Questions to Answer

After running tests, please provide answers to these:

### About Hunyuan3D:

1. **Success Rate:** What % of images successfully generate 3D models?
2. **Quality:** On average, how usable are the outputs (1-5 scale)?
3. **Speed:** Average generation time per model?
4. **Output Format:** Does .glb export work? Any alternative formats available?
5. **Multi-view Support:** Does your RunComfy setup support multi-view input for Hunyuan3D?
6. **Quality Settings:** Are there resolution or quality presets to adjust?
7. **Failures:** What types of images fail? (Too complex, wrong format, etc.)

### About Style Transfer:

8. **Tool Available:** What image editing node is available in RunComfy?
   - Recraft Banana?
   - Flux Dev?
   - SD3 + IP-Adapter?
   - Other?
9. **Structure Preservation:** Does style transfer maintain object silhouette? (1-5 scale)
10. **Style Accuracy:** Do outputs match text prompts? (1-5 scale)
11. **Speed:** How long does style transfer take?

### About the Full Pipeline:

12. **End-to-End Success:** Does the complete pipeline work reliably?
13. **Bottleneck:** What's the slowest stage? (Load, Style, Generate, Save)
14. **Quality Trade-off:** Is styled output worse than direct image-to-3D?
15. **Usability:** Would you use this for game asset iteration? Why/why not?

---

## Data to Send Back

Please provide:

### 1. Generated 3D Models (.glb files)
- At least 3 successful outputs from Test 1
- At least 2 styled outputs from Test 2

### 2. Screenshots
- Before/after for style transfer (show styled images)
- 3D outputs rendered in Blender or viewer
- Any error messages or failures

### 3. Filled Test Results
Use the template above or create a simple document with:
- Success rates
- Timing data
- Quality assessments
- Answers to key questions

### 4. Recommendations
Based on your testing:
- Should we proceed with Hunyuan3D? (Yes/No/Try alternatives)
- Which style transfer tool works best?
- Any workflow changes needed?
- Any blockers or concerns?

---

## Success Criteria for Milestone 1

Milestone 1 is **COMPLETE** when:

✅ **Hunyuan3D validated:** At least 60% success rate with acceptable quality (3+/5)
✅ **Style transfer validated:** Preserves structure adequately (3+/5)
✅ **Full pipeline functional:** End-to-end workflow completes without errors
✅ **Decision made:** Clear recommendation on tools to use for Milestone 2
✅ **Documentation:** Test results documented in TECH_RESEARCH.md

If Hunyuan3D quality is insufficient (< 60% success or < 3/5 quality), we'll need to:
- Adjust workflow (try multi-view immediately)
- Consider alternative models (InstantMesh, LGM, CSM)
- Re-scope expectations

---

## Timeline

**Estimated Test Time:** 2-4 hours
- Test 1: 1 hour (5 images × ~10 min each)
- Test 2: 1-2 hours (multiple prompts and comparisons)
- Documentation: 1 hour

**When Complete:** Notify Claude with results, and we'll create TECH_RESEARCH.md and plan Milestone 2.

---

## Troubleshooting

### Issue: Workflow nodes not found in RunComfy

**Solution:** Node names in JSON are placeholders. Replace with actual RunComfy node names:
- `Hunyuan3D_ImageTo3D` → Find the actual Hunyuan3D node in RunComfy
- `ImageStyleTransfer` → Use Recraft, Flux, or SD3 nodes available
- `Save3DModel` → Use whatever 3D export node is available

**Need help?** Save a working manual workflow in RunComfy and share the JSON. I'll adapt it.

### Issue: Style transfer node unclear

**Solution:** If multiple options, test each:
1. Try Recraft Banana first (best structure preservation)
2. If unavailable, use Flux Dev with image conditioning
3. Fallback: SD3 + IP-Adapter + ControlNet (more complex setup)

### Issue: Generated 3D models won't open

**Solution:**
- Try alternative viewer: https://gltf-viewer.donmccurdy.com/
- Check file size (should be > 0 KB)
- Try exporting as .obj instead of .glb
- Share error message

---

## Notes

- **Don't worry about perfect data:** Rough assessments and a few examples are enough for Milestone 1.
- **Focus on feasibility:** Main question is "Can we build this?" not "Is it perfect?"
- **Be honest about quality:** If outputs are unusable, that's valuable feedback too.
- **Share blockers early:** If something doesn't work, let me know ASAP so we can adjust.

Ready to test! 🚀
