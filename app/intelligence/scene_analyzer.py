def analyze_scene_count(script: dict) -> dict:
    scenes = script.get("scenes", [])
    count = len(scenes)

    return {
        "scene_count": count,
        "is_too_short": count < 4,
        "is_too_long": count > 8,
        "optimal_range": 4 <= count <= 8
    }
