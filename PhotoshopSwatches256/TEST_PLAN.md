# Test Plan: Photoshop Color Swatch Atlas Generator

**Script:** `generate_swatch_atlas.jsx`
**Version:** 1.0
**Last Updated:** 2026-02-03

## Overview

This test plan validates the Photoshop ExtendScript that generates a 16x16 color swatch atlas with painterly gradients. Focus is on visual quality, technical correctness, and editability.

---

## Pre-Test Setup

### Environment
- [ ] Photoshop CC 2019 or later installed
- [ ] At least 2GB free RAM
- [ ] Script file saved to `PhotoshopSwatches256/generate_swatch_atlas.jsx`

### Baseline Expectations
- **Execution time:** 2-5 minutes
- **Output size:** 2048x2048px document
- **Layer count:** 1 group + 16 layers (17 total)
- **No errors or warnings**

---

## Test 1: Script Execution

**Objective:** Verify script runs without errors

### Steps
1. Open Photoshop
2. File > Scripts > Browse
3. Select `generate_swatch_atlas.jsx`
4. Click Open

### Expected Results
- [ ] Script starts immediately (no errors)
- [ ] Photoshop shows document being created
- [ ] Completion alert appears: "Swatch Atlas Complete!"
- [ ] Total execution time: 2-5 minutes

### Pass Criteria
- No JavaScript errors
- Completion message displayed
- New document created

---

## Test 2: Document Structure

**Objective:** Validate document properties and layer organization

### Steps
1. After script completes, check document properties:
   - Image > Image Size
   - Check Layers panel

### Expected Results
**Document Properties:**
- [ ] Width: 2048 pixels
- [ ] Height: 2048 pixels
- [ ] Color Mode: RGB
- [ ] Resolution: 72 PPI

**Layer Structure:**
- [ ] Layer Group exists: "Atlas_Generated"
- [ ] 16 layers inside group
- [ ] Layer names follow pattern: "Row_00_Skin", "Row_01_Hair", etc.
- [ ] No flattened background layer

### Pass Criteria
- All document properties match specifications
- Layer hierarchy is correct and non-destructive

---

## Test 3: Grid Accuracy

**Objective:** Verify each square is exactly 128x128px

### Steps
1. Use Rectangular Marquee Tool
2. Select a square in row 0, column 0
3. Note selection dimensions in Info panel
4. Repeat for squares in different positions:
   - Row 0, Column 15 (top right)
   - Row 15, Column 0 (bottom left)
   - Row 15, Column 15 (bottom right)
   - Row 7, Column 7 (center)

### Expected Results
- [ ] All squares are 128x128px (shown in Info panel)
- [ ] No gaps between squares
- [ ] Grid perfectly fills 2048x2048px canvas

### Pass Criteria
- Every sampled square is exactly 128x128px
- No visible gaps or overlaps

---

## Test 4: Color Palette Validation

**Objective:** Verify each row has the correct color theme

### Visual Inspection Checklist

#### Row 0 - Skin Tones
- [ ] 16 distinct skin tones present
- [ ] Ranges from pale (left) to deep melanin (right)
- [ ] Varied undertones visible (olive, cool, warm)
- [ ] No pure grays or unrealistic colors

#### Row 1 - Hair Colors
- [ ] 16 hair colors from light to dark
- [ ] Includes: Platinum, Blonde, Red, Auburn, Brunette, Black, Grey, White
- [ ] Ombre effect visible (dark bottom-left to light top-right)
- [ ] Natural hair color range

#### Rows 2-4 - Vibrant Colors
- [ ] Bright, saturated colors
- [ ] Primary and secondary colors represented
- [ ] High saturation (colors "pop")
- [ ] Suitable for character clothing

#### Rows 5-7 - Muted/Earth Tones
- [ ] Desaturated colors
- [ ] Olives, terracottas, sages, taupes, browns
- [ ] Natural, earthy palette
- [ ] Lower saturation than vibrant rows

