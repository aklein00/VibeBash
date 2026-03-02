"""
Create a simple PNG icon for EdgeAverager
"""

try:
    from PIL import Image, ImageDraw

    # Create 256x256 image with dark gray background
    img = Image.new('RGB', (256, 256), color='#2a2a2a')
    draw = ImageDraw.Draw(img)

    # Orange color for original edges (faded)
    orange = (255, 136, 68, 100)
    # Blue color for averaged edge
    blue = (68, 170, 255)

    # Draw three parallel curved lines (simplified as straight for PIL)
    # Top edge (faded)
    draw.line([(40, 80), (216, 80)], fill=orange, width=6)
    # Middle edge (faded)
    draw.line([(40, 128), (216, 128)], fill=orange, width=6)
    # Bottom edge (faded)
    draw.line([(40, 176), (216, 176)], fill=orange, width=6)

    # Draw averaged edge (bright blue, thicker)
    draw.line([(40, 128), (216, 128)], fill=blue, width=10)

    # Draw control points
    points = [(40, 128), (90, 120), (140, 128), (190, 136), (216, 128)]
    for x, y in points:
        draw.ellipse([x-4, y-4, x+4, y+4], fill=blue)

    # Draw arrow at top
    draw.polygon([(128, 50), (138, 60), (118, 60)], fill=blue)

    # Save
    icon_path = '/Users/arthurklein/Library/Preferences/Autodesk/maya/2025/scripts/EdgeAverager/icon.png'
    img.save(icon_path)
    print(f"✓ Icon created: {icon_path}")

except ImportError:
    print("PIL not available, using SVG instead")
    print("Icon will use Maya default edge icon")

if __name__ == "__main__":
    pass
