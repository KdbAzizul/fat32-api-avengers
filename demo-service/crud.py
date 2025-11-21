"""
Demo Service - CRUD Operations
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from models import Item, ItemCreate, ItemUpdate
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# CREATE
# ============================================================================

async def create_item(db: AsyncSession, item_data: ItemCreate) -> Item:
    """Create a new item"""
    item = Item(
        name=item_data.name,
        description=item_data.description,
        price=item_data.price,
        quantity=item_data.quantity,
        is_available=item_data.is_available
    )
    
    db.add(item)
    await db.commit()
    await db.refresh(item)
    
    logger.info(f"Created item: {item.name}")
    return item

# ============================================================================
# READ
# ============================================================================

async def get_item_by_id(db: AsyncSession, item_id: str) -> Optional[Item]:
    """Get item by ID"""
    result = await db.execute(
        select(Item).where(Item.id == item_id)
    )
    return result.scalar_one_or_none()

async def get_all_items(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    available_only: bool = False
) -> List[Item]:
    """Get all items with pagination"""
    query = select(Item)
    
    if available_only:
        query = query.where(Item.is_available == True)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

# ============================================================================
# UPDATE
# ============================================================================

async def update_item(
    db: AsyncSession,
    item_id: str,
    item_data: ItemUpdate
) -> Optional[Item]:
    """Update item"""
    item = await get_item_by_id(db, item_id)
    if not item:
        return None
    
    # Update fields
    update_data = item_data.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(item, field, value)
    
    await db.commit()
    await db.refresh(item)
    
    logger.info(f"Updated item: {item.name}")
    return item

# ============================================================================
# DELETE
# ============================================================================

async def delete_item(db: AsyncSession, item_id: str) -> bool:
    """Delete item"""
    item = await get_item_by_id(db, item_id)
    if not item:
        return False
    
    await db.delete(item)
    await db.commit()
    
    logger.info(f"Deleted item: {item.name}")
    return True
