from fastapi import FastAPI
from contextlib import asynccontextmanager
from source.laundry.router import router as laundry_router
from source.laundry.schedules import start_schedule

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     try:
#         print("Starting scheduler")
#         await start_schedule()
#         yield
#     finally:
#         pass



app = FastAPI(
    title="Delivery API",
    summary="A simple API to manage delivery",
    # lifespan=lifespan,
)

    
api_v1_routers = [laundry_router]

for router in api_v1_routers:
    app.include_router(router, prefix="/api/v1")

# @app.on_event("startup")
# async def startup():
#     await start_schedule()