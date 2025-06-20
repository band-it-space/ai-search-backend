from fastapi import APIRouter
from fastapi.responses import JSONResponse
from db.tender_collection import initialize_tender_collection
from utils.logging import setup_logger
from datetime import datetime

logger = setup_logger("debug")

router = APIRouter()
collection = initialize_tender_collection()

@router.get("/tenders")
async def list_all_tenders():
    try:
        collection = initialize_tender_collection()
        results = collection.query(
            expr="",
            output_fields=["tender_id", "tender_name", "created_at", "updated_at"],
            limit=10000
        )

        logger.info(f"DEBUG: tender query results: {results}")

        tenders = {}
        for row in results:
            tid = row["tender_id"]
            if tid not in tenders:
                tenders[tid] = {
                    "tender_id": tid,
                    "tender_name": row["tender_name"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                    "supplier_count": 1
                }
            else:
                tenders[tid]["supplier_count"] += 1

        return JSONResponse(content=list(tenders.values()))

    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "Failed to fetch tenders", "error": str(e)})

@router.get("/tenders/{tender_id}")
async def get_tender_details(tender_id: str):
    try:
        collection = initialize_tender_collection()

        expr = f'tender_id == "{tender_id}"'
        results = collection.query(
            expr=expr,
            output_fields=["supplier_name", "items"],
            # limit=10000
        )

        if not results:
            return JSONResponse(status_code=404, content={"message": "Tender not found"})

        suppliers = []
        for row in results:
            suppliers.append({
                "supplier_name": row["supplier_name"],
                "items": row["items"]
            })

        return JSONResponse(content={"tender_id": tender_id, "suppliers": suppliers})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "Failed to fetch tender", "error": str(e)})

@router.delete("/tenders/{tender_id}")
async def delete_tender(tender_id: str):
    try:
        expr = f'tender_id == "{tender_id}"'
        delete_result = collection.delete(expr)
        return JSONResponse(content={"message": f"Tender '{tender_id}' deleted", "delete_result": delete_result})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "Failed to delete tender", "error": str(e)})

@router.delete("/tenders/{tender_id}/supplier-item")
async def delete_supplier_item(tender_id: str, supplier_name: str, tovar_name: str):
    try:
        expr = f'tender_id == "{tender_id}"'
        results = collection.query(expr=expr, output_fields=[
            "tender_name", "tender_vector", "supplier_name", "items", "created_at"
        ])

        supplier_found = False
        item_found = False
        updated_records = []

        for row in results:
            if row["supplier_name"] != supplier_name:
                updated_records.append(row)
                continue

            supplier_found = True
            original_items = row["items"]
            new_items = [item for item in original_items if item.get("tovar_name") != tovar_name]

            if len(new_items) != len(original_items):
                item_found = True

            if new_items:
                updated_records.append({
                    **row,
                    "items": new_items
                })

        if not supplier_found:
            return JSONResponse(status_code=404, content={"message": f"Supplier '{supplier_name}' not found in tender '{tender_id}'"})

        if not item_found:
            return JSONResponse(status_code=404, content={"message": f"Item with tovar_name '{tovar_name}' not found for supplier '{supplier_name}'"})

        collection.delete(expr=f'tender_id == "{tender_id}"')

        updated_at = datetime.utcnow().isoformat()

        collection.insert([
            [tender_id] * len(updated_records),
            [row["tender_name"] for row in updated_records],
            [row["tender_vector"] for row in updated_records],
            [row["supplier_name"] for row in updated_records],
            [row["items"] for row in updated_records],
            [row["created_at"] for row in updated_records],
            [updated_at] * len(updated_records),
        ])

        return {"message": "Item removed", "tender_id": tender_id}

    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "Failed to delete item", "error": str(e)})
