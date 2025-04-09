from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import datetime

from .models import SpimexTradingResults


class BaseRepository:
    def __init__(self, model):
        self.model = model

    async def get(self, session: AsyncSession):
        result = await session.execute(
            select(self.model)
        ).scalars().all()
        return result

    async def create(self, session: AsyncSession, data: dict):
        pass

    async def delete(self, session: AsyncSession, id: int):
        pass

    async def update(self, session: AsyncSession, id: int, data: dict):
        pass


class SpimexTradingRepository(BaseRepository):
    def __init__(self):
        super().__init__(SpimexTradingResults)

    async def get_last_trading_dates(self,
                                     session: AsyncSession,
                                     days: int
                                     ) -> list[SpimexTradingResults]:
        date = datetime.datetime.now() - datetime.timedelta(days=days)
        result = await session.execute(
            select(self.model.date)
            .where(self.model.date >= date)
            .order_by(self.model.date)
            .distinct()
        )
        return result.scalars().all()

    async def get_dynamics(self,
                           session: AsyncSession,
                           start_date: datetime.date,
                           end_date: datetime.date,
                           oil_id: str = None,
                           delivery_type_id: str = None,
                           delivery_basis_id: str = None
                           ) -> list[SpimexTradingResults]:
        query = select(self.model).where(
                and_(
                    self.model.date >= start_date,
                    self.model.date <= end_date
                )
        )
        
        if oil_id:
            query = query.where(self.model.oil_id() == oil_id)
        if delivery_type_id:
            query = query.where(self.model.delivery_type_id() == delivery_type_id)
        if delivery_basis_id:
            query = query.where(self.model.delivery_basis_id() == delivery_basis_id)
        result = await session.execute(query)
        return result.scalars().all()
