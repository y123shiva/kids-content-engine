from gtts import gTTS
from pathlib import Path
import re
import time
import logging
from typing import Optional, List
from pydub import AudioSegment

# =========================================================
# CONFIG
# =========================================================

AUDIO_ROOT = Path("outputs/audio")
AUDIO_ROOT.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO)


# =========================================================
# UTILITIES
# =========================================================

def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def split_text(text: str, max_chars: int = 4500) -> List[str]:
    """
    Split long narration into chunks safe for gTTS.
    gTTS has ~5000 character limit.
    """

    sentences = text.split(". ")
    chunks = []
    current = ""

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        if len(current) + len(sentence) < max_chars:
            current += sentence + ". "
        else:
            chunks.append(current.strip())
            current = sentence + ". "

    if current.strip():
        chunks.append(current.strip())

    return chunks


# =========================================================
# CORE TTS GENERATOR
# =========================================================

def generate_tts(
    narration: str,
    output_path: Path,
    lang: str = "en",
    slow: bool = False,
    retries: int = 3
) -> Optional[Path]:
    """
    Generate TTS audio from narration text.

    Features:
    - Caches existing files
    - Handles long text
    - Retries on failure
    - Cleans up temp files
    """

    if not narration or not narration.strip():
        return None

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Cache check
    if output_path.exists():
        logging.info(f"TTS cached: {output_path}")
        return output_path

    chunks = split_text(narration.strip())

    temp_files = []

    try:
        for i, chunk in enumerate(chunks):

            temp_path = output_path.parent / f"{output_path.stem}_part{i}.mp3"

            for attempt in range(retries):
                try:
                    tts = gTTS(text=chunk, lang=lang, slow=slow)
                    tts.save(str(temp_path))
                    break
                except Exception as e:
                    logging.warning(f"TTS retry {attempt+1}/{retries} for chunk {i}")
                    if attempt == retries - 1:
                        raise
                    time.sleep(1)

            temp_files.append(temp_path)

        # Merge if multiple chunks
        if len(temp_files) == 1:
            temp_files[0].rename(output_path)
        else:
            merge_audio_files(temp_files, output_path)

        logging.info(f"TTS generated: {output_path}")

        return output_path

    except Exception as e:
        logging.error(f"TTS generation failed for {output_path}: {e}")
        raise

    finally:
        # Cleanup temp files
        for f in temp_files:
            if f.exists():
                try:
                    f.unlink()
                except Exception:
                    pass


# =========================================================
# MP3 MERGE
# =========================================================

def merge_audio_files(files: List[Path], output_path: Path):
    """
    Merge MP3 chunks using pydub.
    Requires: pip install pydub
    """

    combined = AudioSegment.empty()

    for file in files:
        combined += AudioSegment.from_mp3(file)

    combined.export(output_path, format="mp3")
