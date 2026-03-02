/*
 * =============================================================================
 * Gradient Fill Method Diagnostic Test
 * =============================================================================
 *
 * Tests 6 different gradient fill methods to determine which works in your
 * Photoshop version. Creates a test document with 6 swatches, each using a
 * different API approach.
 *
 * Test Colors: Light Cyan (#21D1FC) to Dark Blue (#1A5F7A)
 * Swatch Size: 128×128px
 * Gradient Direction: Vertical (90°)
 *
 * Methods Tested:
 * 1. Fill with ForegroundToBackground (charIDToTypeID) - Current v3.0 approach
 * 2. Fill with ForegroundToBackground (stringIDToTypeID) - Modern API
 * 3. Gradient Overlay Layer Style - Layer effects approach
 * 4. Gradient Fill Adjustment Layer - Adjustment layer approach
 * 5. Gradient Tool Direct - Direct gradient tool invocation
 * 6. Complex Gradient Overlay - Full descriptor setup
 *
 * Version: 1.0
 * Date: 2026-02-03
 * =============================================================================
 */

// Test configuration
var TEST_CONFIG = {
    swatchSize: 128,
    canvasWidth: 384,  // 3 columns × 128px
    canvasHeight: 256, // 2 rows × 128px
    spacing: 0,

    // Test colors - Light Cyan to Dark Blue
    lightColor: {r: 33, g: 209, b: 252},   // #21D1FC
    darkColor: {r: 26, g: 95, b: 122},     // #1A5F7A

    gradientAngle: 90  // Vertical gradient
};

// Test results storage
var testResults = [];

// Helper function to create solid color
function setSolidColor(r, g, b) {
    var color = new SolidColor();
    color.rgb.red = r;
    color.rgb.green = g;
    color.rgb.blue = b;
    return color;
}

// =============================================================================
// TEST METHOD 1: Fill with ForegroundToBackground (charIDToTypeID)
// =============================================================================
function test1_FillForegroundToBackgroundCharID(doc, layer, bounds) {
    try {
        // Select bounds
        doc.selection.select([
            [bounds.x, bounds.y],
            [bounds.x + bounds.width, bounds.y],
            [bounds.x + bounds.width, bounds.y + bounds.height],
            [bounds.x, bounds.y + bounds.height]
        ]);

        // Set colors
        app.foregroundColor = setSolidColor(TEST_CONFIG.lightColor.r, TEST_CONFIG.lightColor.g, TEST_CONFIG.lightColor.b);
        app.backgroundColor = setSolidColor(TEST_CONFIG.darkColor.r, TEST_CONFIG.darkColor.g, TEST_CONFIG.darkColor.b);

        // Fill with gradient using charIDToTypeID
        var fillDesc = new ActionDescriptor();
        fillDesc.putEnumerated(charIDToTypeID("Usng"), charIDToTypeID("FlCn"), charIDToTypeID("FrgdToBckgnd"));
        fillDesc.putUnitDouble(charIDToTypeID("Angl"), charIDToTypeID("#Ang"), TEST_CONFIG.gradientAngle);
        fillDesc.putEnumerated(charIDToTypeID("Type"), charIDToTypeID("GrdT"), charIDToTypeID("Lnr "));
        fillDesc.putBoolean(charIDToTypeID("Dthr"), false);
        fillDesc.putBoolean(charIDToTypeID("Algn"), true);

        executeAction(charIDToTypeID("Fl  "), fillDesc, DialogModes.NO);

        doc.selection.deselect();
        return {success: true, method: "Method 1: Fill FgToBg (charID)", error: null};
    } catch (e) {
        try { doc.selection.deselect(); } catch (e2) {}
        return {success: false, method: "Method 1: Fill FgToBg (charID)", error: e.toString()};
    }
}

