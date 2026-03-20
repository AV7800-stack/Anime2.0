from fastapi import FastAPI, Request, Form, Depends, BackgroundTasks
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
import os
from .database import engine, Base, SessionLocal
from .models import User
from .auth import get_password_hash, verify_password, create_access_token, get_current_user
from sqlalchemy.orm import Session
from .pipeline.orchestrator import run_pipeline

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Anime Video Generator AI")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/output", StaticFiles(directory="output"), name="output")
templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, username: str = Form(None), password: str = Form(None), phone: str = Form(None), db: Session = Depends(get_db)):
    # Phone auth stub
    if phone:
        return templates.TemplateResponse("login.html", {"request": request, "message": f"OTP sent to {phone} (Stub)"})
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})
    response = RedirectResponse(url="/dashboard", status_code=302)
    access_token = create_access_token(data={"sub": user.username})
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response

@app.post("/signup")
async def signup(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == username).first():
         return templates.TemplateResponse("login.html", {"request": request, "error": "Username exists", "is_signup": True})
    new_user = User(username=username, hashed_password=get_password_hash(password))
    db.add(new_user)
    db.commit()
    return templates.TemplateResponse("login.html", {"request": request, "message": "Signup successful. Please login."})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, user: User = Depends(get_current_user)):
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})

@app.post("/api/generate")
async def generate_video(background_tasks: BackgroundTasks, user: User = Depends(get_current_user), prompt: str = Form(...), style: str = Form("cinematic"), low_end_mode: bool = Form(False)):
    job_id = f"job_{os.urandom(4).hex()}"
    background_tasks.add_task(run_pipeline, job_id, prompt, style, low_end_mode)
    return {"status": "success", "job_id": job_id, "message": "Generation started"}
