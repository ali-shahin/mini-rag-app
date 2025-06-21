from fastapi import FastAPI
from contextlib import asynccontextmanager
from core.config import get_settings
from db import connect_to_mongo, close_mongo_connection
from services.llm.ProviderFactory import ProviderFactory as LLMProviderFactory
from services.vectordb.ProviderFactory import ProviderFactory as VectorDBProviderFactory
from routes.v1 import all_routers as v1_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.db_client = await connect_to_mongo()
    
    app.generation_client = LLMProviderFactory.create(get_settings().GENERATION_PROVIDER)
    app.generation_client.set_generation_model(get_settings().GENERATION_MODEL)

    app.embedding_client = LLMProviderFactory.create(get_settings().EMBEDDING_PROVIDER)
    app.embedding_client.set_embedding_model(get_settings().EMBEDDING_MODEL, get_settings().EMBEDDING_SIZE)

    app.vector_db_client = VectorDBProviderFactory.create(get_settings().VECTOR_DB_PROVIDER)
    app.vector_db_client.connect()

    yield
    await close_mongo_connection()
    app.vector_db_client.disconnect()

app = FastAPI(lifespan=lifespan)

# Register routes
for route in v1_routes:
    app.include_router(route)