# ruff: noqa: ANN401

from datetime import datetime, timezone
from typing import Any, Dict, List

from motor.motor_asyncio import (
    AsyncIOMotorCollection,
    AsyncIOMotorDatabase,
)
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.results import DeleteResult, InsertOneResult

from server.constants.error_messages import (
    DEFAULT_DUPLICATE_MESSAGE,
    DUPLICATE_ERROR_MESSAGES,
)
from server.enums.http_error_code_enum import HTTPErrorCode
from server.helpers.custom_graphql_exception_helper import (
    CustomGraphQLExceptionHelper,
)
from server.helpers.logger_helper import LoggerHelper


class MongoHelper:
    """MongoHelper ASYNC para FastAPI / Ariadne (Motor)"""

    def __init__(
        self,
        db: AsyncIOMotorDatabase[dict[str, Any]],
        allowed_collections: set[str] | None = None,
    ) -> None:
        self.db = db
        self.allowed_collections = allowed_collections
        LoggerHelper.success("MongoHelper initialized with database: " + db.name)

    # --------------------------------------------------
    # Internos
    # --------------------------------------------------

    def _check_collection_allowed(self, collection_name: str) -> None:
        if self.allowed_collections and collection_name not in self.allowed_collections:
            raise CustomGraphQLExceptionHelper(
                f"Acceso a colección '{collection_name}' no permitido",
                HTTPErrorCode.BAD_REQUEST,
            )

    def get_collection(self, name: str) -> AsyncIOMotorCollection[dict[str, Any]]:
        self._check_collection_allowed(name)
        return self.db[name]

    # --------------------------------------------------
    # Índices
    # --------------------------------------------------

    async def create_index(
        self,
        collection_name: str,
        keys: list[tuple[str, int | str]],
        name: str | None = None,
        **kwargs: Any,
    ) -> str:
        collection = self.get_collection(collection_name)

        if name:
            kwargs["name"] = name

        try:
            index_name: str = await collection.create_index(keys, **kwargs)
            LoggerHelper.info(f"Índice creado: {index_name} en {collection_name}")
            return index_name
        except PyMongoError as e:
            LoggerHelper.error(f"No se pudo crear índice en {collection_name}: {e}")
            raise

    async def create_ttl_index(
        self,
        collection_name: str,
        field_name: str,
        expire_seconds: int,
    ) -> str:
        return await self.create_index(
            collection_name=collection_name,
            keys=[(field_name, 1)],
            expireAfterSeconds=expire_seconds,
            name=f"{field_name}_ttl_idx",
        )

    # --------------------------------------------------
    # CRUD
    # --------------------------------------------------

    async def insert_one(
        self,
        collection_name: str,
        document: dict[str, Any],
        **kwargs: Any,
    ) -> InsertOneResult:
        collection = self.get_collection(collection_name)

        now = datetime.now(timezone.utc)
        document.setdefault("created_at", now)
        document.setdefault("updated_at", now)

        try:
            result = await collection.insert_one(document, **kwargs)
            return result
        except DuplicateKeyError:
            message = DUPLICATE_ERROR_MESSAGES.get(collection_name, DEFAULT_DUPLICATE_MESSAGE)
            raise CustomGraphQLExceptionHelper(
                message,
                HTTPErrorCode.CONFLICT,
                details={"collection": collection_name},
            )
        except PyMongoError as e:
            raise CustomGraphQLExceptionHelper(
                f"Error al insertar documento: {e}",
                HTTPErrorCode.BAD_REQUEST,
            )

    async def find_one(
        self,
        collection_name: str,
        filter_: Dict[str, Any],
        projection: Dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Dict[str, Any] | None:
        collection = self.get_collection(collection_name)

        try:
            fetched: Dict[str, Any] | None = await collection.find_one(filter_, projection, **kwargs)
            return fetched
        except PyMongoError as e:
            raise CustomGraphQLExceptionHelper(
                f"Error al buscar documento: {e}",
                HTTPErrorCode.BAD_REQUEST,
            )

    async def find_many(
        self,
        collection_name: str,
        filter_: dict[str, Any],
        projection: dict[str, Any] | None = None,
        skip: int = 0,
        limit: int = 0,
        sort: list[tuple[str, int | str]] | None = None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        collection = self.get_collection(collection_name)

        try:
            cursor = collection.find(filter_, projection, **kwargs)

            if sort:
                cursor = cursor.sort(sort)
            if skip:
                cursor = cursor.skip(skip)
            if limit:
                cursor = cursor.limit(limit)
            result: List[Dict[str, Any]] = await cursor.to_list(length=limit or None)
            return result
        except PyMongoError as e:
            raise CustomGraphQLExceptionHelper(
                f"Error al buscar documentos: {e}",
                HTTPErrorCode.BAD_REQUEST,
            )

    async def update_one(
        self,
        collection_name: str,
        filter_: dict[str, Any],
        update: dict[str, Any],
        upsert: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        collection = self.get_collection(collection_name)

        # Aseguramos que siempre se actualice updated_at
        update.setdefault("$set", {})
        update["$set"]["updated_at"] = datetime.now(timezone.utc)

        try:
            # Usamos find_one_and_update para devolver el documento actualizado
            updated_doc: Dict[str, Any] = await collection.find_one_and_update(
                filter_,
                update,
                upsert=upsert,
                return_document=ReturnDocument.AFTER,  # devuelve después de actualizar
                **kwargs,
            )

            if not updated_doc:
                # Si no se encontró nada
                raise CustomGraphQLExceptionHelper(
                    "Documento no encontrado.",
                    HTTPErrorCode.NOT_FOUND,
                    details={"collection": collection_name},
                )

            return updated_doc

        except DuplicateKeyError:
            message = DUPLICATE_ERROR_MESSAGES.get(collection_name, DEFAULT_DUPLICATE_MESSAGE)
            raise CustomGraphQLExceptionHelper(
                message,
                HTTPErrorCode.CONFLICT,
                details={"collection": collection_name},
            )

        except PyMongoError as e:
            raise CustomGraphQLExceptionHelper(
                f"Error al actualizar documento: {e}",
                HTTPErrorCode.BAD_REQUEST,
            )

    async def delete_one(
        self,
        collection_name: str,
        filter_: dict[str, Any],
        **kwargs: Any,
    ) -> DeleteResult:
        collection = self.get_collection(collection_name)

        try:
            return await collection.delete_one(filter_, **kwargs)
        except PyMongoError as e:
            raise CustomGraphQLExceptionHelper(
                f"Error al eliminar documento: {e}",
                HTTPErrorCode.BAD_REQUEST,
            )

    async def delete_many(
        self,
        collection_name: str,
        filter_: dict[str, Any],
        **kwargs: Any,
    ) -> DeleteResult:
        collection = self.get_collection(collection_name)

        try:
            return await collection.delete_many(filter_, **kwargs)
        except PyMongoError as e:
            raise CustomGraphQLExceptionHelper(
                f"Error al eliminar documentos: {e}",
                HTTPErrorCode.BAD_REQUEST,
            )

    # --------------------------------------------------
    # Aggregation
    # --------------------------------------------------

    async def aggregate(
        self,
        collection_name: str,
        pipeline: list[dict[str, Any]],
        allow_disk_use: bool = False,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """
        Ejecuta un aggregation pipeline y devuelve la lista de documentos.
        """
        collection = self.get_collection(collection_name)

        try:
            cursor = collection.aggregate(
                pipeline,
                allowDiskUse=allow_disk_use,
                **kwargs,
            )
            return [doc async for doc in cursor]

        except PyMongoError as e:
            raise CustomGraphQLExceptionHelper(
                f"Error en aggregation: {e}",
                HTTPErrorCode.BAD_REQUEST,
                details={
                    "collection": collection_name,
                    "pipeline": pipeline,
                },
            )
