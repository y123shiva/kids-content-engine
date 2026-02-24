# Complete RAG-Based LLM Script Generation Pipeline

## Overview
The `/rag/generate-complete` endpoint generates a complete kids content package from a text query:
- **Script**: LLM-generated script via RAG with structured scenes
- **Audio**: Text-to-speech narration for each scene
- **Visuals**: Generated images for each scene
- **Video**: Merged audio + visuals into a single MP4 file

## Endpoint

```
POST /rag/generate-complete
```

## Prerequisites
1. Build the FAISS index first:
```bash
curl -X POST http://127.0.0.1:8000/rag/build-index
```

## Request

**Description**: Generate complete content package for a topic

**Request Body**:
```json
{
  "query": "Tell me a story about animals",
  "k": 3
}
```

**Parameters**:
- `query` (string, required): Natural language query for RAG search
- `k` (integer, optional, default=3): Number of similar scenes to retrieve

## Response

**Success (200 OK)**:
```json
{
  "status": "success",
  "script": {
    "title": "Animal Kingdom Adventures",
    "character": "Bibo",
    "age_group": "3-6",
    "duration_seconds": 120,
    "learning_goals": ["Learn about animals", "Understand habitats"],
    "scenes": [
      {
        "scene_number": 1,
        "timestamp": "00:00",
        "speaker": "Bibo",
        "narration": "Welcome to the jungle!",
        "actions": ["wave", "smile"],
        "visuals": ["Bibo in jungle", "colorful trees"]
      },
      {
        "scene_number": 2,
        "timestamp": "00:30",
        "speaker": "Bibo",
        "narration": "Look at the animals!",
        "actions": ["point"],
        "visuals": ["animals", "forest"]
      }
    ]
  },
  "outputs": {
    "audio_dir": "outputs/audio/animal_kingdom_adventures",
    "visuals_dir": "outputs/visuals/animal_kingdom_adventures",
    "video": "outputs/video/animal_kingdom_adventures.mp4"
  },
  "summary": {
    "total_scenes": 2,
    "total_duration": 65.5
  }
}
```

## Pipeline Steps

### 1. Generate Script (RAG + LLM)
- Searches dataset for similar scenes using embeddings
- Builds a RAG prompt with retrieved context
- Calls LLM (OpenAI/Gemini) to generate script
- Validates output against Pydantic schema

### 2. Generate Audio
- Converts each scene's narration to speech using gTTS
- Saves individual scene audio files
- Tracks duration and timestamps

### 3. Generate Visuals
- Creates placeholder images for each scene
- Uses scene narration as image text (can be extended with AI image generation)
- Stores images in `outputs/visuals/{title}/`

### 4. Merge Audio & Visuals
- Creates video clips from images
- Concatenates clips with audio tracks
- Exports final MP4 video file

## Output Files

After successful generation, you'll find:

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

## Error Handling

| Error | Status | Cause |
|-------|--------|-------|
| "Index not built yet" | 400 | FAISS index not initialized |
| "Invalid LLM JSON output" | 500 | LLM returned malformed JSON |
| "LLM output schema validation failed" | 422 | Generated script doesn't match schema |
| "Audio generation failed" | 500 | TTS service error |
| "Unexpected error" | 500 | Other runtime failures |

## Usage Example

### cURL
```bash
curl -X POST http://127.0.0.1:8000/rag/generate-complete \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Tell me about the animal kingdom",
    "k": 5
  }'
```

### Python
```python
import requests

response = requests.post(
    "http://127.0.0.1:8000/rag/generate-complete",
    json={
        "query": "Tell me about the animal kingdom",
        "k": 5
    }
)

result = response.json()
print(f"Video: {result['outputs']['video']}")
print(f"Duration: {result['summary']['total_duration']}s")
```

### JavaScript
```javascript
const response = await fetch('http://127.0.0.1:8000/rag/generate-complete', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: 'Tell me about the animal kingdom',
    k: 5
  })
});

const result = await response.json();
console.log(`Video: ${result.outputs.video}`);
```

## Performance Notes

- **Script Generation**: 5-15s (depends on LLM provider)
- **Audio Generation**: ~2s per scene (depends on narration length)
- **Visual Generation**: ~0.5s per scene
- **Video Merging**: 30-60s (depends on codec and duration)

**Total Time**: ~2-3 minutes for a typical 3-5 scene video

## Configuration

Environment variables in `.env`:
- `LLM_PROVIDER`: "openai" or "gemini"
- `OPENAI_API_KEY`: Your OpenAI API key
- `GEMINI_API_KEY`: Your Gemini API key
- `EMBEDDING_MODEL_NAME`: "all-MiniLM-L6-v2" (default)

## Related Endpoints

- `POST /rag/build-index` - Initialize FAISS index
- `POST /rag/generate-llm` - Generate script only (without audio/video)
- `POST /tts/run/{topic_slug}` - Generate audio/video for existing scripts
