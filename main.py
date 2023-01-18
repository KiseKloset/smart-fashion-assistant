import uvicorn

from pathlib import Path
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from config import settings
from api.retrieval import service
from api.retrieval.router import router as retrieval_router


FILE = Path(__file__).resolve()
ROOT = FILE.parent


app = FastAPI()
app.mount("/static", StaticFiles(directory=ROOT / "static"))


# Preload model, data, ...
@app.on_event('startup')
async def startup_event():
    app.state.static_files = { "directory": str(ROOT / "static"), "prefix": "/static" }
    app.state.retrieval_content = service.preload("cpu")


# Fashion retrieval
@app.get("/", response_class=HTMLResponse)
async def home():
    with open(ROOT / "templates/index.html") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)

app.include_router(retrieval_router, prefix="/retrieval")


# Virtual try-on entry
@app.get("/try-on", response_class=HTMLResponse)
async def try_on():
    with open(ROOT / "templates/tryon.html") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)


# Useless
@app.get("/health", status_code=status.HTTP_200_OK)
def perform_healthcheck():
    return JSONResponse(content={"message": "success"})


if __name__ == "__main__":
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)