// =============================================================================
// TEST METHOD 2: Fill with ForegroundToBackground (stringIDToTypeID)
// =============================================================================
function test2_FillForegroundToBackgroundStringID(doc, layer, bounds) {
    try {
        // Select bounds
        doc.selection.select([
            [bounds.x, bounds.y],
            [bounds.x + bounds.width, bounds.y],
            [bounds.x + bounds.width, bounds.y + bounds.height],
            [bounds.x, bounds.y + bounds.height]
        ]);

        // Set colors
        app.foregroundColor = setSolidColor(TEST_CONFIG.lightColor.r, TEST_CONFIG.lightColor.g, TEST_CONFIG.lightColor.b);
        app.backgroundColor = setSolidColor(TEST_CONFIG.darkColor.r, TEST_CONFIG.darkColor.g, TEST_CONFIG.darkColor.b);

        // Fill with gradient using stringIDToTypeID
        var fillDesc = new ActionDescriptor();
        fillDesc.putEnumerated(stringIDToTypeID("using"), stringIDToTypeID("fillContents"), stringIDToTypeID("foregroundToBackground"));
        fillDesc.putUnitDouble(stringIDToTypeID("angle"), stringIDToTypeID("#Ang"), TEST_CONFIG.gradientAngle);
        fillDesc.putEnumerated(stringIDToTypeID("type"), stringIDToTypeID("gradientType"), stringIDToTypeID("linear"));
        fillDesc.putBoolean(stringIDToTypeID("dither"), false);
        fillDesc.putBoolean(stringIDToTypeID("align"), true);

        executeAction(stringIDToTypeID("fill"), fillDesc, DialogModes.NO);

        doc.selection.deselect();
        return {success: true, method: "Method 2: Fill FgToBg (stringID)", error: null};
    } catch (e) {
        try { doc.selection.deselect(); } catch (e2) {}
        return {success: false, method: "Method 2: Fill FgToBg (stringID)", error: e.toString()};
    }
}

