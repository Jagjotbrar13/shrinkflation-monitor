from typing import cast

from fastapi import HTTPException, Request
from redis.exceptions import RedisError
from starlette.middleware.base import BaseHTTPMiddleware

from api.cache import get_redis


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit: int = 120, window_seconds: int = 60):
        super().__init__(app)
        self.limit = limit
        self.window_seconds = window_seconds

    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/health":
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        key = f"ratelimit:{client_ip}:{request.url.path}"
        redis = get_redis()
        try:
            count = cast(int, redis.incr(key))
            if count == 1:
                redis.expire(key, self.window_seconds)
            if count > self.limit:
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
        except RedisError:
            return await call_next(request)
        return await call_next(request)
