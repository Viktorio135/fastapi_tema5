import json

from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware


class CacheMiddleware(BaseHTTPMiddleware):
    """
    Middleware для кэширования запросов
    """
    async def dispatch(self, request, call_next):
        redis_client = request.app.state.redis_client

        cache_name = f"{request.url.path}?{request.url.query}"

        cache = await redis_client.get(cache_name)
        if cache:
            return Response(
                content=json.loads(cache),
                media_type='application/json'
            )

        response = await call_next(request)

        if hasattr(response, "body"):
            body = response.body
        else:
            body = b"".join([chunk async for chunk in response.body_iterator])

        await redis_client.set(cache_name, json.dumps(body.decode()))

        return Response(
                content=body,
                status_code=response.status_code,
                media_type=response.media_type,
                headers=dict(response.headers)
            )
