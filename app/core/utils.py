import json
import re


def extract_json(text: str) -> dict:
    """
    Extracts the most likely valid JSON object from LLM output.
    Handles:
    - Markdown code blocks
    - Raw JSON in text
    - Multiple JSON objects
    """

    # 1️⃣ Try markdown code blocks first (highest confidence)
    codeblock_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if codeblock_match:
        candidate = codeblock_match.group(1).strip()
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass  # fallback

    # 2️⃣ Balanced brace extraction (safer than regex-only)
    stack = []
    json_candidates = []
    start = None

    for i, char in enumerate(text):
        if char == "{":
            if not stack:
                start = i
            stack.append("{")
        elif char == "}":
            if stack:
                stack.pop()
                if not stack and start is not None:
                    candidate = text[start:i + 1]
                    try:
                        json_candidates.append(json.loads(candidate))
                    except json.JSONDecodeError:
                        pass

    if json_candidates:
        # Heuristic: most complex object = root script
        return max(json_candidates, key=lambda x: len(json.dumps(x)))

    raise ValueError("No valid JSON object found in LLM output")
