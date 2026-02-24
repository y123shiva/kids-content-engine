def build_rag_prompt(
    user_prompt: str,
    scenes: list,
    max_total_duration: float = 60.0,
    target_scene_count: int = 8,
    avg_scene_duration: float = 6.0
) -> str:
    """
    Build a structured RAG prompt for Bibo animation script generation.
    Enforces duration, scene structure, and strict JSON output.
    """

    context_lines = []
    total_duration = 0.0

    # =============================
    # Build Structured Context
    # =============================
    for s in scenes:
        if total_duration >= max_total_duration:
            break

        text = (s.get("text") or s.get("narration") or "").replace("\n", " ").strip()
        title = s.get("title", "Unknown")
        category = s.get("category", "General")

        duration = s.get("estimated_duration", avg_scene_duration)

        try:
            duration = float(duration)
        except (TypeError, ValueError):
            duration = avg_scene_duration

        if total_duration + duration > max_total_duration:
            duration = max_total_duration - total_duration

        total_duration += duration

        context_lines.append(
            f"[Title: {title} | Category: {category} | Approx: {duration:.1f}s]\n{text}"
        )

    context_block = "\n\n".join(context_lines)

    if not context_block:
        context_block = "No relevant examples found. Create an original, high-energy Bibo story."

    # =============================
    # Prompt Template
    # =============================
    return f"""
You are Bibo, a cheerful, high-energy AI teacher for children aged 3–6.

Your task is to generate a structured animation script.

USER REQUEST:
{user_prompt}

REFERENCE EXAMPLES (Do NOT copy. Use only for inspiration):
{context_block}

STRICT GENERATION RULES:

1. EXACTLY {target_scene_count} scenes.
2. Total duration MUST be <= {max_total_duration} seconds.
3. Each scene duration should be around {avg_scene_duration} seconds.
4. Scene numbers MUST be sequential: 1, 2, 3...
5. Each scene MUST contain:
   - scene_number
   - timestamp (example: "00:00-00:06")
   - emotion (HAPPY, EXCITED, SURPRISED, THINKING)
   - speaker
   - narration
   - actions (array)
   - visuals (array)
6. Keep narration short and energetic.
7. NO markdown.
8. Return ONLY raw valid JSON.

JSON FORMAT:

{{
  "title": "Fun video title",
  "character": "Bibo",
  "age_group": "3-6",
  "duration_seconds": {max_total_duration},
  "learning_goals": ["One clear goal"],
  "scenes": [
    {{
      "scene_number": 1,
      "timestamp": "00:00-00:06",
      "emotion": "EXCITED",
      "speaker": "Bibo",
      "narration": "Narration text",
      "actions": ["Action 1"],
      "visuals": ["Visual description"]
    }}
  ]
}}

BIBO STYLE RULES:
- Use phrases like: "Wowie!", "Zoom!", "Are you ready?"
- Keep sentences simple.
- Maximum energy.
- Designed for animation timing.
"""
