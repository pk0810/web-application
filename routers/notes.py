from fastapi import APIRouter, Request, Depends, Body
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from typing import Union

from database import get_db, User, Note
from auth import get_current_user
from models import NoteRequest
from templates import templates  # Import templates from main

router = APIRouter()


@router.get("/notes", response_class=HTMLResponse)
def get_notes(request: Request, db: Session = Depends(get_db), user: Union[User, RedirectResponse] = Depends(get_current_user)):
    if isinstance(user, RedirectResponse):
        return user
    notes = db.query(Note).filter(Note.user_id == user.id).all()
    return templates.TemplateResponse("notes.html", {"request": request, "notes": notes, "nav_user": user})


@router.post("/notes", response_class=HTMLResponse)
def post_notes(
    request: Request,
    body: NoteRequest = Body(...),
    db: Session = Depends(get_db),
    user: Union[User, RedirectResponse] = Depends(get_current_user)
):
    note = body.note
    new_note = Note(content=note, user_id=user.id)
    db.add(new_note)
    db.commit()
    notes = db.query(Note).filter(Note.user_id == user.id).all()
    return templates.TemplateResponse("notes.html", {"request": request, "notes": notes, "nav_user": user})
