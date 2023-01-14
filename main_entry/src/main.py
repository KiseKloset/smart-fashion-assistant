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

@app.on_event('startup')
async def startup_event():
    api_clients = {
        'tgir': {'host': settings.HOST_RETRIEVAL, 'port': settings.PORT_RETRIEVAL},
        'tryon': {'host': settings.HOST_TRYON, 'port': settings.PORT_TRYON}
    }
    for api_name, api_settings in api_clients.items():
        host = api_settings['host']
        port = api_settings['port']
        api = httpx.AsyncClient(base_url=f'http://{host}:{port}/')
        setattr(app.state, api_name + "_api", api)


@app.on_event('shutdown')
async def shutdown_event():
    tgir_api = app.state.tgir_api
    tryon_api = app.state.tryon_api
    await tgir_api.aclose()
    await tryon_api.aclose()


# Set fashion retrieval reverse proxy
async def _retrieval_reverse_proxy(request: Request):
    api = request.app.state.tgir_api
    url = httpx.URL(path=request.url.path, query=request.url.query.encode('utf-8'))
    timeout = httpx.Timeout(10.0, read=None)
    req = api.build_request(
        request.method, url, headers=request.headers.raw, content=request.stream(), timeout=timeout
    )
    r = await api.send(req, stream=True)
    return StreamingResponse(
        r.aiter_raw(),
        status_code=r.status_code,
        headers=r.headers,
        background=BackgroundTask(r.aclose)
    )

app.add_route('/tgir/{path:path}', _retrieval_reverse_proxy, ['POST'])
app.add_route('/static/images/{image:path}', _retrieval_reverse_proxy, ['GET'])


# Set virtual tryon reverse proxy
async def _retrieval_reverse_proxy(request: Request):
    api = request.app.state.tryon_api
    url = httpx.URL(path=request.url.path, query=request.url.query.encode('utf-8'))
    timeout = httpx.Timeout(10.0, read=None)
    req = api.build_request(
        request.method, url, headers=request.headers.raw, content=request.stream(), timeout=timeout
    )
    r = await api.send(req, stream=True)
    return StreamingResponse(
        r.aiter_raw(),
        status_code=r.status_code,
        headers=r.headers,
        background=BackgroundTask(r.aclose)
    )
app.add_route('/try-on/{path:path}', _retrieval_reverse_proxy, ['POST'])


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