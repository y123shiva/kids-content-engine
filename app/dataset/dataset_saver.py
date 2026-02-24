import json
from app.core.config import SCRIPTS_ROOT_DIR


def save_script(data: dict, month: int, version: str):

    version_dir = SCRIPTS_ROOT_DIR / version
    version_dir.mkdir(parents=True, exist_ok=True)

    file_path = version_dir / f"{data['topic_id']}.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return str(file_path)
