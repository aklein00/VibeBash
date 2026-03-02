# Implementation Plan: Photoshop Color Swatch Atlas Generator

## Overview
Photoshop ExtendScript (.jsx) that generates a 16x16 color swatch atlas (256 squares, 2048x2048px) with painterly gradients. Each row is on a separate layer for editability.

## Requirements

### Document Structure
- 2048x2048px canvas (each square is 128x128px)
- Layer Group: "Atlas_Generated"
- 16 separate layers (one per row): "Row_00_Skin", "Row_01_Hair", etc.
- Non-destructive output (no flattening)
- No labels on swatches (clean visual reference)
- No progress alerts (fast, silent execution)
- Pre-defined color palettes (consistent output every run)

### Gradient Logic - "The Artist Algorithm"

**Standard Cloth:**
- Shadow: 10-15% darker in Brightness
- Shadow: +5-10% more Saturated
- Hue shifting based on color temperature:
  - Warm colors (Yellow/Orange) → shift towards Red/Orange
  - Pink → shift towards Red
  - Cool colors (Blue/Green) → shift towards Deep Blue/Purple

**Hair & Metals:**
- Higher contrast allowed
- Diagonal gradients (dark bottom-left to light top-right)

### Gradient Directions
- **Cloth rows (2-15):** Vertical gradient (dark bottom, light top)
- **Hair row (1):** Diagonal gradient (dark bottom-left, light top-right)
- **Materials column (column 15 in all rows):** Diagonal gradient

### Color Palette Specifications

#### Row 0 - Skin Tones
16 skin tones from pale albinism to deep melanin with varied undertones (olive, cool, warm)

#### Row 1 - Hair Colors
16 hair colors: Platinum, Blonde variants, Red, Auburn, Brunette variants, Black, Grey, White
Ombre style with dark roots/bottom transitioning to lighter tips/top

#### Column 15 Override - Materials
Every row's 15th cell (rightmost) becomes a material:
- **Metals (5-7):** Gold, Silver, Bronze, Copper, Steel, Chrome, Gunmetal
- **Woods:** Dark Wood, Light Wood, Weathered Wood
- **Fabrics:** Silk, Polyester, Velvet, Leather
- **Special:** Latex, Glass

Uses diagonal gradient style for all materials.

#### Rows 2-4 - Vibrant Colors
Bright, saturated primary and secondary colors for character clothing

#### Rows 5-7 - Muted/Earth Tones
Desaturated colors: olives, terracottas, sages, taupes, browns

#### Rows 8-10 - Professional Colors
Business attire: Navy blue, charcoal, forest green, slate grey, cream, khaki

#### Rows 11-13 - Pastels
High brightness, low saturation - soft, approachable colors

#### Rows 14-15 - Goth/Dark
Near-blacks, deep purples, burgundy, deep reds, charcoal

## Technical Implementation

### Phase 1: Color Conversion Functions

**Functions:**
1. `rgbToHsb(r, g, b)` - Convert RGB (0-255) to HSB {h: 0-360, s: 0-100, b: 0-100}
2. `hsbToRgb(h, s, b)` - Convert HSB back to RGB {r, g, b}
3. `getShadowColor(colorObj, type, intensity)` - The painterly gradient algorithm

### Phase 2: Painterly Gradient Algorithm

**Function:** `getShadowColor(colorObj, type, intensity)`

Logic flow:
1. Convert input RGB to HSB
2. Determine color temperature (warm/cool) from Hue
3. Apply brightness reduction (10-15% for cloth, 20-30% for hair/materials)
4. Apply saturation boost (+5-10% for cloth)
5. Apply hue shifting:
   - Warm (30-90° hue): shift +5-15° towards red
   - Pink (300-360°): shift -10-20° towards red
   - Cool (180-270°): shift +10-20° towards blue/purple
6. Clamp values to valid ranges
7. Convert back to RGB

### Phase 3: Color Palette Definitions

Pre-define all 256 base colors as constants:

```javascript
var colorPalettes = {
  skin: [{r:..., g:..., b:...}, ...], // 16 RGB colors
  hair: [...], // 16 RGB colors
  vibrant1: [...], // 16 RGB colors
  // ... 16 total palettes
};
```

### Phase 4: Document Setup

**Function:** `createAtlasDocument()`

1. Create new document: 2048x2048px, RGB mode, 72 PPI
2. Create layer group "Atlas_Generated"
3. Return document reference

### Phase 5: Row Generation

**Function:** `generateRow(doc, layerGroup, rowIndex, colorArray, gradientType)`

Process:
1. Create new layer: "Row_XX_Name"
2. Move layer into group
3. Loop through 16 columns:
   - Calculate square bounds (x, y, width, height)
   - If column == 15, override with material color and use diagonal gradient
   - Get base color from colorArray[col]
   - Calculate shadow color using getShadowColor()
   - Set foreground/background colors
   - Select square region
   - Apply gradient (vertical or diagonal)
   - Deselect

