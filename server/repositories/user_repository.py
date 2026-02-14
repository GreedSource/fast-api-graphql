# server/repositories/user_repository.py
from bson import ObjectId

from server.db.mongo import get_mongo_db
from server.decorators.singleton_decorator import singleton
from server.helpers.logger_helper import LoggerHelper
from server.helpers.mongo_helper import MongoHelper


@singleton
class UserRepository:
    def __init__(self):
        self.__mongo = MongoHelper(
            db=get_mongo_db(),
            allowed_collections={"users"},
        )
        LoggerHelper.info("UserRepository initialized")

    async def create(self, user_data: dict):
        return await self.__mongo.insert_one("users", user_data)

    async def find_by_email(self, email: str):
        return await self.__mongo.find_one("users", {"email": email})

    async def find_by_id(self, user_id: str):
        return await self.__mongo.find_one("users", {"_id": ObjectId(user_id)})

    async def find_all(self):
        return await self.__mongo.find_many("users", {})

    # ----------------------
    # Aggregate: user + role
    # ----------------------
    async def aggregate_users_with_roles(self):
        pipeline = [
            {"$addFields": {"roleIdObj": {"$toObjectId": "$role_id"}}},
            {
                "$lookup": {
                    "from": "roles",
                    "localField": "roleIdObj",
                    "foreignField": "_id",
                    "as": "role",
                }
            },
            {"$unwind": {"path": "$role", "preserveNullAndEmptyArrays": True}},
            {
                "$addFields": {
                    "_id": {"$toString": "$_id"},
                    "role._id": {"$toString": "$role._id"},
                }
            },
            {
                "$project": {
                    # USER
                    "password": 0,
                    "role_id": 0,
                    "created_at": 0,
                    "updated_at": 0,
                    # ROLE
                    "role.created_at": 0,
                    "role.updated_at": 0,
                    "role.permissions": 0,
                    # TEMPORALES
                    "roleIdObj": 0,
                }
            },
        ]

        return await self.__mongo.aggregate("users", pipeline)

    async def aggregate_user_with_role(self, user_id: str):
        pipeline = [
            # Convertimos role_id (string) a ObjectId
            {"$addFields": {"roleIdObj": {"$toObjectId": "$role_id"}}},
            # Solo el usuario que queremos
            {"$match": {"_id": ObjectId(user_id)}},
            # Lookup usando roleIdObj
            {
                "$lookup": {
                    "from": "roles",
                    "localField": "roleIdObj",  # <--- usar el ObjectId
                    "foreignField": "_id",
                    "as": "role",
                }
            },
            # Unwind para tener un solo objeto en vez de lista
            {"$unwind": {"path": "$role", "preserveNullAndEmptyArrays": True}},
            # Opcional: remover el campo temporal roleIdObj
            {"$project": {"roleIdObj": 0}},
        ]
        results = await self.__mongo.aggregate("users", pipeline)
        return results[0] if results else None

    async def aggregate_user_with_role_permissions(self, user_id: str):
        pipeline = [
            # 1️⃣ Convertir role_id (string) → ObjectId
            {"$addFields": {"roleIdObj": {"$toObjectId": "$role_id"}}},
            # 2️⃣ Filtrar usuario
            {"$match": {"_id": ObjectId(user_id)}},
            # 3️⃣ Lookup del rol
            {
                "$lookup": {
                    "from": "roles",
                    "localField": "roleIdObj",
                    "foreignField": "_id",
                    "as": "role",
                }
            },
            {"$unwind": {"path": "$role", "preserveNullAndEmptyArrays": True}},
            # 4️⃣ Lookup de permisos
            {
                "$lookup": {
                    "from": "permissions",
                    "localField": "role.permissions",
                    "foreignField": "_id",
                    "as": "role.permissions",
                }
            },
            # 5️⃣ Lookup módulos y actions
            {
                "$lookup": {
                    "from": "modules",
                    "localField": "role.permissions.module_id",
                    "foreignField": "_id",
                    "as": "modules",
                }
            },
            {
                "$lookup": {
                    "from": "actions",
                    "localField": "role.permissions.action_id",
                    "foreignField": "_id",
                    "as": "actions",
                }
            },
            # 6️⃣ Mapear permisos (action + type)
            {
                "$addFields": {
                    "role.permissions": {
                        "$map": {
                            "input": "$role.permissions",
                            "as": "perm",
                            "in": {
                                "action": {
                                    "$arrayElemAt": [
                                        {
                                            "$map": {
                                                "input": {
                                                    "$filter": {
                                                        "input": "$actions",
                                                        "as": "a",
                                                        "cond": {
                                                            "$eq": [
                                                                "$$a._id",
                                                                "$$perm.action_id",
                                                            ]
                                                        },
                                                    }
                                                },
                                                "as": "f",
                                                "in": "$$f.key",
                                            }
                                        },
                                        0,
                                    ]
                                },
                                "type": {
                                    "$arrayElemAt": [
                                        {
                                            "$map": {
                                                "input": {
                                                    "$filter": {
                                                        "input": "$modules",
                                                        "as": "m",
                                                        "cond": {
                                                            "$eq": [
                                                                "$$m._id",
                                                                "$$perm.module_id",
                                                            ]
                                                        },
                                                    }
                                                },
                                                "as": "f",
                                                "in": "$$f.key",
                                            }
                                        },
                                        0,
                                    ]
                                },
                            },
                        }
                    },
                    # ✅ CAST DE IDS A STRING
                    "_id": {"$toString": "$_id"},
                    "role._id": {"$toString": "$role._id"},
                }
            },
            # 7️⃣ Project final (limpio)
            {
                "$project": {
                    # USER
                    "password": 0,
                    "role_id": 0,
                    "created_at": 0,
                    "updated_at": 0,
                    # ROLE
                    "role.created_at": 0,
                    "role.updated_at": 0,
                    # TEMPORALES
                    "roleIdObj": 0,
                    "modules": 0,
                    "actions": 0,
                }
            },
        ]

        results = await self.__mongo.aggregate("users", pipeline)
        return results[0] if results else None

    async def update(self, user_id: str, update_data: dict):
        return await self.__mongo.update_one(
            "users",
            {"_id": ObjectId(user_id)},
            {"$set": update_data},
        )

    async def delete(self, user_id: str):
        return await self.__mongo.delete_one(
            "users",
            {"_id": ObjectId(user_id)},
        )
