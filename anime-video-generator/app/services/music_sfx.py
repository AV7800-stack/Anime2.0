from __future__ import annotations

import re
from pathlib import Path

import numpy as np
from pydub import AudioSegment

from app.services.story_schema import SceneSpec


EMOTION_TO_TEMPO = {
    "excited": 120,
    "tense": 100,
    "determined": 105,
    "heartbroken": 70,
    "romantic": 85,
    "in love": 85,
    "mysterious": 90,
    "angry": 125,
    "sad": 65,
    "fear": 95,
    "neutral": 95,
}

KEY_TO_FREQ = {
    "A": 220.0,
    "C": 261.63,
    "D": 293.66,
    "E": 329.63,
    "F": 349.23,
    "G": 392.0,
}


def _safe_emotion(e: str) -> str:
    if not e:
        return "neutral"
    e2 = e.strip().lower()
    return e2 if e2 in EMOTION_TO_TEMPO else "neutral"


def _tone(freq: float, duration_s: float, sr: int, phase: float = 0.0, decay: float = 1.0) -> np.ndarray:
    t = np.linspace(0, duration_s, int(sr * duration_s), endpoint=False)
    # Simple exponential decay; helps avoid clicks.
    env = np.exp(-t / max(0.0001, duration_s) * (2.0 / decay))
    return (np.sin(2 * np.pi * freq * t + phase) * env).astype(np.float32)


def _generate_music_clip(*, emotion: str, duration_s: float, sr: int = 44100) -> AudioSegment:
    emotion_key = _safe_emotion(emotion)
    tempo = EMOTION_TO_TEMPO.get(emotion_key, 95)

    # Pick a pseudo key based on emotion.
    base_note = "A" if emotion_key in {"excited", "determined", "angry"} else "F" if emotion_key in {"heartbroken", "sad"} else "C"
    base = KEY_TO_FREQ[base_note]

    # Bar-based chord pattern (very lightweight).
    beat_s = 60.0 / tempo
    total_s = duration_s
    clip = np.zeros(int(sr * total_s), dtype=np.float32)

    pattern = [(0, 4), (2, 5), (4, 7), (5, 9)]  # major-ish intervals
    idx = 0
    time_cursor = 0.0
    while time_cursor < total_s:
        chord = pattern[idx % len(pattern)]
        chord_duration = min(beat_s * 2, total_s - time_cursor)
        chord_audio = np.zeros(int(sr * chord_duration), dtype=np.float32)
        for interval in chord:
            f = base * (2 ** (interval / 12))
            chord_audio += _tone(f, chord_duration, sr, decay=1.2)
        # Add light noise texture
        noise = np.random.normal(0, 0.005, size=chord_audio.shape).astype(np.float32)
        chord_audio = 0.75 * chord_audio + 0.25 * noise
        start = int(time_cursor * sr)
        end = start + chord_audio.shape[0]
        clip[start:end] += chord_audio
        time_cursor += chord_duration
        idx += 1

    # Normalize
    clip = np.clip(clip, -1.0, 1.0)
    pcm16 = (clip * 32767.0).astype(np.int16)
    return AudioSegment(
        pcm16.tobytes(),
        frame_rate=sr,
        sample_width=2,
        channels=1,
    )


def _generate_sfx_clip(*, keyword: str, duration_s: float, sr: int = 44100) -> AudioSegment:
    # Very lightweight procedural SFX.
    keyword = keyword.lower()
    if keyword in {"explosion", "boom"}:
        # Fast decaying noise burst
        n = np.random.normal(0, 0.08, size=int(sr * duration_s)).astype(np.float32)
        t = np.linspace(0, duration_s, int(sr * duration_s), endpoint=False)
        env = np.exp(-t * 14.0)
        pcm = n * env
    elif keyword in {"whoosh", "wind"}:
        t = np.linspace(0, duration_s, int(sr * duration_s), endpoint=False)
        env = np.exp(-t * 10.0)
        freq = np.linspace(900, 200, int(sr * duration_s))
        phase = np.cumsum(2 * np.pi * freq / sr)
        pcm = np.sin(phase) * env * 0.35
    elif keyword in {"heartbeat"}:
        # Subtle thump
        pcm = np.zeros(int(sr * duration_s), dtype=np.float32)
        beat = int(sr * 0.6)
        for i in range(0, int(duration_s * sr), beat):
            seg = _tone(55.0, 0.12, sr, decay=0.4)
            j0 = i
            j1 = min(i + seg.shape[0], pcm.shape[0])
            pcm[j0:j1] += seg[: j1 - j0]
    else:
        # Default: tiny click
        pcm = _tone(440.0, duration_s, sr, decay=0.6) * 0.2

    pcm = np.clip(pcm, -1.0, 1.0)
    pcm16 = (pcm * 32767.0).astype(np.int16)
    return AudioSegment(pcm16.tobytes(), frame_rate=sr, sample_width=2, channels=1)


def detect_sfx_keywords(scene: SceneSpec) -> list[str]:
    text = (scene.background + " " + scene.title + " " + scene.emotion + " ".join([d.text for d in scene.dialogue])).lower()
    candidates = [
        ("explosion", ["explosion", "boom", "blast", "detonate"]),
        ("whoosh", ["whoosh", "wind", "dash", "run"]),
        ("sword", ["sword", "blade", "cut", "slash"]),
        ("magic", ["magic", "spell", "runes", "fireball", "beam"]),
        ("heartbeat", ["heartbeat", "pulse", "thump"]),
    ]

    hits = []
    for name, keys in candidates:
        for k in keys:
            if k in text:
                hits.append(name)
                break
    # Normalize by removing duplicates while keeping order
    out = []
    for h in hits:
        if h not in out:
            out.append(h)
    return out


def render_music_sfx_for_scene(
    *,
    scene: SceneSpec,
    duration_s: float,
    out_music_wav: Path,
    out_sfx_wav: Path,
) -> tuple[Path, Path]:
    out_music_wav.parent.mkdir(parents=True, exist_ok=True)
    out_sfx_wav.parent.mkdir(parents=True, exist_ok=True)

    music = _generate_music_clip(emotion=scene.emotion, duration_s=duration_s)
    music = music - 14  # keep under voice
    music.export(str(out_music_wav), format="wav")

    sfx_keywords = detect_sfx_keywords(scene)
    if not sfx_keywords:
        silence = AudioSegment.silent(duration=int(duration_s * 1000))
        silence.export(str(out_sfx_wav), format="wav")
        return out_music_wav, out_sfx_wav

    sfx = AudioSegment.silent(duration=int(duration_s * 1000))
    # Place up to 2 SFX events randomly in the clip timeline.
    # (Deterministic ordering for reproducibility is not critical here.)
    for i, kw in enumerate(sfx_keywords[:2]):
        # Use small durations for punchy effects.
        clip = _generate_sfx_clip(keyword=kw, duration_s=min(0.35, duration_s / 4))
        pos_ms = int((duration_s * 1000) * (0.15 + 0.35 * i))
        sfx = sfx.overlay(clip, position=pos_ms)

    sfx = sfx - 10
    sfx.export(str(out_sfx_wav), format="wav")

    return out_music_wav, out_sfx_wav

