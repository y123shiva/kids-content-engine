from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pathlib import Path

from app.api.routes_script import router as script_router
from app.api.routes_dataset import router as dataset_router
from app.api.routes_rag_media import router as tts_router
from app.api.routes_mass_generation import router as mass_script_router  
from app.api.routes_intelligence import router as intelligence_router  

app = FastAPI(
    title="Bibo AI Children Content Engine",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for folder in ["audio", "visuals", "video"]:
    Path(f"outputs/{folder}").mkdir(parents=True, exist_ok=True)

app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

app.include_router(script_router,  prefix="/template",tags=["Template Builder"])
app.include_router(dataset_router, prefix="/dataset", tags=["Dataset"])
app.include_router(tts_router, prefix="/tts", tags=["Text-to-Speech"])
app.include_router(mass_script_router, prefix="/bulk", tags=["Mass Generation"])
app.include_router(intelligence_router, prefix="/intelligence", tags=["Intelligence"])


@app.get("/")
def health_check():
    return {"status": "Kids Content Engine is running"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
