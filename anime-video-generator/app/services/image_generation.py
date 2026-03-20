from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from app.utils.config import Settings


def _hash_seed(*parts: str, base: int = 12345) -> int:
    h = hashlib.sha256("::".join(map(str, parts)).encode("utf-8")).hexdigest()
    # SD seeds are 32-bit in practice
    return (int(h[:8], 16) + base) % 2**31


def _aspect_to_size(aspect: str, low_end: bool) -> tuple[int, int]:
    # Return (width, height)
    if aspect == "9:16":  # vertical
        # Keep dimensions divisible by 8 for SD compatibility.
        return (768, 1360) if not low_end else (512, 912)
    if aspect == "1:1":
        return (768, 768) if not low_end else (512, 512)
    # 16:9
    return (1024, 576) if not low_end else (768, 432)


NEGATIVE_PROMPT = (
    "low quality, worst quality, blurry, bad anatomy, bad hands, missing fingers, extra fingers, "
    "deformed, poorly drawn face, watermark, signature, text, logo"
)


def style_prompt_for_preset(style_preset: str) -> str:
    s = (style_preset or "").strip().lower()
    mapping = {
        "ghibli": "studio ghibli style, warm colors, soft painterly background",
        "naruto": "naruto style inspired anime look, bold linework, dynamic lighting",
        "aot": "attack on titan style inspired anime look, gritty textures, intense contrast",
        "cyberpunk": "cyberpunk anime style, neon lighting, rain reflections, volumetric light",
        "romance": "romantic anime film look, gentle color grading, soft bokeh",
        "fantasy": "epic fantasy anime look, magical atmosphere, cinematic depth",
    }
    return mapping.get(s, f"anime style preset: {s}")


@dataclass
class GeneratedImage:
    path: Path
    seed: int


class SDImageGenerator:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._pipe_txt2img = None
        self._pipe_img2img = None

    def _get_device(self) -> str:
        # Avoid importing torch globally to keep fast startup.
        try:
            import torch

            if self.settings.force_device:
                return self.settings.force_device
            if torch.cuda.is_available():
                return "cuda"
            if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
                return "mps"
        except Exception:
            pass
        return "cpu"

    def _ensure_pipelines(self) -> None:
        if self._pipe_txt2img is not None:
            return

        from diffusers import EulerAncestralDiscreteScheduler, StableDiffusionImg2ImgPipeline, StableDiffusionPipeline

        import torch

        device = self._get_device()
        dtype = torch.float16 if device in {"cuda"} else torch.float32

        scheduler = EulerAncestralDiscreteScheduler.from_pretrained(self.settings.sd_model, subfolder="scheduler")

        self._pipe_txt2img = StableDiffusionPipeline.from_pretrained(
            self.settings.sd_model,
            scheduler=scheduler,
            torch_dtype=dtype,
        )
        self._pipe_txt2img = self._pipe_txt2img.to(device)
        self._pipe_txt2img.enable_attention_slicing()

        if self.settings.sd_lora_path:
            # Best-effort: LoRA path should point to a .safetensors/.bin
            self._pipe_txt2img.load_lora_weights(self.settings.sd_lora_path, weight_name=None)
            if hasattr(self._pipe_txt2img, "fuse_lora"):
                self._pipe_txt2img.fuse_lora()

        # Optional img2img
        try:
            self._pipe_img2img = StableDiffusionImg2ImgPipeline.from_pretrained(
                self.settings.sd_model,
                scheduler=scheduler,
                torch_dtype=dtype,
            ).to(device)
            self._pipe_img2img.enable_attention_slicing()

            if self.settings.sd_lora_path:
                self._pipe_img2img.load_lora_weights(self.settings.sd_lora_path, weight_name=None)
                if hasattr(self._pipe_img2img, "fuse_lora"):
                    self._pipe_img2img.fuse_lora()
        except Exception:
            self._pipe_img2img = None

    def generate_txt2img(
        self,
        *,
        prompt: str,
        negative_prompt: str = NEGATIVE_PROMPT,
        seed: int,
        out_path: Path,
        aspect: str = "16:9",
    ) -> GeneratedImage:
        self._ensure_pipelines()

        import torch

        out_path.parent.mkdir(parents=True, exist_ok=True)
        device = self._get_device()
        width, height = _aspect_to_size(aspect, self.settings.low_end_mode)

        steps = 18 if self.settings.low_end_mode else 30
        guidance = 7.0 if self.settings.low_end_mode else 8.5

        generator = torch.Generator(device=device).manual_seed(seed)
        image = self._pipe_txt2img(
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=steps,
            guidance_scale=guidance,
            width=width,
            height=height,
            generator=generator,
        ).images[0]

        image.save(out_path)
        return GeneratedImage(path=out_path, seed=seed)

    def generate_img2img(
        self,
        *,
        init_image_path: Path,
        prompt: str,
        negative_prompt: str = NEGATIVE_PROMPT,
        seed: int,
        out_path: Path,
        aspect: str = "16:9",
        strength: float = 0.45,
    ) -> GeneratedImage:
        self._ensure_pipelines()
        if self._pipe_img2img is None:
            # fallback to txt2img if img2img unavailable
            return self.generate_txt2img(
                prompt=prompt,
                negative_prompt=negative_prompt,
                seed=seed,
                out_path=out_path,
                aspect=aspect,
            )

        import torch
        from PIL import Image

        out_path.parent.mkdir(parents=True, exist_ok=True)
        device = self._get_device()
        width, height = _aspect_to_size(aspect, self.settings.low_end_mode)
        steps = 18 if self.settings.low_end_mode else 28
        guidance = 7.0 if self.settings.low_end_mode else 8.0

        init_img = Image.open(init_image_path).convert("RGB")
        init_img = init_img.resize((width, height))

        generator = torch.Generator(device=device).manual_seed(seed)
        image = self._pipe_img2img(
            prompt=prompt,
            negative_prompt=negative_prompt,
            image=init_img,
            strength=strength,
            num_inference_steps=steps,
            guidance_scale=guidance,
            width=width,
            height=height,
            generator=generator,
        ).images[0]
        image.save(out_path)
        return GeneratedImage(path=out_path, seed=seed)


