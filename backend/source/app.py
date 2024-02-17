from fastapi import FastAPI
from contextlib import asynccontextmanager
from source.laundry.router import router as laundry_router

app = FastAPI(
    title="Delivery API",
    summary="A simple API to manage delivery",
)

    
api_v1_routers = [laundry_router]

for router in api_v1_routers:
    app.include_router(router, prefix="/api/v1")
