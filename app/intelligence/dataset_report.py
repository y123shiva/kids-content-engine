from app.intelligence.duration_analyzer import calculate_total_duration
from app.intelligence.scene_analyzer import analyze_scene_count
from app.intelligence.quality_scorer import score_script
from app.intelligence.consistency_checker import check_script_consistency


def analyze_script(script: dict) -> dict:

    return {
        "duration_seconds": calculate_total_duration(script),
        "scene_analysis": analyze_scene_count(script),
        "consistency": check_script_consistency(script),
        "quality": score_script(script),
    }
