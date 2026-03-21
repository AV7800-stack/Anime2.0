from fastapi import APIRouter, Depends, HTTPException, status
from app.models.schemas import UserCreate, UserLogin, Token, UserResponse
from app.core.security import get_password_hash, verify_password, create_access_token, verify_token
from app.db.mongodb import get_db
from datetime import datetime
import uuid
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/signup", response_model=Token)
async def signup(user_data: UserCreate):
    db = get_db()
    
    # Check existing
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    uid = str(uuid.uuid4())
    hashed_password = get_password_hash(user_data.password)
    
    new_user = {
        "uid": uid,
        "email": user_data.email,
        "hashed_password": hashed_password,
        "display_name": user_data.display_name or user_data.email.split("@")[0],
        "photo_url": "",
        "created_at": datetime.utcnow()
    }
    
    await db.users.insert_one(new_user)
    
    access_token = create_access_token(data={"sub": uid})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    db = get_db()
    user = await db.users.find_one({"email": user_data.email})
    
    if not user or not verify_password(user_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token = create_access_token(data={"sub": user["uid"]})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: dict = Depends(verify_token)):
    return UserResponse(**current_user)