def render_character_reference(
    sd: SDImageGenerator,
    *,
    character_name: str,
    character_description: str,
    style_preset: str,
    job_dir: Path,
    aspect: str,
    seed_hint: int,
) -> GeneratedImage:
    # Portrait-focused prompt to anchor the face traits.
    portrait_prompt = (
        f"{style_prompt_for_preset(style_preset)}, anime style portrait of {character_name}. {character_description}. "
        "same face, same character, consistent identity, detailed eyes, clean lineart, "
        "cinematic lighting, 4k, highly detailed"
    )
    seed = _hash_seed(character_name, character_description, base=seed_hint)
    out_path = job_dir / "characters" / f"{character_name}_ref.png"
    return sd.generate_txt2img(prompt=portrait_prompt, seed=seed, out_path=out_path, aspect=aspect)


def render_scene_keyframe(
    sd: SDImageGenerator,
    *,
    scene_index: int,
    scene_title: str,
    background: str,
    emotion: str,
    camera_angle: str,
    character_prompts: list[str],
    style_preset: str,
    job_dir: Path,
    aspect: str,
    seed: int,
    optional_reference_image: Path | None = None,
) -> GeneratedImage:
    character_blurb = "; ".join(character_prompts)
    prompt = (
        f"{style_prompt_for_preset(style_preset)}, anime style, {camera_angle}, cinematic lighting, detailed, 4k, "
        f"emotion: {emotion}. Scene: {scene_title}. Background: {background}. "
        f"Characters: {character_blurb}. "
        "same face, consistent character identity, clean lineart"
    )

    out_path = job_dir / "images" / f"scene_{scene_index:03d}.png"

    if optional_reference_image is not None:
        return sd.generate_img2img(
            init_image_path=optional_reference_image,
            prompt=prompt,
            seed=seed,
            out_path=out_path,
            aspect=aspect,
            strength=0.42,
        )

    return sd.generate_txt2img(prompt=prompt, seed=seed, out_path=out_path, aspect=aspect)

