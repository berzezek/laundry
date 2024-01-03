from bson.objectid import ObjectId
from typing import Generic, TypeVar
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorCollection


# Define the model type
ModelType = TypeVar("ModelType", bound=BaseModel)

# Define the schema types for create and update operations
ModelCollectionType = TypeVar("ModelCollectionType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDMongo(Generic[ModelType, ModelCollectionType, UpdateSchemaType]):
    def __init__(self, model: ModelType):
        self.model = model

    async def get_data(self, collection: AsyncIOMotorCollection) -> ModelCollectionType:
        """
        List all of the data in the database.

        The response is unpaginated and limited to 1000 results.
        """
        data = await collection.find().to_list(1000)
        return self.model.model_validate({"customers": data})

    async def get_data_id(
        self, id: str, collection: AsyncIOMotorCollection
    ) -> ModelType:
        if (data := await collection.find_one({"_id": ObjectId(id)})) is not None:
            return self.model.model_validate(data)

    async def create_data(
        self, data: ModelType, collection: AsyncIOMotorCollection
    ) -> ModelType:
        """
        Insert a new record.

        A unique `id` will be created and provided in the response.
        """
        new_data = await collection.insert_one(
            data.model_dump(by_alias=True, exclude=["id"])
        )
        created_data = await collection.find_one({"_id": new_data.inserted_id})
        return self.model.model_validate(created_data)

    async def update_data(
        self, id: str, data: UpdateSchemaType, collection: AsyncIOMotorCollection
    ) -> ModelType:
        """
        Update a record.

        The record is looked up by `id`.
        """
        if (
            updated_data := await collection.update_one(
                {"_id": ObjectId(id)}, {"$set": data.model_dump(by_alias=True)}
            )
        ).modified_count == 1:
            if (updated_data := await collection.find_one({"_id": ObjectId(id)})) is not None:
                return self.model.model_validate(updated_data)
        return None
    
    async def delete_data(
        self, id: str, collection: AsyncIOMotorCollection
    ) -> ModelType:
        """
        Delete a record.

        The record is looked up by `id`.
        """
        if (
            deleted_data := await collection.delete_one(
                {"_id": ObjectId(id)}
            )
        ).deleted_count == 1:
            return True
        return False
    
