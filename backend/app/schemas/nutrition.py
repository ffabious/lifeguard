from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel

from app.models.nutrition import MealType


class MealBase(BaseModel):
    name: str
    meal_type: MealType
    calories: Optional[int] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fat: Optional[float] = None
    fiber: Optional[float] = None
    serving_size: Optional[str] = None
    notes: Optional[str] = None
    meal_date: date = date.today()


class MealCreate(MealBase):
    pass


class MealUpdate(BaseModel):
    name: Optional[str] = None
    meal_type: Optional[MealType] = None
    calories: Optional[int] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fat: Optional[float] = None
    fiber: Optional[float] = None
    serving_size: Optional[str] = None
    notes: Optional[str] = None
    meal_date: Optional[date] = None


class MealResponse(MealBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WaterLogBase(BaseModel):
    glasses: int = 1
    log_date: date = date.today()


class WaterLogCreate(WaterLogBase):
    pass


class WaterLogResponse(WaterLogBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class DailyNutritionSummary(BaseModel):
    date: date
    total_calories: int
    total_protein: float
    total_carbs: float
    total_fat: float
    total_fiber: float
    water_glasses: int
    meals_count: int
    
    # Goals
    calorie_goal: int
    protein_goal: int
    carbs_goal: int
    fat_goal: int
    water_goal: int
    
    # Progress percentages
    calorie_progress: float
    protein_progress: float
    carbs_progress: float
    fat_progress: float
    water_progress: float
