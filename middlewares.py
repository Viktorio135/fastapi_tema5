import json

from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware


class ChachMiddleware(BaseHTTPMiddleware):
    """
    Middleware для кэширования запросов
    """
    async def dispatch(self, request, call_next):
        redis_client = request.app.state.redis_client

        chach_name = f"{request.url.path}?{request.url.query}"

        chach = await redis_client.get(chach_name)

        if chach:
            return Response(
                content=json.loads(chach),
                media_type='application/json'
            )

        response = await call_next(request)

        if hasattr(response, "body"):
            body = response.body
        else:
            body = b"".join([chunk async for chunk in response.body_iterator])

        await redis_client.set(chach_name, json.dumps(body.decode()))

        return Response(
                content=body,
                status_code=response.status_code,
                media_type=response.media_type,
                headers=dict(response.headers)
            )
