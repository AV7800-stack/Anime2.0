from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SubtitleSegment:
    start_s: float
    end_s: float
    speaker: str
    text: str


def _ms(t: float) -> str:
    total_ms = int(round(t * 1000.0))
    hh = total_ms // 3600000
    mm = (total_ms % 3600000) // 60000
    ss = (total_ms % 60000) // 1000
    ms = total_ms % 1000
    return f"{hh:02d}:{mm:02d}:{ss:02d},{ms:03d}"


def _wrap(text: str, width: int = 42) -> list[str]:
    words = text.split()
    lines = []
    cur = []
    cur_len = 0
    for w in words:
        if cur_len + len(w) + (1 if cur else 0) > width:
            lines.append(" ".join(cur))
            cur = [w]
            cur_len = len(w)
        else:
            cur.append(w)
            cur_len += len(w) + (1 if cur_len else 0)
    if cur:
        lines.append(" ".join(cur))
    return lines if lines else [text]


def write_srt(segments: list[SubtitleSegment], out_path: Path) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)

    parts = []
    for i, seg in enumerate(segments, start=1):
        start = _ms(seg.start_s)
        end = _ms(seg.end_s)
        content_lines = _wrap(seg.text)
        speaker_prefix = f"{seg.speaker}: " if seg.speaker else ""
        # Add speaker prefix to the first subtitle line
        content_lines[0] = speaker_prefix + content_lines[0]
        parts.append(f"{i}\n{start} --> {end}\n" + "\n".join(content_lines) + "\n")

    out_path.write_text("\n".join(parts), encoding="utf-8")
    return out_path

