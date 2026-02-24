from fastapi import FastAPI

from api.routers.auth import router as auth_router
from api.routers.health import router as health_router

app = FastAPI()
app.include_router(health_router)
app.include_router(auth_router)
