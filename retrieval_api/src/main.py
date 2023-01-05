import uvicorn

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from config import settings
from tgir import service, router

app = FastAPI()

app.include_router(router.router, prefix="/tgir")
app.mount(
    "/static/images", StaticFiles(directory=f"{service.data_path}/images")
)


@app.get("/health", status_code=status.HTTP_200_OK)
def perform_healthcheck():
    return JSONResponse(content={"message": "success"})


if __name__ == "__main__":
    clip_model, combiner = service.load_models()
    dataset_metadata = service.load_dataset_metadata()
    dataset_index_names, dataset_index_features = service.load_preprocess_dataset()
    
    app.state.clip_model = clip_model
    app.state.combiner = combiner
    app.state.dataset_metadata = dataset_metadata
    app.state.dataset_index_names = dataset_index_names
    app.state.dataset_index_features = dataset_index_features

    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
