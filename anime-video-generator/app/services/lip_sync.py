from __future__ import annotations

import shutil
import subprocess
import time
from pathlib import Path

from app.utils.config import Settings


def try_run_wav2lip(
    *,
    settings: Settings,
    scene_base_video: Path,
    scene_audio_wav: Path,
    out_mp4: Path,
    device: str | None = None,
) -> Path:
    """
    Best-effort lip sync using Wav2Lip.

    If Wav2Lip is not configured/available, this returns the base video unchanged.
    """
    if not settings.wav2lip_repo_path or not settings.wav2lip_checkpoint:
        return scene_base_video

    repo = Path(settings.wav2lip_repo_path)
    if not repo.exists():
        return scene_base_video

    inference = repo / "inference.py"
    if not inference.exists():
        return scene_base_video

    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    temp_out_dir = out_mp4.parent / f"_wav2lip_{int(time.time())}"
    temp_out_dir.mkdir(parents=True, exist_ok=True)

    # Wav2Lip uses CUDA automatically if available; passing device is optional.
    cmd = [
        "python",
        str(inference),
        "--checkpoint_path",
        str(settings.wav2lip_checkpoint),
        "--face",
        str(scene_base_video),
        "--audio",
        str(scene_audio_wav),
        "--outfile_dir",
        str(temp_out_dir),
    ]
    # Common quality knobs (safe defaults)
    cmd += ["--pads", "0", "20", "0", "0", "--resize_factor", "1"]

    if device:
        # Some wav2lip forks honor --device; if not, it's ignored.
        cmd += ["--device", device]

    try:
        proc = subprocess.run(cmd, cwd=str(repo), capture_output=True, text=True)
        if proc.returncode != 0:
            # Leave base video unchanged on failure.
            return scene_base_video
    except Exception:
        return scene_base_video

    # Pick newest media in outfile_dir
    candidates = []
    for ext in ("*.mp4", "*.avi", "*.mkv"):
        candidates += list(temp_out_dir.glob(ext))

    if not candidates:
        return scene_base_video

    newest = max(candidates, key=lambda p: p.stat().st_mtime)
    # Normalize to out_mp4
    if newest.resolve() == out_mp4.resolve():
        return out_mp4

    shutil.copyfile(str(newest), str(out_mp4))
    return out_mp4

