from fastapi import FastAPI

from app.api.routes.visualization_routes import (
    router as visualization_router
)

app = FastAPI()

app.include_router(
    visualization_router
)