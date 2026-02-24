"""
Audio Alignment & Lip Sync Engine
--------------------------------
Maps narration audio → phonemes → mouth shapes (visemes)
Designed for kids animation (simple, expressive, forgiving).
"""

from typing import List, Dict
import math

# ==========================
# Viseme Definitions
# ==========================
# Simple mouth shapes (cartoon-friendly)
VISEMES = {
    "A": "mouth_open_big",
    "E": "mouth_smile",
    "I": "mouth_open_small",
    "O": "mouth_round",
    "U": "mouth_round_small",
    "M": "mouth_closed",
    "B": "mouth_closed",
    "P": "mouth_closed",
    "F": "mouth_teeth",
    "S": "mouth_teeth",
    "L": "mouth_open_small",
    "DEFAULT": "mouth_neutral"
}

# Fallback vowel groups
VOWELS = {
    "a": "A",
    "e": "E",
    "i": "I",
    "o": "O",
    "u": "U"
}


# ==========================
# Text → Pseudo-Phonemes
# ==========================
def text_to_phonemes(text: str) -> List[str]:
    """
    Lightweight phoneme extractor.
    NOT linguistically perfect — optimized for animation believability.
    """
    phonemes = []

    for char in text.lower():
        if char in VOWELS:
            phonemes.append(VOWELS[char])
        elif char in ["m", "b", "p"]:
            phonemes.append("M")
        elif char in ["f", "s"]:
            phonemes.append("F")
        elif char in ["l"]:
            phonemes.append("L")
        elif char.strip() == "":
            phonemes.append("PAUSE")

    return phonemes


# ==========================
# Phonemes → Visemes
# ==========================
def phoneme_to_viseme(phoneme: str) -> str:
    """
    Map phoneme to mouth shape
    """
    if phoneme == "PAUSE":
        return "mouth_neutral"

    return VISEMES.get(phoneme, VISEMES["DEFAULT"])


# ==========================
# Audio → Lip Timeline
# ==========================
def generate_lip_sync_timeline(
    narration_text: str,
    audio_duration: float,
    fps: int = 24
) -> List[Dict]:
    """
    Generate frame-level mouth shapes.

    Output:
    [
      {"time": 0.00, "viseme": "mouth_open"},
      {"time": 0.04, "viseme": "mouth_round"},
      ...
    ]
    """

    phonemes = text_to_phonemes(narration_text)

    if not phonemes:
        return []

    total_frames = int(audio_duration * fps)
    frames_per_phoneme = max(1, total_frames // len(phonemes))

    timeline = []
    frame = 0

    for phoneme in phonemes:
        viseme = phoneme_to_viseme(phoneme)

        for _ in range(frames_per_phoneme):
            t = frame / fps
            timeline.append({
                "time": round(t, 3),
                "viseme": viseme
            })
            frame += 1

    return timeline


# ==========================
# Runtime Frame Resolver
# ==========================
def get_viseme_at_time(
    timeline: List[Dict],
    t: float
) -> str:
    """
    Get correct mouth shape for a given timestamp
    Called PER FRAME during rendering
    """
    if not timeline:
        return "mouth_neutral"

    # Binary-ish search (fast enough)
    for i in range(len(timeline) - 1):
        if timeline[i]["time"] <= t < timeline[i + 1]["time"]:
            return timeline[i]["viseme"]

    return timeline[-1]["viseme"]

# ==========================
# Public API (used by animation_service)
# ==========================
def align_phonemes(
    narration_text: str,
    audio_duration: float,
    fps: int = 24
):
    """
    Public wrapper used by animation pipeline
    """
    return generate_lip_sync_timeline(
        narration_text=narration_text,
        audio_duration=audio_duration,
        fps=fps
    )
