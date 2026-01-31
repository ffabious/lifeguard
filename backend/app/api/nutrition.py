from datetime import date
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select, func

from app.core.deps import CurrentUser, DbSession
from app.models.nutrition import Meal, WaterLog
from app.schemas.nutrition import (
    MealCreate,
    MealUpdate,
    MealResponse,
    WaterLogCreate,
    WaterLogResponse,
    DailyNutritionSummary,
)

router = APIRouter()


# Meals endpoints
@router.get("/meals", response_model=List[MealResponse])
async def list_meals(
    user: CurrentUser,
    db: DbSession,
    meal_date: Optional[date] = None,
    limit: int = Query(default=50, le=100),
    offset: int = 0,
):
    """List user's meals with optional date filtering."""
    query = (
        select(Meal)
        .where(Meal.user_id == user.id)
        .order_by(Meal.meal_date.desc(), Meal.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    
    if meal_date:
        query = query.where(Meal.meal_date == meal_date)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/meals", response_model=MealResponse, status_code=status.HTTP_201_CREATED)
async def create_meal(
    user: CurrentUser,
    db: DbSession,
    meal_data: MealCreate,
):
    """Log a new meal."""
    meal = Meal(
        user_id=user.id,
        name=meal_data.name,
        meal_type=meal_data.meal_type,
        calories=meal_data.calories,
        protein=meal_data.protein,
        carbs=meal_data.carbs,
        fat=meal_data.fat,
        fiber=meal_data.fiber,
        serving_size=meal_data.serving_size,
        notes=meal_data.notes,
        meal_date=meal_data.meal_date,
    )
    db.add(meal)
    await db.commit()
    await db.refresh(meal)
    
    return meal


@router.get("/meals/{meal_id}", response_model=MealResponse)
async def get_meal(
    user: CurrentUser,
    db: DbSession,
    meal_id: int,
):
    """Get a specific meal."""
    result = await db.execute(
        select(Meal).where(Meal.id == meal_id, Meal.user_id == user.id)
    )
    meal = result.scalar_one_or_none()
    
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")
    
    return meal


@router.patch("/meals/{meal_id}", response_model=MealResponse)
async def update_meal(
    user: CurrentUser,
    db: DbSession,
    meal_id: int,
    meal_update: MealUpdate,
):
    """Update a meal."""
    result = await db.execute(
        select(Meal).where(Meal.id == meal_id, Meal.user_id == user.id)
    )
    meal = result.scalar_one_or_none()
    
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")
    
    update_data = meal_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(meal, field, value)
    
    await db.commit()
    await db.refresh(meal)
    
    return meal


@router.delete("/meals/{meal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_meal(
    user: CurrentUser,
    db: DbSession,
    meal_id: int,
):
    """Delete a meal."""
    result = await db.execute(
        select(Meal).where(Meal.id == meal_id, Meal.user_id == user.id)
    )
    meal = result.scalar_one_or_none()
    
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")
    
    await db.delete(meal)
    await db.commit()


# Water endpoints
@router.get("/water", response_model=List[WaterLogResponse])
async def list_water_logs(
    user: CurrentUser,
    db: DbSession,
    log_date: Optional[date] = None,
):
    """List water logs."""
    query = (
        select(WaterLog)
        .where(WaterLog.user_id == user.id)
        .order_by(WaterLog.log_date.desc(), WaterLog.created_at.desc())
    )
    
    if log_date:
        query = query.where(WaterLog.log_date == log_date)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/water", response_model=WaterLogResponse, status_code=status.HTTP_201_CREATED)
async def log_water(
    user: CurrentUser,
    db: DbSession,
    water_data: WaterLogCreate,
):
    """Log water intake."""
    water_log = WaterLog(
        user_id=user.id,
        glasses=water_data.glasses,
        log_date=water_data.log_date,
    )
    db.add(water_log)
    await db.commit()
    await db.refresh(water_log)
    
    return water_log


@router.get("/water/today", response_model=int)
async def get_today_water(
    user: CurrentUser,
    db: DbSession,
):
    """Get total water intake for today."""
    result = await db.execute(
        select(func.coalesce(func.sum(WaterLog.glasses), 0))
        .where(WaterLog.user_id == user.id, WaterLog.log_date == date.today())
    )
    return result.scalar()


# Daily summary
@router.get("/summary/{summary_date}", response_model=DailyNutritionSummary)
async def get_daily_summary(
    user: CurrentUser,
    db: DbSession,
    summary_date: date,
):
    """Get nutrition summary for a specific date."""
    # Get meals for the day
    result = await db.execute(
        select(Meal).where(Meal.user_id == user.id, Meal.meal_date == summary_date)
    )
    meals = result.scalars().all()
    
    # Calculate totals
    total_calories = sum(m.calories or 0 for m in meals)
    total_protein = sum(m.protein or 0 for m in meals)
    total_carbs = sum(m.carbs or 0 for m in meals)
    total_fat = sum(m.fat or 0 for m in meals)
    total_fiber = sum(m.fiber or 0 for m in meals)
    
    # Get water intake
    water_result = await db.execute(
        select(func.coalesce(func.sum(WaterLog.glasses), 0))
        .where(WaterLog.user_id == user.id, WaterLog.log_date == summary_date)
    )
    water_glasses = water_result.scalar()
    
    # Calculate progress percentages
    def calc_progress(current: float, goal: float) -> float:
        if goal <= 0:
            return 0
        return min(round((current / goal) * 100, 1), 100)
    
    return DailyNutritionSummary(
        date=summary_date,
        total_calories=total_calories,
        total_protein=total_protein,
        total_carbs=total_carbs,
        total_fat=total_fat,
        total_fiber=total_fiber,
        water_glasses=water_glasses,
        meals_count=len(meals),
        calorie_goal=user.daily_calorie_goal,
        protein_goal=user.daily_protein_goal,
        carbs_goal=user.daily_carbs_goal,
        fat_goal=user.daily_fat_goal,
        water_goal=user.daily_water_goal,
        calorie_progress=calc_progress(total_calories, user.daily_calorie_goal),
        protein_progress=calc_progress(total_protein, user.daily_protein_goal),
        carbs_progress=calc_progress(total_carbs, user.daily_carbs_goal),
        fat_progress=calc_progress(total_fat, user.daily_fat_goal),
        water_progress=calc_progress(water_glasses, user.daily_water_goal),
    )
