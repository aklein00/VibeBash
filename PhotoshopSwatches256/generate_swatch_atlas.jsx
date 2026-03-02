/*
 * =============================================================================
 * Photoshop Color Swatch Atlas Generator
 * =============================================================================
 *
 * Generates a 16x16 color swatch atlas (256 swatches) with painterly gradients.
 * Each swatch is 128x128px, creating a 2048x2048px canvas.
 *
 * Features:
 * - 256 individual editable layers (one per swatch, organized in row groups)
 * - Painterly gradients with hue-shifting and saturation boost
 * - Material override for column 15 (metals, woods, fabrics, etc.)
 * - Diagonal ombre gradients for Hair row (Row 2)
 * - Diagonal gradients for all materials in column 15
 * - Pre-defined color palettes for consistency
 *
 * Usage:
 *   File > Scripts > Browse > select this file
 *
 * Expected execution time:
 *   - Test mode (4 rows): ~1-2 minutes
 *   - Full atlas (16 rows): ~5-8 minutes
 *
 * Editability:
 *   Each swatch is a separate rasterized layer
 *   Use adjustment layers, filters, or repaint individual swatches
 *   Layer groups can be collapsed for organization
 *
 * Version: 2.0 Enhanced (Individual Layers)
 * Date: 2026-02-03
 * =============================================================================
 */

// =============================================================================
// CONFIGURATION
// =============================================================================

var CONFIG = {
    canvasWidth: 2048,       // Total canvas width (16 columns × 128px)
    canvasHeight: 2048,      // Total canvas height (16 rows × 128px)
    swatchSize: 128,         // Each swatch is 128x128px
    gridCols: 16,            // 16 columns
    gridRows: 16,            // 16 rows (includes brand row)
    layerGroupName: "Atlas_Generated",
    dpi: 72,
    gradientSteps: 64,       // Number of color steps in gradient (32=faster, 128=smoother) - used in fallback

    // TEST MODE - Set to true to render only 4 rows for quick preview
    testMode: false,
    testRows: [0, 1, 2, 3], // Which rows to render in test mode (Brand, Skin, Hair, Vibrant1) - tests column 15 materials + Row 2 diagonals

    // RENDERING MODE - Photoshop 2026 does not support gradient fill APIs
    useGradientFillLayers: false,  // Gradient fill APIs disabled in PS 2026
    fallbackToManual: true         // Use v2.0 manual rendering with individual layers
};

// =============================================================================
// COLOR CONVERSION UTILITIES
// =============================================================================

/**
 * Convert RGB (0-255) to HSB (Hue: 0-360, Saturation: 0-100, Brightness: 0-100)
 */
function rgbToHsb(r, g, b) {
    r = r / 255;
    g = g / 255;
    b = b / 255;

    var max = Math.max(r, g, b);
    var min = Math.min(r, g, b);
    var delta = max - min;

    var h = 0;
    var s = 0;
    var brightness = max;

    if (max !== 0) {
        s = delta / max;
    }

    if (delta !== 0) {
        if (max === r) {
            h = (g - b) / delta;
        } else if (max === g) {
            h = (b - r) / delta + 2;
        } else {
            h = (r - g) / delta + 4;
        }
        h = h * 60;
        if (h < 0) h += 360;
    }

    return {
        h: h,
        s: s * 100,
        b: brightness * 100
    };
}

/**
 * Convert HSB to RGB (0-255)
 */
function hsbToRgb(h, s, b) {
    s = s / 100;
    b = b / 100;

    var c = b * s;
    var x = c * (1 - Math.abs(((h / 60) % 2) - 1));
    var m = b - c;

    var r = 0, g = 0, bl = 0;

    if (h >= 0 && h < 60) {
        r = c; g = x; bl = 0;
    } else if (h >= 60 && h < 120) {
        r = x; g = c; bl = 0;
    } else if (h >= 120 && h < 180) {
        r = 0; g = c; bl = x;
    } else if (h >= 180 && h < 240) {
        r = 0; g = x; bl = c;
    } else if (h >= 240 && h < 300) {
        r = x; g = 0; bl = c;
    } else {
        r = c; g = 0; bl = x;
    }

    return {
        r: Math.round((r + m) * 255),
        g: Math.round((g + m) * 255),
        b: Math.round((bl + m) * 255)
    };
}

/**
 * Clamp a value between min and max
 */
function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
}

/**
 * Interpolate between two colors
 */
function interpolateColor(color1, color2, t) {
    return {
        r: Math.round(color1.r + (color2.r - color1.r) * t),
        g: Math.round(color1.g + (color2.g - color1.g) * t),
        b: Math.round(color1.b + (color2.b - color1.b) * t)
    };
}

// =============================================================================
// PAINTERLY GRADIENT ALGORITHM - "The Artist Algorithm"
// =============================================================================

/**
 * Calculate shadow color with painterly hue shifting and saturation boost
 */
