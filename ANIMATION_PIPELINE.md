# Animation Pipeline Documentation

## Overview

The Kids Content Engine now supports generating **fully animated videos** with:
- **Phoneme-level lip-sync** — accurate mouth movements synchronized to speech
- **Character sprite layering** — animated character on top of background scenes
- **Multi-scene composition** — automatic concatenation of scenes into final video
- **MP4 export** — ready for YouTube and social media

## Architecture

```
Script Generation
    ↓
  Script (with scene metadata: duration, visual_prompt, camera_action)
    ↓
TTS Generation + Audio
    ↓
  Audio files (one per scene)
    ↓
Phoneme Alignment
    ↓
  Phoneme-to-viseme mapping (closed/open/wide mouth shapes)
    ↓
Frame Rendering
    ├─ Load background image
    ├─ Stack character sprite layer
    ├─ Render mouth sprite (per-frame) based on phoneme timing
    └─ Composite layers → PNG frames
    ↓
Video Composition (FFmpeg)
    ├─ Combine frames + audio for each scene
    └─ Concatenate all scenes into final MP4
    ↓
Final Output
    └─ outputs/video/<title>/<title>.mp4
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
pip install Pillow
```

### 2. Run the Demo Pipeline

```bash
python run_animation_pipeline.py
```

This will:
- Generate a sample script about "Jungle Adventure"
- Convert speech to audio using Google TTS
- Render animation frames with phoneme-level lip-sync
- Compose into a final MP4 video
- Save to `outputs/video/jungle_adventure_demo.mp4`

### 3. Customize for Your Content

Edit or create a custom runner:

```python
from app.services.script_generator import generate_script
from app.services.animation_service import render_script_to_video

topic = {
    "month": "Month_2",
    "category": "learning",
    "title": "Counting with Bibo",
}
script = generate_script(topic)

output = render_script_to_video(
    script,
    out_file=Path("outputs/video/counting.mp4"),
    fps=30,
    resolution=(1280, 720),
)
print(f"Video saved: {output}")
```

## Key Components

### `app/services/script_generator.py`

Generates a script with per-scene metadata:

```python
{
    "title": "Jungle Adventure",
    "scenes": [
        {
            "scene_number": 1,
            "text": "Let's explore the jungle!",
            "duration": 2.5,                        # seconds
            "visual_prompt": "A bright jungle scene",
            "camera_action": "pan_left",
            "audio_cues": ["CLAP"],
            "lip_sync": True,
        },
        ...
    ]
}
```

**Key fields:**
- `duration` — estimated from word count (default: 140 WPM)
- `visual_prompt` — describes the background for image generation
- `camera_action` — guides animation (static, pan, zoom, etc.)

### `app/services/animation_service.py`

**Core functions:**

- `render_shot_frames()` — renders PNG frames for one scene
  - Loads/creates background image
  - Stacks character sprite layer (optional)
  - Generates mouth sprites based on phoneme timing
  - Applies subtle zoom effect
  - Outputs PNG frame sequence

- `compose_shot_with_audio()` — combines frames + audio into MP4
  - Uses `ffmpeg` via moviepy
  - Synchronizes audio with frames

- `render_script_to_video()` — end-to-end orchestration
  - Generates TTS for all scenes
  - Renders all scene frames
  - Composes each scene video
  - Concatenates final MP4

**Canvas resolution (default):** 1280×720 (16:9)
- For YouTube Shorts: pass `resolution=(1080, 1920)`

### `app/services/phoneme_aligner.py`

Maps text → phonemes → visemes (mouth shapes):

```python
from app.services.phoneme_aligner import align_text_to_phonemes, get_viseme_at_time

text = "Hello there!"
duration = 2.5  # seconds

phonemes = align_text_to_phonemes(text, duration)
# [('h', 0.0, 0.3), ('e', 0.3, 0.55), ..., ('ə', 2.2, 2.5)]

viseme = get_viseme_at_time(phonemes, t=1.0)
# → "open" or "closed" or "wide"
```

**Viseme types:**
- `"closed"` — lips together (stops: p, b, t, d, k, g, m, n)
- `"open"` — mouth slightly open (vowels, approximants)
- `"wide"` — mouth wide (fricatives: s, sh, f, th)

## Custom Visuals

To use custom sprites, place files in a visuals directory:

```
outputs/visuals/<title>/
├── scene_01.png              # background image
├── character_neutral.png     # character sprite (optional)
├── mouth_closed.png          # mouth shape (closed, open, wide)
├── mouth_open.png
└── mouth_wide.png
```

Then pass to the renderer:

```python
render_script_to_video(
    script,
    visuals_dir=Path("outputs/visuals/my_story"),
)
```

**Sprite naming conventions:**
- `scene_##.png` — background for scene N
- `character_<pose>.png` — character in pose (neutral, happy, sad)
- `mouth_<viseme>.png` — mouth shape (closed, open, wide)
- `prop_<name>.png` — prop object (e.g., prop_ball.png)

