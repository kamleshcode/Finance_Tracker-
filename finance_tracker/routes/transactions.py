from bson import ObjectId
from fastapi import APIRouter, HTTPException, Query, Depends
from finance_tracker.database.db import mongodb
from finance_tracker.models.transaction import TransactionCreate, TransactionUpdate
from datetime import datetime, timezone

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.post("")
async def create_transaction(data: TransactionCreate):
    try:
        doc = data.model_dump()
        doc["created_at"] = datetime.now(timezone.utc)
        doc["updated_at"] = datetime.now(timezone.utc)
        res = await mongodb.db.transactions.insert_one(doc)
        return {"id": str(res.inserted_id)}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/{id}")
async def get_transaction(id: str):
    try:
        doc = await mongodb.db.transactions.find_one({"_id": ObjectId(id)})
        if not doc:
            raise HTTPException(404, "Transaction not found")
        # When MongoDB sends data back to Python, the _id is still in that binary format.so we need to convert it to string
        doc["_id"] = str(doc["_id"])
        return {"status": "success", "data": doc}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.delete("/{id}")
async def delete_transaction(id: str):
    try:
        doc = await mongodb.db.transactions.delete_one({"_id": ObjectId(id)})
        return {"status": "success", "data": doc}
    except Exception as e:
        raise HTTPException(500, str(e))


@router.delete("/bulk")
async def bulk_delete(category: str | None = Query(None),start_date: datetime | None = Query(None, alias="from"),end_date: datetime | None = Query(None, alias="to")):
    try:
        query = {}
        if category:
            query["category"] = category.lower()
        if start_date or end_date:
            query["date"] = {}
            if start_date: query["date"]["$gte"] = start_date
            if end_date:   query["date"]["$lte"] = end_date
        if not query:
            raise HTTPException(400, "Please provide category or date range")
        res = await mongodb.db.transactions.delete_many(query)
        return {
            "status": "success",
            "deleted_count": res.deleted_count
        }
    except Exception as e:
        raise HTTPException(500, f"Bulk delete failed: {str(e)}")


