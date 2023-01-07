from io import BytesIO

from fastapi import APIRouter, UploadFile
from service import run_tryon


router = APIRouter()


@router.post('/try-on')
async def try_on_cloth(person_image: UploadFile, cloth_image: UploadFile):
    person_image_content = await person_image.read()
    cloth_image_content = await cloth_image.read()
    person = BytesIO(person_image_content)
    cloth = BytesIO(cloth_image_content)

    buffer = BytesIO()
    pil_image = run_tryon(person, cloth)
    pil_image.save(buffer, format='jpg')
    image_bytes = buffer.getvalue()

    return image_bytes




