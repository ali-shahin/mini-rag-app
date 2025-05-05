from fastapi import FastAPI
from routes import base, data
from contextlib import asynccontextmanager
from db import connect_to_mongo, close_mongo_connection, db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()

app = FastAPI(lifespan=lifespan)

app.include_router(base.base_router)
app.include_router(data.data_router)
