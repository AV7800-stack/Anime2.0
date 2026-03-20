from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.utils.config import Settings


@dataclass(frozen=True)
class JobPaths:
    job_dir: Path
    story_json: Path
    scenes_json: Path
    images_dir: Path
    audio_dir: Path
    video_dir: Path
    sfx_bgm_dir: Path
    subtitles_dir: Path
    final_mp4: Path
    subtitles_srt: Path


def make_job_paths(settings: Settings, job_id: str) -> JobPaths:
    job_dir = settings.output_dir / job_id
    images_dir = job_dir / "images"
    audio_dir = job_dir / "audio"
    video_dir = job_dir / "video"
    sfx_bgm_dir = job_dir / "music_sfx"
    subtitles_dir = job_dir / "subtitles"

    job_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)
    audio_dir.mkdir(parents=True, exist_ok=True)
    video_dir.mkdir(parents=True, exist_ok=True)
    sfx_bgm_dir.mkdir(parents=True, exist_ok=True)
    subtitles_dir.mkdir(parents=True, exist_ok=True)

    return JobPaths(
        job_dir=job_dir,
        story_json=job_dir / "story.json",
        scenes_json=job_dir / "scenes.json",
        images_dir=images_dir,
        audio_dir=audio_dir,
        video_dir=video_dir,
        sfx_bgm_dir=sfx_bgm_dir,
        subtitles_dir=subtitles_dir,
        final_mp4=job_dir / "final.mp4",
        subtitles_srt=subtitles_dir / "subtitles.srt",
    )

