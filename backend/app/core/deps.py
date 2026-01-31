from typing import Annotated, Optional

from fastapi import Depends, HTTPException, Header, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_telegram_user_from_init_data
from app.models.user import User


async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    x_telegram_init_data: Annotated[Optional[str], Header()] = None,
) -> User:
    """
    Get current user from Telegram init data.
    
    The webapp sends init data in the X-Telegram-Init-Data header.
    We validate it and return the corresponding user.
    """
    if not x_telegram_init_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Telegram init data required",
        )

    telegram_user = get_telegram_user_from_init_data(x_telegram_init_data)
    if not telegram_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Telegram init data",
        )

    telegram_id = telegram_user.get("id")
    if not telegram_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found in init data",
        )

    # Get or create user
    result = await db.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        # Create new user
        user = User(
            telegram_id=telegram_id,
            username=telegram_user.get("username"),
            first_name=telegram_user.get("first_name", ""),
            last_name=telegram_user.get("last_name"),
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return user


# Type alias for dependency injection
CurrentUser = Annotated[User, Depends(get_current_user)]
DbSession = Annotated[AsyncSession, Depends(get_db)]
