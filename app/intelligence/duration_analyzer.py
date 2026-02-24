def calculate_total_duration(script: dict) -> float:
    return sum(scene.get("duration", 0) for scene in script.get("scenes", []))

def calculate_total_duration(script: dict) -> float:
    return sum(scene.get("duration", 0) for scene in script.get("scenes", []))
