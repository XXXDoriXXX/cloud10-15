from app.repositories.user_repo import UserRepository
from app.schemas.user import UserCreate, UserRead, UserUpdate
from fastapi import HTTPException


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def create_user(self, user_data: UserCreate) -> UserRead:
        new_user = await self.repository.create(user_data)
        return UserRead.model_validate(new_user)

    async def get_all_users(self, skip: int = 0, limit: int = 100) -> list[UserRead]:
        users = await self.repository.get_all(skip, limit)
        return [UserRead.model_validate(u) for u in users]

    async def get_user_by_id(self, user_id: int) -> UserRead:
        user = await self.repository.get_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return UserRead.model_validate(user)

    async def update_user(self, user_id: int, user_data: UserUpdate) -> UserRead:
        updated_user = await self.repository.update(user_id, user_data)
        if updated_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return UserRead.model_validate(updated_user)

    async def delete_user(self, user_id: int) -> bool:
        deleted = await self.repository.delete(user_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="User not found")
        return deleted