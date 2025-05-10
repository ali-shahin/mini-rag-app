from .BaseRepo import BaseRepo
from models.dataChunk import DataChunk
from bson import ObjectId


class DataChunkRepo(BaseRepo):
    def __init__(self, db_client: object):
        super().__init__(db_client)
        self.set_collection("chunks")

    async def create_chunk(self, datachunk: DataChunk):
        chunk_dict = datachunk.model_dump(by_alias=True, exclude_none=True)
        result = await self.collection.insert_one(chunk_dict)
        datachunk.id = result.inserted_id
        return datachunk

    async def get_chunk(self, chunk_id: str):
        chunk = await self.collection.find_one({"_id": ObjectId(chunk_id)})
        if chunk is None:
            return None

        return DataChunk(**chunk)

    async def insert_chunks(self, chunks: list[DataChunk], batch_size: int = 100):
        batches = [
            chunks[i:i + batch_size]
            for i in range(0, len(chunks), batch_size)
        ]

        for batch in batches:
            data = [
                chunk.model_dump(by_alias=True, exclude_none=True)
                for chunk in batch
            ]

            await self.collection.insert_many(data)

        return len(chunks)

    async def get_project_chunks(self, project_id: ObjectId, page: int = 1, limit: int = 10):
        curser = self.collection.find({"chunk_project_id": project_id}).skip(
            (page - 1) * limit).limit(limit)
        chunks = []
        async for chunk in curser:
            chunks.append(DataChunk(**chunk))

        return chunks, len(chunks)

    async def delete_chunks(self, project_id: ObjectId):
        result = await self.collection.delete_many({"chunk_project_id": project_id})
        return result.deleted_count