// =============================================================================
// TEST METHOD 3: Gradient Overlay Layer Style
// =============================================================================
function test3_GradientOverlayLayerStyle(doc, layer, bounds) {
    try {
        // Select bounds and fill with base color first
        doc.selection.select([
            [bounds.x, bounds.y],
            [bounds.x + bounds.width, bounds.y],
            [bounds.x + bounds.width, bounds.y + bounds.height],
            [bounds.x, bounds.y + bounds.height]
        ]);

        // Fill with mid-tone base color
        var midR = Math.round((TEST_CONFIG.lightColor.r + TEST_CONFIG.darkColor.r) / 2);
        var midG = Math.round((TEST_CONFIG.lightColor.g + TEST_CONFIG.darkColor.g) / 2);
        var midB = Math.round((TEST_CONFIG.lightColor.b + TEST_CONFIG.darkColor.b) / 2);
        app.foregroundColor = setSolidColor(midR, midG, midB);
        doc.selection.fill(app.foregroundColor);
        doc.selection.deselect();

        // Apply Gradient Overlay layer style
        var styleDesc = new ActionDescriptor();
        var effectsDesc = new ActionDescriptor();
        var gradientOverlayDesc = new ActionDescriptor();

        // Create gradient
        var gradientDesc = new ActionDescriptor();
        var colorList = new ActionList();

        // Light color stop (0%)
        var stop1 = new ActionDescriptor();
        var color1 = new ActionDescriptor();
        color1.putDouble(stringIDToTypeID("red"), TEST_CONFIG.lightColor.r);
        color1.putDouble(stringIDToTypeID("grain"), TEST_CONFIG.lightColor.g);
        color1.putDouble(stringIDToTypeID("blue"), TEST_CONFIG.lightColor.b);
        stop1.putObject(stringIDToTypeID("color"), stringIDToTypeID("RGBColor"), color1);
        stop1.putEnumerated(stringIDToTypeID("type"), stringIDToTypeID("colorStopType"), stringIDToTypeID("userStop"));
        stop1.putInteger(stringIDToTypeID("location"), 0);
        stop1.putInteger(stringIDToTypeID("midpoint"), 50);
        colorList.putObject(stringIDToTypeID("colorStop"), stop1);

        // Dark color stop (100%)
        var stop2 = new ActionDescriptor();
        var color2 = new ActionDescriptor();
        color2.putDouble(stringIDToTypeID("red"), TEST_CONFIG.darkColor.r);
        color2.putDouble(stringIDToTypeID("grain"), TEST_CONFIG.darkColor.g);
        color2.putDouble(stringIDToTypeID("blue"), TEST_CONFIG.darkColor.b);
        stop2.putObject(stringIDToTypeID("color"), stringIDToTypeID("RGBColor"), color2);
        stop2.putEnumerated(stringIDToTypeID("type"), stringIDToTypeID("colorStopType"), stringIDToTypeID("userStop"));
        stop2.putInteger(stringIDToTypeID("location"), 4096);
        stop2.putInteger(stringIDToTypeID("midpoint"), 50);
        colorList.putObject(stringIDToTypeID("colorStop"), stop2);

        gradientDesc.putList(stringIDToTypeID("colors"), colorList);
        gradientDesc.putEnumerated(stringIDToTypeID("gradientForm"), stringIDToTypeID("gradientForm"), stringIDToTypeID("customStops"));

        gradientOverlayDesc.putBoolean(stringIDToTypeID("enabled"), true);
        gradientOverlayDesc.putEnumerated(stringIDToTypeID("mode"), stringIDToTypeID("blendMode"), stringIDToTypeID("normal"));
        gradientOverlayDesc.putUnitDouble(stringIDToTypeID("opacity"), stringIDToTypeID("#Prc"), 100);
        gradientOverlayDesc.putObject(stringIDToTypeID("gradient"), stringIDToTypeID("gradient"), gradientDesc);
        gradientOverlayDesc.putUnitDouble(stringIDToTypeID("angle"), stringIDToTypeID("#Ang"), TEST_CONFIG.gradientAngle);
        gradientOverlayDesc.putEnumerated(stringIDToTypeID("type"), stringIDToTypeID("gradientType"), stringIDToTypeID("linear"));
        gradientOverlayDesc.putBoolean(stringIDToTypeID("reverse"), false);
        gradientOverlayDesc.putBoolean(stringIDToTypeID("align"), true);
        gradientOverlayDesc.putUnitDouble(stringIDToTypeID("scale"), stringIDToTypeID("#Prc"), 100);

        effectsDesc.putObject(stringIDToTypeID("gradientFill"), stringIDToTypeID("gradientFill"), gradientOverlayDesc);
        styleDesc.putObject(stringIDToTypeID("to"), stringIDToTypeID("layerEffects"), effectsDesc);

        executeAction(stringIDToTypeID("set"), styleDesc, DialogModes.NO);

        return {success: true, method: "Method 3: Gradient Overlay Style", error: null};
    } catch (e) {
        try { doc.selection.deselect(); } catch (e2) {}
        return {success: false, method: "Method 3: Gradient Overlay Style", error: e.toString()};
    }
}

