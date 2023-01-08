import base64
from io import BytesIO

from fastapi import APIRouter, UploadFile
from fastapi.responses import StreamingResponse
from .service import run_tryon


router = APIRouter()


@router.post('/try-on')
async def try_on_cloth(person_image: UploadFile, cloth_image: UploadFile):
    person_image_content = await person_image.read()
    cloth_image_content = await cloth_image.read()
    person = BytesIO(person_image_content)
    cloth = BytesIO(cloth_image_content)

    pil_image = run_tryon(person, cloth)

    image_buffer = BytesIO()
    pil_image.save(image_buffer, format='JPEG')
    image_buffer.seek(0)

    base64_string = "data:image/jpeg;base64,"+base64.b64encode(image_buffer.getvalue()).decode()
    
    # return StreamingResponse(image_buffer, media_type="image/jpeg")
    return base64_string





