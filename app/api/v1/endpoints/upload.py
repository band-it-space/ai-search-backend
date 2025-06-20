from fastapi import APIRouter, UploadFile, File
import shutil
import uuid
import pandas as pd
import os
from services.vector_service import store_product_records
from utils.logging import setup_logger

# logger = setup_logger("upload_endpoint")

router = APIRouter()


@router.post("/")
async def upload_excel(file: UploadFile = File(...)):
    temp_path = f"/tmp/{uuid.uuid4()}_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        ext = os.path.splitext(file.filename)[-1].lower()
        engine = "xlrd" if ext == ".xls" else "openpyxl"
        df = pd.read_excel(temp_path, engine=engine)

        expected_columns = ["date_prihod", "costs", "costs_NDS", "name", "tovar_name", "name_tovar_1C"]
        df = df[expected_columns].dropna(subset=["name_tovar_1C"])

        records = df.to_dict(orient="records")
        new_records = store_product_records(records)

        # logger.info(f"Uploaded and processed file: {file.filename} with {len(records)} records")
        return {"message": "Upload successful", "original_count": len(records), "inserted_count": len(new_records)}

    except Exception as error:
        # logger.error(f"Upload failed: {error}")
        return {"message": "Upload failed", "error": str(error)}
