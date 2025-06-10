from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import Union
from database import get_db, User
from auth import get_current_user
from models import SSRFRequest
from templates import templates  # Import templates from main
from utils import is_url_safe
from fastapi import HTTPException
import requests

router = APIRouter()


router = APIRouter()


@router.get("/ssrf", response_class=HTMLResponse)
async def ssrf_page(request: Request, nav_user: Union[User, None] = Depends(get_current_user)):
    """Renders the SSRF form."""
    return templates.TemplateResponse("ssrf.html", {"request": request, "nav_user": nav_user})


@router.post("/api/ssrf")
async def perform_ssrf(ssrf_request: SSRFRequest, nav_user: Union[User, None] = Depends(get_current_user)):
    """
    Performs an SSRF request to a whitelisted domain.
    """
    url = ssrf_request.url  # Extract URL from the request model
    if not is_url_safe(url):
        raise HTTPException(status_code=400, detail="URL is not whitelisted")
    try:
        response = requests.get(url, timeout=5)  # Add timeout
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        content = response.text
        return {"content": content}  # Return JSON response
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))  # Handle request errors