## Export Presets

### YouTube (Landscape)

```python
render_script_to_video(
    script,
    resolution=(1920, 1080),  # 1080p
    fps=30,
)
```

### YouTube Shorts (Vertical)

```python
render_script_to_video(
    script,
    resolution=(1080, 1920),  # 9:16 vertical
    fps=30,
)
```

### Web (Small Bitrate)

```python
# Use lower resolution and FPS
render_script_to_video(
    script,
    resolution=(640, 360),
    fps=24,
)
```

## Performance Tips

1. **Reduce frame count:** Lower `fps` for faster rendering
   ```python
   render_script_to_video(script, fps=12)  # faster, smaller file
   ```

2. **Smaller resolution:** Start with 720p
   ```python
   render_script_to_video(script, resolution=(1280, 720))
   ```

3. **Skip custom visuals:** Defaults are fast (solid colors + text)
   ```python
   render_script_to_video(script, visuals_dir=None)
   ```

4. **Batch process:** Generate multiple videos in sequence
   ```python
   for topic in topics:
       script = generate_script(topic)
       render_script_to_video(script)
   ```

## File Structure

After running the pipeline:

```
outputs/
├── audio/
│   └── <title>/
│       ├── scene_01.mp3
│       ├── scene_02.mp3
│       └── ...
├── visuals/
│   └── <title>/
│       ├── scene_01.png
│       └── ...
└── video/
    └── <title>/
        ├── scene_01/
        │   └── frames/
        │       ├── 00000.png
        │       ├── 00001.png
        │       └── ...
        ├── scene_02/
        │   └── frames/
        │       └── ...
        ├── scene_01.mp4
        ├── scene_02.mp4
        └── <title>.mp4    # Final concatenated video
```

## Troubleshooting

### FFmpeg errors

**Error:** `"ffmpeg not found"`
- Install: `sudo apt-get install ffmpeg` (Linux) or `brew install ffmpeg` (macOS)
- Or: `pip install imageio-ffmpeg`

### Audio not syncing

- Ensure TTS duration matches `scene['duration']` estimate
- Increase `duration` parameter if scenes feel cut off

### Mouth animation not showing

- Check mouth sprite files exist in visuals directory
- Verify phoneme_aligner is generating valid phonemes
- Try with verbose logging: add `print(f"Viseme: {viseme}")` in render loop

### Video export fails

- Check disk space: video files are large (can be 100MB+)
- Verify ffmpeg codec support: `ffmpeg -codecs | grep libx264`
- Try lower resolution first

## Advanced: Custom Animation

To extend the pipeline:

1. **Custom camera moves:** Modify `_subtle_zoom_transform()` in animation_service.py
2. **Character poses:** Generate multi-pose character sprites, select by time
3. **Particle effects:** Render particles as additional layers (confetti, sparkles)
4. **Background music:** Add background track in post-production
5. **Sound effects:** Layer SFX on top of dialogue

Example: Pan camera left

```python
def pan_left_transform(img, t, duration, offset=50):
    # Create a larger canvas, shift left over time
    px = int((t / duration) * offset)
    # ... shift image
    return shifted_img
```

## API Reference

### `generate_script(topic: dict, min_scenes=3, max_scenes=6) → dict`

Generates a script with random scenes.

**Returns:** `dict` with keys:
- `title` – str
- `scenes` – list of scene dicts
  - `scene_number` – int
  - `text` / `narration` – str
  - `duration` – float (seconds)
  - `visual_prompt` – str
  - `camera_action` – str
  - `audio_cues` – list[str]
  - `lip_sync` – bool

### `render_script_to_video(script, visuals_dir=None, out_file=None, fps=24, resolution=(1280, 720)) → str`

Renders script → final MP4.

**Args:**
- `script` – dict (from generate_script)
- `visuals_dir` – Path or None (custom sprites directory)
- `out_file` – Path or None (defaults to outputs/video/<title>/<title>.mp4)
- `fps` – int (24 or 30 recommended)
- `resolution` – tuple (width, height)

**Returns:** str (path to output MP4)

### `render_shot_frames(...) → tuple[list[str], list]`

Renders frames for a single scene.

**Returns:**
- `list[str]` – paths to PNG frames
- `list` – phoneme times (for debugging)

### `align_text_to_phonemes(text: str, duration: float) → list[tuple]`

Maps text to phoneme timestamps.

**Returns:** list of `(phoneme_str, start_time, end_time)`

### `get_viseme_at_time(phonemes, t: float) → str`

Gets mouth shape for a given time.

**Returns:** "closed", "open", or "wide"

## Next Steps

- [ ] Add background music (audio mixing)
- [ ] Implement text/title overlay rendering
- [ ] Add simple skeletal animation for character poses
- [ ] Support frame interpolation for smoother motion
- [ ] Integrate with YouTube API for auto-upload
- [ ] Add subtitle generation and rendering
- [ ] Create web UI for pipeline

---

**Questions?** Check `run_animation_pipeline.py` for a working example!
