import asyncio

from sqlalchemy.exc import OperationalError

from app.core.config import settings
from app.core.database import engine
from app.models.user import Base


async def init_db():
    print(f"Connecting to database: {settings.DATABASE_URL}")
    try:
        async with engine.begin() as conn:

            print("Creating database tables...")

            await conn.run_sync(Base.metadata.create_all)
        print("Database initialization complete.")
    except OperationalError as e:
        print(f"!!! Database connection failed. Ensure DB service is running and configured correctly. Error: {e}")


if __name__ == "__main__":

    asyncio.run(init_db())
