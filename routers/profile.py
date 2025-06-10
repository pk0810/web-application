from fastapi import APIRouter, Request, Depends, Body
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from typing import Union

from database import get_db, User
from auth import get_current_user
from models import ProfileUpdateRequest
from templates import templates  # Import templates from main

router = APIRouter()


@router.get("/profile", response_class=HTMLResponse)
def get_profile(request: Request, db: Session = Depends(get_db), user: Union[User, RedirectResponse] = Depends(get_current_user)):
    if isinstance(user, RedirectResponse):
        return user
    return templates.TemplateResponse("profile.html", {"request": request, "user": user, "nav_user": user})


@router.post("/profile", response_class=HTMLResponse)
def update_profile(
    request: Request,
    body: ProfileUpdateRequest = Body(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    email = body.email
    mobile = body.mobile
    if not mobile.isdigit() or len(mobile) != 10:
        return templates.TemplateResponse("profile.html", {"request": request, "user": user, "nav_user": user, "error": "Mobile number must be 10 digits"})
    user.email = email
    user.mobile = mobile
    db.commit()
    return templates.TemplateResponse("profile.html", {"request": request, "user": user, "nav_user": user, "message": "Profile updated successfully"})