function getShadowColor(colorObj, type) {
    var hsb = rgbToHsb(colorObj.r, colorObj.g, colorObj.b);
    var h = hsb.h;
    var s = hsb.s;
    var b = hsb.b;

    var brightnessReduction = 0;
    var saturationBoost = 0;
    var hueShift = 0;

    // Darker darks for all gradients - increased contrast
    if (type === "cloth") {
        brightnessReduction = 28;  // Increased from 19 for darker darks
        saturationBoost = 7;
    } else if (type === "hair") {
        brightnessReduction = 40;  // Increased from 32 for darker darks
        saturationBoost = 5;
    } else if (type === "material") {
        brightnessReduction = 50;  // Increased from 37 for much more contrasty metals
        saturationBoost = 3;
    }

    b = b - brightnessReduction;
    if (s > 10) {
        s = s + saturationBoost;
    }

    if (b > 5 && s > 15) {
        if (h >= 30 && h < 90) {
            hueShift = -8;
        } else if (h >= 300 && h <= 360) {
            hueShift = -15;
        } else if (h >= 150 && h < 270) {
            hueShift = 12;
        } else if (h >= 0 && h < 30) {
            hueShift = 5;
        }
    }

    h = h + hueShift;
    if (h < 0) h += 360;
    if (h >= 360) h -= 360;

    s = clamp(s, 0, 100);
    b = clamp(b, 0, 100);

    return hsbToRgb(h, s, b);
}

/**
 * Calculate mid-tone color for 3-stop gradients (Fantasy row)
 * Returns a color halfway between base and full shadow
 */
function getMidToneColor(colorObj, type) {
    var hsb = rgbToHsb(colorObj.r, colorObj.g, colorObj.b);
    var h = hsb.h;
    var s = hsb.s;
    var b = hsb.b;

    var brightnessReduction = 0;
    var saturationBoost = 0;

    // Mid-tone is 50% of full shadow reduction
    if (type === "fantasy") {
        brightnessReduction = 15;  // Half of cloth reduction (28 / 2 ≈ 15)
        saturationBoost = 3;       // Half of cloth boost (7 / 2 ≈ 3)
    }

    b = b - brightnessReduction;
    if (s > 10) {
        s = s + saturationBoost;
    }

    s = clamp(s, 0, 100);
    b = clamp(b, 0, 100);

    return hsbToRgb(h, s, b);
}

// =============================================================================
// COLOR PALETTE DEFINITIONS (272 Pre-defined Colors - includes brand row)
// =============================================================================

// Brand Colors Row - 7 core brand colors with tints and shades
// Core colors: #21D1FC, #2EE6BB, #FFD33F, #FF595A, #2B2F37, #1F2126, #FFFFFF
var PALETTE_BRAND = [
    // Tint of cyan (lighter)
    {r: 145, g: 234, b: 253},
    // Core cyan #21D1FC
    {r: 33, g: 209, b: 252},
    // Shade of cyan (darker)
    {r: 16, g: 104, b: 126},

    // Tint of teal (lighter)
    {r: 151, g: 243, b: 219},
    // Core teal #2EE6BB
    {r: 46, g: 230, b: 187},
    // Shade of teal (darker)
    {r: 23, g: 115, b: 93},

    // Tint of yellow (lighter)
    {r: 255, g: 233, b: 143},
    // Core yellow #FFD33F
    {r: 255, g: 211, b: 63},
    // Shade of yellow (darker)
    {r: 204, g: 152, b: 0},

    // Tint of coral (lighter)
    {r: 255, g: 156, b: 157},
    // Core coral #FF595A
    {r: 255, g: 89, b: 90},
    // Shade of coral (darker)
    {r: 204, g: 44, b: 45},

    // Core dark gray #2B2F37
    {r: 43, g: 47, b: 55},
    // Core darker gray #1F2126
    {r: 31, g: 33, b: 38},
    // Core white #FFFFFF
    {r: 255, g: 255, b: 255}
];

var PALETTE_SKIN = [
    // Pale tones (healthy and sickly variants)
    {r: 255, g: 250, b: 245},  // Very pale cool (porcelain)
    {r: 255, g: 240, b: 220},  // Very pale warm (peachy)
    {r: 245, g: 225, b: 210},  // Light cool (pink undertone)
    {r: 240, g: 215, b: 185},  // Light warm (golden undertone)
    // Medium tones (tan vs olive)
    {r: 220, g: 180, b: 140},  // Light-medium tan (warm/sunny)
    {r: 205, g: 185, b: 150},  // Light-medium olive (green undertone)
    {r: 190, g: 150, b: 110},  // Medium tan (standard warm)
    {r: 175, g: 160, b: 130},  // Medium olive (cooler/green)
    // Deep/dark tones
    {r: 150, g: 115, b: 85},   // Medium-deep (rich warm brown)
    {r: 100, g: 70, b: 50},    // Deep (dark brown)
    // Alien skin colors (muted tones)
    {r: 140, g: 160, b: 130},  // Muted green skin
    {r: 130, g: 150, b: 170},  // Muted blue skin
    {r: 150, g: 130, b: 160},  // Muted purple skin
    {r: 180, g: 140, b: 150},  // Muted pink skin
    // Zombie/sickly placeholders (user will replace)
    {r: 150, g: 155, b: 140},  // Placeholder 1 - sickly pale green
    {r: 140, g: 145, b: 135}   // Placeholder 2 - grayish zombie
];

