from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import Union

from database import get_db, User
from auth import get_current_user
from models import SearchRequest
from templates import templates  # Import templates from main

router = APIRouter()


@router.get("/search", response_class=HTMLResponse)
async def search_page(request: Request, nav_user: Union[User, None] = Depends(get_current_user)):
    """Renders the search form."""
    return templates.TemplateResponse("search.html", {"request": request, "nav_user": nav_user})
@router.post("/api/search", response_class=JSONResponse)
async def search_users(search_data: SearchRequest, db: Session = Depends(get_db), nav_user: Union[User, None] = Depends(get_current_user)):
    """Searches for users in the database"""
    # Validate and sanitize the username (important!)
    search_term = search_data.username.strip()  # Remove leading/trailing spaces
    if not search_term:
        return []  # Or handle empty search term appropriately
    # Use SQLAlchemy to perform the database query
    users = db.query(User).filter(User.username.ilike(f"%{search_term}%")).all()
    return users
