from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select

from app.core.deps import CurrentUser, DbSession
from app.models.shopping import ShoppingItem, ShoppingCategory
from app.schemas.shopping import (
    ShoppingItemCreate,
    ShoppingItemUpdate,
    ShoppingItemResponse,
    ShoppingListSummary,
)

router = APIRouter()


@router.get("", response_model=List[ShoppingItemResponse])
async def list_shopping_items(
    user: CurrentUser,
    db: DbSession,
    category: Optional[ShoppingCategory] = None,
    purchased: Optional[bool] = None,
):
    """List user's shopping items."""
    query = (
        select(ShoppingItem)
        .where(ShoppingItem.user_id == user.id)
        .order_by(ShoppingItem.is_purchased, ShoppingItem.category, ShoppingItem.created_at.desc())
    )
    
    if category:
        query = query.where(ShoppingItem.category == category)
    if purchased is not None:
        query = query.where(ShoppingItem.is_purchased == purchased)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=ShoppingItemResponse, status_code=status.HTTP_201_CREATED)
async def create_shopping_item(
    user: CurrentUser,
    db: DbSession,
    item_data: ShoppingItemCreate,
):
    """Add a new shopping item."""
    item = ShoppingItem(
        user_id=user.id,
        name=item_data.name,
        quantity=item_data.quantity,
        category=item_data.category,
        notes=item_data.notes,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    
    return item


@router.post("/bulk", response_model=List[ShoppingItemResponse], status_code=status.HTTP_201_CREATED)
async def create_shopping_items_bulk(
    user: CurrentUser,
    db: DbSession,
    items_data: List[ShoppingItemCreate],
):
    """Add multiple shopping items at once."""
    items = []
    for item_data in items_data:
        item = ShoppingItem(
            user_id=user.id,
            name=item_data.name,
            quantity=item_data.quantity,
            category=item_data.category,
            notes=item_data.notes,
        )
        db.add(item)
        items.append(item)
    
    await db.commit()
    
    for item in items:
        await db.refresh(item)
    
    return items


@router.get("/summary", response_model=ShoppingListSummary)
async def get_shopping_summary(
    user: CurrentUser,
    db: DbSession,
):
    """Get shopping list summary."""
    result = await db.execute(
        select(ShoppingItem).where(ShoppingItem.user_id == user.id)
    )
    items = result.scalars().all()
    
    purchased = sum(1 for item in items if item.is_purchased)
    pending = len(items) - purchased
    
    items_by_category = {}
    for item in items:
        if not item.is_purchased:
            cat = item.category.value
            items_by_category[cat] = items_by_category.get(cat, 0) + 1
    
    return ShoppingListSummary(
        total_items=len(items),
        purchased_items=purchased,
        pending_items=pending,
        items_by_category=items_by_category,
    )


@router.get("/{item_id}", response_model=ShoppingItemResponse)
async def get_shopping_item(
    user: CurrentUser,
    db: DbSession,
    item_id: int,
):
    """Get a specific shopping item."""
    result = await db.execute(
        select(ShoppingItem).where(
            ShoppingItem.id == item_id,
            ShoppingItem.user_id == user.id,
        )
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return item


@router.patch("/{item_id}", response_model=ShoppingItemResponse)
async def update_shopping_item(
    user: CurrentUser,
    db: DbSession,
    item_id: int,
    item_update: ShoppingItemUpdate,
):
    """Update a shopping item."""
    result = await db.execute(
        select(ShoppingItem).where(
            ShoppingItem.id == item_id,
            ShoppingItem.user_id == user.id,
        )
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    update_data = item_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    
    await db.commit()
    await db.refresh(item)
    
    return item


@router.patch("/{item_id}/toggle", response_model=ShoppingItemResponse)
async def toggle_shopping_item(
    user: CurrentUser,
    db: DbSession,
    item_id: int,
):
    """Toggle purchased status of a shopping item."""
    result = await db.execute(
        select(ShoppingItem).where(
            ShoppingItem.id == item_id,
            ShoppingItem.user_id == user.id,
        )
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    item.is_purchased = not item.is_purchased
    await db.commit()
    await db.refresh(item)
    
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shopping_item(
    user: CurrentUser,
    db: DbSession,
    item_id: int,
):
    """Delete a shopping item."""
    result = await db.execute(
        select(ShoppingItem).where(
            ShoppingItem.id == item_id,
            ShoppingItem.user_id == user.id,
        )
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    await db.delete(item)
    await db.commit()


@router.delete("/clear/purchased", status_code=status.HTTP_204_NO_CONTENT)
async def clear_purchased_items(
    user: CurrentUser,
    db: DbSession,
):
    """Clear all purchased items from the list."""
    result = await db.execute(
        select(ShoppingItem).where(
            ShoppingItem.user_id == user.id,
            ShoppingItem.is_purchased == True,
        )
    )
    items = result.scalars().all()
    
    for item in items:
        await db.delete(item)
    
    await db.commit()
