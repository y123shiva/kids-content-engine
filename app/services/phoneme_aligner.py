"""Phoneme-level alignment for lip-sync.

This module provides simple phoneme timings for accurate viseme selection.
Uses a lightweight heuristic approach (no heavy forced-aligner dependencies).
"""

from typing import List, Tuple, Dict


# Simple phoneme groups and typical relative durations
PHONEME_GROUPS = {
    "vowels": ["a", "e", "i", "o", "u", "ə"],
    "fricatives": ["f", "v", "s", "z", "sh", "zh", "th"],
    "stops": ["p", "b", "t", "d", "k", "g"],
    "nasals": ["m", "n", "ng"],
    "approximants": ["w", "y", "l", "r"],
}

# Viseme mapping: phonemes -> viseme name
PHONEME_TO_VISEME = {
    # Vowels and approximants: open mouth
    "a": "open", "e": "open", "i": "open", "o": "open", "u": "open", "ə": "open",
    "w": "open", "y": "open", "l": "open", "r": "open",
    # Fricatives and stops: wide mouth
    "f": "wide", "v": "wide", "s": "wide", "z": "wide",
    "sh": "wide", "zh": "wide", "th": "wide",
    "p": "closed", "b": "closed", "t": "closed", "d": "closed", "k": "closed", "g": "closed",
    "m": "closed", "n": "closed", "ng": "closed",
}


def _simple_word_to_phonemes(word: str) -> List[str]:
    """Convert a word to a simple phoneme-like sequence.

    This is a heuristic: we break words by common phoneme patterns.
    For true phoneme alignment, you'd use a grapheme-to-phoneme (G2P) model.
    """
    word = word.lower().strip()
    if not word:
        return []

    phonemes = []
    i = 0
    while i < len(word):
        # Check for digraphs
        if i + 1 < len(word):
            digraph = word[i : i + 2]
            if digraph in ("sh", "ch", "th", "zh", "ng"):
                phonemes.append(digraph)
                i += 2
                continue

        # Single character
        phonemes.append(word[i])
        i += 1

    return phonemes


def _estimate_phoneme_duration(phoneme: str, total_duration: float, word_phonemes: List[str]) -> float:
    """Estimate the duration of a single phoneme."""
    if not word_phonemes:
        return total_duration
    # Simple heuristic: longer phonemes get slightly longer duration
    if phoneme in PHONEME_GROUPS["vowels"]:
        relative_length = 1.5
    elif phoneme in PHONEME_GROUPS["fricatives"]:
        relative_length = 1.2
    elif phoneme in PHONEME_GROUPS["stops"]:
        relative_length = 0.8
    else:
        relative_length = 1.0

    total_relative = sum(
        1.5 if p in PHONEME_GROUPS["vowels"]
        else 1.2 if p in PHONEME_GROUPS["fricatives"]
        else 0.8 if p in PHONEME_GROUPS["stops"]
        else 1.0
        for p in word_phonemes
    )

    return (relative_length / total_relative) * total_duration


def align_text_to_phonemes(
    text: str, total_duration: float
) -> List[Tuple[str, float, float]]:
    """Align text to phoneme timestamps.

    Returns:
      List of (phoneme, start_time, end_time) tuples.
    """
    words = [w for w in text.split() if w.strip()]
    if not words:
        return []

    phonemes_all = []
    for word in words:
        phonemes_all.extend(_simple_word_to_phonemes(word))

    if not phonemes_all:
        return []

    # Distribute duration across phonemes
    per_phoneme = total_duration / len(phonemes_all)
    result = []
    current_time = 0.0

    for phoneme in phonemes_all:
        duration = per_phoneme
        result.append((phoneme, current_time, current_time + duration))
        current_time += duration

    return result


def map_phoneme_to_viseme(phoneme: str) -> str:
    """Map a phoneme to a viseme (mouth shape)."""
    return PHONEME_TO_VISEME.get(phoneme, "closed")


def get_viseme_at_time(
    phoneme_times: List[Tuple[str, float, float]], t: float
) -> str:
    """Get the viseme for a given time within a phoneme sequence."""
    for phoneme, start, end in phoneme_times:
        if start <= t < end:
            return map_phoneme_to_viseme(phoneme)
    return "closed"
