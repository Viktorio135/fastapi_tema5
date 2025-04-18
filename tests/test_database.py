import datetime
import pytest
import pytest_asyncio


from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


from database.repositories import SpimexTradingRepository
from database.models import SpimexTradingResults, Base


engine = create_async_engine("sqlite+aiosqlite:///:memory:")
async_session = async_sessionmaker(engine, expire_on_commit=False)


@pytest_asyncio.fixture(scope='module')
async def get_db():
    async with async_session() as session:
        today = datetime.date.today()
        session.add_all([
            SpimexTradingResults(
                date=today,
                oil_id=1,
                delivery_type_id=2,
                delivery_basis_id=3
            ),
            SpimexTradingResults(
                date=today - datetime.timedelta(days=1),
                oil_id=1,
                delivery_type_id=2,
                delivery_basis_id=3
            ),
            SpimexTradingResults(
                date=today - datetime.timedelta(days=11),
                oil_id=3,
                delivery_type_id=2,
                delivery_basis_id=3
            ),
        ])
        await session.commit()
        yield session


@pytest_asyncio.fixture(scope='module', autouse=True)
async def create_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture
def repo():
    return SpimexTradingRepository()


@pytest.mark.asyncio
async def test_get_last_trading_dates(get_db, repo):
    result = await repo.get_last_trading_dates(
        session=get_db,
        days=9
    )

    assert len(result) == 2


@pytest.mark.asyncio
async def test_get_dynamics(get_db, repo):
    result = await repo.get_dynamics(
        session=get_db,
        filters={
            "start_date": datetime.date.today() - datetime.timedelta(days=11),
            "end_date": datetime.date.today()
        }
    )

    assert len(result) == 3


@pytest.mark.asyncio
async def test_get_trading_results(get_db, repo):
    result = await repo.get_trading_results(
        session=get_db,
    )
    print(result)
    assert len(result) == 1
