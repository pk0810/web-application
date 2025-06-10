from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from routers import auth, notes, profile, search, ssrf, upload

app = FastAPI()

# Template setup
templates = Jinja2Templates(directory="templates")

app.include_router(auth.router)
app.include_router(notes.router)
app.include_router(profile.router)
app.include_router(search.router)
app.include_router(ssrf.router)
app.include_router(upload.router)


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
