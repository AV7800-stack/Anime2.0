from __future__ import annotations

import os
import subprocess
from pathlib import Path

from app.utils.config import Settings


def maybe_upload_to_youtube(
    *,
    settings: Settings,
    mp4_path: Path,
    title: str,
    description: str,
    category_id: str,
) -> dict | None:
    """
    Best-effort YouTube upload via OAuth.

    Requires:
    - GOOGLE_CLIENT_SECRETS_JSON configured
    - User must complete OAuth consent flow once
    """
    if not mp4_path or not Path(mp4_path).exists():
        return None
    if not settings.youtube_upload and not os.environ.get("YOUTUBE_UPLOAD"):
        return None
    if not settings.google_client_secrets_json:
        # Not configured; skip.
        return None

    try:
        import google.auth.transport.requests
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload

        scopes = ["https://www.googleapis.com/auth/youtube.upload"]
        client_secrets = settings.google_client_secrets_json

        # token.json stored in project root for reuse.
        token_path = settings.project_root / "token.json"

        creds = None
        if token_path.exists():
            import json
            from google.oauth2.credentials import Credentials

            creds = Credentials.from_authorized_user_file(str(token_path), scopes=scopes)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(google.auth.transport.requests.Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(client_secrets, scopes)
                creds = flow.run_local_server(port=0)
            token_path.write_text(creds.to_json(), encoding="utf-8")

        youtube = build("youtube", "v3", credentials=creds)
        body = {
            "snippet": {
                "title": title[:95],
                "description": description[:5000],
                "categoryId": category_id,
            },
            "status": {"privacyStatus": "unlisted"},
        }

        media = MediaFileUpload(str(mp4_path), chunksize=-1, resumable=True)
        request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        response = None
        while response is None:
            status, response = request.next_chunk()
        video_id = response.get("id")
        return {"uploaded": True, "video_id": video_id}
    except Exception:
        # Do not kill the whole pipeline if upload fails.
        return {"uploaded": False}