#### Rows 8-10 - Professional Colors
- [ ] Business-appropriate colors
- [ ] Navy blue, charcoal, forest green, slate grey, cream
- [ ] Subdued, professional appearance
- [ ] Not overly bright or dark

#### Rows 11-13 - Pastels
- [ ] High brightness, low saturation
- [ ] Soft, approachable colors
- [ ] Pastel pink, blue, yellow, green, etc.
- [ ] Light and airy appearance

#### Rows 14-15 - Goth/Dark
- [ ] Near-blacks and very dark colors
- [ ] Deep purples, burgundy, deep reds
- [ ] Dramatic, moody palette
- [ ] Still retains some color (not pure black)

### Pass Criteria
- Each row's color theme is distinct and recognizable
- Colors match the intended aesthetic
- No duplicate or nearly identical colors across the atlas

---

## Test 5: Column 15 - Material Override

**Objective:** Verify column 15 in every row shows materials, not cloth colors

### Steps
1. Zoom to column 15 (rightmost column)
2. Visually inspect each cell from row 0 to row 15
3. Use Eyedropper Tool to sample colors if needed

### Expected Materials (top to bottom)
- [ ] Row 0: Gold (warm, reflective)
- [ ] Row 1: Silver (cool, reflective)
- [ ] Row 2: Bronze (warm metal)
- [ ] Row 3: Copper (reddish metal)
- [ ] Row 4: Steel (cool, industrial)
- [ ] Row 5: Chrome (bright, reflective)
- [ ] Row 6: Gunmetal (dark metal)
- [ ] Row 7: Dark Wood (walnut/mahogany)
- [ ] Row 8: Light Wood (birch/maple)
- [ ] Row 9: Weathered Wood (gray/aged)
- [ ] Row 10: Silk (subtle sheen)
- [ ] Row 11: Polyester (synthetic look)
- [ ] Row 12: Velvet (deep, rich)
- [ ] Row 13: Leather (brown leather)
- [ ] Row 14: Latex (high gloss, high contrast)
- [ ] Row 15: Glass (translucent feel)

### Visual Quality Check
- [ ] Materials look distinct from cloth colors
- [ ] Diagonal gradients applied (not vertical)
- [ ] High contrast for metals and latex
- [ ] Subtle sheen for silk and glass

### Pass Criteria
- All 16 materials are visually distinct
- Column 15 does not repeat any cloth colors from rows 2-15
- Diagonal gradient direction is correct

---

## Test 6: Gradient Quality - "Painterly" Effect

**Objective:** Verify gradients have artistic quality, not flat darkening

### Visual Inspection

#### Cloth Rows (Rows 2-15, excluding column 15)
- [ ] Gradients flow from dark (bottom) to light (top)
- [ ] Shadow colors are NOT just darkened versions
- [ ] Shadow colors have visible saturation boost (richer, not muddy)
- [ ] Subtle hue shifting visible (warm colors shift towards red, cool towards blue)
- [ ] No harsh gradient banding

#### Hair Row (Row 1)
- [ ] Diagonal gradient visible (dark bottom-left to light top-right)
- [ ] Ombre effect looks natural (root-to-tip transition)
- [ ] Higher contrast than cloth gradients
- [ ] Smooth gradient transitions

#### Materials (Column 15)
- [ ] Diagonal gradients applied consistently
- [ ] High contrast for reflective materials (gold, silver, chrome, latex)
- [ ] Lower contrast for matte materials (woods, fabric)
- [ ] Gradient enhances material illusion

### Hue Shifting Validation

Pick 3 random warm colors (yellows, oranges):
- [ ] Shadow shifts towards red/orange (not brown)

Pick 3 random cool colors (blues, greens):
- [ ] Shadow shifts towards deep blue/purple (not gray)

Pick 2 pink colors:
- [ ] Shadow shifts towards red (not purple)