// =============================================================================
// TEST METHOD 4: Gradient Fill Adjustment Layer
// =============================================================================
function test4_GradientFillAdjustmentLayer(doc, layer, bounds) {
    try {
        // Note: This creates a fill layer, not an adjustment layer
        // We'll create it and then crop to bounds

        // Create gradient fill layer
        var fillDesc = new ActionDescriptor();
        var gradientDesc = new ActionDescriptor();
        var colorList = new ActionList();

        // Light color stop (0%)
        var stop1 = new ActionDescriptor();
        var color1 = new ActionDescriptor();
        color1.putDouble(stringIDToTypeID("red"), TEST_CONFIG.lightColor.r);
        color1.putDouble(stringIDToTypeID("grain"), TEST_CONFIG.lightColor.g);
        color1.putDouble(stringIDToTypeID("blue"), TEST_CONFIG.lightColor.b);
        stop1.putObject(stringIDToTypeID("color"), stringIDToTypeID("RGBColor"), color1);
        stop1.putEnumerated(stringIDToTypeID("type"), stringIDToTypeID("colorStopType"), stringIDToTypeID("userStop"));
        stop1.putInteger(stringIDToTypeID("location"), 0);
        stop1.putInteger(stringIDToTypeID("midpoint"), 50);
        colorList.putObject(stringIDToTypeID("colorStop"), stop1);

        // Dark color stop (100%)
        var stop2 = new ActionDescriptor();
        var color2 = new ActionDescriptor();
        color2.putDouble(stringIDToTypeID("red"), TEST_CONFIG.darkColor.r);
        color2.putDouble(stringIDToTypeID("grain"), TEST_CONFIG.darkColor.g);
        color2.putDouble(stringIDToTypeID("blue"), TEST_CONFIG.darkColor.b);
        stop2.putObject(stringIDToTypeID("color"), stringIDToTypeID("RGBColor"), color2);
        stop2.putEnumerated(stringIDToTypeID("type"), stringIDToTypeID("colorStopType"), stringIDToTypeID("userStop"));
        stop2.putInteger(stringIDToTypeID("location"), 4096);
        stop2.putInteger(stringIDToTypeID("midpoint"), 50);
        colorList.putObject(stringIDToTypeID("colorStop"), stop2);

        gradientDesc.putList(stringIDToTypeID("colors"), colorList);
        gradientDesc.putEnumerated(stringIDToTypeID("gradientForm"), stringIDToTypeID("gradientForm"), stringIDToTypeID("customStops"));

        fillDesc.putObject(stringIDToTypeID("gradient"), stringIDToTypeID("gradient"), gradientDesc);
        fillDesc.putUnitDouble(stringIDToTypeID("angle"), stringIDToTypeID("#Ang"), TEST_CONFIG.gradientAngle);
        fillDesc.putEnumerated(stringIDToTypeID("type"), stringIDToTypeID("gradientType"), stringIDToTypeID("linear"));

        var layerDesc = new ActionDescriptor();
        layerDesc.putObject(stringIDToTypeID("type"), stringIDToTypeID("gradientLayer"), fillDesc);

        var makeDesc = new ActionDescriptor();
        makeDesc.putObject(stringIDToTypeID("null"), stringIDToTypeID("contentLayer"), layerDesc);

        executeAction(stringIDToTypeID("make"), makeDesc, DialogModes.NO);

        // Crop to bounds using layer mask
        doc.selection.select([
            [bounds.x, bounds.y],
            [bounds.x + bounds.width, bounds.y],
            [bounds.x + bounds.width, bounds.y + bounds.height],
            [bounds.x, bounds.y + bounds.height]
        ]);

        // Create layer mask from selection
        executeAction(stringIDToTypeID("make"), new ActionDescriptor().putClass(stringIDToTypeID("null"), stringIDToTypeID("channel")), DialogModes.NO);
        doc.selection.deselect();

        return {success: true, method: "Method 4: Gradient Fill Layer", error: null};
    } catch (e) {
        try { doc.selection.deselect(); } catch (e2) {}
        return {success: false, method: "Method 4: Gradient Fill Layer", error: e.toString()};
    }
}

