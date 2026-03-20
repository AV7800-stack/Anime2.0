from __future__ import annotations

import json
import os
import traceback
from pathlib import Path
from typing import Callable

from app.models import GenerateAnimeRequest
from app.pipeline.youtube_upload import maybe_upload_to_youtube
from app.services.character_consistency import select_reference_for_scene
from app.services.image_generation import (
    SDImageGenerator,
    render_character_reference,
    render_scene_keyframe,
)
from app.services.llm_client import LLMClient
from app.services.lip_sync import try_run_wav2lip
from app.services.music_sfx import render_music_sfx_for_scene
from app.services.motion_video import make_kenburns_video
from app.services.subtitles import SubtitleSegment, write_srt
from app.services.story_generation import generate_story
from app.services.story_schema import DialogueLine, SceneSpec, StorySpec
from app.services.tts import TTSService
from app.services.video_assembler import assemble_final_video
from app.utils.config import ensure_dirs, load_settings
from app.utils.job_paths import make_job_paths


ProgressCb = Callable[[float, str | None], None]


def _safe_write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _create_placeholder_scene_image(scene: SceneSpec, out_path: Path, width: int = 1024, height: int = 576) -> None:
    from PIL import Image, ImageDraw, ImageFont

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (width, height), (20, 24, 45))
    draw = ImageDraw.Draw(img)

    # Use default PIL font (no external font dependency).
    text = f"{scene.title}\nEmotion: {scene.emotion}\n{scene.background[:60]}..."
    y = 20
    for line in text.split("\n"):
        draw.text((20, y), line, fill=(220, 230, 255))
        y += 24

    # Save
    img.save(out_path)


def _combine_dialogue_lines_to_wav(
    *,
    tts: TTSService,
    scene: SceneSpec,
    job_dir: Path,
    language: str,
    voice_style: str,
    progress_cb: ProgressCb | None,
) -> tuple[Path, list[SubtitleSegment], float]:
    from pydub import AudioSegment

    audio_dir = job_dir / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)

    scene_wav = audio_dir / f"scene_{scene.index:03d}_dialogue.wav"
    line_wavs = []
    subtitle_segments: list[SubtitleSegment] = []

    cur_time = 0.0
    # Generate each dialogue line sequentially so we get accurate timings.
    for li, dlg in enumerate(scene.dialogue):
        line_wav = audio_dir / f"scene_{scene.index:03d}_line_{li:02d}.wav"
        if progress_cb:
            progress_cb(0.0, f"TTS: scene {scene.index+1}/{scene.index+1} line {li+1}/{len(scene.dialogue)}")
        dur = tts.synthesize_to_wav(
            text=dlg.text,
            language=language,
            voice_style=voice_style,
            out_wav=line_wav,
        )
        line_wavs.append((line_wav, cur_time, cur_time + dur, dlg))
        cur_time += dur

    # Concatenate
    combined = None
    for line_wav, _, _, _dlg in line_wavs:
        seg = AudioSegment.from_file(str(line_wav))
        combined = seg if combined is None else combined + seg
    if combined is None:
        combined = AudioSegment.silent(duration=1000)
    combined.export(str(scene_wav), format="wav")

    total_dur = float(len(combined) / 1000.0)

    # Build subtitle segments with timings
    for _line_wav, start_s, end_s, dlg in line_wavs:
        subtitle_segments.append(
            SubtitleSegment(
                start_s=start_s,
                end_s=end_s,
                speaker=dlg.speaker,
                text=dlg.text,
            )
        )

    return scene_wav, subtitle_segments, total_dur


