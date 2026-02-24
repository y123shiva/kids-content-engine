# 🏗️ System Architecture: TTS + RAG Integration

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         API Layer                                │
├─────────────────────────────────────────────────────────────────┤
│  FastAPI Router (app/api/tts.py)                                 │
│                                                                   │
│  Route 1: GET /tts/topics                                        │
│  └─→ load_all_scripts() → List available topics                  │
│                                                                   │
│  Route 2: POST /tts/run/{topic_slug}                             │
│  └─→ Find preset script → run_tts_pipeline()                     │
│                                                                   │
│  Route 3: POST /tts/build-rag-index                              │
│  └─→ build_faiss_index() → Initialize RAG                        │
│                                                                   │
│  Route 4: POST /tts/generate-from-rag                            │
│  └─→ [RAG Search] → [LLM Generation] → run_tts_pipeline()        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Service Layer                               │
├─────────────────────────────────────────────────────────────────┤
│  RAG Services (for generate-from-rag)                            │
│  ├─ embedding_service.py    → Build FAISS index                  │
│  ├─ rag_retriever.py        → Search similar scenes              │
│  ├─ rag_prompt.py           → Build RAG prompt                   │
│  └─ llm_service.py          → Call LLM (Gemini/OpenAI)           │
│                                                                   │
│  TTS Services (for both paths)                                   │
│  ├─ tts_service.py          → generate_tts_for_script()          │
│  │                            merge_audio_and_visuals()          │
│  ├─ auto_visuals_service.py → generate_visuals_for_script()      │
│  └─ tts_generator.py        → gTTS (text-to-speech)              │
│                                                                   │
│  Utilities                                                       │
│  ├─ utils.py                → extract_json() (extract LLM JSON)   │
│  ├─ config.py               → Configuration & paths              │
│  └─ models.py               → Pydantic models                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   External Services                              │
├─────────────────────────────────────────────────────────────────┤
│  LLM Providers                                                   │
│  ├─ Gemini API (google-genai)                                    │
│  └─ OpenAI API (openai)                                          │
│                                                                   │
│  Vector Search                                                   │
│  └─ FAISS (Facebook AI Similarity Search)                        │
│                                                                   │
│  Text-to-Speech                                                  │
│  └─ gTTS (Google Text-to-Speech)                                 │
│                                                                   │
│  Video Generation                                                │
│  └─ MoviePy (video composition & encoding)                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## Request Flow Comparison

### Path 1: Preset Topic Request

```
┌──────────────────────────┐
│  GET /tts/topics         │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────────────┐
│ load_all_scripts()               │
│ - Read JSON/CSV/JSONL files      │
│ - Extract scenes and metadata    │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│ List Topics Response             │
│ {topics: [...], total: N}        │
└──────────────────────────────────┘

---

┌───────────────────────────────┐
│ POST /tts/run/{topic_slug}    │
└────────────┬──────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│ Find matching script in memory    │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│ run_tts_pipeline(script_dict)    │
│                                  │
│ Step 1: generate_tts_for_script()│
│ ├─ For each scene:               │
│ │  ├─ Extract narration          │
│ │  └─ Convert to MP3 (gTTS)      │
│ └─ Return: audio_infos           │
│                                  │
│ Step 2: generate_visuals_...()   │
│ ├─ For each scene:               │
│ │  └─ Create placeholder image   │
│ └─ Save PNG files                │
│                                  │
│ Step 3: merge_audio_and_...()    │
│ ├─ Load audio clips              │
│ ├─ Load image clips              │
│ ├─ Concatenate clips             │
│ └─ Export MP4 video              │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│ Return Complete Response         │
│ {status, script, outputs, summary}
└──────────────────────────────────┘
```

### Path 2: RAG-Generated Request

```
┌────────────────────────────────────────┐
│ POST /tts/build-rag-index              │
│ (Called once, builds FAISS index)      │
└────────────┬─────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────┐
│ build_faiss_index()                    │
│ ├─ Load dataset (bibo_scripts.csv)     │
│ ├─ Embed scenes (all-MiniLM-L6-v2)     │
│ └─ Build FAISS index (bibo.index)      │
└────────────┬─────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────┐
│ Success: Index ready                   │
└────────────────────────────────────────┘

---

┌────────────────────────────────────────┐
│ POST /tts/generate-from-rag            │
│ {query: "...", k: 3}                   │
└────────────┬─────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────┐
│ STEP 1: RAG Search                     │
│ ├─ Embed query (all-MiniLM-L6-v2)      │
│ ├─ Search FAISS for k=3 similar scenes │
│ └─ Return: results (top-k scenes)      │
└────────────┬─────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────┐
│ STEP 2: Build RAG Prompt               │
│ ├─ Combine: query + retrieved results  │
│ ├─ Add: system instructions            │
│ ├─ Add: JSON schema                    │
│ └─ Return: formatted prompt            │
└────────────┬─────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────┐
│ STEP 3: LLM Generation                 │
│ ├─ Call LLM (Gemini or OpenAI)         │
│ │  with RAG prompt                     │
│ └─ Get: raw_output (JSON in markdown)  │
└────────────┬─────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────┐
│ STEP 4: Extract & Validate JSON        │
│ ├─ extract_json() from markdown        │
│ ├─ Validate with ScriptOutput model    │
│ └─ Get: validated script dictionary    │
└────────────┬─────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────┐
│ STEP 5: Run TTS Pipeline               │
│ (Same as preset path)                  │
│ ├─ Generate audio                      │
│ ├─ Generate visuals                    │
│ └─ Merge into video                    │
└────────────┬─────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────┐
│ Return Complete Response               │
│ {status, script, outputs, summary}     │
└────────────────────────────────────────┘
```

