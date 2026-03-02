#!/usr/bin/env python3
"""
Batch Image Generator using Google Imagen 3
Supports style-aware generation with opt-in cropping
"""
import os
import json
import sys
import shutil
from PIL import Image
from io import BytesIO

# --- CONFIGURATION ---
# Google Cloud Project for Vertex AI
GOOGLE_PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "abiding-lead-486316-t7")
GOOGLE_LOCATION = "us-central1"

MANIFEST_FILE = "image_prompts.json"

# Output folders
RAW_OUTPUT_FOLDER = "generated_images_raw"
CROPPED_FOLDER = "generated_images_final_cropped"

# --- SCRIPT LOGIC ---

def detect_asset_type(prompt):
    """Detect asset type from prompt text for style matching."""
    prompt_lower = prompt.lower()

    # Character keywords
    char_keywords = ["character", "sprite", "avatar", "person", "hero", "enemy", "npc",
                     "player", "fighter", "wizard", "warrior", "animal", "creature"]
    if any(keyword in prompt_lower for keyword in char_keywords):
        return "characters"

    # Environment keywords
    env_keywords = ["background", "landscape", "scene", "level", "world", "map",
                   "terrain", "biome", "location", "setting", "environment", "facility"]
    if any(keyword in prompt_lower for keyword in env_keywords):
        return "environment"

    # UI keywords
    ui_keywords = ["button", "icon", "menu", "panel", "hud", "interface", "ui",
                  "banner", "badge", "notification", "popup", "dialog", "navigation"]
    if any(keyword in prompt_lower for keyword in ui_keywords):
        return "ui"

    # Object keywords
    obj_keywords = ["item", "object", "prop", "collectible", "pickup", "powerup",
                   "weapon", "tool", "equipment", "consumable", "resource", "material"]
    if any(keyword in prompt_lower for keyword in obj_keywords):
        return "objects"

    return None  # Default - use general style description

def generate_image_google(prompt, width, height, seed=None):
    """Generate image using Google Imagen via Vertex AI SDK"""
    try:
        from google.cloud import aiplatform
        from vertexai.preview.vision_models import ImageGenerationModel
    except ImportError:
        return None, "Error: Install google-cloud-aiplatform: pip3 install google-cloud-aiplatform"

    try:
        # Initialize Vertex AI
        GOOGLE_PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "abiding-lead-486316-t7")
        GOOGLE_LOCATION = "us-central1"
        aiplatform.init(project=GOOGLE_PROJECT_ID, location=GOOGLE_LOCATION)

        # Map dimensions to aspect ratio
        aspect_ratio_value = width / height
        if 0.9 <= aspect_ratio_value <= 1.1:
            aspect_ratio = "1:1"
        elif aspect_ratio_value > 1.5:
            aspect_ratio = "16:9"
        elif aspect_ratio_value > 1.2:
            aspect_ratio = "4:3"
        elif aspect_ratio_value < 0.7:
            aspect_ratio = "9:16"
        else:
            aspect_ratio = "3:4"

        print(f"Requesting image from Google Imagen (aspect ratio: {aspect_ratio})...")

        model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-001")

        # Build generation parameters
        gen_params = {
            "prompt": prompt,
            "number_of_images": 1,
            "aspect_ratio": aspect_ratio,
            "safety_filter_level": "block_some",
            "person_generation": "allow_adult",
        }

        # Add seed if provided
        if seed is not None:
            gen_params["seed"] = int(seed)

        response = model.generate_images(**gen_params)

        img_bytes = response.images[0]._image_bytes

        return img_bytes, None

    except Exception as e:
        return None, f"Google Imagen error: {str(e)}"

