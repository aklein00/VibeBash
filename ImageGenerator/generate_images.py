import os
import json
import sys
import shutil
from openai import OpenAI
import requests
from PIL import Image
from io import BytesIO

# --- CONFIGURATION ---
API_KEY = "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"

MANIFEST_FILE = "image_prompts.json"

# UPDATED: New folder names for clarity
RAW_OUTPUT_FOLDER = "generated_images_raw"
CROPPED_FOLDER = "generated_images_final_cropped"

# --- SCRIPT LOGIC (No need to edit below this line) ---

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

def main():
    """Main function to run the image generation batch process."""
    # Check for --dry-run flag
    dry_run = "--dry-run" in sys.argv

    if API_KEY == "YOUR_OPENAI_API_KEY_HERE":
        print("ERROR: Please replace 'YOUR_OPENAI_API_KEY_HERE' with your actual OpenAI API key in the script.")
        return

    client = OpenAI(api_key=API_KEY)

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
            print(f"📋 Style-aware batch generation mode")
            print(f"   Style: {style_config.get('style_name', 'default')}")
            print(f"   Base style: {style_config.get('base_style', 'none')[:60]}...")
            print(f"   Seed: {style_config.get('seed', 'random')}")
            print(f"   Project: {style_config.get('project', 'default')}")
        else:
            print(f"📋 Batch generation mode (dict format, no style config)")
    else:
        # Legacy format - array of prompts
        style_config = {}
        prompts_data = manifest
        print(f"📋 Standard batch generation mode (legacy array format)")

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

            aspect_ratio = target_width / target_height

            if aspect_ratio > 1.3:
                dalle_size = "1792x1024"
            elif aspect_ratio < 0.7:
                dalle_size = "1024x1792"
            else:
                dalle_size = "1024x1024"

            print(f"Requesting image from DALL-E 3 at {dalle_size} resolution...")

            response = client.images.generate(
                model="dall-e-3",
                prompt=final_prompt,
                size=dalle_size,
                quality="hd",
                n=1,
            )
            image_url = response.data[0].url

            print("Downloading image...")
            image_response = requests.get(image_url)
            img_data = image_response.content

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
                print(f"         (Requested size was {target_width}x{target_height}, kept DALL-E native resolution)")

        except Exception as e:
            print(f"ERROR: Failed to process '{image_name}'. Reason: {e}")

    if dry_run:
        print("\n--- Dry run complete! No images were generated. ---")
        print("Remove --dry-run flag to actually generate images.")
    else:
        print("\n--- Batch generation complete! ---")

if __name__ == "__main__":
    main()