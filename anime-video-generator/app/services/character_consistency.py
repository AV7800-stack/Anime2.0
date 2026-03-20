from __future__ import annotations

from pathlib import Path

from app.services.story_schema import SceneSpec


def select_reference_for_scene(scene: SceneSpec, reference_images: dict[str, Path]) -> Path | None:
    """
    Best-effort character identity anchor.

    We don't have multi-character face identity guarantees without specialized pipelines.
    This chooses a single reference image (if available) to condition img2img.
    """
    # Prefer the first speaker in the dialogue (often the main talking character).
    for dlg in scene.dialogue:
        if dlg.speaker in reference_images:
            return reference_images[dlg.speaker]

    # If scene contains character_descriptions and they mention known names, try that.
    for name, ref in reference_images.items():
        if name.lower() in (scene.background + " " + scene.title).lower():
            return ref

    # Fall back to any available ref.
    if reference_images:
        return next(iter(reference_images.values()))

    return None

