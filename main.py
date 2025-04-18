from fastapi import FastAPI, Query, Depends
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger


from middlewares import CacheMiddleware
from database.database import engine, Base, get_db
from database.repositories import SpimexTradingRepository
from schemas import GetDynamicsFilters, GetTradingResults


@asynccontextmanager
async def lifespan(app):
    """
    Создание моделей базы, подключение Redis и определение шедулера
    """
    global redis_client

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    app.state.redis_client = Redis()

    scheduler.add_job(
        clear_cache,
        trigger=CronTrigger(hour=14, minute=11)
    )

    scheduler.start()

    yield

    if scheduler.running:
        scheduler.shutdown()
    if app.state.redis_client:
        await app.state.redis_client.close()


app = FastAPI(lifespan=lifespan)
redis_client: Redis | None = None
scheduler = AsyncIOScheduler()

app.add_middleware(CacheMiddleware)


async def clear_cache():
    """
    Очистка кэша
    """
    try:
        if app.state.redis_client:
            await app.state.redis_client.flushdb()
    except Exception:
        pass


def get_user_repo():
    return SpimexTradingRepository()


@app.get('/get_last_trading_dates')
async def get_last_trading_dates(days: int = Query(default=10, gt=0),
                                 session: AsyncSession = Depends(get_db),
                                 repo: SpimexTradingRepository = Depends(
                                     get_user_repo
                                 )):
    result = await repo.get_last_trading_dates(session, days)
    return result


@app.get('/get_dynamics')
async def get_dynamics(filters: GetDynamicsFilters = Depends(),
                       session: AsyncSession = Depends(get_db),
                       repo: SpimexTradingRepository = Depends(get_user_repo)):
    result = await repo.get_dynamics(
        session,
        filters.model_dump(exclude_none=True)
    )
    return result


@app.get('/get_trading_results')
async def get_trading_results(filters: GetTradingResults = Depends(),
                              session: AsyncSession = Depends(get_db),
                              repo: SpimexTradingRepository = Depends(
                                  get_user_repo
                              )):
    result = await repo.get_trading_results(
        session,
        filters.model_dump(exclude_none=True)
    )

    return result
