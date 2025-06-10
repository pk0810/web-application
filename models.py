from pydantic import BaseModel, EmailStr, constr, validator
import re



class SignupRequest(BaseModel):
    username: str
    password: str

    @validator("username")
    def validate_username(cls, username):
        if len(username) < 4:
            raise ValueError("Username must be at least 4 characters long")
        return username

    @validator("password")
    def validate_password(cls, password):
        if len(password) < 8 or len(password) > 15:
            raise ValueError("Password must be between 8 and 15 characters long")
        if not re.search(r"[^a-zA-Z0-9\s]", password):
            raise ValueError("Password must contain at least one special character")
        return password

class LoginRequest(BaseModel):
    username: str
    password: str

class ProfileUpdateRequest(BaseModel):
    email: EmailStr
    mobile: constr(min_length=10, max_length=10, pattern="^[0-9]+$")

class NoteRequest(BaseModel):
    note: str

class SearchRequest(BaseModel):
    username: str

class SSRFRequest(BaseModel):
    url: str