var PALETTE_HAIR = [
    // Natural hair colors
    {r: 250, g: 245, b: 230},  // Platinum blonde
    {r: 230, g: 210, b: 170},  // Light blonde
    {r: 200, g: 160, b: 90},   // Golden blonde
    {r: 140, g: 110, b: 75},   // Light brown
    {r: 80, g: 60, b: 40},     // Dark brown
    {r: 50, g: 40, b: 35},     // Black
    {r: 160, g: 160, b: 155},  // Gray
    {r: 110, g: 80, b: 50},    // Brown (for brown-to-blonde ombre)
    // Fantasy/Wacky hair colors (based on reference image)
    {r: 120, g: 180, b: 220},  // Steel blue (icy blue ombre)
    {r: 255, g: 180, b: 60},   // Sunset orange-yellow
    {r: 255, g: 130, b: 150},  // Coral pink
    {r: 210, g: 180, b: 230},  // Lavender (pastel purple)
    {r: 255, g: 120, b: 140},  // Berry pink-coral
    {r: 180, g: 130, b: 220},  // Vibrant purple
    {r: 100, g: 220, b: 200},  // Teal-turquoise (aqua)
    {r: 255, g: 100, b: 60}    // Fire red-orange
];

var PALETTE_VIBRANT1 = [
    {r: 255, g: 0, b: 0}, {r: 255, g: 60, b: 0}, {r: 255, g: 120, b: 0}, {r: 255, g: 180, b: 0},
    {r: 255, g: 220, b: 0}, {r: 200, g: 255, b: 0}, {r: 120, g: 255, b: 0}, {r: 0, g: 255, b: 60},
    {r: 0, g: 255, b: 150}, {r: 0, g: 240, b: 200}, {r: 0, g: 200, b: 255}, {r: 0, g: 120, b: 255},
    {r: 60, g: 60, b: 255}, {r: 120, g: 0, b: 255}, {r: 180, g: 0, b: 255}, {r: 255, g: 0, b: 180}
];

var PALETTE_VIBRANT2 = [
    // Deep saturated colors (medium brightness 160-200, full saturation)
    {r: 200, g: 0, b: 0},     // Deep red
    {r: 200, g: 80, b: 0},    // Deep orange-red
    {r: 200, g: 130, b: 0},   // Deep orange
    {r: 200, g: 160, b: 0},   // Deep gold
    {r: 180, g: 180, b: 0},   // Deep yellow
    {r: 120, g: 180, b: 0},   // Deep lime
    {r: 0, g: 180, b: 60},    // Deep green
    {r: 0, g: 180, b: 120},   // Deep sea green
    {r: 0, g: 160, b: 180},   // Deep teal
    {r: 0, g: 100, b: 200},   // Deep cyan-blue
    {r: 0, g: 60, b: 200},    // Deep blue
    {r: 80, g: 0, b: 200},    // Deep indigo
    {r: 140, g: 0, b: 200},   // Deep purple
    {r: 180, g: 0, b: 180},   // Deep magenta
    {r: 200, g: 0, b: 120}    // Deep rose
];

var PALETTE_BOLD = [
    // Jewel tones + classic artist colors (deep saturated)
    {r: 153, g: 0, b: 76},    // Ruby (deep red-purple)
    {r: 220, g: 20, b: 60},   // Crimson
    {r: 178, g: 34, b: 34},   // Alizarin crimson
    {r: 220, g: 120, b: 0},   // Burnt orange
    {r: 184, g: 134, b: 11},  // Dark goldenrod
    {r: 85, g: 107, b: 47},   // Dark olive
    {r: 0, g: 100, b: 0},     // Dark green
    {r: 0, g: 128, b: 128},   // Teal
    {r: 0, g: 139, b: 139},   // Dark cyan/turquoise
    {r: 25, g: 25, b: 112},   // Midnight blue
    {r: 0, g: 51, b: 153},    // Cobalt/Ultramarine
    {r: 65, g: 105, b: 225},  // Royal blue/Sapphire
    {r: 75, g: 0, b: 130},    // Indigo
    {r: 102, g: 51, b: 153},  // Amethyst
    {r: 128, g: 0, b: 128}    // Deep purple
];

var PALETTE_EARTH1 = [
    // Warm earth tones - terracotta, rust, warm browns
    {r: 180, g: 100, b: 70},   // Terracotta
    {r: 170, g: 90, b: 60},    // Clay
    {r: 160, g: 82, b: 45},    // Sienna
    {r: 150, g: 75, b: 40},    // Rust
    {r: 140, g: 70, b: 35},    // Deep rust
    {r: 160, g: 100, b: 60},   // Warm brown
    {r: 140, g: 90, b: 50},    // Chestnut
    {r: 120, g: 80, b: 40},    // Saddle brown
    {r: 130, g: 100, b: 80},   // Warm taupe
    {r: 110, g: 85, b: 65},    // Warm mocha
    {r: 100, g: 75, b: 55},    // Coffee
    {r: 90, g: 65, b: 45},     // Deep coffee
    {r: 120, g: 100, b: 85},   // Warm sand
    {r: 110, g: 90, b: 75},    // Warm beige
    {r: 100, g: 80, b: 65}     // Warm tan
];

