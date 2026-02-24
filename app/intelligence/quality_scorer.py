def score_script(script: dict) -> dict:

    scenes = script.get("scenes", [])

    score = 0
    max_score = 100

    # Scene count score
    scene_count = len(scenes)
    if 4 <= scene_count <= 8:
        score += 20

    # Duration score
    total_duration = sum(s.get("duration", 0) for s in scenes)
    if 60 <= total_duration <= 180:
        score += 20

    # Interaction cues score
    interaction_count = sum(
        len(s.get("audio_cues", [])) for s in scenes
    )
    if interaction_count >= 2:
        score += 15

    # Camera variety score
    camera_actions = {s.get("camera_action") for s in scenes}
    if len(camera_actions) >= 2:
        score += 15

    # Lip sync consistency
    if all(s.get("lip_sync", False) for s in scenes):
        score += 15

    # Closing scene check
    if "Great job" in scenes[-1].get("text", ""):
        score += 15

    return {
        "score": score,
        "max_score": max_score,
        "percentage": round((score / max_score) * 100, 2)
    }
