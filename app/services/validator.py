from typing import Dict, List

INTERACTIVE_CUES = {"CLAP", "JUMP", "STOMP", "SHAKE", "SPIN"}


def validate_scene(scene: Dict, index: int | None = None) -> None:
    """
    Validate a single scene dictionary.
    """

    prefix = f"[Scene index {index}] " if index is not None else ""

    # scene_number
    if "scene_number" not in scene:
        raise ValueError(prefix + "scene_number missing")

    if not isinstance(scene["scene_number"], int):
        raise TypeError(prefix + "scene_number must be an integer")

    if scene["scene_number"] <= 0:
        raise ValueError(prefix + "scene_number must be positive")

    # text (canonical narration)
    if not scene.get("text"):
        raise ValueError(prefix + "text missing")

    if not isinstance(scene["text"], str):
        raise TypeError(prefix + "text must be a string")

    # visuals
    if not scene.get("visuals"):
        raise ValueError(prefix + "visuals missing")

    if not isinstance(scene["visuals"], str):
        raise TypeError(prefix + "visuals must be a string")

    # audio_cues (optional)
    if "audio_cues" in scene:
        if not isinstance(scene["audio_cues"], list):
            raise TypeError(prefix + "audio_cues must be a list")

        for cue in scene["audio_cues"]:
            if cue not in INTERACTIVE_CUES:
                raise ValueError(prefix + f"Invalid audio cue: {cue}")

    # timestamp (optional)
    if "timestamp" in scene:
        if not isinstance(scene["timestamp"], str):
            raise TypeError(prefix + "timestamp must be a string")


def validate_script(script: Dict, enforce_sequential: bool = True) -> None:
    """
    Validate full script structure.
    """

    # title
    if not script.get("title"):
        raise ValueError("Title missing")

    if not isinstance(script["title"], str):
        raise TypeError("Title must be a string")

    # scenes
    if "scenes" not in script:
        raise ValueError("No scenes found")

    if not isinstance(script["scenes"], list):
        raise TypeError("Scenes must be a list")

    if len(script["scenes"]) == 0:
        raise ValueError("Scenes list is empty")

    scene_numbers = []
    for idx, scene in enumerate(script["scenes"]):
        validate_scene(scene, idx)
        scene_numbers.append(scene["scene_number"])

    # duplicate check
    if len(scene_numbers) != len(set(scene_numbers)):
        raise ValueError("Duplicate scene numbers detected")

    # enforce sequential ordering (optional)
    if enforce_sequential:
        expected = list(range(1, len(scene_numbers) + 1))
        if sorted(scene_numbers) != expected:
            raise ValueError(
                f"Scene numbers must be sequential starting at 1. "
                f"Expected {expected}, got {sorted(scene_numbers)}"
            )