var PALETTE_EARTH2 = [
    // Cool earth tones - olive, sage, mossy greens
    {r: 107, g: 120, b: 80},   // Olive drab
    {r: 100, g: 130, b: 90},   // Sage
    {r: 85, g: 107, b: 70},    // Moss green
    {r: 128, g: 128, b: 105},  // Olive gray
    {r: 110, g: 140, b: 100},  // Artichoke
    {r: 90, g: 120, b: 85},    // Forest moss
    {r: 75, g: 100, b: 70},    // Deep sage
    {r: 120, g: 105, b: 80},   // Khaki
    {r: 140, g: 130, b: 100},  // Olive tan
    {r: 95, g: 100, b: 85},    // Lichen
    {r: 80, g: 90, b: 75},     // Slate olive
    {r: 105, g: 95, b: 80},    // Stone
    {r: 125, g: 115, b: 95},   // Putty
    {r: 100, g: 90, b: 75},    // Mushroom
    {r: 85, g: 75, b: 65}      // Deep taupe
];

var PALETTE_GRAYS = [
    // Cool grays (strong blue undertone) - 5 colors
    {r: 150, g: 160, b: 180},  // Light cool gray (blue tint visible)
    {r: 130, g: 140, b: 160},  // Medium-light cool gray
    {r: 110, g: 120, b: 140},  // Medium cool gray
    {r: 90, g: 100, b: 120},   // Medium-dark cool gray
    {r: 70, g: 80, b: 100},    // Dark cool gray

    // Neutral grays (equal RGB - pure grays) - 5 colors
    {r: 160, g: 160, b: 160},  // Light neutral gray
    {r: 140, g: 140, b: 140},  // Medium-light neutral gray
    {r: 120, g: 120, b: 120},  // Medium neutral gray
    {r: 100, g: 100, b: 100},  // Medium-dark neutral gray
    {r: 80, g: 80, b: 80},     // Dark neutral gray

    // French grays (strong warm undertone) - 5 colors
    {r: 180, g: 170, b: 160},  // Light French gray (peachy/warm tint visible)
    {r: 160, g: 150, b: 140},  // Medium-light French gray
    {r: 140, g: 130, b: 120},  // Medium French gray
    {r: 120, g: 110, b: 100},  // Medium-dark French gray
    {r: 100, g: 90, b: 80}     // Dark French gray
];

var PALETTE_PROFESSIONAL1 = [
    {r: 30, g: 50, b: 80}, {r: 40, g: 60, b: 90}, {r: 50, g: 70, b: 100}, {r: 60, g: 80, b: 110},
    {r: 70, g: 90, b: 115}, {r: 80, g: 95, b: 105}, {r: 50, g: 60, b: 55}, {r: 60, g: 75, b: 65},
    {r: 70, g: 85, b: 75}, {r: 50, g: 50, b: 50}, {r: 60, g: 60, b: 60}, {r: 80, g: 80, b: 80},
    {r: 100, g: 100, b: 100}, {r: 120, g: 120, b: 120}, {r: 220, g: 215, b: 205}, {r: 240, g: 238, b: 230}
];

var PALETTE_PROFESSIONAL2 = [
    {r: 45, g: 55, b: 75}, {r: 55, g: 65, b: 85}, {r: 65, g: 75, b: 90}, {r: 75, g: 85, b: 95},
    {r: 85, g: 90, b: 95}, {r: 90, g: 90, b: 90}, {r: 55, g: 65, b: 60}, {r: 65, g: 80, b: 70},
    {r: 75, g: 90, b: 80}, {r: 55, g: 50, b: 50}, {r: 70, g: 65, b: 65}, {r: 90, g: 85, b: 85},
    {r: 110, g: 105, b: 105}, {r: 140, g: 135, b: 135}, {r: 210, g: 205, b: 195}, {r: 230, g: 228, b: 220}
];

var PALETTE_PROFESSIONAL3 = [
    {r: 35, g: 45, b: 70}, {r: 50, g: 60, b: 80}, {r: 60, g: 70, b: 85}, {r: 70, g: 75, b: 85},
    {r: 80, g: 85, b: 90}, {r: 95, g: 95, b: 95}, {r: 45, g: 60, b: 55}, {r: 60, g: 75, b: 68},
    {r: 70, g: 85, b: 78}, {r: 45, g: 45, b: 45}, {r: 65, g: 60, b: 60}, {r: 85, g: 80, b: 80},
    {r: 115, g: 110, b: 110}, {r: 150, g: 145, b: 145}, {r: 200, g: 195, b: 185}, {r: 225, g: 223, b: 215}
];

var PALETTE_PASTEL1 = [
    // Light pastels (very light 240-255 range)
    {r: 255, g: 210, b: 210},  // Light pink
    {r: 255, g: 220, b: 200},  // Light peach
    {r: 255, g: 235, b: 190},  // Light apricot
    {r: 255, g: 245, b: 190},  // Light cream
    {r: 250, g: 255, b: 195},  // Light lemon
    {r: 225, g: 255, b: 210},  // Light mint
    {r: 210, g: 255, b: 230},  // Light seafoam
    {r: 210, g: 250, b: 250},  // Light aqua
    {r: 210, g: 240, b: 255},  // Light sky
    {r: 220, g: 230, b: 255},  // Light periwinkle
    {r: 235, g: 220, b: 255},  // Light lavender
    {r: 250, g: 220, b: 255},  // Light orchid
    {r: 255, g: 220, b: 245},  // Light rose
    {r: 255, g: 220, b: 230},  // Light blush
    {r: 255, g: 225, b: 225}   // Light shell
];

