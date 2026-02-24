def normalize_llm_script(raw_script: dict) -> dict:
    normalized_scenes = []

    for idx, scene in enumerate(raw_script.get("scenes", []), start=1):
        # Normalize visuals (string | list → string)
        visuals = scene.get("visuals", "")
        if isinstance(visuals, list):
            visuals = visuals[0] if visuals else ""

        # Normalize audio cues
        audio_cues = scene.get("audio_cues", [])
        if isinstance(audio_cues, str):
            audio_cues = [audio_cues]

        normalized_scenes.append({
            "scene_number": idx,
            "timestamp": scene.get("timestamp", "00:00"),
            "type": scene.get("type", "dialogue"),
            "speaker": scene.get("speaker", raw_script.get("character", "Bibo")),
            "text": scene.get("narration") or scene.get("text", ""),
            "visuals": visuals,
            "audio_cues": audio_cues
        })

    return {
        "title": raw_script.get("title", "Untitled Story"),
        "age_group": raw_script.get("age_group", "3-6"),
        "duration_seconds": raw_script.get("duration_seconds", 180),
        "main_character": raw_script.get("character", "Bibo"),
        "scenes": normalized_scenes
    }
