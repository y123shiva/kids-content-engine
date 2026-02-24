# Animation Pipeline Quick Reference

## TL;DR: Get Animated Video in 3 Steps

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the pipeline
python run_full_animation_pipeline.py

# 3. Check outputs/video/
# Ready-to-upload videos in multiple formats!
```

## What You Get

| File | Format | Use Case |
|------|--------|----------|
| `youtube_720p.mp4` | 1280×720 @ 24fps | YouTube regular videos |
| `youtube_shorts.mp4` | 1080×1920 @ 30fps | YouTube Shorts |
| `instagram_reels.mp4` | 1080×1920 @ 30fps | Instagram Reels |
| `web_preview.mp4` | 640×360 @ 24fps | Website/preview |
| `thumbnail.jpg` | 1280×720 | Video thumbnail |
| `metadata.json` | JSON | YouTube upload data |

## Code Examples

### Generate & Export Video

```python
from app.services.script_generator import generate_script
from app.services.animation_service import render_script_to_video
from app.services.export_service import export_with_preset
from pathlib import Path

# Create script
topic = {"month": "Month_1", "category": "fun", "title": "My Story"}
script = generate_script(topic)

# Render animation
video = render_script_to_video(script)

# Export to YouTube Shorts format
shorts = export_with_preset(
    Path(video),
    Path("outputs/video/my_story_shorts.mp4"),
    preset_name="shorts_vertical"
)
```

### Generate Thumbnail

```python
from app.services.export_service import generate_thumbnail
from pathlib import Path

thumb = generate_thumbnail(
    Path("outputs/video/my_story/my_story.mp4"),
    title="My Amazing Story",
    time_offset=2.0,  # Extract frame at 2 seconds
)
```

### Export Presets Available

```python
from app.services.export_service import list_presets

for name, preset in list_presets().items():
    print(f"{name}: {preset['resolution']} @ {preset['fps']}fps")

# Output:
# youtube_1080p: (1920, 1080) @ 30fps
# youtube_720p: (1280, 720) @ 24fps
# shorts_vertical: (1080, 1920) @ 30fps
# instagram_reels: (1080, 1920) @ 30fps
# web_preview: (640, 360) @ 24fps
# mobile_hd: (1080, 1080) @ 24fps
```

## Custom Visuals Setup

To use custom character sprites and backgrounds:

```
outputs/visuals/my_story/
├── scene_01.png                 # Background for scene 1
├── character_neutral.png        # Character sprite
├── mouth_closed.png             # Mouth shape (closed)
├── mouth_open.png               # Mouth shape (open)
└── mouth_wide.png               # Mouth shape (wide)
```

Then use:
```python
render_script_to_video(
    script,
    visuals_dir=Path("outputs/visuals/my_story"),
)
```

## Output Locations

```
outputs/
├── audio/
│   └── my_story/
│       ├── scene_01.mp3
│       ├── scene_02.mp3
│       └── ...
└── video/
    └── my_story/
        ├── master.mp4              # Master video (1280×720)
        ├── youtube_720p.mp4        # YouTube optimized
        ├── youtube_shorts.mp4      # Shorts format (vertical)
        ├── instagram_reels.mp4     # Instagram format
        ├── web_preview.mp4         # Low-bitrate preview
        ├── thumbnail.jpg
        ├── metadata.json
        └── scene_01/
            └── frames/             # Intermediate PNG frames
                ├── 00000.png
                ├── 00001.png
                └── ...
