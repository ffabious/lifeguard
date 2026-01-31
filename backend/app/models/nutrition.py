from datetime import datetime, date
from typing import Optional, TYPE_CHECKING

from sqlalchemy import ForeignKey, String, DateTime, Integer, Float, Text, Date, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class MealType(str, enum.Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"


class Meal(Base):
    __tablename__ = "meals"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    
    name: Mapped[str] = mapped_column(String(255))
    meal_type: Mapped[MealType] = mapped_column(Enum(MealType))
    
    # Nutrition info (all optional for manual entry)
    calories: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    protein: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # grams
    carbs: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # grams
    fat: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # grams
    fiber: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # grams
    
    serving_size: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    meal_date: Mapped[date] = mapped_column(Date, default=date.today)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="meals")

    def __repr__(self) -> str:
        return f"<Meal {self.id}: {self.name}>"


class WaterLog(Base):
    __tablename__ = "water_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    
    glasses: Mapped[int] = mapped_column(Integer, default=1)  # 1 glass = 250ml
    log_date: Mapped[date] = mapped_column(Date, default=date.today)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="water_logs")

    def __repr__(self) -> str:
        return f"<WaterLog {self.id}: {self.glasses} glasses>"
