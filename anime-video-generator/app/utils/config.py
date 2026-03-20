from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _env_bool(name: str, default: bool = False) -> bool:
    v = os.environ.get(name)
    if v is None:
        return default
    return v.strip().lower() in {"1", "true", "yes", "y", "on"}


@dataclass(frozen=True)
class Settings:
    # LLM
    openai_api_key: str | None
    openai_model: str
    ollama_host: str | None
    ollama_model: str

    # Stable Diffusion
    sd_model: str
    sd_lora_path: str | None
    sd_lora_weight: float
    character_ref_image: str | None

    # TTS
    tts_provider: str
    elevenlabs_api_key: str | None
    elevenlabs_voice_id: str
    coqui_model_name: str
    coqui_speaker_wav: str | None

    # External APIs
    gemini_api_key: str | None
    stability_api_key: str | None
    pika_api_key: str | None
    synclabs_api_key: str | None
    
    # Cloudinary
    cloudinary_cloud_name: str | None
    cloudinary_api_key: str | None
    cloudinary_api_secret: str | None

    # Wav2Lip (optional)
    wav2lip_repo_path: str | None
    wav2lip_checkpoint: str | None

    # Output dirs
    project_root: Path
    data_dir: Path
    output_dir: Path

    # Runtime / performance
    low_end_mode: bool

    # Optional YouTube upload
    youtube_upload: bool
    google_client_secrets_json: str | None
    youtube_category_id: str

    # Device hint
    force_device: str | None


def load_settings() -> Settings:
    # Note: we load from anime-video-generator/ directory.
    project_root = Path(__file__).resolve().parents[2]

    return Settings(
        openai_api_key=os.environ.get("OPENAI_API_KEY"),
        openai_model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
        ollama_host=os.environ.get("OLLAMA_HOST"),
        ollama_model=os.environ.get("OLLAMA_MODEL", "llama3"),
        gemini_api_key=os.environ.get("GEMINI_API_KEY"),
        stability_api_key=os.environ.get("STABILITY_API_KEY"),
        pika_api_key=os.environ.get("PIKA_API_KEY"),
        synclabs_api_key=os.environ.get("SYNCLABS_API_KEY"),
        cloudinary_cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
        cloudinary_api_key=os.environ.get("CLOUDINARY_API_KEY"),
        cloudinary_api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
        sd_model=os.environ.get("SD_MODEL", "runwayml/stable-diffusion-v1-5"),
        sd_lora_path=os.environ.get("SD_LORA_PATH"),
        sd_lora_weight=float(os.environ.get("SD_LORA_WEIGHT", "0.8")),
        character_ref_image=os.environ.get("CHARACTER_REF_IMAGE"),
        tts_provider=os.environ.get("TTS_PROVIDER", "elevenlabs"),
        elevenlabs_api_key=os.environ.get("ELEVENLABS_API_KEY"),
        elevenlabs_voice_id=os.environ.get("ELEVENLABS_VOICE_ID", "EXAVITQu4vr4xnSDxMaL"),
        coqui_model_name=os.environ.get("COQUI_MODEL_NAME", "tts_models/en/ljspeech/tacotron2-DDC"),
        coqui_speaker_wav=os.environ.get("COQUI_SPEAKER_WAV"),
        wav2lip_repo_path=os.environ.get("WAV2LIP_REPO_PATH"),
        wav2lip_checkpoint=os.environ.get("WAV2LIP_CHECKPOINT"),
        data_dir=project_root / os.environ.get("DATA_DIR", "data"),
        output_dir=project_root / os.environ.get("OUTPUT_DIR", "output"),
        low_end_mode=_env_bool("LOW_END_MODE", False),
        youtube_upload=_env_bool("YOUTUBE_UPLOAD", False),
        google_client_secrets_json=os.environ.get("GOOGLE_CLIENT_SECRETS_JSON"),
        youtube_category_id=os.environ.get("YOUTUBE_CATEGORY_ID", "22"),
        project_root=project_root,
        force_device=os.environ.get("FORCE_DEVICE"),
    )


def ensure_dirs(settings: Settings) -> None:
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.output_dir.mkdir(parents=True, exist_ok=True)

