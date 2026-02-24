# Quick Reference: TTS + RAG Pipeline

## 🚀 Quick Start

### Option 1: Preset Topic (Fastest)
```bash
# List topics
curl http://127.0.0.1:8000/tts/topics

# Generate
curl -X POST http://127.0.0.1:8000/tts/run/animals-sound
```

### Option 2: Custom Query (Flexible)
```bash
# Setup (first time only)
curl -X POST http://127.0.0.1:8000/tts/build-rag-index

# Generate
curl -X POST http://127.0.0.1:8000/tts/generate-from-rag \
  -H "Content-Type: application/json" \
  -d '{"query": "Tell me about animals", "k": 3}'
```

---

## 📋 Available Endpoints

### GET /tts/topics
```bash
curl http://127.0.0.1:8000/tts/topics

Response:
{
  "total_topics": 2,
  "topics": [
    {"title": "animals sound", "slug": "animals-sound", "scenes": 4},
    {"title": "learning colours with balloons", "slug": "learning-colours-with-balloons", "scenes": 4}
  ]
}
```

### POST /tts/run/{topic_slug}
```bash
curl -X POST http://127.0.0.1:8000/tts/run/animals-sound

Response: { "status": "success", "outputs": {...} }
```

### POST /tts/build-rag-index
```bash
curl -X POST http://127.0.0.1:8000/tts/build-rag-index

Response: { "message": "RAG FAISS index built successfully" }
```

### POST /tts/generate-from-rag
```bash
curl -X POST http://127.0.0.1:8000/tts/generate-from-rag \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Tell me about colors",
    "k": 3
  }'

Response: { "status": "success", "script": {...}, "outputs": {...} }
```

---

## 📁 Output Files

After generation, find files here:

```
outputs/
├── audio/{title}/
│   ├── scene_01.mp3
│   ├── scene_02.mp3
│   └── ...
├── visuals/{title}/
│   ├── scene_01.png
│   ├── scene_02.png
│   └── ...
└── video/
    └── {title}.mp4
```

---

## ⏱️ Timing

| Operation | Time |
|-----------|------|
| List topics | <1s |
| Preset generation | 30-60s |
| Build RAG index | 1-2s |
| RAG generation | 60-80s |

---

## 🐍 Python Quick Code

```python
import requests

# Preset topic
resp = requests.post("http://127.0.0.1:8000/tts/run/animals-sound")
print(resp.json()['outputs']['video'])

# RAG query
requests.post("http://127.0.0.1:8000/tts/build-rag-index")
resp = requests.post(
    "http://127.0.0.1:8000/tts/generate-from-rag",
    json={"query": "Story about colors", "k": 3}
)
print(resp.json()['outputs']['video'])
```

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| "RAG index not ready" | Run `/tts/build-rag-index` first |
| "No topic found" | Check `/tts/topics` for correct slug |
| "Audio generation failed" | Narration might be too long or LLM API issue |
| Server not responding | Check `uvicorn app.main:app --reload` is running |

---

## 📚 Full Documentation

- [TTS_RAG_INTEGRATION.md](TTS_RAG_INTEGRATION.md) - Complete guide
- [COMPLETE_PIPELINE.md](COMPLETE_PIPELINE.md) - Pipeline details
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - What was changed

---

## 🎯 Choose Your Path

**Use Preset Topics when you want:**
- ✅ Fast generation (30-60s)
- ✅ Pre-curated content
- ✅ Guaranteed quality
- ❌ Limited flexibility

**Use RAG Query when you want:**
- ✅ Custom content
- ✅ Natural language flexibility
- ✅ Any topic imaginable
- ❌ Slightly slower (60-80s)
- ❌ Depends on LLM quality

---

## 🎬 Example Workflows

### Workflow 1: Browse & Generate
```bash
# Step 1: See what's available
curl http://127.0.0.1:8000/tts/topics

# Step 2: Pick one and generate
curl -X POST http://127.0.0.1:8000/tts/run/animals-sound

# Step 3: Watch the video
open outputs/video/animals_sound.mp4
```

### Workflow 2: Custom Request
```bash
# Step 1: Setup
curl -X POST http://127.0.0.1:8000/tts/build-rag-index

# Step 2: Generate custom content
curl -X POST http://127.0.0.1:8000/tts/generate-from-rag \
  -H "Content-Type: application/json" \
  -d '{"query": "Tell me about the moon and stars", "k": 3}'

# Step 3: Watch the video
open outputs/video/*.mp4
```

---

**That's it! You're ready to generate content.** 🚀