### Pass Criteria
- Gradients enhance colors rather than just darkening
- Hue shifting is subtle but present
- No flat or muddy gradients
- Material gradients feel three-dimensional

---

## Test 7: Edge Cases & Error Handling

**Objective:** Test edge cases in color calculations

### Black/Near-Black Colors (Rows 14-15)
- [ ] Near-black colors have minimal but visible gradients
- [ ] No color breaks or unexpected hues
- [ ] Darkness is preserved (not accidentally brightened)

### White/Near-White Colors (Row 11, some pastels)
- [ ] Light colors don't blow out to pure white
- [ ] Gradients still visible on light backgrounds
- [ ] Saturation boost doesn't create unrealistic colors

### Saturation Boundaries
- [ ] No colors exceed 100% saturation (no clipping)
- [ ] Desaturated colors in earth tone rows don't become gray

### Pass Criteria
- Extreme colors (very dark/light) handle gracefully
- No color calculation errors visible
- All colors stay within valid RGB ranges

---

## Test 8: Layer Editability

**Objective:** Confirm non-destructive workflow

### Steps
1. In Layers panel, select "Row_00_Skin"
2. Try to move layer outside group
3. Try to edit layer opacity
4. Try to add layer mask
5. Try to apply layer style (drop shadow, etc.)
6. Hide/show individual row layers

### Expected Results
- [ ] All layer operations work without errors
- [ ] Layers are fully editable (not rasterized/flattened)
- [ ] Layer group can be collapsed/expanded
- [ ] Individual rows can be hidden/shown
- [ ] Layer names are clear and descriptive

### Pass Criteria
- Complete non-destructive workflow
- All standard layer operations function correctly
- User can easily edit or tweak any row

---

## Test 9: Performance & Stability

**Objective:** Verify script performance and Photoshop stability

### Metrics
- [ ] Execution time: 2-5 minutes
- [ ] Memory usage: < 2GB during execution
- [ ] No Photoshop crashes or freezes
- [ ] Script completes without warnings
- [ ] Final PSD file size: < 50MB (before saving)

### Stress Test (Optional)
- [ ] Run script 3 times consecutively
- [ ] Photoshop remains stable
- [ ] Each run produces identical output

### Pass Criteria
- Script completes consistently in expected time
- No memory leaks or instability
- Photoshop remains responsive after script finishes

---

## Test 10: Cross-Version Compatibility (Optional)

**Objective:** Test on different Photoshop versions

### Test Environments
- [ ] Photoshop CC 2019
- [ ] Photoshop CC 2020
- [ ] Photoshop CC 2021+

### Expected Results
- Script runs without errors on all tested versions
- Output is visually identical across versions

---

## Test Summary

### Overall Pass Criteria

**Critical (Must Pass):**
- [ ] Script executes without errors
- [ ] Document is 2048x2048px with correct layer structure
- [ ] All 256 squares are exactly 128x128px
- [ ] Column 15 materials are present and distinct
- [ ] Gradients are painterly (not flat darkening)

**Important (Should Pass):**
- [ ] Each row's color theme is recognizable
- [ ] Hue shifting is visible in gradients
- [ ] Layers are fully editable
- [ ] Execution time is 2-5 minutes

**Nice to Have:**
- [ ] Material illusions are convincing
- [ ] No gradient banding
- [ ] Works across Photoshop versions

### Sign-Off

**Tester:** ___________________
**Date:** ___________________
**Photoshop Version:** ___________________
**Result:** ☐ Pass  ☐ Fail  ☐ Pass with Minor Issues

**Notes:**
```
[Space for tester notes and observations]
```

---

## Known Issues & Limitations

_(To be filled in after first test run)_

1. ...
2. ...
3. ...

---

## Future Test Scenarios

- Export to .ASE or .ACO color swatch file
- Import custom color palettes
- Generate different atlas sizes (8x8, 32x32)
- Add text labels mode
- Test on 4K/5K displays for visual quality
