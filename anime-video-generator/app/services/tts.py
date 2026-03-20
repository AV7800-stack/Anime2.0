from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

from app.utils.config import Settings


def _audio_duration_s(wav_path: Path) -> float:
    from pydub import AudioSegment

    seg = AudioSegment.from_file(str(wav_path))
    return float(seg.duration_seconds)


class TTSService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._coqui = None

    def _require_key(self) -> str:
        if not self.settings.elevenlabs_api_key:
            raise RuntimeError("ELEVENLABS_API_KEY missing in environment")
        return self.settings.elevenlabs_api_key

    def _elevenlabs_voice_settings(self) -> dict:
        # Provider-specific voice parameters; keep simple defaults.
        return {
            "stability": 0.35,
            "similarity_boost": 0.75,
            "style": 0.2,
            "use_speaker_boost": True,
        }

    def synthesize_to_wav(
        self,
        *,
        text: str,
        language: str,
        voice_style: str,
        out_wav: Path,
    ) -> float:
        """
        Returns duration in seconds.
        """
        out_wav.parent.mkdir(parents=True, exist_ok=True)

        if self.settings.tts_provider.lower() == "elevenlabs":
            return self._synthesize_elevenlabs(text=text, out_wav=out_wav)
        return self._synthesize_coqui(text=text, out_wav=out_wav)

    def _synthesize_elevenlabs(self, *, text: str, out_wav: Path) -> float:
        import requests
        from pydub import AudioSegment

        api_key = self._require_key()
        voice_id = self.settings.elevenlabs_voice_id
        model_id = os.environ.get("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2")

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {"xi-api-key": api_key, "Content-Type": "application/json"}
        payload = {
            "text": text,
            "model_id": model_id,
            "voice_settings": self._elevenlabs_voice_settings(),
        }

        r = requests.post(url, headers=headers, json=payload, timeout=180)
        r.raise_for_status()

        tmp_mp3 = out_wav.with_suffix(".mp3")
        tmp_mp3.write_bytes(r.content)

        audio = AudioSegment.from_file(str(tmp_mp3))
        audio.export(str(out_wav), format="wav")
        try:
            tmp_mp3.unlink(missing_ok=True)
        except Exception:
            pass
        return _audio_duration_s(out_wav)

    def _synthesize_coqui(self, *, text: str, out_wav: Path) -> float:
        from TTS.api import TTS

        model_name = self.settings.coqui_model_name
        if self._coqui is None:
            # Coqui TTS loads a heavy model; cache in memory.
            self._coqui = TTS(model_name=model_name)

        speaker_wav = self.settings.coqui_speaker_wav
        # Some models accept speaker_wav, others ignore it; try both.
        kwargs = {}
        if speaker_wav:
            kwargs["speaker_wav"] = speaker_wav

        self._coqui.tts_to_file(text=text, file_path=str(out_wav), **kwargs)
        return _audio_duration_s(out_wav)