var PALETTE_PASTEL2 = [
    // Mid-tone pastels (medium brightness 200-230 range, more saturated)
    {r: 255, g: 180, b: 180},  // Mid pink
    {r: 255, g: 200, b: 170},  // Mid coral
    {r: 255, g: 220, b: 160},  // Mid peach
    {r: 250, g: 235, b: 160},  // Mid buff
    {r: 235, g: 245, b: 170},  // Mid pale yellow
    {r: 200, g: 240, b: 180},  // Mid mint green
    {r: 180, g: 240, b: 210},  // Mid seafoam
    {r: 180, g: 230, b: 240},  // Mid aqua
    {r: 180, g: 215, b: 250},  // Mid sky blue
    {r: 200, g: 205, b: 250},  // Mid periwinkle
    {r: 220, g: 190, b: 250},  // Mid lavender
    {r: 240, g: 190, b: 250},  // Mid lilac
    {r: 250, g: 190, b: 230},  // Mid mauve
    {r: 250, g: 190, b: 210},  // Mid rose
    {r: 245, g: 200, b: 200}   // Mid dusty pink
];

var PALETTE_FANTASY = [
    // Rainbow spectrum with 3-stop gradients (light→mid→dark)
    {r: 255, g: 100, b: 100},  // Red-coral (base for red spectrum)
    {r: 255, g: 150, b: 80},   // Orange (base for orange spectrum)
    {r: 255, g: 200, b: 80},   // Golden (base for yellow spectrum)
    {r: 200, g: 255, b: 100},  // Lime (base for yellow-green)
    {r: 100, g: 255, b: 150},  // Spring green (base for green)
    {r: 100, g: 255, b: 200},  // Mint (base for cyan-green)
    {r: 100, g: 220, b: 255},  // Sky (base for cyan)
    {r: 100, g: 150, b: 255},  // Azure (base for blue)
    {r: 140, g: 100, b: 255},  // Periwinkle (base for indigo)
    {r: 180, g: 100, b: 255},  // Violet (base for purple)
    {r: 220, g: 100, b: 255},  // Fuchsia (base for magenta)
    {r: 255, g: 100, b: 220},  // Hot pink (base for pink)
    {r: 255, g: 100, b: 180},  // Rose (base for pink-red)
    {r: 255, g: 120, b: 140},  // Coral pink (base for light red)
    {r: 255, g: 180, b: 120}   // Peach (base for warm)
];

var PALETTE_DARK = [
    // 20% lighter fashion darks (mix of muted and saturated)
    {r: 48, g: 24, b: 24},     // Deep maroon (muted)
    {r: 72, g: 24, b: 36},     // Burgundy (saturated)
    {r: 60, g: 30, b: 36},     // Wine (muted)
    {r: 84, g: 36, b: 42},     // Deep rose (saturated)
    {r: 24, g: 36, b: 60},     // Navy blue (saturated)
    {r: 36, g: 42, b: 54},     // Midnight (muted)
    {r: 24, g: 48, b: 42},     // Forest green (saturated)
    {r: 36, g: 54, b: 48},     // Deep moss (muted)
    {r: 48, g: 30, b: 60},     // Deep purple (saturated)
    {r: 42, g: 36, b: 48},     // Aubergine (muted)
    {r: 54, g: 42, b: 36},     // Deep brown (muted)
    {r: 60, g: 48, b: 42},     // Espresso (saturated)
    {r: 42, g: 42, b: 42},     // Charcoal (neutral)
    {r: 36, g: 36, b: 36},     // Dark gray (neutral)
    {r: 30, g: 30, b: 30}      // Near black (neutral)
];

// PALETTE_DARK2 removed - using 16 rows instead of 17

var MATERIALS = [
    {name: "Gold", base: {r: 255, g: 215, b: 0}, shadow: {r: 140, g: 90, b: 0}},        // Much darker gold shadow
    {name: "Silver", base: {r: 192, g: 192, b: 192}, shadow: {r: 80, g: 80, b: 80}},   // Much darker silver shadow
    {name: "Bronze", base: {r: 205, g: 127, b: 50}, shadow: {r: 100, g: 60, b: 25}},   // Much darker bronze shadow
    {name: "Copper", base: {r: 184, g: 115, b: 51}, shadow: {r: 110, g: 55, b: 15}},   // Much darker copper shadow
    {name: "Steel", base: {r: 176, g: 196, b: 222}, shadow: {r: 70, g: 85, b: 100}},   // Much darker steel shadow
    {name: "Chrome", base: {r: 220, g: 230, b: 240}, shadow: {r: 130, g: 140, b: 150}},// Much darker chrome shadow
    {name: "Gunmetal", base: {r: 82, g: 91, b: 99}, shadow: {r: 30, g: 35, b: 40}},  // Much darker gunmetal shadow
    {name: "Dark Wood", base: {r: 101, g: 67, b: 33}, shadow: {r: 59, g: 41, b: 20}},
    {name: "Light Wood", base: {r: 222, g: 184, b: 135}, shadow: {r: 160, g: 120, b: 80}},
    {name: "Weathered Wood", base: {r: 139, g: 125, b: 107}, shadow: {r: 90, g: 80, b: 68}},
    {name: "Silk", base: {r: 245, g: 235, b: 225}, shadow: {r: 200, g: 185, b: 170}},
    {name: "Polyester", base: {r: 75, g: 90, b: 110}, shadow: {r: 50, g: 60, b: 75}},
    {name: "Velvet", base: {r: 120, g: 40, b: 80}, shadow: {r: 60, g: 20, b: 40}},
    {name: "Leather", base: {r: 139, g: 90, b: 43}, shadow: {r: 92, g: 64, b: 30}},
    {name: "Latex", base: {r: 30, g: 30, b: 35}, shadow: {r: 10, g: 10, b: 12}},
    {name: "Glass", base: {r: 200, g: 230, b: 255}, shadow: {r: 140, g: 180, b: 220}}
];

