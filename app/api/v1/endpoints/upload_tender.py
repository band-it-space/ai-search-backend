from fastapi import APIRouter, UploadFile, File, Request, Form
from fastapi.responses import JSONResponse
from services.tender_services.upload_tender_file import upload_tender_file

router = APIRouter()

@router.post("/")
async def upload_tender(
    request: Request,
    file: UploadFile = File(...),
    tender_name: str = Form(...)
):
    try:
        content = await file.read()
        result = upload_tender_file(request, file.filename, content, tender_name)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "Unexpected error", "error": str(e)})
