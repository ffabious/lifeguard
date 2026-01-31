from fastapi import APIRouter

from app.api import users, workouts, nutrition, shopping

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(workouts.router, prefix="/workouts", tags=["workouts"])
api_router.include_router(nutrition.router, prefix="/nutrition", tags=["nutrition"])
api_router.include_router(shopping.router, prefix="/shopping", tags=["shopping"])