// =============================================================================
// TEST METHOD 5: Gradient Tool Direct Invocation
// =============================================================================
function test5_GradientToolDirect(doc, layer, bounds) {
    try {
        // Select bounds
        doc.selection.select([
            [bounds.x, bounds.y],
            [bounds.x + bounds.width, bounds.y],
            [bounds.x + bounds.width, bounds.y + bounds.height],
            [bounds.x, bounds.y + bounds.height]
        ]);

        // Set colors
        app.foregroundColor = setSolidColor(TEST_CONFIG.lightColor.r, TEST_CONFIG.lightColor.g, TEST_CONFIG.lightColor.b);
        app.backgroundColor = setSolidColor(TEST_CONFIG.darkColor.r, TEST_CONFIG.darkColor.g, TEST_CONFIG.darkColor.b);

        // Use gradient tool directly
        var gradientDesc = new ActionDescriptor();
        var gradientFillDesc = new ActionDescriptor();

        gradientFillDesc.putEnumerated(stringIDToTypeID("gradientForm"), stringIDToTypeID("gradientForm"), stringIDToTypeID("foregroundToBackground"));

        gradientDesc.putObject(stringIDToTypeID("gradient"), stringIDToTypeID("gradient"), gradientFillDesc);
        gradientDesc.putUnitDouble(stringIDToTypeID("angle"), stringIDToTypeID("#Ang"), TEST_CONFIG.gradientAngle);
        gradientDesc.putEnumerated(stringIDToTypeID("type"), stringIDToTypeID("gradientType"), stringIDToTypeID("linear"));

        // Calculate start and end points (vertical gradient)
        var startPoint = new ActionDescriptor();
        startPoint.putUnitDouble(stringIDToTypeID("horizontal"), stringIDToTypeID("#Pxl"), bounds.x + bounds.width / 2);
        startPoint.putUnitDouble(stringIDToTypeID("vertical"), stringIDToTypeID("#Pxl"), bounds.y + bounds.height);

        var endPoint = new ActionDescriptor();
        endPoint.putUnitDouble(stringIDToTypeID("horizontal"), stringIDToTypeID("#Pxl"), bounds.x + bounds.width / 2);
        endPoint.putUnitDouble(stringIDToTypeID("vertical"), stringIDToTypeID("#Pxl"), bounds.y);

        gradientDesc.putObject(stringIDToTypeID("from"), stringIDToTypeID("point"), startPoint);
        gradientDesc.putObject(stringIDToTypeID("to"), stringIDToTypeID("point"), endPoint);
        gradientDesc.putBoolean(stringIDToTypeID("dither"), true);

        executeAction(stringIDToTypeID("gradientEvent"), gradientDesc, DialogModes.NO);

        doc.selection.deselect();
        return {success: true, method: "Method 5: Gradient Tool Direct", error: null};
    } catch (e) {
        try { doc.selection.deselect(); } catch (e2) {}
        return {success: false, method: "Method 5: Gradient Tool Direct", error: e.toString()};
    }
}

