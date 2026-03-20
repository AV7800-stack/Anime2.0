from __future__ import annotations

import json
from typing import Any

from tenacity import retry, stop_after_attempt, wait_exponential

from app.services.llm_client import LLMClient, LLMError
from app.services.story_schema import StorySpec


def _style_prompt(style_preset: str) -> str:
    s = (style_preset or "").strip().lower()
    mapping = {
        "ghibli": "studio ghibli inspired anime film look, warm colors, soft painterly background, cinematic lighting",
        "naruto": "high-energy shonen anime look, bold linework, dynamic lighting, dramatic motion feel",
        "aot": "dark realistic anime look, gritty textures, intense contrast, military cinematic framing",
        "cyberpunk": "neon cyberpunk anime look, rain reflections, cinematic volumetric light, high detail city",
        "romance": "romantic anime film look, gentle color grading, soft bokeh, tender emotional composition",
        "fantasy": "epic fantasy anime look, magical atmosphere, detailed costumes, cinematic depth",
    }
    return mapping.get(s, f"anime style preset: {s}, cinematic lighting, high detail")


@retry(wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(3))
async def generate_story(
    llm: LLMClient,
    *,
    idea: str,
    style_preset: str,
    language: str,
    num_scenes: int,
) -> StorySpec:
    style_prompt = _style_prompt(style_preset)
    prompt = f"""
You are an expert anime screenwriter.
Generate a UNIQUE anime story based on the user's idea.

User idea:
{idea}

Requirements:
- Must be self-contained, with a clear beginning, middle, and end.
- Output MUST be JSON only (no markdown, no extra text).
- Use exactly {num_scenes} scenes.
- Dialogues must be in: {language}.
- Every character must feel consistent (same core personality + recurring traits).
- Scene scenes must include: character_descriptions, background, emotion, camera_angle, narration, and dialogue lines.
- camera_angle must be short like: "low-angle close-up", "wide establishing shot", "over-the-shoulder", etc.
- emotion must be one word or short phrase: "determined", "heartbroken", "excited", "tense", etc.
- narration should be 1-3 sentences, suitable for voiceover.

Return this exact JSON schema:
{{
  "title": string,
  "genre": string,
  "logline": string,
  "style_preset": string,
  "main_characters": [
    {{
      "name": string,
      "role": string,
      "description": string,
      "face_traits": string,
      "prompt_seed_hint": integer
    }}
  ],
  "scenes": [
    {{
      "index": integer,
      "title": string,
      "background": string,
      "emotion": string,
      "camera_angle": string,
      "character_descriptions": [string],
      "dialogue": [
        {{
          "speaker": string,
          "text": string,
          "emotion": string,
          "sfx_keywords": [string]
        }}
      ],
      "narration": string
    }}
  ]
}}

Style hint for prompts inside the story:
{style_prompt}
"""
    result = await llm.generate_json(prompt=prompt)
    data = result.data
    # If the model returned raw_text, it might have nested JSON; handle a bit.
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except Exception:
            pass
    return StorySpec.model_validate(data)

