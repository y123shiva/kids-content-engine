import json
import csv
from pathlib import Path


def build_dataset(
    scripts_root_dir: Path,
    version: str,
    csv_path: Path,
    jsonl_path: Path
):
    rows = []

    version_dir = scripts_root_dir / version

    if not version_dir.exists():
        raise ValueError(f"Version folder '{version}' not found.")

    # More robust JSON scan
    for json_file in version_dir.rglob("*.json"):

        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Support both structures
        script = data.get("script", data)
        month = script.get("month")
        category = script.get("category")
        title = script.get("title")
        summary = script.get("summary", "")

        if not title:
            continue

        for scene in script.get("scenes", []):

            text = scene.get("text") or scene.get("narration", "")

            # 🔥 Hybrid RAG chunk format
            chunk_text = (
                f"Title: {title}\n"
                f"Category: {category}\n"
                f"Scene {scene.get('scene_number')}:\n"
                f"{text}"
            )

            rows.append({
                "version": version,
                "month": month,
                "category": category,
                "title": title,
                "summary": summary,
                "scene_number": scene.get("scene_number"),
                "text": text,
                "chunk_text": chunk_text,  # 🔥 critical for RAG
                "visuals": scene.get("visuals", ""),
                "audio_cues": scene.get("audio_cues", []),
                "duration": scene.get("duration", 0),
                "camera_action": scene.get("camera_action", ""),
                "source_file": str(json_file)
            })

    if not rows:
        raise ValueError("No scenes found in scripts directory.")

    csv_path.parent.mkdir(parents=True, exist_ok=True)
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)

    # ---------- WRITE CSV ----------
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()

        for row in rows:
            row_copy = row.copy()
            row_copy["audio_cues"] = json.dumps(row_copy["audio_cues"], ensure_ascii=False)
            writer.writerow(row_copy)

    # ---------- WRITE JSONL ----------
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    return {
        "total_scenes": len(rows),
        "version": version
    }
