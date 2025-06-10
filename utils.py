import os
from urllib.parse import urlparse

ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg", "gif"}

# Only hostnames, not full URLs
ALLOWED_DOMAINS = [
    "github.com",
    "example.com",
]

def is_url_safe(url: str) -> bool:
    """
    Checks if a URL is safe based on a whitelist of allowed domains.
    """
    from urllib.parse import urlparse  # Import here to avoid circular dependency
    try:
        parsed_url = urlparse(url)
        return parsed_url.netloc in ALLOWED_DOMAINS
    except Exception:
        return False  # Handle parsing errors as unsafe

def is_safe_path(basedir, path, follow_symlinks=True):
    if follow_symlinks:
        return os.path.realpath(path).startswith(os.path.realpath(basedir))
    return os.path.abspath(path).startswith(os.path.abspath(basedir))

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def is_whitelisted(hostname: str) -> bool:
    return hostname in ALLOWED_DOMAINS
