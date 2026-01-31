from datetime import datetime, date
from typing import Optional, List

from pydantic import BaseModel

from app.models.workout import WorkoutType


class ExerciseBase(BaseModel):
    name: str
    sets: Optional[int] = None
    reps: Optional[int] = None
    weight: Optional[float] = None
    duration_seconds: Optional[int] = None
    distance_meters: Optional[float] = None
    notes: Optional[str] = None
    order: int = 0


class ExerciseCreate(ExerciseBase):
    pass


class ExerciseUpdate(BaseModel):
    name: Optional[str] = None
    sets: Optional[int] = None
    reps: Optional[int] = None
    weight: Optional[float] = None
    duration_seconds: Optional[int] = None
    distance_meters: Optional[float] = None
    notes: Optional[str] = None
    order: Optional[int] = None


class ExerciseResponse(ExerciseBase):
    id: int
    workout_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class WorkoutBase(BaseModel):
    name: str
    workout_type: WorkoutType = WorkoutType.OTHER
    duration_minutes: int = 0
    calories_burned: Optional[int] = None
    notes: Optional[str] = None
    workout_date: date = date.today()


class WorkoutCreate(WorkoutBase):
    exercises: List[ExerciseCreate] = []


class WorkoutUpdate(BaseModel):
    name: Optional[str] = None
    workout_type: Optional[WorkoutType] = None
    duration_minutes: Optional[int] = None
    calories_burned: Optional[int] = None
    notes: Optional[str] = None
    workout_date: Optional[date] = None


class WorkoutResponse(WorkoutBase):
    id: int
    user_id: int
    exercises: List[ExerciseResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WorkoutSummary(BaseModel):
    total_workouts: int
    total_duration_minutes: int
    total_calories_burned: int
    workouts_by_type: dict[str, int]
