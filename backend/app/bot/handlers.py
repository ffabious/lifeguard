from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import async_session_maker
from app.models.user import User
from app.models.shopping import ShoppingItem


async def get_or_create_user(session: AsyncSession, telegram_user) -> User:
    """Get existing user or create new one from Telegram user data."""
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_user.id)
    )
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            telegram_id=telegram_user.id,
            username=telegram_user.username,
            first_name=telegram_user.first_name or "",
            last_name=telegram_user.last_name,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

    return user


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Get main menu inline keyboard with Web App button."""
    keyboard = [
        [
            InlineKeyboardButton(
                "🏋️ Open Fitness App",
                web_app=WebAppInfo(url=settings.telegram_webapp_url)
            )
        ],
        [
            InlineKeyboardButton("📊 Today's Summary", callback_data="today"),
            InlineKeyboardButton("🛒 Shopping List", callback_data="shopping"),
        ],
        [
            InlineKeyboardButton("⚙️ Settings", callback_data="settings"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command - onboarding and main menu."""
    telegram_user = update.effective_user
    
    async with async_session_maker() as session:
        user = await get_or_create_user(session, telegram_user)
    
    welcome_text = f"""
👋 Welcome to Lifeguard, {user.first_name}!

I'm your personal fitness and nutrition assistant. Here's what I can help you with:

🏋️ **Fitness Tracking**
Log workouts, track exercises, and monitor your progress.

🍎 **Nutrition Tracking**
Log meals, track calories & macros, and stay hydrated.

🛒 **Shopping List**
Keep track of groceries and health products to buy.

Use the buttons below or open the full app for more features!
"""
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="Markdown"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command."""
    help_text = """
🆘 **Lifeguard Help**

**Commands:**
/start - Main menu and open the app
/today - View today's summary
/shop - View shopping list
/add - Quick add items (e.g., /add milk, eggs)
/water - Log water intake
/help - Show this help message

**Quick Actions:**
• Open the Web App for full features
• Use inline buttons for common actions
• Send food items to quick-log meals

