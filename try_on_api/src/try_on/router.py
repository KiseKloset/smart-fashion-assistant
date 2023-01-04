from fastapi import APIRouter, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


router = APIRouter()

@router.exception_handler(RequestValidationError)
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


@router.post('/try-one-cloth')
def try_one_cloth(person_image: UploadFile, cloth_image: UploadFile):
    pass




