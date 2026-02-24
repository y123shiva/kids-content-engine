# ✅ Complete RAG-Based Content Generation Pipeline

## What You Now Have

A full end-to-end pipeline that generates **audio, video, and scenes** from a RAG-based LLM query:

```
User Query
    ↓
RAG Search (FAISS)  ← Retrieve similar scenes from dataset
    ↓
LLM Generation      ← Generate new script using context
    ↓
Audio Generation    ← Convert narration to speech (TTS)
    ↓
Visual Generation   ← Create images for each scene
    ↓
Video Merging       ← Combine audio + visuals into MP4
    ↓
Response            ← Script, file paths, summary
```

## New Endpoint

### `POST /rag/generate-complete`

Generates a complete content package in one API call.

**Request:**
```json
{
  "query": "Tell me a story about animals in the jungle",
  "k": 3
}
```

**Response:**
```json
{
  "status": "success",
  "script": {
    "title": "Bibo's Jungle Adventure",
    "character": "Bibo",
    "age_group": "3-6",
    "duration_seconds": 45,
    "learning_goals": [...],
    "scenes": [...]
  },
  "outputs": {
    "audio_dir": "outputs/audio/bibo's_jungle_adventure/",
    "visuals_dir": "outputs/visuals/bibo's_jungle_adventure/",
    "video": "outputs/video/bibo's_jungle_adventure.mp4"
  },
  "summary": {
    "total_scenes": 3,
    "total_duration": 41.9
  }
}
```

## Test Results

✅ **Successfully Generated:**
- Title: "Bibo's Jungle Action Adventure!"
- Character: Bibo
- Age Group: 3-6
- Duration: 45 seconds
- Learning Goals: Identify animal actions, Practice motor skills, Engage with storytelling
- Scenes: 3
- Audio Files: 3 MP3s (41.9s total)
- Visual Files: 3 PNGs
- Video: 0.8 MB MP4
- **Time Taken**: 62.6 seconds

## Complete File Structure

After generation, you have:

```
outputs/
├── audio/
│   └── bibo's_jungle_action_adventure!/
│       ├── scene_01.mp3
│       ├── scene_02.mp3
│       └── scene_03.mp3
├── visuals/
│   └── bibo's_jungle_action_adventure!/
│       ├── scene_01.png
│       ├── scene_02.png
│       └── scene_03.png
└── video/
    └── bibo's_jungle_action_adventure!.mp4
```

## How to Use

### 1. Start the Server
```bash
cd /workspaces/kids-content-engine
uvicorn app.main:app --reload
```

### 2. Build Index (first time only)
```bash
curl -X POST http://127.0.0.1:8000/rag/build-index
```

### 3. Generate Complete Content
```bash
curl -X POST http://127.0.0.1:8000/rag/generate-complete \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Tell me a story about animals",
    "k": 3
  }'
```

### 4. Access the Files
- **Audio**: `outputs/audio/{title}/scene_*.mp3`
- **Visuals**: `outputs/visuals/{title}/scene_*.png`
- **Video**: `outputs/video/{title}.mp4`

## What Happens In Each Step

### 1. RAG Search
- Embeds your query using `all-MiniLM-L6-v2` model
- Searches FAISS index for k similar scenes
- Returns matching scenes from the dataset

### 2. LLM Generation
- Builds RAG prompt with retrieved scenes
- Calls Gemini (or OpenAI) to generate new script
- Returns structured JSON with schema:
  - `title`, `character`, `age_group`, `duration_seconds`, `learning_goals`
  - `scenes[]` with `scene_number`, `timestamp`, `speaker`, `narration`, `actions`, `visuals`

### 3. Audio Generation
- Converts each scene's narration to MP3 using gTTS
- Tracks audio duration per scene
- Creates `outputs/audio/{title}/` directory

### 4. Visual Generation
- Creates placeholder images for each scene
- Uses narration text as image text
- Stores as PNG in `outputs/visuals/{title}/`

### 5. Video Merging
- Creates video clips from images with proper duration
- Concatenates all clips
- Overlays audio tracks
- Exports final MP4 file

## API Endpoints Available

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/rag/build-index` | POST | Initialize FAISS index (run once) |
| `/rag/generate-llm` | POST | Generate script only (no audio/video) |
| `/rag/generate-complete` | POST | **Full pipeline (NEW)** |
| `/tts/topics` | GET | List available preset topics |
| `/tts/run/{topic}` | POST | Generate audio/video for preset topics |

## Configuration

Set in `.env`:
```bash
# LLM Provider
LLM_PROVIDER=gemini  # or 'openai'
GEMINI_API_KEY=your_key
OPENAI_API_KEY=your_key

# Models
GEMINI_MODEL_NAME=gemini-2.5-flash
OPENAI_MODEL_NAME=gpt-4o-mini
EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2
```

## Performance

| Step | Time |
|------|------|
| RAG Search | 1-2s |
| LLM Generation | 10-15s |
| Audio Generation | 5-10s (depends on narration length) |
| Visual Generation | 1-2s |
| Video Merging | 30-40s |
| **Total** | **60-80s per request** |

## Error Handling

Common errors and solutions:

| Error | Cause | Solution |
|-------|-------|----------|
| "Index not built yet" | FAISS not initialized | Call `/rag/build-index` first |
| "Invalid LLM JSON output" | LLM returned malformed JSON | Retry, or check LLM API key |
| "Audio generation failed" | TTS service error | Check audio narration length |
| "Address already in use" | Port 8000 occupied | Change port or kill existing process |

## Files Modified

1. **[app/api/routes_rag.py](app/api/routes_rag.py)** - Added `/generate-complete` endpoint
2. **[app/services/tts_service.py](app/services/tts_service.py)** - Added `animated_image_clip()` function
3. **[app/core/utils.py](app/core/utils.py)** - Fixed JSON extraction for markdown code blocks

## Documentation

- **[COMPLETE_PIPELINE.md](COMPLETE_PIPELINE.md)** - Detailed API reference
- **[test_complete_pipeline.py](test_complete_pipeline.py)** - Test script with examples

## Next Steps

You can now:
1. ✅ Query the RAG system naturally
2. ✅ Generate complete kid-friendly video scripts
3. ✅ Auto-generate audio narration
4. ✅ Create visual assets
5. ✅ Produce final MP4 videos

All from a single API call! 🎉
