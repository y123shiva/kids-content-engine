import math
from typing import List, Tuple, Dict

# ==========================
# Motion Registry
# ==========================
MOTION_TYPES = {
    "JUMP",
    "WAVE",
    "BLINK",
    "SPIN",
    "SHAKE",
    "CLAP"
}


# ==========================
# Motion Resolver
# ==========================
def resolve_motions(audio_cues: List[str]) -> List[Dict]:
    """
    Convert audio cues into motion instructions.
    Called ONCE per scene.
    """
    motions = []

    for cue in audio_cues:
        cue = cue.upper()

        if cue not in MOTION_TYPES:
            continue

        if cue == "JUMP":
            motions.append({
                "type": "jump",
                "amplitude": 40,
                "frequency": 1.2
            })

        elif cue == "SHAKE":
            motions.append({
                "type": "shake",
                "amplitude": 10,
                "frequency": 10
            })

        elif cue == "SPIN":
            motions.append({
                "type": "spin",
                "speed": 1.5
            })

        elif cue == "WAVE":
            motions.append({
                "type": "wave",
                "amplitude": 15,
                "frequency": 2.0
            })

        elif cue == "BLINK":
            motions.append({
                "type": "blink",
                "interval": 3.0
            })

        elif cue == "CLAP":
            motions.append({
                "type": "clap",
                "frequency": 2.0
            })

    return motions


# ==========================
# Motion Applier
# ==========================
def apply_motion(
    motion: Dict,
    t: float,
    pos: Tuple[int, int]
) -> Tuple[int, int]:
    """
    Apply motion math to (x, y) position.
    Called PER FRAME.
    """
    x, y = pos
    mtype = motion["type"]

    if mtype == "jump":
        return _jump_motion(x, y, t, motion)

    if mtype == "shake":
        return _shake_motion(x, y, t, motion)

    if mtype == "wave":
        return _wave_motion(x, y, t, motion)

    # Spin, clap, blink handled at sprite/layer level
    return x, y


# ==========================
# Individual Motions
# ==========================
def _jump_motion(x, y, t, motion):
    """
    Smooth up-down jump (ease-in-out)
    """
    amp = motion["amplitude"]
    freq = motion["frequency"]

    offset = abs(math.sin(t * math.pi * freq))
    return x, y - int(amp * offset)


def _shake_motion(x, y, t, motion):
    """
    Fast left-right shake
    """
    amp = motion["amplitude"]
    freq = motion["frequency"]

    dx = math.sin(t * freq * 2 * math.pi) * amp
    return x + int(dx), y


def _wave_motion(x, y, t, motion):
    """
    Gentle floating motion
    """
    amp = motion["amplitude"]
    freq = motion["frequency"]

    dy = math.sin(t * freq * 2 * math.pi) * amp
    return x, y + int(dy)


# ==========================
# OPTIONAL (future-ready hooks)
# ==========================
def should_blink(t: float, interval: float = 3.0) -> bool:
    """
    Use this to swap eye sprites
    """
    return int(t) % int(interval) == 0


def spin_angle(t: float, speed: float = 1.0) -> float:
    """
    Rotation angle in degrees
    """
    return (t * speed * 360) % 360


def clap_phase(t: float, frequency: float = 2.0) -> float:
    """
    Phase value for arm movement
    """
    return abs(math.sin(t * frequency * math.pi))