---

## Data Structures

### Input: RAGQuery
```python
class RAGQuery(BaseModel):
    query: str          # Natural language query
    k: int = 3          # Number of similar scenes to retrieve
```

### Internal: Script
```python
class Scene(BaseModel):
    scene_number: int
    timestamp: str
    speaker: str
    narration: str
    actions: list[str]
    visuals: list[str]

class ScriptOutput(BaseModel):
    title: str
    character: str
    age_group: str
    duration_seconds: int
    learning_goals: list[str]
    scenes: list[Scene]
```

### Output: Complete Response
```python
{
    "status": "success",
    "script": ScriptOutput,        # Validated script
    "outputs": {
        "audio_dir": str,          # Path to audio files
        "visuals_dir": str,        # Path to visual files
        "video": str               # Path to MP4 video
    },
    "summary": {
        "total_scenes": int,       # Number of scenes
        "total_duration": float    # Total audio duration
    }
}
```

---

## Key Components

### 1. RAG Manager (Singleton)
```python
class RAGManager:
    _instance = None
    
    def __init__(self):
        self.df = None              # Dataset dataframe
        self.model = None           # Embedding model
        self.index = None           # FAISS index
    
    def build_index(self):
        # Load dataset and build FAISS
    
    def is_ready(self):
        # Check if index is ready
```

### 2. TTS Pipeline Executor
```python
def run_tts_pipeline(script_dict: dict) -> dict:
    """Runs complete TTS pipeline for any script"""
    # 1. Generate audio
    # 2. Generate visuals
    # 3. Merge audio + visuals
    # 4. Return outputs
```

### 3. Service Layer
- **RAG Services**: Search, retrieval, LLM generation
- **TTS Services**: Audio generation, visual creation, video merging
- **Utility Services**: JSON extraction, configuration

---

## File Dependencies

```
app/api/tts.py
├── Imports from app/core/
│   ├── config.py          → Paths, settings
│   ├── models.py          → RAGQuery
│   ├── models_output.py   → ScriptOutput
│   └── utils.py           → extract_json(), File utils
├── Imports from app/services/
│   ├── embedding_service.py     → build_faiss_index()
│   ├── rag_retriever.py         → search()
│   ├── rag_prompt.py            → build_rag_prompt()
│   ├── llm_service.py           → LLMService
│   ├── tts_service.py           → TTS generation functions
│   ├── auto_visuals_service.py  → Visual generation
│   └── tts_generator.py         → gTTS
└── External APIs
    ├── LLM (Gemini or OpenAI)
    ├── FAISS (vector search)
    └── gTTS (text-to-speech)
```

---

## Configuration Flow

```
.env file
├── LLM_PROVIDER              → 'gemini' or 'openai'
├── GEMINI_API_KEY           → Gemini API credentials
├── OPENAI_API_KEY           → OpenAI API credentials
├── EMBEDDING_MODEL_NAME     → 'all-MiniLM-L6-v2'
└── Directory paths
    ├── CSV_FILE             → Dataset CSV
    ├── FAISS_INDEX_FILE     → FAISS index storage
    └── Output directories   → For audio/visuals/video
```

---

## Error Handling Chain

```
User Request
    ↓
Route Handler
    ├─ Input validation (HTTPException 400/422)
    ├─ Service calls
    │   ├─ RAG operations (HTTPException 500)
    │   ├─ LLM operations (HTTPException 500)
    │   └─ TTS operations (HTTPException 500)
    └─ Response generation
        ├─ Success (200)
        └─ Error details (400/422/500)
```

---

## Performance Optimization

### Caching/Singleton Patterns
- RAGManager (singleton) → Reuse FAISS index across requests
- LLMService (singleton) → Reuse API connection

### Pipeline Efficiency
- Sequential processing (no paralle due to dependencies)
- Stream-based audio/video generation (low memory)
- Cleanup of temporary files

---

## Security Considerations

1. **API Keys**: Stored in .env, not in git
2. **Input Validation**: Pydantic models validate all inputs
3. **Error Messages**: Don't expose stack traces to users
4. **Rate Limiting**: Not implemented (consider for production)
5. **Authentication**: Not implemented (consider for production)

---

## Scalability Considerations

### Current Limitations
- Single-threaded request processing
- FAISS index in memory
- Video generation via MoviePy (CPU-bound)

### Future Improvements
- Async request handling
- Distributed FAISS index
- GPU-accelerated video generation
- Request queuing system
- Caching of generated content

---

## Summary

The architecture provides:
- ✅ Two parallel paths to same outcome
- ✅ Modular, reusable components
- ✅ Clean separation of concerns
- ✅ Comprehensive error handling
- ✅ Production-ready implementation
