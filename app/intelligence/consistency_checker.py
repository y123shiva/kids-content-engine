def check_script_consistency(script: dict) -> dict:
    scenes = script.get("scenes", [])

    durations = [scene.get("duration", 0) for scene in scenes]

    if not durations:
        return {"consistent": False}

    avg_duration = sum(durations) / len(durations)

    variance = max(durations) - min(durations)

    return {
        "average_scene_duration": round(avg_duration, 2),
        "duration_variance": round(variance, 2),
        "consistent": variance < 5  # threshold adjustable
    }