var ROW_NAMES = [
    "Brand", "Skin", "Hair", "Vibrant1", "Vibrant2", "Bold",
    "Earth1", "Earth2", "Grays",
    "Professional1", "Professional2", "Professional3",
    "Pastel1", "Pastel2", "Fantasy",
    "Dark"
];

var ALL_PALETTES = [
    PALETTE_BRAND, PALETTE_SKIN, PALETTE_HAIR,
    PALETTE_VIBRANT1, PALETTE_VIBRANT2, PALETTE_BOLD,
    PALETTE_EARTH1, PALETTE_EARTH2, PALETTE_GRAYS,
    PALETTE_PROFESSIONAL1, PALETTE_PROFESSIONAL2, PALETTE_PROFESSIONAL3,
    PALETTE_PASTEL1, PALETTE_PASTEL2, PALETTE_FANTASY,
    PALETTE_DARK
];

// =============================================================================
// PHOTOSHOP DOCUMENT SETUP
// =============================================================================

function createAtlasDocument() {
    var docRef = app.documents.add(
        UnitValue(CONFIG.canvasWidth, "px"),
        UnitValue(CONFIG.canvasHeight, "px"),
        CONFIG.dpi,
        "Color_Swatch_Atlas",
        NewDocumentMode.RGB,
        DocumentFill.WHITE
    );
    return docRef;
}

function createLayerGroup(doc, groupName) {
    var layerGroup = doc.layerSets.add();
    layerGroup.name = groupName;
    return layerGroup;
}

function setSolidColor(r, g, b) {
    var color = new SolidColor();
    color.rgb.red = r;
    color.rgb.green = g;
    color.rgb.blue = b;
    return color;
}

// =============================================================================
// GRADIENT FILL LAYER RENDERING (v3.0)
// =============================================================================

/**
 * Create a gradient fill layer for a single swatch
 * This creates an editable gradient fill layer that can be adjusted in Photoshop UI
 * @returns {boolean} true if successful, false if gradient fill API not supported
 */
function createGradientFillLayer(doc, rowGroup, swatchName, bounds, lightColor, darkColor, direction) {
    try {
        // Set active layer to row group so new layer is created inside it
        doc.activeLayer = rowGroup;

        // Create selection for the swatch bounds
        var selectionArray = [
            [bounds.x, bounds.y],
            [bounds.x + bounds.width, bounds.y],
            [bounds.x + bounds.width, bounds.y + bounds.height],
            [bounds.x, bounds.y + bounds.height]
        ];
        doc.selection.select(selectionArray);

        // Create simple gradient using fill with foreground to background
        var angle = (direction === "diagonal") ? 135 : 90;

        // Set foreground and background colors
        app.foregroundColor = setSolidColor(lightColor.r, lightColor.g, lightColor.b);
        app.backgroundColor = setSolidColor(darkColor.r, darkColor.g, darkColor.b);

        // Create new layer in the row group
        var newLayer = rowGroup.artLayers.add();
        newLayer.name = swatchName;

        // Fill with gradient using ActionDescriptor
        var fillDesc = new ActionDescriptor();
        fillDesc.putEnumerated(charIDToTypeID("Usng"), charIDToTypeID("FlCn"), charIDToTypeID("FrgdToBckgnd"));
        fillDesc.putUnitDouble(charIDToTypeID("Angl"), charIDToTypeID("#Ang"), angle);
        fillDesc.putEnumerated(charIDToTypeID("Type"), charIDToTypeID("GrdT"), charIDToTypeID("Lnr "));
        fillDesc.putBoolean(charIDToTypeID("Dthr"), false);
        fillDesc.putBoolean(charIDToTypeID("Algn"), true);

        executeAction(charIDToTypeID("Fl  "), fillDesc, DialogModes.NO);

        // Deselect
        doc.selection.deselect();

        return true;

    } catch (e) {
        // Gradient fill layer API not supported - return false to trigger fallback
        try {
            doc.selection.deselect();
        } catch (e2) {}
        return false;
    }
}

// =============================================================================
// MANUAL GRADIENT RENDERING (v2.0 Fallback)
// =============================================================================

/**
 * Draw gradient manually by drawing multiple thin stripes
 * This method works on ALL Photoshop versions (doesn't use ActionDescriptor)
 * Used as fallback when gradient fill layer API is not available
 * @param {Object} midColor - Optional mid-tone color for 3-stop gradients (Fantasy row)
 */