### Phase 6: Gradient Application

**Function:** `applyGradient(direction, bounds)`

Directions:
- "vertical": Start point bottom, end point top
- "diagonal": Start point bottom-left, end point top-right

Uses Photoshop's gradient tool API (ActionDescriptor system).

### Phase 7: Main Execution

**Function:** `main()`

1. Call createAtlasDocument()
2. Get layer group reference
3. Define all 16 color palettes
4. Loop i = 0 to 15:
   - Determine gradient type
   - Call generateRow() with appropriate palette
5. Display completion message
6. No flattening - leave layers intact

### Phase 8: Error Handling

Wrap main() in try/catch to handle:
- Photoshop not running
- Insufficient memory
- Invalid color values
- Layer creation failures

## Material Color Definitions

For column 15 overrides across 16 rows:

| Material | Base RGB | Shadow RGB | Notes |
|----------|----------|------------|-------|
| Gold | 255, 215, 0 | 184, 134, 11 | Warm, reflective |
| Silver | 192, 192, 192 | 128, 128, 128 | Cool, reflective |
| Bronze | 205, 127, 50 | 139, 90, 43 | Warm metal |
| Copper | 184, 115, 51 | 142, 74, 23 | Reddish metal |
| Steel | 176, 196, 222 | 112, 128, 144 | Cool, industrial |
| Chrome | 220, 230, 240 | 180, 190, 200 | Bright, reflective |
| Gunmetal | 82, 91, 99 | 52, 58, 64 | Dark metal |
| Dark Wood | 101, 67, 33 | 59, 41, 20 | Walnut/mahogany |
| Light Wood | 222, 184, 135 | 160, 120, 80 | Birch/maple |
| Weathered Wood | 139, 125, 107 | 90, 80, 68 | Gray/aged |
| Silk | 245, 235, 225 | 200, 185, 170 | Subtle sheen |
| Polyester | 75, 90, 110 | 50, 60, 75 | Synthetic look |
| Velvet | 120, 40, 80 | 60, 20, 40 | Deep, rich |
| Leather | 139, 90, 43 | 92, 64, 30 | Brown leather |
| Latex | 30, 30, 35 | 10, 10, 12 | High gloss |
| Glass | 200, 230, 255 | 140, 180, 220 | Translucent |

## Implementation Summary

### Files Created
1. **generate_swatch_atlas.jsx** - Complete ExtendScript (~1000 lines)
2. **README.md** - Usage instructions
3. **IMPLEMENTATION_PLAN.md** - This document
4. **TEST_PLAN.md** - Testing checklist

### Key Technical Challenges

1. **RGB ↔ HSB Conversion**: Manual math implementation
2. **Hue Shifting Logic**: Conditional color temperature detection
3. **Gradient API**: ActionDescriptor system for precise control
4. **Material Realism**: Highlight/shadow colors that evoke material properties
5. **Color Distribution**: Visual variety within rows while maintaining coherence

### Execution Flow

```
main()
├─ Create 2048x2048px document
├─ Create "Atlas_Generated" layer group
├─ FOR each row (0-15):
│  ├─ Create layer "Row_XX_Name"
│  ├─ FOR each column (0-15):
│  │  ├─ Get base color from pre-defined palette
│  │  ├─ IF column == 15: Override with material color
│  │  ├─ Calculate shadow color (painterly algorithm)
│  │  ├─ Select 128x128px square region
│  │  ├─ Set foreground (light) and background (shadow)
│  │  ├─ Apply gradient (vertical or diagonal)
│  │  └─ Deselect
│  └─ Move layer into group
└─ Alert "Complete!"
```

## Edge Cases

1. **Saturation overflow:** Clamp saturation values to 0-100%
2. **Hue wrapping:** Hue values wrap at 0° and 360°
3. **Black/white colors:** Near-black colors (brightness < 5%) have minimal hue shift
4. **Column 15 override:** Material colors replace cloth colors consistently
5. **Layer naming:** Use underscores instead of spaces

## Performance

- Pre-calculate all 256 colors at start
- Expected runtime: 2-5 minutes for 256 squares with gradients
- No progress indicators for speed

## User Customization

All 256 colors are hardcoded as constants at the top of the script for easy editing. Materials in column 15 are clearly marked and commented. Layer structure allows per-row editing in Photoshop.

## Extensibility

Future enhancements:
- Custom color palette JSON import
- Variable atlas size (8x8, 32x32)
- Export swatches as ASE or ACO files
- Optional text labels mode
- Generate companion HTML color reference sheet
- Custom material library for column 15
