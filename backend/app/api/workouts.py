from datetime import date, timedelta
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.core.deps import CurrentUser, DbSession
from app.models.workout import Workout, Exercise
from app.schemas.workout import (
    WorkoutCreate,
    WorkoutUpdate,
    WorkoutResponse,
    WorkoutSummary,
    ExerciseCreate,
    ExerciseUpdate,
    ExerciseResponse,
)

router = APIRouter()


@router.get("", response_model=List[WorkoutResponse])
async def list_workouts(
    user: CurrentUser,
    db: DbSession,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = Query(default=50, le=100),
    offset: int = 0,
):
    """List user's workouts with optional date filtering."""
    query = (
        select(Workout)
        .where(Workout.user_id == user.id)
        .options(selectinload(Workout.exercises))
        .order_by(Workout.workout_date.desc(), Workout.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    
    if start_date:
        query = query.where(Workout.workout_date >= start_date)
    if end_date:
        query = query.where(Workout.workout_date <= end_date)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=WorkoutResponse, status_code=status.HTTP_201_CREATED)
async def create_workout(
    user: CurrentUser,
    db: DbSession,
    workout_data: WorkoutCreate,
):
    """Create a new workout with exercises."""
    workout = Workout(
        user_id=user.id,
        name=workout_data.name,
        workout_type=workout_data.workout_type,
        duration_minutes=workout_data.duration_minutes,
        calories_burned=workout_data.calories_burned,
        notes=workout_data.notes,
        workout_date=workout_data.workout_date,
    )
    db.add(workout)
    await db.flush()
    
    # Add exercises
    for i, exercise_data in enumerate(workout_data.exercises):
        exercise = Exercise(
            workout_id=workout.id,
            name=exercise_data.name,
            sets=exercise_data.sets,
            reps=exercise_data.reps,
            weight=exercise_data.weight,
            duration_seconds=exercise_data.duration_seconds,
            distance_meters=exercise_data.distance_meters,
            notes=exercise_data.notes,
            order=exercise_data.order or i,
        )
        db.add(exercise)
    
    await db.commit()
    
    # Reload with exercises
    result = await db.execute(
        select(Workout)
        .where(Workout.id == workout.id)
        .options(selectinload(Workout.exercises))
    )
    return result.scalar_one()


@router.get("/{workout_id}", response_model=WorkoutResponse)
async def get_workout(
    user: CurrentUser,
    db: DbSession,
    workout_id: int,
):
    """Get a specific workout."""
    result = await db.execute(
        select(Workout)
        .where(Workout.id == workout_id, Workout.user_id == user.id)
        .options(selectinload(Workout.exercises))
    )
    workout = result.scalar_one_or_none()
    
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    
    return workout


@router.patch("/{workout_id}", response_model=WorkoutResponse)
async def update_workout(
    user: CurrentUser,
    db: DbSession,
    workout_id: int,
    workout_update: WorkoutUpdate,
):
    """Update a workout."""
    result = await db.execute(
        select(Workout)
        .where(Workout.id == workout_id, Workout.user_id == user.id)
        .options(selectinload(Workout.exercises))
    )
    workout = result.scalar_one_or_none()
    
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    
    update_data = workout_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(workout, field, value)
    
    await db.commit()
    await db.refresh(workout)
    
    return workout


@router.delete("/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workout(
    user: CurrentUser,
    db: DbSession,
    workout_id: int,
):
    """Delete a workout."""
    result = await db.execute(
        select(Workout).where(Workout.id == workout_id, Workout.user_id == user.id)
    )
    workout = result.scalar_one_or_none()
    
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    
    await db.delete(workout)
    await db.commit()


@router.post("/{workout_id}/exercises", response_model=ExerciseResponse, status_code=status.HTTP_201_CREATED)
async def add_exercise(
    user: CurrentUser,
    db: DbSession,
    workout_id: int,
    exercise_data: ExerciseCreate,
):
    """Add an exercise to a workout."""
    result = await db.execute(
        select(Workout).where(Workout.id == workout_id, Workout.user_id == user.id)
    )
    workout = result.scalar_one_or_none()
    
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    
    exercise = Exercise(
        workout_id=workout.id,
        name=exercise_data.name,
        sets=exercise_data.sets,
        reps=exercise_data.reps,
        weight=exercise_data.weight,
        duration_seconds=exercise_data.duration_seconds,
        distance_meters=exercise_data.distance_meters,
        notes=exercise_data.notes,
        order=exercise_data.order,
    )
    db.add(exercise)
    await db.commit()
    await db.refresh(exercise)
    
    return exercise


@router.patch("/{workout_id}/exercises/{exercise_id}", response_model=ExerciseResponse)
async def update_exercise(
    user: CurrentUser,
    db: DbSession,
    workout_id: int,
    exercise_id: int,
    exercise_update: ExerciseUpdate,
):
    """Update an exercise."""
    result = await db.execute(
        select(Exercise)
        .join(Workout)
        .where(
            Exercise.id == exercise_id,
            Exercise.workout_id == workout_id,
            Workout.user_id == user.id,
        )
    )
    exercise = result.scalar_one_or_none()
    
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    update_data = exercise_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(exercise, field, value)
    
    await db.commit()
    await db.refresh(exercise)
    
    return exercise


@router.delete("/{workout_id}/exercises/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_exercise(
    user: CurrentUser,
    db: DbSession,
    workout_id: int,
    exercise_id: int,
):
    """Delete an exercise from a workout."""
    result = await db.execute(
        select(Exercise)
        .join(Workout)
        .where(
            Exercise.id == exercise_id,
            Exercise.workout_id == workout_id,
            Workout.user_id == user.id,
        )
    )
    exercise = result.scalar_one_or_none()
    
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    await db.delete(exercise)
    await db.commit()


@router.get("/summary/weekly", response_model=WorkoutSummary)
async def get_weekly_summary(
    user: CurrentUser,
    db: DbSession,
):
    """Get workout summary for the current week."""
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    
    result = await db.execute(
        select(Workout)
        .where(
            Workout.user_id == user.id,
            Workout.workout_date >= week_start,
            Workout.workout_date <= today,
        )
    )
    workouts = result.scalars().all()
    
    workouts_by_type = {}
    total_duration = 0
    total_calories = 0
    
    for workout in workouts:
        workout_type = workout.workout_type.value
        workouts_by_type[workout_type] = workouts_by_type.get(workout_type, 0) + 1
        total_duration += workout.duration_minutes
        total_calories += workout.calories_burned or 0
    
    return WorkoutSummary(
        total_workouts=len(workouts),
        total_duration_minutes=total_duration,
        total_calories_burned=total_calories,
        workouts_by_type=workouts_by_type,
    )