function drawManualGradient(doc, bounds, lightColor, darkColor, direction, midColor) {
    var steps = CONFIG.gradientSteps;

    if (direction === "vertical") {
        var stripeHeight = bounds.height / steps;

        for (var i = 0; i < steps; i++) {
            var t = i / (steps - 1);
            var color;

            if (midColor) {
                // 3-stop gradient: dark (0-33%) → mid (33-66%) → light (66-100%)
                if (t < 0.33) {
                    // Interpolate dark → mid (0-33%)
                    var localT = t / 0.33;
                    color = interpolateColor(darkColor, midColor, localT);
                } else if (t < 0.66) {
                    // Interpolate mid → light (33-66%)
                    var localT = (t - 0.33) / 0.33;
                    color = interpolateColor(midColor, lightColor, localT);
                } else {
                    // Continue light (66-100%)
                    var localT = (t - 0.66) / 0.34;
                    color = interpolateColor(midColor, lightColor, 0.5 + localT * 0.5);
                }
            } else {
                // 2-stop gradient (original behavior)
                color = interpolateColor(darkColor, lightColor, t);
            }

            var y = bounds.y + bounds.height - (i * stripeHeight);
            var selectionArray = [
                [bounds.x, y - stripeHeight],
                [bounds.x + bounds.width, y - stripeHeight],
                [bounds.x + bounds.width, y],
                [bounds.x, y]
            ];

            doc.selection.select(selectionArray);
            doc.selection.fill(setSolidColor(color.r, color.g, color.b));
        }

    } else {
        // Diagonal gradient (from bottom-left to top-right)
        // Use MANY THIN stripes for smooth gradients without distortion
        var diagonalSteps = steps * 4; // 256 steps (4× base) for smooth diagonal gradients
        var diagonalLength = Math.sqrt(bounds.width * bounds.width + bounds.height * bounds.height);
        var stripeWidth = diagonalLength / diagonalSteps;

        for (var i = 0; i < diagonalSteps; i++) {
            var t = i / (diagonalSteps - 1);
            var color;

            if (midColor) {
                // 3-stop gradient: dark (0-33%) → mid (33-66%) → light (66-100%)
                if (t < 0.33) {
                    var localT = t / 0.33;
                    color = interpolateColor(darkColor, midColor, localT);
                } else if (t < 0.66) {
                    var localT = (t - 0.33) / 0.33;
                    color = interpolateColor(midColor, lightColor, localT);
                } else {
                    var localT = (t - 0.66) / 0.34;
                    color = interpolateColor(midColor, lightColor, 0.5 + localT * 0.5);
                }
            } else {
                // 2-stop gradient (original behavior)
                color = interpolateColor(darkColor, lightColor, t);
            }

            var progress = t;
            var x1 = bounds.x + (bounds.width * progress);
            var y1 = bounds.y + bounds.height - (bounds.height * progress);

            // Use moderate overlap (3×) to ensure coverage without cumulative rounding errors
            // More steps + less overlap = smoother gradient + accurate 128×128px squares
            var size = stripeWidth * 3;

            var selectionArray = [
                [Math.max(bounds.x, x1 - size), Math.max(bounds.y, y1 - size)],
                [Math.min(bounds.x + bounds.width, x1 + size), Math.max(bounds.y, y1 - size)],
                [Math.min(bounds.x + bounds.width, x1 + size), Math.min(bounds.y + bounds.height, y1 + size)],
                [Math.max(bounds.x, x1 - size), Math.min(bounds.y + bounds.height, y1 + size)]
            ];

            doc.selection.select(selectionArray);
            doc.selection.fill(setSolidColor(color.r, color.g, color.b));
        }
    }

    doc.selection.deselect();
}

// =============================================================================
// ROW GENERATION
// =============================================================================

/**
 * Generate a row of swatches using gradient fill layers (v3.0) or manual rendering (v2.0 fallback)
 */
