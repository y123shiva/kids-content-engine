from app.core.config import (
    LLM_PROVIDER,
    OPENAI_API_KEY,
    OPENAI_MODEL_NAME,
    GEMINI_API_KEY,
    GEMINI_MODEL_NAME
)

import json
import re
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO)

# =========================================================
# Conditional SDK Imports
# =========================================================

if LLM_PROVIDER == "gemini":
    try:
        from google import genai
    except ImportError:
        raise ImportError("Gemini SDK not installed. Run: pip install google-genai")

elif LLM_PROVIDER == "openai":
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("OpenAI SDK not installed. Run: pip install openai")

else:
    raise ValueError(f"Unsupported LLM_PROVIDER: {LLM_PROVIDER}")


# =========================================================
# LLM Service
# =========================================================

class LLMService:
    """
    Unified LLM Service supporting:
    - OpenAI
    - Gemini

    Designed for:
    - Script generation
    - RAG augmentation
    - Strict JSON output
    """

    def __init__(self):
        self.provider = LLM_PROVIDER

        if self.provider == "gemini":
            self.client = genai.Client(api_key=GEMINI_API_KEY)
            self.model_name = GEMINI_MODEL_NAME
        else:
            self.client = OpenAI(api_key=OPENAI_API_KEY)
            self.model_name = OPENAI_MODEL_NAME

    # =====================================================
    # Core Text Generation
    # =====================================================

    def generate(
        self,
        prompt: str,
        system_prompt: str = "You are a professional children's educational script writer.",
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> str:

        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        try:

            # ================= GEMINI =================
            if self.provider == "gemini":

                full_prompt = f"{system_prompt}\n\n{prompt}"

                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=full_prompt,
                    config={
                        "temperature": temperature,
                        "max_output_tokens": max_tokens,
                    }
                )

                text = getattr(response, "text", None)

                if not text:
                    raise RuntimeError("Gemini returned empty response.")

                return text.strip()

            # ================= OPENAI =================
            else:

                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                )

                content = response.choices[0].message.content

                if not content:
                    raise RuntimeError("OpenAI returned empty response.")

                return content.strip()

        except Exception as e:
            raise RuntimeError(f"LLM generation failed: {str(e)}")

    # =====================================================
    # RAG-Enhanced Generation
    # =====================================================

    def generate_with_context(
        self,
        user_prompt: str,
        context: Optional[str] = None,
        system_prompt: str = "You are a professional children's educational script writer.",
        temperature: float = 0.7,
        max_tokens: int = 1200,
    ) -> str:
        """
        Generate text with RAG context injected.
        """

        if context:
            combined_prompt = f"""
Use the following reference material to improve the script:

---------------------
{context}
---------------------

Now generate the requested script:

{user_prompt}
"""
        else:
            combined_prompt = user_prompt

        return self.generate(
            prompt=combined_prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    # =====================================================
    # Strict JSON Generation (Production Safe)
    # =====================================================

    def generate_json(
        self,
        prompt: str,
        system_prompt: str = "Return ONLY valid JSON. No markdown. No explanation.",
        temperature: float = 0.4,
        max_tokens: int = 1500,
        retries: int = 2,
    ) -> dict:

        for attempt in range(retries):

            raw_output = self.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )

            cleaned = self._clean_json_output(raw_output)

            try:
                return json.loads(cleaned)

            except json.JSONDecodeError:
                logging.warning(f"JSON parsing failed (attempt {attempt+1}). Retrying...")

                # On retry, force stricter instruction
                prompt = f"""
Your previous output was not valid JSON.

Return ONLY valid JSON.
No markdown.
No explanation.

{prompt}
"""

        raise RuntimeError(
            f"LLM did not return valid JSON after {retries} attempts."
        )

    # =====================================================
    # Internal Helpers
    # =====================================================

    def _clean_json_output(self, text: str) -> str:
        """
        Removes markdown fences and extra text around JSON.
        """

        # Remove ```json fences
        text = re.sub(r"```json|```", "", text).strip()

        # Extract first JSON object if extra text exists
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return match.group(0)

        return text.strip()
