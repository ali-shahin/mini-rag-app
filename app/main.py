from fastapi import FastAPI
from routes import base, data
from contextlib import asynccontextmanager
from db import connect_to_mongo, close_mongo_connection
from core.config import get_settings
from services.llm.ProviderFactory import ProviderFactory


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.db_client = await connect_to_mongo()
    
    app.generation_client = ProviderFactory.create(get_settings().GENERATION_PROVIDER)
    app.generation_client.set_generation_model(get_settings().GENERATION_MODEL)

    app.embedding_client = ProviderFactory.create(get_settings().EMBEDDING_PROVIDER)
    app.embedding_client.set_embedding_model(get_settings().EMBEDDING_MODEL, get_settings().EMBEDDING_SIZE)

    yield
    await close_mongo_connection()

app = FastAPI(lifespan=lifespan)

# Register routes
app.include_router(base.base_router)
app.include_router(data.data_router)
