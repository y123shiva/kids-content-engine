# app/services/motion_rules.py

from typing import List, Dict

MOTION_LIBRARY = {
    "JUMP": {
        "type": "vertical",
        "amplitude": 40,
        "duration": 0.6
    },
    "WAVE": {
        "type": "arm_rotation",
        "angle": 25,
        "duration": 1.0
    },
    "BLINK": {
        "type": "eye_scale",
        "scale": 0.1,
        "duration": 0.2
    }
}

def resolve_motions(audio_cues: List[str]) -> List[Dict]:
    motions = []
    for cue in audio_cues:
        if cue in MOTION_LIBRARY:
            motions.append(MOTION_LIBRARY[cue])
    return motions
