from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
import datetime

from .models import SpimexTradingResults


class BaseRepository:
    """
    Тут можно реализовать базовые методы, но по ТЗ они не нужны(
    """
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
    """
    Репозиторий для модели SpimexTradingResults
    """
    def __init__(self):
        super().__init__(SpimexTradingResults)

    def _apply_filters(self, query, filters):
        """
        Включение необходимых фильтров в query
        """
        oil_id = filters.get('oil_id', None)
        delivery_type_id = filters.get('delivery_type_id', None)
        delivery_basis_id = filters.get('delivery_basis_id', None)
        start_date = filters.get('start_date', None)
        end_date = filters.get('end_date', None)

        if start_date:
            query = query.where(
                self.model.date >= start_date
            )
        if end_date:
            query = query.where(
                self.model.date <= end_date
            )
        if oil_id:
            query = query.where(
                self.model.oil_id() == oil_id
            )
        if delivery_type_id:
            query = query.where(
                self.model.delivery_type_id() == delivery_type_id
            )
        if delivery_basis_id:
            query = query.where(
                self.model.delivery_basis_id() == delivery_basis_id
            )
        return query

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
                           filters: dict
                           ) -> list[SpimexTradingResults]:

        query = select(self.model)
        filters_query = self._apply_filters(query, filters)

        result = await session.execute(filters_query)
        return result.scalars().all()

    async def get_trading_results(self,
                                  session: AsyncSession,
                                  filters: str
                                  ) -> list[SpimexTradingResults]:
        date_query = select(self.model.date).order_by(desc(self.model.date))
        last_date = await session.execute(date_query)
        last_date = last_date.scalars().first()
        all_trades_query = select(self.model).where(
            self.model.date == last_date
        )

        filters_query = self._apply_filters(all_trades_query, filters)

        result = await session.execute(filters_query)
        return result.scalars().all()
