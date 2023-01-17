import uvicorn
import httpx

from pathlib import Path
from fastapi import FastAPI, status, Request
from fastapi.responses import JSONResponse, HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from starlette.background import BackgroundTask

from config import settings

FILE = Path(__file__).resolve()
ROOT = FILE.parent


app = FastAPI()
app.mount("/static", StaticFiles(directory=ROOT / "static"))
app.include_router(tryon.router.router, prefix="/try-on")

# Preload model 
@app.on_event('startup')
async def startup_event():
    clip_model, combiner = service.load_models()
    dataset_metadata = service.load_dataset_metadata()
    dataset_index_names, dataset_index_features = service.load_preprocess_dataset()
    
    app.state.clip_model = clip_model
    app.state.combiner = combiner
    app.state.dataset_metadata = dataset_metadata
    app.state.dataset_index_names = dataset_index_names
    app.state.dataset_index_features = dataset_index_features
    setattr(app.state, api_name + "_api", api)


# Exception handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Get the original 'detail' list of errors
    details = exc.errors()
    error_details = []

    for error in details:
        error_details.append(
            {
                "error": error["msg"] + " " + str(error["loc"])
            }
        )
    return JSONResponse(content={"message": error_details})


# Fashion retrieval
@app.get("/", response_class=HTMLResponse)
async def home():
    with open(ROOT / "templates/index.html") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)


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