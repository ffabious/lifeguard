from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import BigInteger, String, DateTime, Integer, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.workout import Workout
    from app.models.nutrition import Meal, WaterLog
    from app.models.shopping import ShoppingItem


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str] = mapped_column(String(255))
    last_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # User settings
    daily_calorie_goal: Mapped[int] = mapped_column(Integer, default=2000)
    daily_protein_goal: Mapped[int] = mapped_column(Integer, default=150)  # grams
    daily_carbs_goal: Mapped[int] = mapped_column(Integer, default=250)  # grams
    daily_fat_goal: Mapped[int] = mapped_column(Integer, default=65)  # grams
    daily_water_goal: Mapped[int] = mapped_column(Integer, default=8)  # glasses (250ml each)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    workouts: Mapped[List["Workout"]] = relationship(
        "Workout", back_populates="user", cascade="all, delete-orphan"
    )
    meals: Mapped[List["Meal"]] = relationship(
        "Meal", back_populates="user", cascade="all, delete-orphan"
    )
    water_logs: Mapped[List["WaterLog"]] = relationship(
        "WaterLog", back_populates="user", cascade="all, delete-orphan"
    )
    shopping_items: Mapped[List["ShoppingItem"]] = relationship(
        "ShoppingItem", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User {self.telegram_id}: {self.first_name}>"
