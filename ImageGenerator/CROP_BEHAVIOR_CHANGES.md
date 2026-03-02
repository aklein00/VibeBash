# Image Cropping Behavior Changes

## Summary of Changes

The batch image generator (`generate_images.py`) has been updated to **disable cropping by default** and make it an opt-in feature. This prevents unwanted loss of image content.

## What Changed

### Before
- All images were automatically center-cropped to exact target dimensions
- Up to 47.7% of generated image area could be discarded
- No control over whether cropping happened

### After
- Images are kept at full DALL-E resolution by default
- Cropping is opt-in via `"crop": true` field in JSON
- Both raw and final versions are saved (raw/ and final_cropped/ folders)

## Why This Matters

**DALL-E only generates 3 resolutions:**
- 1024x1024 (square)
- 1792x1024 (wide)
- 1024x1792 (tall)

**Example of old behavior:**
- User requests 1200x800 image
- DALL-E generates 1792x1024
- Script cropped to 1200x800
- **Lost 592px width + 224px height = 47.7% of image**

**New behavior:**
- User requests 1200x800 image
- DALL-E generates 1792x1024
- Script keeps full 1792x1024 (unless `"crop": true` specified)
- **No loss of content**

## How to Use

### Keep Full Size (Default)

```json
{
  "images": [
    {
      "id": "character-sprite",
      "image": "Fantasy warrior with sword",
      "size": "512x512"
    }
  ]
}
```

Or explicitly:

```json
{
  "id": "landscape",
  "image": "Mountain scene",
  "size": "600x400",
  "crop": false
}
```

### Crop to Exact Dimensions (Opt-in)

```json
{
  "id": "ui-button",
  "image": "Game button with icon",
  "size": "256x128",
  "crop": true
}
```

## When to Enable Cropping

**Use `"crop": true` for:**
- UI elements (buttons, icons, badges)
- Splash screens with specific aspect requirements
- Assets that must fit exact layout specifications
- Any case where precise pixel dimensions are critical

**Use default (no crop) for:**
- Characters and sprites (composition matters)
- Environments and backgrounds (full frame important)
- Objects and props (may have off-center subjects)
- Most general use cases

## Output Behavior

### Without Cropping (Default)
```
generated_images_raw/image-name.png          → 1792x1024 (DALL-E native)
generated_images_final_cropped/image-name.png → 1792x1024 (copy of raw)
```

Console output:
```
SUCCESS: Saved raw image to 'generated_images_raw/image-name.png'
Keeping full-size image (no crop)
SUCCESS: Saved full-size image (1792x1024) to 'generated_images_final_cropped/image-name.png'
         (Requested size was 600x400, kept DALL-E native resolution)
```

### With Cropping (`"crop": true`)
```
generated_images_raw/image-name.png          → 1024x1024 (DALL-E native)
generated_images_final_cropped/image-name.png → 256x256 (cropped)
```

Console output:
```
SUCCESS: Saved raw image to 'generated_images_raw/image-name.png'
Cropping image to your specified size: 256x256...
SUCCESS: Saved cropped image (256x256) to 'generated_images_final_cropped/image-name.png'
```

## Testing

Run the test file to verify behavior:

```bash
cd ImageGenerator
python3 generate_images.py
# Use test_crop_behavior.json to test both modes
```

Expected results:
- `test-no-crop.png`: Full 1792x1024 size (requested 600x400)
- `test-with-crop.png`: Exact 256x256 size (cropped from 1024x1024)

## Backward Compatibility

**Existing JSON files will work without modification:**
- If `crop` field is missing, defaults to `false` (no crop)
- Images will be kept at full size instead of cropped
- If you want the old behavior (cropping), add `"crop": true` to each image

## Files Modified

1. **generate_images.py**
   - Added `import shutil` for file copying
   - Added `crop_enabled = item.get('crop', False)` check
   - Split logic into crop/no-crop branches
   - Updated console messages

2. **CLAUDE.md** (project documentation)
   - Updated "How It Works" section
   - Added "Image Cropping Behavior" section
   - Updated examples to show `crop` field

3. **~/.claude/CLAUDE.md** (global documentation)
   - Added cropping behavior notes
   - Updated batch generation examples

## Examples

See these files for complete examples:
- `image_prompts_crop_example.json` - Shows both crop modes
- `test_crop_behavior.json` - Simple test cases

## Benefits

✅ Preserves full AI-generated composition by default
✅ No unwanted loss of image content (up to 47.7% saved)
✅ User control over when to crop
✅ Clear visual feedback about what happened
✅ Both raw and final versions always saved
✅ Backward compatible with existing JSON files
