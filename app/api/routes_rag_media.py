from fastapi import APIRouter, HTTPException
from pathlib import Path
import json
import csv
from typing import List, Dict
import re
import threading

from app.core.config import (
    SCRIPTS_ROOT_DIR,
    CSV_FILE,
    FAISS_INDEX_FILE,
    EMBEDDING_MODEL_NAME,
)

from app.services.tts_service import (
    generate_tts_for_script,
    merge_audio_and_visuals,
)

# from app.services.auto_visuals_service import generate_visuals_for_script
from app.services.validator import validate_script

# RAG imports
from app.core.models import RAGQuery
from app.services.embedding_service import build_faiss_index
from app.services.rag_adapter import retrieve_context
from app.services.rag_prompt import build_rag_prompt
from app.services.llm_service import LLMService
from app.core.models_output import ScriptOutput
from app.core.utils import extract_json


router = APIRouter()
llm_service = LLMService()


# ============================================================
# RAG MANAGER (Thread Safe Singleton)
# ============================================================

class RAGManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.df = None
            cls._instance.model = None
            cls._instance.index = None
        return cls._instance

    def build_index(self):
        with self._lock:
            self.df, self.model, self.index = build_faiss_index(
                CSV_FILE,
                FAISS_INDEX_FILE,
                EMBEDDING_MODEL_NAME
            )

    def is_ready(self):
        return all([
            self.df is not None,
            self.model is not None,
            self.index is not None
        ])


rag_manager = RAGManager()


# ============================================================
# UTILS
# ============================================================

def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def save_rag_script(script_dict: dict) -> Path:
    save_dir = SCRIPTS_ROOT_DIR / "rag_generated"
    save_dir.mkdir(parents=True, exist_ok=True)

    filename = slugify(script_dict["title"]) + ".json"
    file_path = save_dir / filename

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(script_dict, f, indent=2, ensure_ascii=False)

    return file_path


def load_all_scripts(directory: Path) -> List[dict]:
    scripts = []

    for file in directory.glob("**/*"):
        if not file.is_file():
            continue

        try:
            # JSON
            if file.suffix == ".json":
                data = json.loads(file.read_text(encoding="utf-8"))
                scripts.append(data)

            # CSV
            elif file.suffix == ".csv":
                scenes = []
                with open(file, encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for i, row in enumerate(reader, 1):
                        scenes.append({
                            "scene_number": int(row.get("scene_number", i)),
                            "text": row.get("text") or row.get("narration", ""),
                        })

                scripts.append({
                    "title": file.stem.replace("_", " "),
                    "scenes": scenes
                })

            # JSONL
            elif file.suffix == ".jsonl":
                scenes = []
                with open(file, encoding="utf-8") as f:
                    for i, line in enumerate(f, 1):
                        row = json.loads(line)
                        scenes.append({
                            "scene_number": int(row.get("scene_number", i)),
                            "text": row.get("text") or row.get("narration", ""),
                        })

                scripts.append({
                    "title": file.stem.replace("_", " "),
                    "scenes": scenes
                })

        except Exception:
            continue

    return scripts


# ============================================================
# PIPELINE EXECUTION
# ============================================================

def run_full_pipeline(script_dict: dict) -> dict:

    title = script_dict.get("title", "generated_story")
    scenes = script_dict.get("scenes", [])

    if not scenes:
        raise HTTPException(status_code=400, detail="Script has no scenes")

    title_slug = slugify(title)

    # ----------------------
    # 1️⃣ AUDIO
    # ----------------------
    audio_infos = generate_tts_for_script(script_dict)

    if not audio_infos:
        raise HTTPException(status_code=500, detail="Audio generation failed")

    # ----------------------
    # 2️⃣ VISUALS (SDXL / OpenAI)
    # ----------------------
    # generate_visuals_for_script(script_dict, version="v1")

    # ----------------------
    # 3️⃣ VIDEO MERGE
    # ----------------------
    video_path = merge_audio_and_visuals(
        title=title,
        audio_infos=audio_infos
    )

    return {
        "status": "success",
        "script": script_dict,
        "outputs": {
            "audio_dir": f"outputs/audio/{title_slug}",
            "visuals_dir": f"outputs/visuals/v1/{title_slug}",
            "video": str(video_path),
        },
        "summary": {
            "total_scenes": len(audio_infos),
            "total_duration": sum(a.get("duration", 0) for a in audio_infos),
        },
    }


# ============================================================
# 1️⃣ LIST AVAILABLE TOPICS
# ============================================================

@router.get("/topics")
def list_available_topics():
    scripts = load_all_scripts(SCRIPTS_ROOT_DIR)

    topics = []

    for script in scripts:
        title = script.get("title", "story")
        scenes = script.get("scenes", [])

        if scenes:
            topics.append({
                "title": title,
                "slug": slugify(title),
                "scenes": len(scenes),
            })

    if not topics:
        raise HTTPException(status_code=404, detail="No topics found")

    return {
        "total_topics": len(topics),
        "topics": topics,
    }


# ============================================================
# 2️⃣ GENERATE FROM EXISTING TOPIC
# ============================================================

@router.post("/generate-from-topic/{slug}")
def generate_from_existing_topic(slug: str):

    scripts = load_all_scripts(SCRIPTS_ROOT_DIR)

    selected_script = None

    for script in scripts:
        if slugify(script.get("title", "")) == slug:
            selected_script = script
            break

    if not selected_script:
        raise HTTPException(status_code=404, detail="Topic not found")

    try:
        validate_script(selected_script)
        return run_full_pipeline(selected_script)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Generation failed: {e}"
        )


# ============================================================
# 3️⃣ BUILD RAG INDEX
# ============================================================

@router.post("/build-rag-index")
def build_rag_index():
    try:
        rag_manager.build_index()
        return {"message": "RAG FAISS index built successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Index build failed: {e}"
        )


# ============================================================
# 4️⃣ GENERATE FROM RAG + FULL PIPELINE
# ============================================================

@router.post("/generate-from-rag")
def generate_content_from_rag(req: RAGQuery):

    if not rag_manager.is_ready():
        raise HTTPException(
            status_code=400,
            detail="RAG index not ready. Call /build-rag-index first."
        )

    try:
        # 1️⃣ Retrieve Context
        results = retrieve_context(
            req=req,
            df=rag_manager.df,
            model=rag_manager.model,
            index=rag_manager.index,
            mode="faiss"
        )

        # 2️⃣ Build Prompt
        prompt = build_rag_prompt(req.query, results)

        # 3️⃣ LLM Generate
        raw_output = llm_service.generate(prompt)

        # 4️⃣ Extract JSON
        json_data = extract_json(raw_output)

        # 5️⃣ Validate Schema
        validated_output = ScriptOutput(**json_data)
        script_dict = validated_output.model_dump()

        # 6️⃣ Business Validation
        validate_script(script_dict)

        # 7️⃣ Save Script
        saved_path = save_rag_script(script_dict)

        # 8️⃣ Run Full Media Pipeline
        pipeline_result = run_full_pipeline(script_dict)

        pipeline_result["saved_script_path"] = str(saved_path)

        return pipeline_result

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {e}"
        )
