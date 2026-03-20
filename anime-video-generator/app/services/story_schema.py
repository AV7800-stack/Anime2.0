from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field


class CharacterSpec(BaseModel):
    name: str
    role: str = Field(..., description="Protagonist / love interest / villain / mentor, etc.")
    description: str = Field(..., description="Physical + style + anime face description.")
    face_traits: str = Field(
        ...,
        description="Unique facial traits to keep consistent (eyes, hair color, scars, etc.).",
    )
    prompt_seed_hint: int = Field(12345, description="Seed hint for character generation.")


class DialogueLine(BaseModel):
    speaker: str
    text: str
    # Emotion tag for SFX/BGM style.
    emotion: str = Field("neutral")
    # Optional cue for scene SFX
    sfx_keywords: list[str] = Field(default_factory=list)


class SceneSpec(BaseModel):
    index: int
    title: str
    background: str
    emotion: str
    camera_angle: str
    # Used to render the scene image(s)
    character_descriptions: list[str]
    # Dialogue included in this scene
    dialogue: list[DialogueLine]
    # Narration text (VO or subtitles)
    narration: str = ""


class StorySpec(BaseModel):
    title: str
    genre: str
    logline: str
    style_preset: str
    main_characters: list[CharacterSpec]
    scenes: list[SceneSpec]

