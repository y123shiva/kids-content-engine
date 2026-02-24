# from pathlib import Path
# from typing import Dict
# import logging

# from app.services.image_prompt_service import (
#     build_prompt,
#     load_characters,
#     slugify,
# )

# from app.services.image_generator_service import generate_image


# VISUAL_ROOT = Path("outputs/visuals")
# logging.basicConfig(level=logging.INFO)


# def generate_visuals_for_script(
#     script: Dict,
#     version: str = "v1",
# ) -> Path:

#     title = script.get("title", "story")
#     slug = slugify(title)

#     scenes = script.get("scenes", [])
#     scenes = sorted(scenes, key=lambda x: x.get("scene_number", 0))

#     out_dir = VISUAL_ROOT / version / slug
#     out_dir.mkdir(parents=True, exist_ok=True)

#     characters = load_characters(slug)

#     for idx, scene in enumerate(scenes, start=1):

#         scene_no = int(scene.get("scene_number", idx))
#         text = scene.get("text") or scene.get("narration") or ""

#         if not text.strip():
#             continue

#         image_path = out_dir / f"scene_{scene_no:02d}.png"

#         # Cache
#         if image_path.exists():
#             logging.info(f"Skipping existing image: {image_path.name}")
#             continue

#         # 🔥 1. Build Prompt
#         prompt = build_prompt(
#             title=title,
#             scene_text=text,
#             scene_no=scene_no,
#             characters=characters,
#         )

#         try:
#             logging.info(f"Generating image for scene {scene_no}")

#             # 🔥 2. Call SDXL generator
#             generate_image(
#                 prompt=prompt,
#                 output_path=image_path,
#                 width=1280,
#                 height=720,
#             )

#         except Exception as e:
#             logging.error(f"Image generation failed: {e}")
#             continue

#     return out_dir
