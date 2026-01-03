import asyncio
from database.database import engine
from schemas.schemas import Base

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Таблицы созданы/проверены")

if __name__ == "__main__":
    asyncio.run(init_db())