def main():
    """Main function to run the image generation batch process."""
    # Check for --dry-run flag
    dry_run = "--dry-run" in sys.argv

    # Create both output folders
    os.makedirs(RAW_OUTPUT_FOLDER, exist_ok=True)
    os.makedirs(CROPPED_FOLDER, exist_ok=True)

    try:
        with open(MANIFEST_FILE, 'r') as f:
            manifest = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: The file '{MANIFEST_FILE}' was not found. Make sure it's in the same folder as the script.")
        return
    except json.JSONDecodeError:
        print(f"ERROR: Could not read '{MANIFEST_FILE}'. Please ensure it is a valid JSON file.")
        return

    # Check format: dict with "images" key (new) or array (legacy)
    if isinstance(manifest, dict) and "images" in manifest:
        # New dict format - may or may not have style_config
        style_config = manifest.get("style_config", {})
        prompts_data = manifest.get("images", [])

        if style_config:
            print(f"📋 Style-aware batch generation mode (Google Imagen)")
            print(f"   Style: {style_config.get('style_name', 'default')}")
            print(f"   Base style: {style_config.get('base_style', 'none')[:60]}...")
            print(f"   Seed: {style_config.get('seed', 'random')}")
            print(f"   Project: {style_config.get('project', 'default')}")
        else:
            print(f"📋 Batch generation mode (Google Imagen, no style config)")
    else:
        # Legacy format - array of prompts
        style_config = {}
        prompts_data = manifest
        print(f"📋 Standard batch generation mode (Google Imagen)")

    print(f"Found {len(prompts_data)} prompts to generate. Starting the batch process...")

    if dry_run:
        print("\n🔍 DRY RUN MODE - No images will be generated\n")

    for item in prompts_data:
        image_name = item['id'] + ".png"
        base_prompt = item['image']
        target_size_str = item['size']

        raw_output_path = os.path.join(RAW_OUTPUT_FOLDER, image_name)
        cropped_output_path = os.path.join(CROPPED_FOLDER, image_name)

        if os.path.exists(raw_output_path) and os.path.exists(cropped_output_path):
            print(f"Skipping '{image_name}' because both raw and cropped versions already exist.")
            continue

        print(f"\n--- Generating '{image_name}' ---")

        # Build enhanced prompt with style config if present
        if style_config:
            base_style = style_config.get('base_style', '')
            style_override = item.get('style_override', None)
            asset_type = detect_asset_type(base_prompt)
            seed = style_config.get('seed', None)

            if style_override:
                final_prompt = f"{style_override}. {base_prompt}"
            elif base_style:
                final_prompt = f"{base_style}. {base_prompt}"
            else:
                final_prompt = base_prompt

            print(f"Base prompt: {base_prompt[:60]}...")
            if asset_type:
                print(f"Detected type: {asset_type}")
            if base_style:
                print(f"Style applied: {base_style[:60]}...")
            print(f"Final prompt: {final_prompt[:80]}...")
        else:
            final_prompt = base_prompt
            seed = None
            print(f"Prompt: {final_prompt[:80]}...")

        if dry_run:
            print(f"[DRY RUN] Would generate with prompt: {final_prompt[:120]}...")
            continue

        try:
            # Parse target dimensions
            if 'x' in target_size_str:
                target_width, target_height = map(int, target_size_str.split('x'))
            else:
                # Square format
                target_width = target_height = int(target_size_str)

            # Generate image with Google Imagen
            img_data, error = generate_image_google(final_prompt, target_width, target_height, seed)

            if error:
                print(f"ERROR: {error}")
                continue

            print("Image generated successfully!")

            # Save the original, large, raw image
            with open(raw_output_path, "wb") as f:
                f.write(img_data)
            print(f"SUCCESS: Saved raw image to '{raw_output_path}'")

            # Check if cropping is requested (default is FALSE - keep full size)
            crop_enabled = item.get('crop', False)

            img = Image.open(BytesIO(img_data))
            current_width, current_height = img.size

            if crop_enabled:
                # --- PRECISE CROPPING LOGIC ---
                print(f"Cropping image to your specified size: {target_width}x{target_height}...")

                left = (current_width - target_width) / 2
                top = (current_height - target_height) / 2
                right = (current_width + target_width) / 2
                bottom = (current_height + target_height) / 2

                img_cropped = img.crop((left, top, right, bottom))

                # Save the final, cropped image to the new folder
                img_cropped.save(cropped_output_path)
                print(f"SUCCESS: Saved cropped image ({target_width}x{target_height}) to '{cropped_output_path}'")
            else:
                # Keep full-size image (no cropping)
                print(f"Keeping full-size image (no crop)")
                shutil.copy(raw_output_path, cropped_output_path)
                print(f"SUCCESS: Saved full-size image ({current_width}x{current_height}) to '{cropped_output_path}'")
                print(f"         (Requested size was {target_width}x{target_height}, kept Imagen native resolution)")

        except Exception as e:
            print(f"ERROR: Failed to process '{image_name}'. Reason: {e}")

    if dry_run:
        print("\n--- Dry run complete! No images were generated. ---")
        print("Remove --dry-run flag to actually generate images.")
    else:
        print("\n--- Batch generation complete! ---")

if __name__ == "__main__":
    main()
