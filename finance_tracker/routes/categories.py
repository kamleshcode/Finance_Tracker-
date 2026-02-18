from fastapi import APIRouter, HTTPException
from finance_tracker.database.db import mongodb
from finance_tracker.models.category import CategoryCreate,CategoryUpdate
from datetime import datetime, timezone

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.post("")
async def create_category(data: CategoryCreate):
    """
    Create a new category
    :param data: The category schema containing name and metadata.
    :return: dict
    """
    try:
        doc = data.model_dump()
        doc["created_at"] = datetime.now(timezone.utc)
        await mongodb.db.categories.insert_one(doc)
        return {"message": "Category created"}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.delete("/{name}")
async def delete_category(name: str):
    """
    Delete a category
    :param name: The case-insensitive name of the category to remove
    :return: dict
    """
    category_name = name.lower().strip()
    try:
        delete_res = await mongodb.db.categories.delete_one({"name": category_name})
        if delete_res.deleted_count == 0:
            raise HTTPException(404, "Category not found")
        # Logic: Update all linked transactions to "uncategorized"
        update_res = await mongodb.db.transactions.update_many(
            {"category": category_name},
            {"$set": {"category": "uncategorized"}}
        )
        return {
            "status": "success",
            "message": f"Category '{category_name}' deleted.",
            "updated_transactions": update_res.modified_count
        }
    except Exception as e:
        raise HTTPException(500, f"Error: {str(e)}")

@router.get("")
async def list_categories():
    """
    Retrieve a list of all existing financial categories.
    :return: list[dict]
    """
    try:
        cursor = mongodb.db.categories.find()
        results = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            results.append(doc)
        return results
    except Exception as e:
        raise HTTPException(500, f"Failed to fetch categories: {str(e)}")

#in transaction table not getting updated
@router.patch("/{name}")
async def update_category(data: CategoryUpdate, name: str):
    """
    Update a category
    :param data: The partial update data.
    :param name: The current name of the category to identify the record.
    :return: dict
    """
    try:
        category_name = name.lower().strip()
        update_data = data.model_dump(exclude_unset=True)

        if not update_data:
            raise HTTPException(400, "At least one field must be provided to update")
        result = await mongodb.db.categories.update_one(
            {"name": category_name},
            {"$set": update_data}
        )
        if result.matched_count == 0:
            raise HTTPException(404, f"Category '{name}' not found")
        return {
            "status": "success",
            "message": f"Category '{category_name}' updated successfully",
            "updated_fields": list(update_data.keys())
        }
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(500, f"Database error: {str(e)}")