// =============================================================================
// TEST METHOD 6: Complex Gradient Overlay (Full Descriptor)
// =============================================================================
function test6_ComplexGradientOverlay(doc, layer, bounds) {
    try {
        // Select bounds and fill with base color first
        doc.selection.select([
            [bounds.x, bounds.y],
            [bounds.x + bounds.width, bounds.y],
            [bounds.x + bounds.width, bounds.y + bounds.height],
            [bounds.x, bounds.y + bounds.height]
        ]);

        // Fill with mid-tone base color
        var midR = Math.round((TEST_CONFIG.lightColor.r + TEST_CONFIG.darkColor.r) / 2);
        var midG = Math.round((TEST_CONFIG.lightColor.g + TEST_CONFIG.darkColor.g) / 2);
        var midB = Math.round((TEST_CONFIG.lightColor.b + TEST_CONFIG.darkColor.b) / 2);
        app.foregroundColor = setSolidColor(midR, midG, midB);
        doc.selection.fill(app.foregroundColor);
        doc.selection.deselect();

        // Apply complex gradient overlay with full transparency list
        var styleDesc = new ActionDescriptor();
        var effectsDesc = new ActionDescriptor();
        var gradientFillDesc = new ActionDescriptor();

        // Create gradient with transparency stops
        var gradientDesc = new ActionDescriptor();

        // Color stops
        var colorList = new ActionList();
        var stop1 = new ActionDescriptor();
        var color1 = new ActionDescriptor();
        color1.putDouble(charIDToTypeID("Rd  "), TEST_CONFIG.lightColor.r);
        color1.putDouble(charIDToTypeID("Grn "), TEST_CONFIG.lightColor.g);
        color1.putDouble(charIDToTypeID("Bl  "), TEST_CONFIG.lightColor.b);
        stop1.putObject(charIDToTypeID("Clr "), charIDToTypeID("RGBC"), color1);
        stop1.putEnumerated(charIDToTypeID("Type"), charIDToTypeID("Clry"), charIDToTypeID("UsrS"));
        stop1.putInteger(charIDToTypeID("Lctn"), 0);
        colorList.putObject(charIDToTypeID("Clrt"), stop1);

        var stop2 = new ActionDescriptor();
        var color2 = new ActionDescriptor();
        color2.putDouble(charIDToTypeID("Rd  "), TEST_CONFIG.darkColor.r);
        color2.putDouble(charIDToTypeID("Grn "), TEST_CONFIG.darkColor.g);
        color2.putDouble(charIDToTypeID("Bl  "), TEST_CONFIG.darkColor.b);
        stop2.putObject(charIDToTypeID("Clr "), charIDToTypeID("RGBC"), color2);
        stop2.putEnumerated(charIDToTypeID("Type"), charIDToTypeID("Clry"), charIDToTypeID("UsrS"));
        stop2.putInteger(charIDToTypeID("Lctn"), 4096);
        colorList.putObject(charIDToTypeID("Clrt"), stop2);

        gradientDesc.putList(charIDToTypeID("Clrs"), colorList);

        // Transparency stops
        var transparencyList = new ActionList();
        var trans1 = new ActionDescriptor();
        trans1.putUnitDouble(charIDToTypeID("Opct"), charIDToTypeID("#Prc"), 100);
        trans1.putInteger(charIDToTypeID("Lctn"), 0);
        trans1.putInteger(charIDToTypeID("Mdpn"), 50);
        transparencyList.putObject(charIDToTypeID("TrnS"), trans1);

        var trans2 = new ActionDescriptor();
        trans2.putUnitDouble(charIDToTypeID("Opct"), charIDToTypeID("#Prc"), 100);
        trans2.putInteger(charIDToTypeID("Lctn"), 4096);
        trans2.putInteger(charIDToTypeID("Mdpn"), 50);
        transparencyList.putObject(charIDToTypeID("TrnS"), trans2);

        gradientDesc.putList(charIDToTypeID("Trns"), transparencyList);
        gradientDesc.putEnumerated(charIDToTypeID("GrdF"), charIDToTypeID("GrdF"), charIDToTypeID("CstS"));

        gradientFillDesc.putBoolean(charIDToTypeID("enab"), true);
        gradientFillDesc.putEnumerated(charIDToTypeID("Md  "), charIDToTypeID("BlnM"), charIDToTypeID("Nrml"));
        gradientFillDesc.putUnitDouble(charIDToTypeID("Opct"), charIDToTypeID("#Prc"), 100);
        gradientFillDesc.putObject(charIDToTypeID("Grad"), charIDToTypeID("Grdn"), gradientDesc);
        gradientFillDesc.putUnitDouble(charIDToTypeID("Angl"), charIDToTypeID("#Ang"), TEST_CONFIG.gradientAngle);
        gradientFillDesc.putEnumerated(charIDToTypeID("Type"), charIDToTypeID("GrdT"), charIDToTypeID("Lnr "));
        gradientFillDesc.putBoolean(charIDToTypeID("Rvrs"), false);
        gradientFillDesc.putBoolean(charIDToTypeID("Algn"), true);
        gradientFillDesc.putUnitDouble(charIDToTypeID("Scl "), charIDToTypeID("#Prc"), 100);

        effectsDesc.putObject(charIDToTypeID("GrFl"), charIDToTypeID("GrFl"), gradientFillDesc);
        styleDesc.putObject(charIDToTypeID("T   "), charIDToTypeID("Lefx"), effectsDesc);

        executeAction(charIDToTypeID("setd"), styleDesc, DialogModes.NO);

        return {success: true, method: "Method 6: Complex Overlay (charID)", error: null};
    } catch (e) {
        try { doc.selection.deselect(); } catch (e2) {}
        return {success: false, method: "Method 6: Complex Overlay (charID)", error: e.toString()};
    }
}

