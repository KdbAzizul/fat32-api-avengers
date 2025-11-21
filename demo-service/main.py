"""
Demo Service - Simple microservice for demonstration
Handles basic CRUD operations for items
"""

from fastapi import FastAPI, HTTPException, Depends
from typing import List
import logging

from database import get_db, init_db
from models import Item, ItemCreate, ItemUpdate, ItemResponse
from crud import (
    create_item,
    get_item_by_id,
    get_all_items,
    update_item,
    delete_item
)
from prometheus_fastapi_instrumentator import Instrumentator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Demo Service",
    description="Demo microservice for item management",
    version="1.0.0"
)

# Initialize tracing after app is created
try:
    from middleware.tracing import init_tracing
    init_tracing(app)
    logger.info("Tracing initialized")
except Exception as e:
    logger.warning(f"Tracing failed: {e}")

Instrumentator().instrument(app).expose(app, endpoint="/metrics")

@app.on_event("startup")
async def startup():
    """Initialize database on startup"""
    logger.info("Initializing Demo Service...")
    await init_db()
    logger.info("Demo Service started successfully")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "demo-service"}

# ============================================================================
# ITEM ENDPOINTS
# ============================================================================

@app.post("/items", status_code=201, response_model=ItemResponse)
async def create_new_item(item_data: ItemCreate, db = Depends(get_db)):
    """Create a new item"""
    item = await create_item(db, item_data)
    return ItemResponse.from_orm(item)

@app.get("/items", response_model=List[ItemResponse])
async def list_items(
    skip: int = 0,
    limit: int = 100,
    available_only: bool = False,
    db = Depends(get_db)
):
    """List all items with optional filtering"""
    items = await get_all_items(db, skip=skip, limit=limit, available_only=available_only)
    return [ItemResponse.from_orm(item) for item in items]

@app.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(item_id: str, db = Depends(get_db)):
    """Get item by ID"""
    item = await get_item_by_id(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return ItemResponse.from_orm(item)

@app.put("/items/{item_id}", response_model=ItemResponse)
async def update_existing_item(
    item_id: str,
    item_data: ItemUpdate,
    db = Depends(get_db)
):
    """Update an existing item"""
    item = await update_item(db, item_id, item_data)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return ItemResponse.from_orm(item)

@app.delete("/items/{item_id}")
async def delete_existing_item(item_id: str, db = Depends(get_db)):
    """Delete an item"""
    success = await delete_item(db, item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)
