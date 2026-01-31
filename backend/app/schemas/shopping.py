from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.shopping import ShoppingCategory


class ShoppingItemBase(BaseModel):
    name: str
    quantity: Optional[str] = None
    category: ShoppingCategory = ShoppingCategory.OTHER
    notes: Optional[str] = None


class ShoppingItemCreate(ShoppingItemBase):
    pass


class ShoppingItemUpdate(BaseModel):
    name: Optional[str] = None
    quantity: Optional[str] = None
    category: Optional[ShoppingCategory] = None
    notes: Optional[str] = None
    is_purchased: Optional[bool] = None


class ShoppingItemResponse(ShoppingItemBase):
    id: int
    user_id: int
    is_purchased: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ShoppingListSummary(BaseModel):
    total_items: int
    purchased_items: int
    pending_items: int
    items_by_category: dict[str, int]
