from fastapi import Request, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
import datetime

from database import get_db, User, SessionToken
# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = "supersecretjwtkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer(auto_error=False)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(
        request: Request,
        db: Session = Depends(get_db),
        credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = None

    if credentials:
        token = credentials.credentials
    elif "access_token" in request.cookies:
        token = request.cookies.get("access_token")

    if not token:
        if "text/html" in request.headers.get("accept", ""):
            return RedirectResponse(url="/login?reason=unauthenticated", status_code=302)
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
    except JWTError:
        if "text/html" in request.headers.get("accept", ""):
            return RedirectResponse(url="/login?reason=invalid_token", status_code=302)
        raise HTTPException(status_code=401, detail="Invalid token")

    session_exists = db.query(SessionToken).filter_by(user_id=user_id, token=token).first()
    if not session_exists:
        if "text/html" in request.headers.get("accept", ""):
            return RedirectResponse(url="/login?reason=session_expired", status_code=302)
        raise HTTPException(status_code=401, detail="Session expired")

    return db.query(User).get(user_id)
