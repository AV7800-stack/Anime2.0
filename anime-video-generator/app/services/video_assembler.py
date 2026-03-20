from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Iterable

import numpy as np
from moviepy.editor import AudioFileClip, VideoFileClip, concatenate_videoclips
from pydub import AudioSegment


def mix_audio_tracks(*, tracks: list[Path], out_wav: Path, target_frame_rate: int = 44100) -> Path:
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    base = None
    for p in tracks:
        if p is None or not p.exists():
            continue
        seg = AudioSegment.from_file(str(p))
        if base is None:
            base = seg
        else:
            base = base.overlay(seg)
    if base is None:
        # Silence
        base = AudioSegment.silent(duration=1000, frame_rate=target_frame_rate)
    base.export(str(out_wav), format="wav")
    return out_wav


def render_subtitles_ffmpeg(*, input_mp4: Path, srt_path: Path, out_mp4: Path) -> Path:
    out_mp4.parent.mkdir(parents=True, exist_ok=True)

    # Quotes/escaping: use Windows-friendly path quoting.
    font_size = int(os.environ.get("SUBTITLE_FONT_SIZE", "26"))
    style = f"Fontsize={font_size},PrimaryColour=&HFFFFFF,OutlineColour=&H000000,Outline=2,Shadow=0"
    srt_ffmpeg_path = str(srt_path).replace("\\", "/")
    vf = f"subtitles={srt_ffmpeg_path}:force_style='{style}'"

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(input_mp4),
        "-vf",
        vf,
        "-c:a",
        "copy",
        str(out_mp4),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        # If subtitle burn fails, return the input video.
        return input_mp4
    return out_mp4


def assemble_final_video(
    *,
    scene_video_paths: list[Path],
    scene_audio_paths: list[Path],
    out_video_mp4: Path,
    subtitles_srt: Path | None = None,
    crossfade_s: float = 0.3,
) -> Path:
    if len(scene_video_paths) != len(scene_audio_paths):
        raise ValueError("scene_video_paths and scene_audio_paths lengths must match")
    out_video_mp4.parent.mkdir(parents=True, exist_ok=True)

    clips = []
    for vp, ap in zip(scene_video_paths, scene_audio_paths):
        v = VideoFileClip(str(vp))
        audio = AudioFileClip(str(ap))
        if crossfade_s > 0 and audio is not None:
            # Fade audio at boundaries (simple transitions).
            try:
                audio = audio.audio_fadein(crossfade_s).audio_fadeout(crossfade_s)
            except Exception:
                pass
        v = v.set_audio(audio)
        # fade effects for simple transitions
        clips.append(v)

    final = concatenate_videoclips(clips, method="compose")
    tmp_path = out_video_mp4.parent / "_tmp_no_subs.mp4"
    final.write_videofile(str(tmp_path), fps=24, audio_codec="aac", codec="libx264", threads=2, verbose=False, logger=None)

    if subtitles_srt and subtitles_srt.exists():
        rendered = out_video_mp4
        render_subtitles_ffmpeg(input_mp4=tmp_path, srt_path=subtitles_srt, out_mp4=out_video_mp4)
        try:
            tmp_path.unlink(missing_ok=True)
        except Exception:
            pass
        return rendered

    return tmp_path

