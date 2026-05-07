from bson import ObjectId
from fastapi import APIRouter, HTTPException, Query, Depends
from finance_tracker.database.db import mongodb
from finance_tracker.models.transaction import TransactionCreate, TransactionUpdate
from datetime import datetime, timezone

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.post("")
async def create_transaction(data: TransactionCreate):
    """
    Register a new financial transaction.
    :param data: Transaction details including amount, type, and category.
    :return: dict
    """
    try:
        doc = data.model_dump()
        doc["created_at"] = datetime.now(timezone.utc)
        doc["updated_at"] = datetime.now(timezone.utc)
        res = await mongodb.db.transactions.insert_one(doc)
        return {"id": str(res.inserted_id)}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/search")
async def search_transactions(q: str,page: int = Query(1, ge=1),page_size: int = Query(20, le=100)):
    """
    Search transactions by title or description with pagination.
    :param q: Search keyword to filter title and description.
    :param page: Current page number (starts at 1).
    :param page_size: Number of records per page (max 100).
    :return: dict
    """
    try:
        search_term = q.lower().strip()
        all_records = []
        async for doc in mongodb.db.transactions.find():
            all_records.append(doc)

        filtered_results = []
        for item in all_records:
            title = item.get("title", "").lower()
            description = item.get("description", "").lower()

            if search_term in title or search_term in description:
                # IMPORTANT: Convert ObjectId to string here so it's ready for JSON
                item["_id"] = str(item["_id"])
                filtered_results.append(item)

        total_found = len(filtered_results)
        skip = (page - 1) * page_size
        paginated_data = filtered_results[skip : skip + page_size]

        return {
            "status": "success",
            "metadata": {
                "total_records": total_found,
                "page": page,
                "total_pages": (total_found // page_size) + (1 if total_found % page_size > 0 else 0)
            },
            "data": paginated_data
        }
    except Exception as e:
        raise HTTPException(500, f"Search error: {str(e)}")

@router.get("/summary")
async def get_monthly_summary(month: str = Query(..., description="Format: YYYY-MM")):
    """
    Generate a financial summary for a specific month.
    :param month: The month to summarize in 'YYYY-MM' format.
    :return: dict
    """
    try:
        year, mon = map(int, month.split("-"))
        start_date = datetime(year, mon, 1, tzinfo=timezone.utc)

        if mon == 12:
            end_date = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
        else:
            end_date = datetime(year, mon + 1, 1, tzinfo=timezone.utc)

        pipeline = [
            {"$match": {"date": {"$gte": start_date, "$lt": end_date}}},
            {"$facet": {
                "totals": [
                    {"$group": {"_id": "$type", "sum": {"$sum": "$amount"}}}
                ],
                "categories": [
                    {"$match": {"type": "expense"}},
                    {"$group": {"_id": "$category", "total": {"$sum": "$amount"}}}
                ],
                "highest_expense": [
                    {"$match": {"type": "expense"}},
                    {"$sort": {"amount": -1}},
                    {"$limit": 1}
                ]
            }}
        ]

        result = await mongodb.db.transactions.aggregate(pipeline).to_list(1)
        data = result[0] if result else {}
        income = next((i['sum'] for i in data['totals'] if i['_id'] == 'income'), 0)
        expense = next((i['sum'] for i in data['totals'] if i['_id'] == 'expense'), 0)
        category_breakdown = []
        for cat in data['categories']:
            percentage = (cat['total'] / expense * 100) if expense > 0 else 0
            category_breakdown.append({
                "category": cat['_id'],
                "total": cat['total'],
                "percentage": round(percentage, 2)
            })
        top_exp = data['highest_expense'][0] if data['highest_expense'] else None
        if top_exp: top_exp["_id"] = str(top_exp["_id"])
        return {
            "month": month,
            "total_income": income,
            "total_expense": expense,
            "net_balance": round(income - expense, 2),
            "category_breakdown": category_breakdown,
            "highest_expense": top_exp
        }

    except ValueError:
        raise HTTPException(400, "Invalid month format. Use YYYY-MM")
    except Exception as e:
        raise HTTPException(500, f"Aggregation failed: {str(e)}")


@router.delete("/bulk")
async def bulk_delete(category: str | None = Query(None),start_date: datetime | None = Query(None, alias="from"),end_date: datetime | None = Query(None, alias="to")):
    """
    Delete multiple transactions based on category or date range.
    :param category: Category filter for deletion.
    :param start_date: Start boundary for deletion range
    :param end_date: End boundary for deletion range.
    :return: dict
    """
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

@router.get("")
async def get_transactions(page: int = 1, page_size: int = 20):
    """
    Fetch a paginated list of all transactions.
    :param page: Current page.
    :param page_size: Number of items per page.
    :return: dict
    """
    try:
        skip = (page - 1) * page_size
        total = await mongodb.db.transactions.count_documents({})
        cursor = mongodb.db.transactions.find().skip(skip).limit(page_size)
        records = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            records.append(doc)
        return {
            "page": page,
            "page_size": page_size,
            "total_records": total,
            "total_pages": (total // page_size) + (1 if total % page_size > 0 else 0),
            "data": records
        }
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(500, detail="Internal Server Error")


@router.get("/{id}")
async def get_transaction(id: str):
    """
    Retrieve a single transaction by its unique ID.
    :param id: ObjectID
    :return: dict
    """
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
    """
    Remove a transaction from the database.
    :param id: ObjectID
    :return: dict
    """
    try:
        doc = await mongodb.db.transactions.delete_one({"_id": ObjectId(id)})
        return {"status": "success", "data": doc}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.patch("/{id}")
async def update_transaction(id: str,data: TransactionUpdate,):
    """
    Update a transaction.
    :param id: ObjectID
    :param data: Partial fields to update.
    :return: dict
    """
    if not ObjectId.is_valid(id):
        raise HTTPException(400, "Invalid ID format")

    try:
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(400, "No fields provided for update")

        update_data["updated_at"] = str(datetime.now(timezone.utc))
        result = await mongodb.db.transactions.update_one(
            {"_id": ObjectId(id)},
            {"$set": update_data}
        )

        if result.matched_count == 0:
            raise HTTPException(404, "Transaction not found")
        return {
            "status": "success",
            "message": "Transaction updated",
            "updated_fields": list(update_data.keys())
        }
    except Exception as e:
        raise HTTPException(500, f"Update failed: {str(e)}")


