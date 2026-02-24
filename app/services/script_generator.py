import random
from app.services.validator import validate_script

INTERACTIVE_CUES = ["CLAP", "JUMP", "STOMP", "SHAKE", "SPIN"]
CAMERA_ACTIONS = ["static", "pan_left", "pan_right", "zoom_in", "zoom_out"]


def _estimate_duration_seconds(text: str, wpm: int = 140) -> float:
    words = [w for w in text.split() if w.strip()]
    if not words:
        return 1.0
    minutes = len(words) / float(wpm)
    return max(0.5, minutes * 60.0)


def generate_script(topic: dict, min_scenes: int = 3, max_scenes: int = 6):
    """Generate a simple script object enriched with per-scene shot metadata.

    Each scene will include estimated `duration` (seconds), a `visual_prompt`
    string and a `camera_action` to guide animation rendering.
    """
    scenes = []
    total_scenes = random.randint(min_scenes, max_scenes)

    text_templates = [
        "Let's explore {title}!,",
        "Look! Here is a colorful {title}!",
        "Can you count the {title} with me?",
        "Let's find the hidden {title} in the jungle!",
        "Amazing! We saw {title}!"
    ]

    for i in range(1, total_scenes + 1):
        text = text_templates[(i - 1) % len(text_templates)].format(
            title=topic["title"]
        )

        duration = _estimate_duration_seconds(text)
        scene = {
            "scene_number": i,
            "timestamp": "00:00",
            "text": text,
            "narration": text,
            "visuals": f"Visuals for scene {i} of {topic['title']}",
            "duration": duration,
            "visual_prompt": f"A bright, colorful scene showing {topic['title']} (kid-friendly)",
            "camera_action": random.choice(CAMERA_ACTIONS),
            "audio_cues": (
                [random.choice(INTERACTIVE_CUES)] if random.random() < 0.7 else []
            ),
            "lip_sync": True,
        }

        scenes.append(scene)

    # Closing scene
    closing_text = "Great job! See you next time!"
    scenes.append({
        "scene_number": total_scenes + 1,
        "timestamp": "00:00",
        "text": closing_text,
        "narration": closing_text,
        "visuals": "Visuals for ending scene",
        "duration": _estimate_duration_seconds(closing_text),
        "visual_prompt": "A friendly closing scene with confetti and applause",
        "camera_action": "zoom_out",
        "audio_cues": ["CLAP"],
        "lip_sync": True,
    })

    script = {
        "month": topic.get("month"),
        "category": topic.get("category"),
        "title": topic.get("title"),
        "scenes": scenes,
    }

    validate_script(script)
    return script
