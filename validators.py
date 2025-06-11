import re
from typing import List

def validate_signup_data(username: str, password: str) -> List[str]:
    errors = []

    if len(username) < 4:
        errors.append("Username must be at least 4 characters long")

    if len(password) < 8 or len(password) > 15:
        errors.append("Password must be between 8 and 15 characters long")

    if not re.search(r"[^a-zA-Z0-9\s]", password):
        errors.append("Password must contain at least one special character")

    return errors
