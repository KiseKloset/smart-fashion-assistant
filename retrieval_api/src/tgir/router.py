import io

from fastapi import APIRouter, UploadFile, Request, Form, File
from fastapi.responses import JSONResponse

from service import compute_fashionIQ_results

router = APIRouter()

@router.post("/retrieve")
async def text_guided_image_retrieval(ref_image: UploadFile = File(), caption: str = Form(), request: Request = None):
    ref_image_content = await ref_image.read()
    img = io.BytesIO(ref_image_content)
    results = compute_fashionIQ_results(
        img, 
        caption, 
        5,
        request.app.state.clip_model,
        request.app.state.combiner,
        request.app.state.dataset_index_names, 
        request.app.state.dataset_index_features
    )

    response = {}
    for result in results:
        metadata = request.app.state.dataset_metadata[result]

        if metadata["category"] not in response:
            response[metadata["category"]] = []
        response[metadata["category"]].append({"id": result, "url": metadata["url"]})

    return JSONResponse(content=response)