function generateRow(doc, parentGroup, rowIndex, colorArray, gradientType) {
    var rowName = "Row_" + (rowIndex < 10 ? "0" : "") + rowIndex + "_" + ROW_NAMES[rowIndex];

    // v3.0: Create row group directly inside parent group (not at document level)
    var rowGroup = parentGroup.layerSets.add();
    rowGroup.name = rowName;

    // If using gradient fill layers, we'll create 16 individual gradient layers (one per column)
    // If fallback mode, we'll create one layer and draw manually
    if (CONFIG.useGradientFillLayers && !CONFIG.fallbackToManual) {
        // v3.0: Try gradient fill layers
        for (var col = 0; col < CONFIG.gridCols; col++) {
            var x = col * CONFIG.swatchSize;
            var y = rowIndex * CONFIG.swatchSize;
            var width = CONFIG.swatchSize;
            var height = CONFIG.swatchSize;

            var baseColor, shadowColor, gradientDir;

            if (col === 15) {
                baseColor = MATERIALS[rowIndex].base;
                shadowColor = MATERIALS[rowIndex].shadow;
                gradientDir = "vertical"; // All gradients are vertical (user will adjust UVs for diagonal effect)
            } else {
                baseColor = colorArray[col];
                var type = (rowIndex === 2) ? "hair" : "cloth"; // Row 2 is Hair (was Row 1 before Brand row)
                shadowColor = getShadowColor(baseColor, type);
                gradientDir = gradientType;
            }

            var bounds = {x: x, y: y, width: width, height: height};
            var swatchName = "Swatch_" + (rowIndex < 10 ? "0" : "") + rowIndex + "_" + (col < 10 ? "0" : "") + col;

            var success = createGradientFillLayer(doc, rowGroup, swatchName, bounds, baseColor, shadowColor, gradientDir);

            // If first swatch fails, switch to fallback mode
            if (!success && col === 0) {
                CONFIG.fallbackToManual = true;
                alert("Gradient fill layers not supported in your Photoshop version.\n\n" +
                      "Switching to manual rendering (v2.0).\n" +
                      "This will take longer but works on all versions.\n\n" +
                      "Continuing...");

                // Delete the row group and restart with fallback
                rowGroup.remove();
                generateRow(doc, parentGroup, rowIndex, colorArray, gradientType);
                return;
            }
        }

    } else {
        // v2.0 Enhanced: Manual rendering with INDIVIDUAL LAYERS per swatch
        // Creates 16 separate layers (one per column) instead of one layer for the whole row
        // This gives the user 256 total layers (16×16) for easier editing
        for (var col = 0; col < CONFIG.gridCols; col++) {
            var x = col * CONFIG.swatchSize;
            var y = rowIndex * CONFIG.swatchSize;
            var width = CONFIG.swatchSize;
            var height = CONFIG.swatchSize;

            var baseColor, shadowColor, gradientDir;

            var baseColor, shadowColor, gradientDir, midColor;

            if (col === 15) {
                baseColor = MATERIALS[rowIndex].base;
                shadowColor = MATERIALS[rowIndex].shadow;
                gradientDir = "vertical"; // All gradients are vertical (user will adjust UVs for diagonal effect)
                midColor = undefined; // Materials use 2-stop gradients
            } else if (rowIndex === 14) {
                // Row 14 (Fantasy) uses 3-stop gradients
                baseColor = colorArray[col];
                midColor = getMidToneColor(baseColor, "fantasy");
                shadowColor = getShadowColor(baseColor, "cloth"); // Use cloth type for Fantasy
                gradientDir = gradientType;
            } else {
                baseColor = colorArray[col];
                var type = (rowIndex === 2) ? "hair" : "cloth"; // Row 2 is Hair (was Row 1 before Brand row)
                shadowColor = getShadowColor(baseColor, type);
                gradientDir = gradientType;
                midColor = undefined; // Standard rows use 2-stop gradients
            }

            // Create individual layer for this swatch
            var swatchName = "Swatch_" + (rowIndex < 10 ? "0" : "") + rowIndex + "_" + (col < 10 ? "0" : "") + col;
            var layer = rowGroup.artLayers.add();
            layer.name = swatchName;
            doc.activeLayer = layer;

            var bounds = {x: x, y: y, width: width, height: height};
            drawManualGradient(doc, bounds, baseColor, shadowColor, gradientDir, midColor);
        }
    }
}

// =============================================================================
// MAIN EXECUTION
// =============================================================================

function main() {
    var startTime = new Date();

    var doc = createAtlasDocument();
    var layerGroup = createLayerGroup(doc, CONFIG.layerGroupName);

    try {
        doc.backgroundLayer.remove();
    } catch (e) {}

    var rowsToRender = [];
    if (CONFIG.testMode) {
        rowsToRender = CONFIG.testRows;
    } else {
        for (var i = 0; i < CONFIG.gridRows; i++) {
            rowsToRender.push(i);
        }
    }

    for (var idx = 0; idx < rowsToRender.length; idx++) {
        var i = rowsToRender[idx];
        var palette = ALL_PALETTES[i];
        var gradientType = "vertical"; // All rows use vertical gradients (user will adjust UVs for diagonal effect)

        generateRow(doc, layerGroup, i, palette, gradientType);

        if (idx % 2 === 1 && idx > 0) {
            doc.name = "Rendering... " + (idx + 1) + "/" + rowsToRender.length + " rows";
        }
    }

    // Collapse all row groups for organization
    for (var idx = 0; idx < layerGroup.layerSets.length; idx++) {
        layerGroup.layerSets[idx].collapsed = true;
    }

    doc.name = "Color_Swatch_Atlas";

    var endTime = new Date();
    var elapsed = Math.round((endTime - startTime) / 1000);

    var renderingMethod = "Enhanced Manual Rendering (v2.0) - Individual Layers";
    var editability = "To edit: Use adjustment layers, filters, or select and repaint individual swatch layers";
    var layerCount = rowsToRender.length * CONFIG.gridCols;

    var mode = CONFIG.testMode ? " (TEST MODE: " + rowsToRender.length + " rows)" : "";
    alert("Swatch Atlas Complete!" + mode + "\n\n" +
          "Document: " + CONFIG.canvasWidth + "x" + CONFIG.canvasHeight + "px\n" +
          "Rows: " + rowsToRender.length + " of " + CONFIG.gridRows + " total\n" +
          "Swatches: " + (rowsToRender.length * CONFIG.gridCols) + "\n" +
          "Layers: " + layerCount + " individual swatch layers (one per swatch)\n" +
          "Time: " + elapsed + " seconds\n" +
          "Method: " + renderingMethod + "\n\n" +
          editability);
}

try {
    main();
} catch (e) {
    alert("ERROR:\n\n" + e.toString() + "\n\nLine: " + e.line);
}