```

## Performance Tips

| Goal | Setting | Impact |
|------|---------|--------|
| Faster rendering | fps=12 | 2-3x faster, lower quality |
| Faster rendering | resolution=(640, 360) | 10x faster, small file |
| Better quality | fps=30 | Larger file, smoother motion |
| Better quality | resolution=(1920, 1080) | 4x larger file, sharp |
| Offline only | visuals_dir=None | Uses generated defaults |

Example: Fast preview draft
```python
render_script_to_video(script, fps=12, resolution=(640, 360))
```

## Troubleshooting

**FFmpeg not found:**
```bash
pip install imageio-ffmpeg
```

**Out of memory:**
- Reduce resolution or FPS
- Process fewer scenes at once
- Clear `outputs/video/*/scene_*/frames/` after encoding

**Audio out of sync:**
- Check TTS duration is >= scene duration
- Increase scene `duration` estimate
- Check `requirements.txt` has `mutagen` (audio duration detection)

**Mouth animation wrong:**
- Verify `phoneme_aligner.py` is being used
- Check viseme sprites exist in visuals directory
- Try with default visemes (auto-generated)

## What's Happening Under the Hood

```
Script
  ↓ (scene_generator)
Scene metadata (text, duration, etc.)
  ↓ (tts_service)
Audio files (.mp3)
  ↓ (animation_service + phoneme_aligner)
Phonemes & visemes per frame
  ↓ (animation_service)
PNG frames (one per scene)
  ↓ (moviepy + ffmpeg)
MP4 video (scene-level)
  ↓ (concatenate)
Final MP4 (all scenes)
  ↓ (export_service)
Multiple formats (YouTube, Shorts, Instagram, web)
```

## API Quick Reference

### Script Generation
```python
from app.services.script_generator import generate_script

script = generate_script(
    topic={"month": "...", "category": "...", "title": "..."},
    min_scenes=2,
    max_scenes=6
)
```

### Animation Rendering
```python
from app.services.animation_service import render_script_to_video

video_path = render_script_to_video(
    script=script,
    visuals_dir=Path("..."),  # Optional
    out_file=Path("..."),     # Optional
    fps=24,
    resolution=(1280, 720),
)
```

### Export
```python
from app.services.export_service import export_with_preset

export_with_preset(
    input_video=Path("video.mp4"),
    output_path=Path("output.mp4"),
    preset_name="shorts_vertical",  # or youtube_720p, instagram_reels, etc.
)
```

### Thumbnail
```python
from app.services.export_service import generate_thumbnail

thumbnail = generate_thumbnail(
    video_path=Path("video.mp4"),
    output_path=Path("thumb.jpg"),
    title="Video Title",
    time_offset=2.0,
)
```

### Metadata
```python
from app.services.export_service import create_video_metadata, save_metadata

metadata = create_video_metadata(
    title="My Video",
    description="...",
    tags=["kids", "animation"],
    category="Kids",
    thumbnail_path=Path("thumb.jpg"),
)

save_metadata(metadata, Path("metadata.json"))
```

## Common Workflows

### Workflow 1: Quick Preview
```bash
python run_animation_pipeline.py
```

### Workflow 2: Multiple Exports
```bash
python run_full_animation_pipeline.py
# Generates all formats automatically
```

### Workflow 3: Custom Script
```python
from pathlib import Path
from app.services.script_generator import generate_script
from app.services.animation_service import render_script_to_video
from app.services.export_service import export_with_preset

# Your topic
topic = {"month": "Month_2", "category": "learning", "title": "Shapes"}
script = generate_script(topic)

# Render
video = render_script_to_video(script)

# Export to Shorts
export_with_preset(
    Path(video),
    Path(f"outputs/video/{script['title']}_shorts.mp4"),
    preset_name="shorts_vertical"
)
```

### Workflow 4: YouTube Upload Ready
```python
from pathlib import Path
from app.services.export_service import (
    export_with_preset, generate_thumbnail, 
    create_video_metadata, save_metadata
)

video = Path("outputs/video/my_story/master.mp4")

# Export
export_with_preset(video, Path("video.mp4"), "youtube_720p")

# Thumbnail
thumb = generate_thumbnail(video, Path("thumb.jpg"), title="My Story")

# Metadata
metadata = create_video_metadata(
    title="My Story",
    description="...",
    tags=["kids", "animation"],
    thumbnail_path=thumb,
)
save_metadata(metadata, Path("metadata.json"))

print("✓ Ready to upload!")
```

---

**Need more help?** See `ANIMATION_PIPELINE.md` for full documentation.
