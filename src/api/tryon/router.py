import base64
from PIL import Image
from io import BytesIO

from fastapi import APIRouter, UploadFile
from fastapi.responses import JSONResponse
import torchvision as tv

from .service import TryonService
from .utils import gdrive_download, url_download


router = APIRouter()

gdrive_download(url='https://drive.google.com/uc?id=1rbSTGKAE-MTxBYHd-51l2hMOQPT_7EPy', output='u2netp.pt')
gdrive_download(url='https://drive.google.com/uc?id=1ngpLuaiDbMBT2qrxft82Ujy_rxggsvyZ', output='mobile_warp.pt')
gdrive_download(url='https://drive.google.com/uc?id=1eAAMkxFDum1sKPqyi1BSQ1aRc69T5onI', output='mobile_gen.pt')
url_download(url='https://github.com/WongKinYiu/yolov7/releases/download/v0.1/yolov7-w6-pose.pt', output='yolov7-w6-pose.pt')

tryon_service = TryonService(
    tryon_ckpt={'warp': 'mobile_warp.pt', 'gen': 'mobile_gen.pt'},
    edge_detect_ckpt='u2netp.pt', 
    yolo_ckpt='yolov7-w6-pose.pt',
    device='cuda:0',
)


@router.post('/try-on')
async def try_on_image(person_image: UploadFile, garment_image: UploadFile):
    person_image_content = await person_image.read()
    cloth_image_content = await garment_image.read()

    pil_img = Image.open(BytesIO(person_image_content)).convert('RGB')
    pil_clothes = Image.open(BytesIO(cloth_image_content)).convert('RGB')

    tryon_cv = tryon_service.tryon_image(pil_img, pil_clothes)
    if tryon_cv is not None:
        pil_tryon = Image.fromarray(tryon_cv)
    else:
        pil_tryon = pil_img

    image_buffer = BytesIO()
    pil_tryon.save(image_buffer, 'JPEG')
    image_buffer.seek(0)

    base64_string = "data:image/jpeg;base64,"+base64.b64encode(image_buffer.getvalue()).decode()
    
    return  JSONResponse(content={
                            'message': 'success',
                            'result': base64_string,
                        }
                    )


