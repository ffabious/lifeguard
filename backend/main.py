import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.router import api_router
from app.bot.handlers import create_bot_application


bot_app = None


async def start_bot():
    """Start the Telegram bot polling in background."""
    global bot_app
    if not settings.telegram_bot_token:
        print("⚠️ No Telegram bot token provided, bot not started")
        return
    
    bot_app = create_bot_application()
    await bot_app.initialize()
    await bot_app.start()
    await bot_app.updater.start_polling(drop_pending_updates=True)
    print("🤖 Telegram bot started in polling mode")


async def stop_bot():
    """Stop the Telegram bot gracefully."""
    global bot_app
    if bot_app:
        await bot_app.updater.stop()
        await bot_app.stop()
        await bot_app.shutdown()
        print("🤖 Telegram bot stopped")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print(f"🚀 Starting {settings.app_name}...")
    
    # Initialize bot if token is provided
    if settings.environment == "development":
        await start_bot()
    else:
        # In production, use webhooks
        # await bot_app.bot.set_webhook(url=f"{settings.api_url}/webhook")
        print("🤖 Telegram bot configured for webhooks")
    
    yield
    
    # Shutdown
    await stop_bot()
    print(f"👋 Shutting down {settings.app_name}...")


app = FastAPI(
    title=settings.app_name,
    description="Fitness & Nutrition Tracking Telegram Bot with Web App",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware for webapp
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.telegram_webapp_url,
        "http://localhost:5173",
        "http://localhost:3000",
        "https://telegram.org",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "app": settings.app_name,
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )
