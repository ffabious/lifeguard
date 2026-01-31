from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UserBase(BaseModel):
    username: Optional[str] = None
    first_name: str
    last_name: Optional[str] = None


class UserCreate(UserBase):
    telegram_id: int


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    daily_calorie_goal: Optional[int] = None
    daily_protein_goal: Optional[int] = None
    daily_carbs_goal: Optional[int] = None
    daily_fat_goal: Optional[int] = None
    daily_water_goal: Optional[int] = None


class UserResponse(UserBase):
    id: int
    telegram_id: int
    daily_calorie_goal: int
    daily_protein_goal: int
    daily_carbs_goal: int
    daily_fat_goal: int
    daily_water_goal: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserGoals(BaseModel):
    daily_calorie_goal: int
    daily_protein_goal: int
    daily_carbs_goal: int
    daily_fat_goal: int
    daily_water_goal: int