def generate_anime_job(
    req: GenerateAnimeRequest,
    *,
    job_id: str,
    progress_cb: ProgressCb | None = None,
) -> dict:
    settings = load_settings()
    ensure_dirs(settings)

    # Apply request runtime overrides
    if req.low_end:
        # freeze dataclass by creating a new settings-like behavior
        # easiest: just set env var for low-end, since SD generator uses settings.low_end_mode.
        os.environ["LOW_END_MODE"] = "1"

    # Reload settings to reflect low_end_mode env if needed.
    settings = load_settings()
    ensure_dirs(settings)

    job_paths = make_job_paths(settings, job_id)

    progress_cb = progress_cb or (lambda p, m=None: None)

    try:
        progress_cb(0.08, "Story generation (LLM)...")
        llm = LLMClient(settings)
        import asyncio

        story: StorySpec = asyncio.run(
            generate_story(
                llm,
                idea=req.idea,
                style_preset=req.style,
                language=req.language,
                num_scenes=req.num_scenes,
            )
        )
        _safe_write_json(job_paths.story_json, story.model_dump())

        progress_cb(0.15, "Scene images + character anchors...")

        # Init SD generator (may be heavy)
        sd = SDImageGenerator(settings)

        # Render character reference images (best-effort)
        characters_dir = job_paths.images_dir / "characters"
        characters_dir.mkdir(parents=True, exist_ok=True)
        reference_images: dict[str, Path] = {}

        for ch in story.main_characters:
            try:
                ref_img = render_character_reference(
                    sd,
                    character_name=ch.name,
                    character_description=ch.description + " " + ch.face_traits,
                    style_preset=req.style,
                    job_dir=job_paths.job_dir,
                    aspect=req.output_aspect,
                    seed_hint=ch.prompt_seed_hint,
                )
                reference_images[ch.name] = ref_img.path
            except Exception:
                # Placeholder portrait if SD fails
                placeholder = characters_dir / f"{ch.name}_ref.png"
                _create_placeholder_scene_image(
                    scene=SceneSpec(
                        index=0,
                        title=f"{ch.name}",
                        background="character portrait placeholder",
                        emotion="neutral",
                        camera_angle="front close-up",
                        character_descriptions=[ch.description],
                        dialogue=[],
                        narration="",
                    ),
                    out_path=placeholder,
                    width=1024,
                    height=1024,
                )
                reference_images[ch.name] = placeholder

        # Render one key image per scene
        for scene in story.scenes:
            # Pick init reference image if possible for stronger identity consistency
            optional_ref = select_reference_for_scene(scene, reference_images)

            character_prompts = scene.character_descriptions
            seed = (scene.index + 1) * 1337 + int(abs(hash(req.style)) % 100000)

            try:
                render_scene_keyframe(
                    sd,
                    scene_index=scene.index,
                    scene_title=scene.title,
                    background=scene.background,
                    emotion=scene.emotion,
                    camera_angle=scene.camera_angle,
                    character_prompts=character_prompts,
                    style_preset=req.style,
                    job_dir=job_paths.job_dir,
                    aspect=req.output_aspect,
                    seed=seed,
                    optional_reference_image=optional_ref,
                )
            except Exception:
                out_path = job_paths.images_dir / f"scene_{scene.index:03d}.png"
                _create_placeholder_scene_image(scene=scene, out_path=out_path)

        _safe_write_json(job_paths.scenes_json, story.model_dump()["scenes"])

        # TTS per scene
        progress_cb(0.35, "Text-to-speech (dialogues)...")
        tts = TTSService(settings)

        scene_dialogue_vw: list[tuple[Path, list[SubtitleSegment], float]] = []
        for scene in story.scenes:
            scene_img_duration_anchor = None
            scene_wav, scene_subs, scene_dur = _combine_dialogue_lines_to_wav(
                tts=tts,
                scene=scene,
                job_dir=job_paths.job_dir,
                language=req.language,
                voice_style=req.voice_style,
                progress_cb=None,
            )
            scene_dialogue_vw.append((scene_wav, scene_subs, scene_dur))

        # Create full SRT with cumulative timing
        progress_cb(0.48, "Background music + SFX (procedural)...")
        timeline_segments: list[SubtitleSegment] = []
        scene_audio_paths: list[Path] = []
        scene_video_base_paths: list[Path] = []

        # Mix audio and generate per-scene ken burns video

        scene_videos_for_assembler: list[Path] = []
        for scene, (dialogue_wav, scene_subs, scene_dur) in zip(story.scenes, scene_dialogue_vw):
            # Music + SFX
            music_wav = job_paths.sfx_bgm_dir / f"scene_{scene.index:03d}_music.wav"
            sfx_wav = job_paths.sfx_bgm_dir / f"scene_{scene.index:03d}_sfx.wav"
            if req.enable_music:
                try:
                    render_music_sfx_for_scene(
                        scene=scene,
                        duration_s=scene_dur,
                        out_music_wav=music_wav,
                        out_sfx_wav=sfx_wav,
                    )
                except Exception:
                    # If procedural music fails, use silence
                    from pydub import AudioSegment

                    silence = AudioSegment.silent(duration=int(scene_dur * 1000))
                    silence.export(str(music_wav), format="wav")
                    silence.export(str(sfx_wav), format="wav")

                # Mix for final scene audio (dialogue + music + sfx)
                from app.services.video_assembler import mix_audio_tracks

                scene_audio_out = job_paths.audio_dir / f"scene_{scene.index:03d}_audio_mix.wav"
                mix_audio_tracks(tracks=[dialogue_wav, music_wav, sfx_wav], out_wav=scene_audio_out)
                scene_audio_paths.append(scene_audio_out)
            else:
                # No music/SFX requested; use dialogue only.
                scene_audio_paths.append(dialogue_wav)

            # Build absolute subtitle timings using cumulative offset
            if not timeline_segments:
                cur_offset = 0.0
            else:
                cur_offset = max(seg.end_s for seg in timeline_segments)
            # Note: scene_subs start at 0; shift by cur_offset
            for seg in scene_subs:
                timeline_segments.append(
                    SubtitleSegment(
                        start_s=seg.start_s + cur_offset,
                        end_s=seg.end_s + cur_offset,
                        speaker=seg.speaker,
                        text=seg.text,
                    )
                )

            # Create motion video from scene image, duration matching dialogue
            scene_image_path = job_paths.images_dir / f"scene_{scene.index:03d}.png"
            scene_video_base = job_paths.video_dir / f"scene_{scene.index:03d}_base.mp4"
            progress_cb(0.55, f"Ken Burns motion: scene {scene.index+1}/{len(story.scenes)}")
            make_kenburns_video(
                image_path=scene_image_path,
                out_mp4=scene_video_base,
                duration_s=scene_dur,
                fps=18 if settings.low_end_mode or req.low_end else 24,
                low_end=settings.low_end_mode or req.low_end,
            )

            # Lip sync (optional)
            scene_video_final = job_paths.video_dir / f"scene_{scene.index:03d}_final.mp4"
            if req.enable_lip_sync:
                progress_cb(0.68, f"Lip sync: scene {scene.index+1}/{len(story.scenes)}")
                scene_video_final = try_run_wav2lip(
                    settings=settings,
                    scene_base_video=scene_video_base,
                    scene_audio_wav=dialogue_wav,
                    out_mp4=scene_video_final,
                )
            else:
                scene_video_final = scene_video_base

            scene_videos_for_assembler.append(scene_video_final)

        # Write subtitles SRT
        progress_cb(0.82, "Subtitles (SRT)...")
        write_srt(timeline_segments, job_paths.subtitles_srt)

        # Assemble final video + burn subtitles
        progress_cb(0.9, "Rendering final MP4...")
        out_final = assemble_final_video(
            scene_video_paths=scene_videos_for_assembler,
            scene_audio_paths=scene_audio_paths,
            out_video_mp4=job_paths.final_mp4,
            subtitles_srt=job_paths.subtitles_srt,
            crossfade_s=0.3,
        )

        # Optional YouTube upload
        if req.enable_upload_youtube or settings.youtube_upload:
            progress_cb(0.97, "Uploading to YouTube (optional)...")
            maybe_upload_to_youtube(
                settings=settings,
                mp4_path=out_final,
                title=story.title,
                description=f"AI-generated anime video: {story.logline}",
                category_id=settings.youtube_category_id,
            )

        progress_cb(1.0, "Done.")
        return {
            "final_mp4": str(out_final),
            "subtitles_srt": str(job_paths.subtitles_srt),
            "job_dir": str(job_paths.job_dir),
        }

    except Exception as e:
        # Provide a readable error for the UI.
        msg = f"{e}\n\n{traceback.format_exc()}"
        raise RuntimeError(msg)

