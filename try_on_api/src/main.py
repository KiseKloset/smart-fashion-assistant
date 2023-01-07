import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from try_on import router as tryon_router
from config import settings


app = FastAPI()

app.include_router(tryon_router.router, prefix="/try-on")


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


@app.get('/health', status_code=status.HTTP_200_OK)
def perform_healthcheck():  
    return JSONResponse(content={'message': 'success'})


if __name__ == "__main__":
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
