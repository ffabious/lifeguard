from datetime import datetime, date
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import ForeignKey, String, DateTime, Integer, Float, Text, Date, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class WorkoutType(str, enum.Enum):
    STRENGTH = "strength"
    CARDIO = "cardio"
    FLEXIBILITY = "flexibility"
    HIIT = "hiit"
    SPORTS = "sports"
    OTHER = "other"


class Workout(Base):
    __tablename__ = "workouts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    
    name: Mapped[str] = mapped_column(String(255))
    workout_type: Mapped[WorkoutType] = mapped_column(
        Enum(WorkoutType), default=WorkoutType.OTHER
    )
    duration_minutes: Mapped[int] = mapped_column(Integer, default=0)
    calories_burned: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    workout_date: Mapped[date] = mapped_column(Date, default=date.today)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="workouts")
    exercises: Mapped[List["Exercise"]] = relationship(
        "Exercise", back_populates="workout", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Workout {self.id}: {self.name}>"


class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    workout_id: Mapped[int] = mapped_column(ForeignKey("workouts.id", ondelete="CASCADE"))
    
    name: Mapped[str] = mapped_column(String(255))
    sets: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    reps: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    weight: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # kg
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    distance_meters: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    # Relationships
    workout: Mapped["Workout"] = relationship("Workout", back_populates="exercises")

    def __repr__(self) -> str:
        return f"<Exercise {self.id}: {self.name}>"
