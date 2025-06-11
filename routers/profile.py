from fastapi import APIRouter, Request, Depends, Body, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse,JSONResponse
from sqlalchemy.orm import Session
from typing import Union
import os
import shutil

from database import get_db, User
from auth import get_current_user
from models import ProfileUpdateRequest
from templates import templates  # Import templates from main

from utils import allowed_file, is_safe_path

router = APIRouter()

UPLOAD_DIR = "static/uploads/profile_pics"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/profile")
async def get_profile(user: User = Depends(get_current_user)):
    return {
        "username": user.username,
        "email": user.email,
        "mobile": user.mobile,
        "profile_image_url": user.profile_image_url if hasattr(user, "profile_image_url") else None
    }

@router.post("/profile/edit")
async def edit_profile(
    body: ProfileUpdateRequest = Body(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user.email = body.email
    user.mobile = body.mobile
    db.commit()
    return JSONResponse({"message": "Profile updated successfully."})

@router.post("/profile/upload-image")
async def upload_image(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="File type not allowed.")
    
    filename = f"{user.id}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    if not is_safe_path(UPLOAD_DIR, file_path):
        raise HTTPException(status_code=400, detail="Invalid file path.")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    user.profile_image_url = f"/{file_path}"
    db.commit()
    
    return JSONResponse({"message": "Profile image uploaded successfully.", "profile_image_url": user.profile_image_url})