Need more help? Open the app and check Settings!
"""
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def today_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /today command - show daily summary."""
    telegram_user = update.effective_user
    
    async with async_session_maker() as session:
        user = await get_or_create_user(session, telegram_user)
        
        # TODO: Fetch actual daily stats from database
        summary_text = f"""
📊 **Today's Summary**

🏋️ **Workouts**
No workouts logged yet.

🍎 **Nutrition**
Calories: 0 / {user.daily_calorie_goal}
Protein: 0g / {user.daily_protein_goal}g
Carbs: 0g / {user.daily_carbs_goal}g
Fat: 0g / {user.daily_fat_goal}g

💧 **Water**
0 / {user.daily_water_goal} glasses

Open the app to log activities and meals!
"""
    
    keyboard = [
        [
            InlineKeyboardButton(
                "📝 Log Activity",
                web_app=WebAppInfo(url=f"{settings.telegram_webapp_url}/workout/new")
            ),
            InlineKeyboardButton(
                "🍽️ Log Meal",
                web_app=WebAppInfo(url=f"{settings.telegram_webapp_url}/nutrition/new")
            ),
        ],
        [
            InlineKeyboardButton("💧 +1 Water", callback_data="water_add"),
        ],
    ]
    
    await update.message.reply_text(
        summary_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


async def shop_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /shop command - show shopping list."""
    telegram_user = update.effective_user
    
    async with async_session_maker() as session:
        user = await get_or_create_user(session, telegram_user)
        
        result = await session.execute(
            select(ShoppingItem)
            .where(ShoppingItem.user_id == user.id)
            .where(ShoppingItem.is_purchased == False)
            .order_by(ShoppingItem.category, ShoppingItem.created_at.desc())
        )
        items = result.scalars().all()
    
    if not items:
        text = "🛒 Your shopping list is empty!\n\nUse /add item1, item2 to add items."
    else:
        text = "🛒 **Shopping List**\n\n"
        for item in items:
            quantity_str = f" ({item.quantity})" if item.quantity else ""
            text += f"• {item.name}{quantity_str}\n"
        text += f"\n📦 {len(items)} items pending"
    
    keyboard = [
        [
            InlineKeyboardButton(
                "📝 Manage List",
                web_app=WebAppInfo(url=f"{settings.telegram_webapp_url}/shopping")
            ),
        ],
    ]
    
    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /add command - quick add shopping items."""
    telegram_user = update.effective_user
    
    if not context.args:
        await update.message.reply_text(
            "Usage: /add item1, item2, item3\n\nExample: /add milk, eggs, bread"
        )
        return
    
    # Parse items (comma or space separated)
    items_text = " ".join(context.args)
    items = [item.strip() for item in items_text.split(",") if item.strip()]
    
    if not items:
        await update.message.reply_text("Please specify items to add.")
        return
    
    async with async_session_maker() as session:
        user = await get_or_create_user(session, telegram_user)
        
        for item_name in items:
            item = ShoppingItem(
                user_id=user.id,
                name=item_name,
            )
            session.add(item)
        
        await session.commit()
    
    await update.message.reply_text(
        f"✅ Added {len(items)} item(s) to your shopping list:\n" +
        "\n".join(f"• {item}" for item in items)
    )


async def water_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /water command - log water intake."""
    telegram_user = update.effective_user
    
    glasses = 1
    if context.args:
        try:
            glasses = int(context.args[0])
        except ValueError:
            pass
    
    async with async_session_maker() as session:
        from app.models.nutrition import WaterLog
        from datetime import date
        
        user = await get_or_create_user(session, telegram_user)
        
        # Add water log
        water_log = WaterLog(
            user_id=user.id,
            glasses=glasses,
            log_date=date.today(),
        )
        session.add(water_log)
        await session.commit()
        
        # Get total for today
        from sqlalchemy import func
        result = await session.execute(
            select(func.sum(WaterLog.glasses))
            .where(WaterLog.user_id == user.id)
            .where(WaterLog.log_date == date.today())
        )
        total = result.scalar() or 0
    
    await update.message.reply_text(
        f"💧 Logged {glasses} glass(es) of water!\n\n"
        f"Today's total: {total} / {user.daily_water_goal} glasses"
    )


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle callback queries from inline buttons."""
    query = update.callback_query
    await query.answer()
    
    telegram_user = update.effective_user
    
    if query.data == "today":
        # Redirect to today command
        await today_command(update, context)
    
    elif query.data == "shopping":
        await shop_command(update, context)
    
    elif query.data == "water_add":
        async with async_session_maker() as session:
            from app.models.nutrition import WaterLog
            from datetime import date
            
            user = await get_or_create_user(session, telegram_user)
            
            water_log = WaterLog(
                user_id=user.id,
                glasses=1,
                log_date=date.today(),
            )
            session.add(water_log)
            await session.commit()
            
            from sqlalchemy import func
            result = await session.execute(
                select(func.sum(WaterLog.glasses))
                .where(WaterLog.user_id == user.id)
                .where(WaterLog.log_date == date.today())
            )
            total = result.scalar() or 0
        
        await query.edit_message_text(
            f"💧 +1 glass of water!\n\nToday's total: {total} glasses",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💧 +1 More", callback_data="water_add")],
                [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")],
            ])
        )
    
    elif query.data == "menu":
        await query.edit_message_text(
            "🏠 Main Menu\n\nChoose an option below:",
            reply_markup=get_main_menu_keyboard()
        )
    
    elif query.data == "settings":
        await query.edit_message_text(
            "⚙️ **Settings**\n\nOpen the app to manage your goals and preferences.",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "⚙️ Open Settings",
                        web_app=WebAppInfo(url=f"{settings.telegram_webapp_url}/settings")
                    )
                ],
                [InlineKeyboardButton("🔙 Back", callback_data="menu")],
            ]),
            parse_mode="Markdown"
        )


def create_bot_application() -> Application:
    """Create and configure the Telegram bot application."""
    application = Application.builder().token(settings.telegram_bot_token).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("today", today_command))
    application.add_handler(CommandHandler("shop", shop_command))
    application.add_handler(CommandHandler("add", add_command))
    application.add_handler(CommandHandler("water", water_command))
    application.add_handler(CallbackQueryHandler(callback_handler))
    
    return application
