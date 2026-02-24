from pathlib import Path
import json
import logging
import re
from typing import Dict

CHAR_ROOT = Path("data/characters")

logging.basicConfig(level=logging.INFO)


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def load_characters(slug: str) -> str:
    char_file = CHAR_ROOT / f"{slug}.json"

    if not char_file.exists():
        char_file = CHAR_ROOT / "default.json"

    if not char_file.exists():
        return ""

    try:
        data = json.loads(char_file.read_text(encoding="utf-8"))

        return ", ".join(
            f"{name}: {info.get('description', '')}"
            for name, info in data.items()
        )

    except Exception as e:
        logging.warning(f"Failed to load character file: {e}")
        return ""


def build_prompt(
    title: str,
    scene_text: str,
    scene_no: int,
    characters: str,
) -> str:

    return f"""
Children's story illustration in high-quality cartoon style.

Story title: {title}
Scene number: {scene_no}

Scene description:
{scene_text}

Characters (must remain visually consistent):
{characters}

Style rules (STRICT):
- cute cartoon illustration
- bright, cheerful colors
- soft lighting
- friendly facial expressions
- safe for children age 2–6
- no scary elements
- no darkness
- no text, letters, or captions
- cinematic framing
- 16:9 aspect ratio
""".strip()
