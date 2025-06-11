from fastapi import APIRouter, Request, Depends, Response, Body
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from typing import Union, List

from database import get_db, User, SessionToken
from auth import get_current_user, create_access_token, pwd_context
from models import SignupRequest, LoginRequest
from templates import templates  # Import templates from main
from pydantic import ValidationError
from fastapi.responses import JSONResponse



router = APIRouter()


@router.get("/signup", response_class=HTMLResponse)
def get_signup(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@router.post("/signup")
async def post_signup(body: SignupRequest, db: Session = Depends(get_db)):
    username = body.username
    password = body.password
    # Run custom validation
    validation_errors = validate_signup_data(username, password)
    if validation_errors:
        # Return errors in a JSON structure similar to Pydantic
        return JSONResponse(status_code=400, content={"detail": validation_errors})
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        return JSONResponse(status_code=400, content={"detail": ["Username already taken."]})
    # If validations pass, proceed with user creation
    hashed_password = pwd_context.hash(password)
    user = User(username=username, password=hashed_password)
    db.add(user)
    db.commit()
    return RedirectResponse(url="/login", status_code=302)



@router.get("/login", response_class=HTMLResponse)
def get_login(request: Request, reason: str = "", error: str = ""):
    reason_message = ""
    if reason == "session_expired":
        reason_message = "Your session has expired. Please log in again."
    elif reason == "unauthenticated":
        reason_message = "You must be logged in to access this page."
    elif reason == "invalid_token":
        reason_message = "Invalid session. Please log in again."
    return templates.TemplateResponse("login.html", {"request": request, "reason": reason_message, "error": error})


@router.post("/login", response_class=HTMLResponse)
def post_login(
    response: Response,
    body: LoginRequest = Body(...),
    db: Session = Depends(get_db)
):
    username = body.username
    password = body.password
    user = db.query(User).filter(User.username == username).first()
    if not user or not pwd_context.verify(password, user.password):
        return RedirectResponse(url="/login?error=invalid_credentials", status_code=302)
    token_data = {"sub": str(user.id)}
    token = create_access_token(data=token_data)
    db_token = SessionToken(user_id=user.id, token=token)
    db.add(db_token)
    db.commit()
    response = RedirectResponse(url="/search", status_code=302)
    response.set_cookie(key="access_token", value=token, httponly=True)
    return response


@router.get("/logout", response_class=HTMLResponse)
def logout(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if token:
        db.query(SessionToken).filter_by(token=token).delete()
        db.commit()
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("access_token")
    return response
