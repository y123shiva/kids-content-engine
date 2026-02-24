#!/usr/bin/env python3
"""
Complete animation pipeline with multi-format export.

Demonstrates:
  1. Generate script
  2. Render animation
  3. Export to multiple platforms (YouTube, Shorts, Instagram, etc.)
  4. Generate thumbnails and metadata

Usage:
  python run_full_animation_pipeline.py
"""

import sys
from pathlib import Path

from app.services.script_generator import generate_script
from app.services.animation_service import render_script_to_video
from app.services.export_service import (
    export_with_preset,
    generate_thumbnail,
    create_video_metadata,
    save_metadata,
    list_presets,
)


def run_pipeline():
    """Run complete animation pipeline with exports."""
    print("=" * 70)
    print("Kids Content Engine: Complete Animation + Export Pipeline")
    print("=" * 70)

    # === STEP 1: Generate Script ===
    print("\n[1/6] Generating script...")
    topic = {
        "month": "Month_1",
        "category": "learning",
        "title": "Colors of the Rainbow",
    }
    script = generate_script(topic, min_scenes=2, max_scenes=3)
    print(f"  ✓ Generated {len(script['scenes'])} scenes")

    # === STEP 2: Generate Animations ===
    print("\n[2/6] Rendering animated video with lip-sync...")
    output_dir = Path("outputs/video") / script["title"].replace(" ", "_").lower()
    output_file = output_dir / "master.mp4"

    try:
        output_file = render_script_to_video(
            script=script,
            out_file=output_file,
            fps=24,
            resolution=(1280, 720),  # Start with landscape
        )
        print(f"  ✓ Master video created: {output_file}")
    except Exception as e:
        print(f"  ✗ Failed to render: {e}")
        return 1

    if not Path(output_file).exists():
        print(f"  ✗ Output file not found")
        return 1

    # === STEP 3: Generate Thumbnail ===
    print("\n[3/6] Generating thumbnail...")
    try:
        thumb_path = generate_thumbnail(
            Path(output_file),
            output_path=output_dir / "thumbnail.jpg",
            title=script["title"],
            time_offset=1.0,
        )
        print(f"  ✓ Thumbnail: {thumb_path}")
    except Exception as e:
        print(f"  ⚠ Thumbnail generation skipped: {e}")
        thumb_path = None

    # === STEP 4: Create Metadata ===
    print("\n[4/6] Creating metadata...")
    description = f"""
Watch {script['title']} - an interactive story for kids!

Category: {script['category']}
Duration: {sum(s.get('duration', 0) for s in script['scenes']):.1f} seconds

Made for Kids™
Subscribe for more content!
    """.strip()

    metadata = create_video_metadata(
        title=script["title"],
        description=description,
        tags=["kids", "animation", "education", script["category"]],
        category="Kids",
        thumbnail_path=thumb_path,
    )
    metadata_file = output_dir / "metadata.json"
    save_metadata(metadata, metadata_file)
    print(f"  ✓ Metadata: {metadata_file}")

    # === STEP 5: Export to Multiple Presets ===
    print("\n[5/6] Exporting to multiple platforms...")
    presets_available = list_presets()

    exports = {
        "youtube_720p": output_dir / "youtube_720p.mp4",
        "shorts_vertical": output_dir / "youtube_shorts.mp4",
        "instagram_reels": output_dir / "instagram_reels.mp4",
        "web_preview": output_dir / "web_preview.mp4",
    }

    for preset_name, output_path in exports.items():
        if preset_name not in presets_available:
            print(f"  ⚠ {preset_name} not available")
            continue
        try:
            print(f"    Exporting {preset_name}...")
            export_with_preset(
                Path(output_file),
                output_path,
                preset_name=preset_name,
                verbose=False,
            )
            size_mb = output_path.stat().st_size / (1024 * 1024)
            print(f"      ✓ {output_path.name} ({size_mb:.1f} MB)")
        except Exception as e:
            print(f"      ✗ Failed: {e}")

    # === STEP 6: Summary ===
    print("\n[6/6] Pipeline Complete!")
    print("\n" + "=" * 70)
    print("OUTPUT FILES:")
    print("=" * 70)
    print(f"\nMaster video: {output_file}")
    print(f"  └─ All formats and originals in: {output_dir}/")
    print(f"\nMetadata: {metadata_file}")
    print(f"Thumbnail: {thumb_path}")

    print("\n" + "=" * 70)
    print("READY TO UPLOAD:")
    print("=" * 70)
    print("\nYouTube:")
    print(f"  • Video: {output_dir / 'youtube_720p.mp4'}")
    print(f"  • Thumbnail: {thumb_path}")
    print(f"  • Title: {metadata['title']}")
    print(f"  • Tags: {', '.join(metadata['tags'])}")

    print("\nYouTube Shorts:")
    print(f"  • Video: {output_dir / 'youtube_shorts.mp4'}")

    print("\nInstagram Reels:")
    print(f"  • Video: {output_dir / 'instagram_reels.mp4'}")

    print("\nWeb:")
    print(f"  • Preview: {output_dir / 'web_preview.mp4'}")

    print("\n" + "=" * 70)
    print("NEXT STEPS:")
    print("=" * 70)
    print("\n1. Review videos in outputs/video/")
    print("2. Customize script and visuals for your stories")
    print("3. Upload to platform of choice using metadata")
    print("4. Create new scripts and repeat!")

    return 0


if __name__ == "__main__":
    sys.exit(run_pipeline())
