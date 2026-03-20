# Anime Video Generator (AI End-to-End)

This project automatically generates an anime-style video from a user story idea:

`idea -> structured story -> scenes -> images (Stable Diffusion) -> motion video (Ken Burns) -> TTS -> optional lip-sync -> background music + sound effects -> final MP4 + subtitles`

## Quick Start (Windows)

1. Install Python 3.10+.
2. Open a terminal in `anime-video-generator/`.
3. Copy env file:
   - Copy `.env.example` to `.env`
   - Fill keys you want to use (OpenAI or Ollama, ElevenLabs, etc.)
4. Install dependencies:
   - `pip install -r requirements.txt`
5. Install system dependencies:
   - `ffmpeg` must be available on PATH (required by MoviePy and subtitle rendering)
6. Run the web app:
   - `python run.py`
7. Open:
   - `http://localhost:8000`

## Notes on “Complete” AI Steps

Some steps (like lip-sync with Wav2Lip and character consistency with IP-Adapter/LoRA) require external model weights and/or third-party repos.

This code includes:
- Integration hooks for Wav2Lip, LoRA, IP-Adapter (if you provide paths / install those extras)
- A fully working fallback path so the system still generates a video even without those optional components.

## Outputs

All generation artifacts are written under:
- `output/<job_id>/...`

The final MP4 is:
- `output/<job_id>/final.mp4`

Subtitles:
- `output/<job_id>/subtitles.srt`

