from fastapi import FastAPI, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import engine, Base, get_db
from database.repositories import SpimexTradingRepository
from schemas import TradingDateResponse, GetDynamicsFilters


app = FastAPI()

def get_user_repo():
    return SpimexTradingRepository()


@app.get('/get_last_trading_dates')
async def get_last_trading_dates(days: int = Query(default=10, gt=0),
                                 session: AsyncSession = Depends(get_db),
                                 repo: SpimexTradingRepository = Depends(get_user_repo)):
    result = await repo.get_last_trading_dates(session, days)
    datas = [TradingDateResponse(date=obj) for obj in result]
    return datas


@app.get('/get_dynamics')
async def get_dynamics(filters: GetDynamicsFilters = Depends(),
                       session: AsyncSession = Depends(get_db),
                       repo: SpimexTradingRepository = Depends(get_user_repo)):
    result = await repo.get_dynamics(
        session,
        **filters.model_dump(exclude_unset=True)
    )
    return result



async def lifespan(app):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
