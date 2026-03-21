from fastapi import APIRouter
from app.api.endpoints import auth, generate, history

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(generate.router, prefix="/generate", tags=["Generate"])
api_router.include_router(history.router, prefix="/history", tags=["History"])