from bson.objectid import ObjectId
from typing import Generic, TypeVar
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import ReturnDocument
from fastapi import HTTPException


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
        data = {
            k: v for k, v in data.model_dump(by_alias=True).items() if v is not None
        }
        if len(data) >= 1:
            update_result = await collection.find_one_and_update(
                {"_id": ObjectId(id)},
                {"$set": data},
                return_document=ReturnDocument.AFTER,
            )
            if update_result is not None:
                return self.model.model_validate(update_result)
            else:
                raise HTTPException(status_code=404, detail=f"Data {id} not found")

        # The update is empty, but we should still return the matching document:
        if (existing_data := await collection.find_one({"_id": id})) is not None:
            return self.model.model_validate(existing_data)

        raise HTTPException(status_code=404, detail=f"Data {id} not found")

    async def delete_data(
        self, id: str, collection: AsyncIOMotorCollection
    ) -> ModelType:
        """
        Delete a record.

        The record is looked up by `id`.
        """
        if (
            deleted_data := await collection.delete_one({"_id": ObjectId(id)})
        ).deleted_count == 1:
            return True
        return False