// =============================================================================
// MAIN TEST EXECUTION
// =============================================================================
function runDiagnosticTests() {
    var startTime = new Date();

    // Create test document
    var doc = app.documents.add(
        UnitValue(TEST_CONFIG.canvasWidth, "px"),
        UnitValue(TEST_CONFIG.canvasHeight, "px"),
        72,
        "Gradient_Diagnostic_Test",
        NewDocumentMode.RGB,
        DocumentFill.WHITE
    );

    // Create layer group
    var testGroup = doc.layerSets.add();
    testGroup.name = "Diagnostic_Tests";

    // Test methods array
    var testMethods = [
        {name: "Method_1_CharID_Fill", func: test1_FillForegroundToBackgroundCharID, row: 0, col: 0},
        {name: "Method_2_StringID_Fill", func: test2_FillForegroundToBackgroundStringID, row: 0, col: 1},
        {name: "Method_3_LayerStyle", func: test3_GradientOverlayLayerStyle, row: 0, col: 2},
        {name: "Method_4_FillLayer", func: test4_GradientFillAdjustmentLayer, row: 1, col: 0},
        {name: "Method_5_GradientTool", func: test5_GradientToolDirect, row: 1, col: 1},
        {name: "Method_6_ComplexOverlay", func: test6_ComplexGradientOverlay, row: 1, col: 2}
    ];

    // Run each test
    for (var i = 0; i < testMethods.length; i++) {
        var test = testMethods[i];

        // Create layer for this test
        var layer = testGroup.artLayers.add();
        layer.name = test.name;
        doc.activeLayer = layer;

        // Calculate bounds
        var bounds = {
            x: test.col * TEST_CONFIG.swatchSize,
            y: test.row * TEST_CONFIG.swatchSize,
            width: TEST_CONFIG.swatchSize,
            height: TEST_CONFIG.swatchSize
        };

        // Run test
        var result = test.func(doc, layer, bounds);
        result.layerName = test.name;
        testResults.push(result);

        // Add text label if test failed
        if (!result.success) {
            try {
                var textLayer = doc.artLayers.add();
                textLayer.kind = LayerKind.TEXT;
                textLayer.name = test.name + "_FAILED";
                var textItem = textLayer.textItem;
                textItem.contents = "X";
                textItem.size = 72;
                textItem.color = setSolidColor(255, 0, 0);
                textItem.position = [bounds.x + 40, bounds.y + 90];
                textLayer.move(testGroup, ElementPlacement.INSIDE);
            } catch (e) {}
        }
    }

    // Remove background layer
    try {
        doc.backgroundLayer.remove();
    } catch (e) {}

    var endTime = new Date();
    var elapsed = Math.round((endTime - startTime) / 1000);

    // Generate results report
    var report = "=== GRADIENT FILL DIAGNOSTIC RESULTS ===\n\n";
    report += "Photoshop Version: " + app.version + "\n";
    report += "Test Duration: " + elapsed + " seconds\n";
    report += "Test Colors: Cyan (#21D1FC) to Blue (#1A5F7A)\n\n";

    var successCount = 0;
    for (var i = 0; i < testResults.length; i++) {
        var result = testResults[i];
        if (result.success) {
            successCount++;
            report += "✓ " + result.method + " - SUCCESS\n";
        } else {
            report += "✗ " + result.method + " - FAILED\n";
            report += "  Error: " + result.error + "\n";
        }
    }

    report += "\n=== SUMMARY ===\n";
    report += successCount + " of " + testResults.length + " methods succeeded\n\n";

    if (successCount > 0) {
        report += "RECOMMENDATION:\n";
        for (var i = 0; i < testResults.length; i++) {
            if (testResults[i].success) {
                report += "Use " + testResults[i].method + "\n";
                report += "(Layer: " + testResults[i].layerName + ")\n";
                break;
            }
        }
    } else {
        report += "WARNING: No gradient fill methods worked!\n";
        report += "Fallback to manual rendering (v2.0) required.\n";
    }

    report += "\n=== NEXT STEPS ===\n";
    report += "1. Review the test document visually\n";
    report += "2. Note which swatches show gradients\n";
    report += "3. Share this report with Claude Code\n";
    report += "4. Working methods will be implemented in main script\n";

    alert(report);

    // Save report to file (optional - commented out)
    // var reportFile = new File("~/Desktop/gradient_diagnostic_report.txt");
    // reportFile.open("w");
    // reportFile.write(report);
    // reportFile.close();
}

// Run tests
try {
    runDiagnosticTests();
} catch (e) {
    alert("DIAGNOSTIC ERROR:\n\n" + e.toString() + "\n\nLine: " + e.line);
}
