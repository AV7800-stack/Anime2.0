from __future__ import annotations

import threading
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, Depends, Header
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.models import (
    GenerateAnimeRequest,
    GenerateAnimeResponse,
    JobStatusResponse,
)
from app.pipeline.generator import generate_anime_job

import firebase_admin
from firebase_admin import credentials, auth

# Initialize Firebase Admin (Requires downloaded service account JSON)
# For local dev without auth, wrap in try-except
try:
    # Attempt to load from project root
    project_root = Path(__file__).resolve().parents[1]
    cred_path = project_root / "firebase-adminsdk.json"
    if cred_path.exists():
        cred = credentials.Certificate(str(cred_path))
        firebase_admin.initialize_app(cred)
        AUTH_ENABLED = True
        print("Firebase auth initialized successfully.")
    else:
        raise FileNotFoundError("firebase-adminsdk.json not found")
except Exception as e:
    print(f"Firebase auth not initialized. Running without auth in LOCAL mode. Error: {e}")
    AUTH_ENABLED = False

def create_app() -> FastAPI:
    app = FastAPI(title="Anime Video Generator", version="1.0")

    project_root = Path(__file__).resolve().parents[1]

    # Static frontend & Templates
    app.mount("/static", StaticFiles(directory=str(project_root / "static")), name="static")
    
    # Ensure templates directory exists
    templates_dir = project_root / "templates"
    templates_dir.mkdir(exist_ok=True)
    templates = Jinja2Templates(directory=str(templates_dir))

    jobs: dict[str, JobStatusResponse] = {}
    jobs_lock = threading.Lock()

    def _set_job(job_id: str, **kwargs) -> None:
        with jobs_lock:
            cur = jobs.get(job_id)
            if cur is None:
                jobs[job_id] = JobStatusResponse(job_id=job_id, state="queued")
                cur = jobs[job_id]
            data = cur.model_dump()
            data.update(kwargs)
            jobs[job_id] = JobStatusResponse(**data)

    async def verify_token(authorization: str = Header(None)):
        if not AUTH_ENABLED:
            return "local_dev_user"
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Unauthorized")
        token = authorization.split("Bearer ")[1]
        try:
            decoded_token = auth.verify_id_token(token)
            return decoded_token['uid']
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid Token")

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request) -> HTMLResponse:
        return templates.TemplateResponse("index.html", {"request": request})

    @app.get("/dashboard", response_class=HTMLResponse)
    async def dashboard_page(request: Request) -> HTMLResponse:
        return templates.TemplateResponse("dashboard.html", {"request": request})

    @app.post("/api/generate", response_model=GenerateAnimeResponse)
    async def generate(req: GenerateAnimeRequest, uid: str = Depends(verify_token)) -> GenerateAnimeResponse:
        job_id = uuid.uuid4().hex
        _set_job(job_id, state="queued", progress=0.0, message=f"Created {datetime.utcnow().isoformat()}Z")

        def worker() -> None:
            try:
                _set_job(job_id, state="running", progress=0.05, message="Generating story...")
                result = generate_anime_job(req, job_id=job_id, progress_cb=lambda p, m=None: _set_job(job_id, progress=p, message=m))
                _set_job(job_id, state="done", progress=1.0, message="Done", result=result)
            except Exception as e:
                _set_job(job_id, state="failed", progress=1.0, message=str(e))

        # Run the heavy pipeline outside the request context.
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        return GenerateAnimeResponse(
            job_id=job_id,
            status_url=f"/api/status/{job_id}",
            result_url=f"/api/result/{job_id}",
        )

    @app.get("/api/status/{job_id}", response_model=JobStatusResponse)
    async def status(job_id: str) -> JobStatusResponse:
        with jobs_lock:
            job = jobs.get(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="Unknown job_id")
        return job

    @app.get("/api/result/{job_id}")
    async def result(job_id: str) -> FileResponse:
        with jobs_lock:
            job = jobs.get(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="Unknown job_id")
        if job.state != "done" or not job.result:
            raise HTTPException(status_code=400, detail="Job not finished yet")

        mp4_path = job.result.get("final_mp4")
        if not mp4_path:
            raise HTTPException(status_code=500, detail="No final MP4 produced")

        return FileResponse(mp4_path, media_type="video/mp4", filename=f"anime_{job_id}.mp4")

    return app
