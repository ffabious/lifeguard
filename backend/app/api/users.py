from fastapi import APIRouter

from app.core.deps import CurrentUser, DbSession
from app.schemas.user import UserResponse, UserUpdate, UserGoals

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(user: CurrentUser):
    """Get current user information."""
    return user


@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    user: CurrentUser,
    db: DbSession,
    user_update: UserUpdate,
):
    """Update current user information."""
    update_data = user_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    await db.commit()
    await db.refresh(user)
    
    return user


@router.get("/me/goals", response_model=UserGoals)
async def get_user_goals(user: CurrentUser):
    """Get user's daily goals."""
    return UserGoals(
        daily_calorie_goal=user.daily_calorie_goal,
        daily_protein_goal=user.daily_protein_goal,
        daily_carbs_goal=user.daily_carbs_goal,
        daily_fat_goal=user.daily_fat_goal,
        daily_water_goal=user.daily_water_goal,
    )


@router.put("/me/goals", response_model=UserGoals)
async def update_user_goals(
    user: CurrentUser,
    db: DbSession,
    goals: UserGoals,
):
    """Update user's daily goals."""
    user.daily_calorie_goal = goals.daily_calorie_goal
    user.daily_protein_goal = goals.daily_protein_goal
    user.daily_carbs_goal = goals.daily_carbs_goal
    user.daily_fat_goal = goals.daily_fat_goal
    user.daily_water_goal = goals.daily_water_goal
    
    await db.commit()
    await db.refresh(user)
    
    return goals
