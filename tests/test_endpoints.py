import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

from main import app, get_user_repo, get_db
from database.repositories import SpimexTradingRepository


@pytest.fixture
def mock_redis(mocker):
    """
    Мокаем редис
    """
    if not hasattr(app.state, "redis_client"):
        app.state.redis_client = None

    mock_redis = AsyncMock()
    mocker.patch.object(app.state, "redis_client", mock_redis)
    return mock_redis


@pytest.fixture
def mock_repo():
    """
    Мокаем репозиторий БД
    """
    mock_repo = MagicMock(spec=SpimexTradingRepository)
    mock_repo.get_last_trading_dates = AsyncMock(return_value=["2025-04-04"])
    mock_repo.get_dynamics = AsyncMock(return_value=[])
    mock_repo.get_trading_results = AsyncMock(return_value=[])
    return mock_repo


@pytest.fixture
def mock_session():
    """
    Мокаем сессию БД
    """
    mock_session = MagicMock(spec=AsyncSession)
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_result.scalars.return_value.first.return_value = "2025-04-04"
    mock_session.execute.return_value = mock_result
    return mock_session


@pytest_asyncio.fixture
async def async_client(mock_repo, mock_session):
    """
    Фикстура для подгрузки клиена и
    замены зависимостей
    """
    app.dependency_overrides[get_user_repo] = lambda: mock_repo
    app.dependency_overrides[get_db] = lambda: mock_session

    client = AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    )
    yield client
    await client.aclose()
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_last_trading_dates(async_client, mock_repo,
                                      mock_session, mock_redis):
    mock_redis.get.return_value = None
    mock_repo.get_last_trading_dates.return_value = ["2025-04-04"]
    async with async_client as client:
        response = await client.get("/get_last_trading_dates?days=50")

    assert response.status_code == 200
    assert response.json() == ["2025-04-04"]
    mock_repo.get_last_trading_dates.assert_awaited_once_with(mock_session, 50)
