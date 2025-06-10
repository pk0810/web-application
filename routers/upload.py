from fastapi import APIRouter, Request, Depends, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from sqlalchemy.orm import Session
from typing import Union
import os
from fastapi.responses import RedirectResponse

from database import get_db, User, Upload
from auth import get_current_user
from utils import allowed_file, is_safe_path
from templates import templates  # Import templates from main

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter()


@router.get("/upload", response_class=HTMLResponse)
def upload_page(request: Request, user: Union[User, RedirectResponse] = Depends(get_current_user), db: Session = Depends(get_db)):
    if isinstance(user, RedirectResponse):
        return user
    uploads = db.query(Upload).filter_by(user_id=user.id).all()
    return templates.TemplateResponse("upload.html", {"request": request, "nav_user": user, "uploads": uploads})


@router.post("/upload", response_class=HTMLResponse)
def handle_upload(
        request: Request,
        file: UploadFile = File(...),
        user: Union[User, RedirectResponse] = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    if isinstance(user, RedirectResponse):
        return user
    if not allowed_file(file.filename):
        return templates.TemplateResponse("upload.html", {"request": request, "nav_user": user, "error": "File type not allowed"})

    filename = os.path.basename(file.filename)
    file_location = os.path.join(UPLOAD_DIR, filename)
    if not is_safe_path(UPLOAD_DIR, file_location):
        return templates.TemplateResponse("upload.html", {"request": request, "nav_user": user, "error": "Invalid file path"})

    with open(file_location, "wb") as f:
        f.write(file.file.read())

    upload_record = Upload(filename=filename, path=file_location, user_id=user.id)
    db.add(upload_record)
    db.commit()

    uploads = db.query(Upload).filter_by(user_id=user.id).all()
    return templates.TemplateResponse("upload.html", {"request": request, "nav_user": user, "message": f"Uploaded to {filename}", "uploads": uploads})


@router.get("/delete", response_class=HTMLResponse)
def show_delete_files(request: Request, user: Union[User, RedirectResponse] = Depends(get_current_user), db: Session = Depends(get_db)):
    if isinstance(user, RedirectResponse):
        return user
    uploads = db.query(Upload).filter_by(user_id=user.id).all()
    return templates.TemplateResponse("delete.html", {"request": request, "nav_user": user, "uploads": uploads})


@router.get("/download/{file_id}")
def download_file(
    file_id: int,
    user: Union[User, RedirectResponse] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if isinstance(user, RedirectResponse):
        return user
    upload = db.query(Upload).filter_by(id=file_id, user_id=user.id).first()
    if not upload:
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=upload.path, filename=upload.filename, media_type='application/octet-stream')


@router.post("/delete/{file_id}", response_class=HTMLResponse)
def delete_file(
    request: Request,
    file_id: int,
    user: Union[User, RedirectResponse] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if isinstance(user, RedirectResponse):
        return user
    upload = db.query(Upload).filter_by(id=file_id, user_id=user.id).first()
    if not upload:
        raise HTTPException(status_code=404, detail="File not found")
    if os.path.exists(upload.path):
        os.remove(upload.path)
    db.delete(upload)
    db.commit()
    uploads = db.query(Upload).filter_by(user_id=user.id).all()
    return templates.TemplateResponse("upload.html", {"request": request, "nav_user": user, "message": f"Deleted {upload.filename}", "uploads": uploads})


@router.get("/read", response_class=HTMLResponse)
def read_file(
    request: Request,
    filename: str,
    user: Union[User, RedirectResponse] = Depends(get_current_user)
):
    if isinstance(user, RedirectResponse):
        return user
    safe_path = os.path.join(UPLOAD_DIR, os.path.basename(filename))
    if not is_safe_path(UPLOAD_DIR, safe_path):
        return templates.TemplateResponse("read.html", {"request": request, "nav_user": user, "error": "Access denied"})

    try:
        with open(safe_path, "r") as f:
            content = f.read()
        return templates.TemplateResponse("read.html", {"request": request, "nav_user": user, "content": content})
    except Exception as e:
        return templates.TemplateResponse("read.html", {"request": request, "nav_user": user, "error": str(e)})
