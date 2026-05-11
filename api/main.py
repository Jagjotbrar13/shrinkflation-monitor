import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.auth.router import router as auth_router
from api.config import get_settings
from api.middleware.logging import RequestLoggingMiddleware
from api.middleware.rate_limit import RateLimitMiddleware
from api.routes.alerts import router as alerts_router
from api.routes.insights import router as insights_router
from api.routes.products import router as products_router
from api.routes.public import router as public_router
from api.routes.reports import router as reports_router
from api.routes.watchlist import router as watchlist_router

settings = get_settings()

if settings.sentry_dsn:
    sentry_sdk.init(dsn=settings.sentry_dsn, traces_sample_rate=0.1)

app = FastAPI(
    title="Grocery Shrinkflation Monitor API",
    version="0.1.0",
    description="Tracks price and package-size changes across Canadian grocery stores.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^http://(localhost|127\.0\.0\.1):30\d{2}$",
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware)

app.include_router(auth_router)
app.include_router(products_router)
app.include_router(public_router)
app.include_router(watchlist_router)
app.include_router(alerts_router)
app.include_router(insights_router)
app.include_router(reports_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.app_env}
