from .BaseRepo import BaseRepo
from models.asset import Asset
from bson import ObjectId


class AssetRepo(BaseRepo):
    def __init__(self, db_client: object):
        super().__init__(db_client)
        self.set_collection("assets")

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self):
        await self.collection.create_index("asset_project_id", unique=False)
        await self.collection.create_index(
            ["asset_project_id", "asset_name"], unique=True
        )

    async def create_asset(self, asset: Asset):
        asset_dict = asset.model_dump(by_alias=True, exclude_none=True)
        result = await self.collection.insert_one(asset_dict)
        asset.id = result.inserted_id
        return asset

    async def get_asset(self, asset_id: str):
        asset = await self.collection.find_one({"_id": ObjectId(asset_id)})
        if asset is None:
            return None

        return Asset(**asset)

    async def get_project_assets(self, project_id: ObjectId, asset_type: str = None):
        assets = await self.collection.find({
            "asset_project_id": project_id,
            "asset_type": asset_type,
        }).to_list(length=None)

        return [Asset(**asset) for asset in assets]
