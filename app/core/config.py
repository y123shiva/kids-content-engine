import os
from pathlib import Path
from dotenv import load_dotenv

# 👇 PROJECT ROOT (two levels up from config.py)
PROJECT_DIR = Path(__file__).resolve().parents[2]

# Load .env from root
load_dotenv(PROJECT_DIR / ".env")

APP_DIR = PROJECT_DIR / "app"
DATA_DIR = APP_DIR / "data"

SCRIPTS_ROOT_DIR = DATA_DIR / "scripts"
DATASET_DIR = DATA_DIR / "dataset"
FAISS_DIR = DATA_DIR / "faiss"

CSV_FILE = DATASET_DIR / "bibo_scripts.csv"
JSONL_FILE = DATASET_DIR / "bibo_scripts.jsonl"
FAISS_INDEX_FILE = FAISS_DIR / "bibo.index"

# ======================
# 🔤 EMBEDDINGS
# ======================
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# ======================
# 🤖 LLM PROVIDER CONFIG
# ======================

# Provider switch: "openai" or "gemini"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()

# ---- OpenAI ----
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")

# ---- Gemini ----
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")


# ======================
# 🚨 VALIDATION
# ======================
if LLM_PROVIDER == "openai":
    if not OPENAI_API_KEY:
        raise ValueError(
            "LLM_PROVIDER=openai but OPENAI_API_KEY is missing. "
            "Please set it in your .env file."
        )

elif LLM_PROVIDER == "gemini":
    if not GEMINI_API_KEY:
        raise ValueError(
            "LLM_PROVIDER=gemini but GEMINI_API_KEY is missing. "
            "Please set it in your .env file."
        )

else:
    raise ValueError(
        f"Unsupported LLM_PROVIDER '{LLM_PROVIDER}'. "
        "Use 'openai' or 'gemini'."
    )

# ======================
# 📁 ENSURE DIRECTORIES
# ======================
DATA_DIR.mkdir(parents=True, exist_ok=True)
SCRIPTS_ROOT_DIR.mkdir(parents=True, exist_ok=True)
DATASET_DIR.mkdir(parents=True, exist_ok=True)
FAISS_DIR.mkdir(parents=True, exist_ok=True)

# ======================
# 🎬 SCRIPT VERSIONING
# ======================
DEFAULT_SCRIPT_VERSION = "v1"
RAG_SCRIPT_VERSION = "v2"
