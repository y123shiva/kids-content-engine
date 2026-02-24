from fastapi import APIRouter, HTTPException, status, Query
from typing import Dict, Any
from app.services.bulk_generator import generate_month_dataset

router = APIRouter(prefix="/bulk", tags=["Bulk Generation"])


@router.post(
    "/generate-month",
    status_code=status.HTTP_201_CREATED
)
def generate_month(
    month: int = Query(..., ge=1, le=12, description="Month number (1-12)"),
    version: str = Query("v1", min_length=1, description="Dataset version")
) -> Dict[str, Any]:
    """
    Generate full dataset for a given month and version.
    """

    try:
        results = generate_month_dataset(month, version)

        return {
            "status": "success",
            "month": month,
            "version": version,
            "total_generated": len(results),
            "generated_titles": [r.get("title") for r in results]
        }

    except FileExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk generation failed: {str(e)}"
        )
