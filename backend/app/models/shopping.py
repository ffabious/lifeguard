from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import ForeignKey, String, DateTime, Boolean, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class ShoppingCategory(str, enum.Enum):
    PRODUCE = "produce"
    DAIRY = "dairy"
    MEAT = "meat"
    SEAFOOD = "seafood"
    BAKERY = "bakery"
    FROZEN = "frozen"
    PANTRY = "pantry"
    BEVERAGES = "beverages"
    SNACKS = "snacks"
    SUPPLEMENTS = "supplements"
    OTHER = "other"


class ShoppingItem(Base):
    __tablename__ = "shopping_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    
    name: Mapped[str] = mapped_column(String(255))
    quantity: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    category: Mapped[ShoppingCategory] = mapped_column(
        Enum(ShoppingCategory), default=ShoppingCategory.OTHER
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    is_purchased: Mapped[bool] = mapped_column(Boolean, default=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="shopping_items")

    def __repr__(self) -> str:
        return f"<ShoppingItem {self.id}: {self.name}>"
