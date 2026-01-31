# Lifeguard - Fitness & Nutrition Telegram Bot

A Telegram bot with Mini App for fitness tracking, nutrition logging, and shopping list management.

## Features (MVP)

### Fitness Tracking

- Log workouts (type, duration, exercises, sets/reps)
- View workout history and weekly summary
- Set workout reminders via Telegram notifications

### Nutrition Tracking

- Log meals with calories/macros (manual entry)
- Daily calorie/macro targets and progress
- Water intake tracking

### Shopping/Products

- Create and manage grocery lists
- Quick-add items via bot commands
- Mark items as purchased

## Tech Stack

- **Backend**: Python, FastAPI, python-telegram-bot
- **Frontend**: React, Vite, shadcn/ui, Tailwind CSS
- **Database**: PostgreSQL with SQLAlchemy
- **Auth**: Telegram-only authentication

## Project Structure

```
lifeguard/
├── backend/
│   ├── app/
│   │   ├── api/          # REST API routes
│   │   ├── bot/          # Telegram bot handlers
│   │   ├── core/         # Config, security, deps
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   └── services/     # Business logic
│   ├── alembic/          # Database migrations
│   ├── requirements.txt
│   └── main.py
├── webapp/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   ├── hooks/        # Custom hooks
│   │   ├── lib/          # Utilities
│   │   └── api/          # API client
│   └── package.json
├── docker-compose.yml
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Docker & Docker Compose (optional)

### Quick Start with Docker

```bash
# Copy environment file
cp .env.example .env

# Edit .env with your Telegram bot token
# Get one from @BotFather on Telegram

# Start all services
docker-compose up -d

# Run database migrations
docker-compose exec backend alembic upgrade head
```

### Manual Setup

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start server
uvicorn main:app --reload
```

#### Webapp

```bash
cd webapp

# Install dependencies
npm install

# Start dev server
npm run dev
```

### Create Telegram Bot

1. Open Telegram and search for @BotFather
2. Send `/newbot` and follow the prompts
3. Copy the bot token to your `.env` file
4. Send `/setmenubutton` to @BotFather
5. Select your bot and set the Web App URL

## Development

### API Documentation

Once the backend is running, visit:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## License

MIT
