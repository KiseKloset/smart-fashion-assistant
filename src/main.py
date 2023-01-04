import uvicorn
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

import try_on
from config import settings


app = FastAPI()

app.include_router(try_on.router.router, prefix="/try-on")

@app.get('/health', status_code=status.HTTP_200_OK)
def perform_healthcheck():  
    return JSONResponse(content={'message': 'success'})


if __name__ == "__main__":
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
