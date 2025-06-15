from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="Store Monitoring Service",
    description="APIs for monitoring store uptime/downtime",
    version="1.0"
)
app.include_router(router)