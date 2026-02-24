from fastapi import APIRouter, HTTPException, status 
from app.core.models import TopicRequest 
from app.services.script_generator import generate_script 
from app.core.normalizer import normalize_llm_script
from app.services.validator import validate_script 
from app.core.config import SCRIPTS_ROOT_DIR 
import re
from slugify import slugify
import json 

router = APIRouter()

@router.post("/template/generate", status_code=status.HTTP_201_CREATED)
def generate(topic: TopicRequest):
    try:
        # 1️⃣ Generate script from LLM
        raw_script = generate_script(topic.dict())
        script = normalize_llm_script(raw_script)

        # 2️⃣ Validate script structure
        validate_script(script)

        # 3️⃣ Prepare save path
        save_dir = SCRIPTS_ROOT_DIR / f"Month_{topic.month}" / topic.category
        save_dir.mkdir(parents=True, exist_ok=True)

        filename = slugify(topic.title) + ".json"
        file_path = save_dir / filename

        # 4️⃣ Prevent duplicates
        if file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Script already exists"
            )

        # 5️⃣ Save script only
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(script, f, indent=2, ensure_ascii=False)

        return {
            "status": "script_created",
            "file_path": str(file_path),
            "scene_count": len(script["scenes"]),
            "title": script["title"]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
