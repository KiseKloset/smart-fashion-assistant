import uvicorn
import httpx

from pathlib import Path
from fastapi import FastAPI, status, Request
from fastapi.responses import JSONResponse, HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from starlette.background import BackgroundTask

from config import settings, retrieval_settings, tryon_settings

FILE = Path(__file__).resolve()
ROOT = FILE.parent


app = FastAPI()

@app.on_event('startup')
async def startup_event():
    api_clients = {
        'tgir': {'host': retrieval_settings.HOST, 'port': retrieval_settings.PORT},
        'tryon': {'host': tryon_settings.HOST, 'port': tryon_settings.PORT}
    }
    for api_name, api_settings in api_clients.items():
        host = api_settings['host']
        port = api_settings['port']
        api = httpx.AsyncClient(base_url=f'http://{host}:{port}/')
        app.state[api_name + '_api'] = api



@app.on_event('shutdown')
async def shutdown_event():
    tgir_api = app.state.tgir_api
    tryon_api = app.state.tryon_api
    await tgir_api.aclose()
    await tryon_api.aclose()


# Set fashion retrieval reverse proxy
async def _reverse_proxy(request: Request, api_name: str):
    api = request.app.state[api_name]
    url = httpx.URL(path=request.url.path, query=request.url.query.encode('utf-8'))
    req = api.build_request(
        request.method, url, headers=request.headers.raw, content=request.stream()
    )
    r = await api.send(req, stream=True)
    return StreamingResponse(
        r.aiter_raw(),
        status_code=r.status_code,
        headers=r.headers,
        background=BackgroundTask(r.aclose)
    )

app.add_route('/tgir/{path:path}', lambda request: _reverse_proxy(request, 'tgir_api'), ['POST'])
app.add_route('/static/images/{image:path}', lambda request: _reverse_proxy(request, 'tgir_api'), ['GET'])
app.add_route('/try-on/{path:path}', lambda request: _reverse_proxy(request, 'tryon_api'), ['POST'])


# Fashion retrieval entry
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


# Serve static files
app.mount("/static", StaticFiles(directory=ROOT / "static"))


# Useless
@app.get("/health", status_code=status.HTTP_200_OK)
def perform_healthcheck():
    return JSONResponse(content={"message": "success"})


if __name__ == "__main__":
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)