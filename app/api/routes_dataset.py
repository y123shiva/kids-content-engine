from fastapi import APIRouter, HTTPException, status
from app.services.dataset_builder import build_dataset
from app.core.config import SCRIPTS_ROOT_DIR, CSV_FILE, JSONL_FILE

router = APIRouter(prefix="/dataset", tags=["Dataset"])

@router.post(
    "/build",
    status_code=status.HTTP_201_CREATED,
    summary="Build structured dataset from scripts",
    description="Reads template scripts and builds CSV + JSONL dataset for RAG indexing."
)
def build_dataset_endpoint():
    try:
        build_dataset(SCRIPTS_ROOT_DIR, CSV_FILE, JSONL_FILE)

        return {
            "status": "success",
            "message": "Dataset built successfully",
            "outputs": {
                "csv_path": str(CSV_FILE),
                "jsonl_path": str(JSONL_FILE)
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
