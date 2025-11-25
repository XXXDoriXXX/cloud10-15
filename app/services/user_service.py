from fastapi import HTTPException, status

from app.core.logging.decorators import monitor_async
from app.repositories.user_repo import UserAlreadyExistsError, UserRepository
from app.schemas.user import UserCreate, UserRead, UserUpdate


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    @monitor_async(operation_name="SERVICE: Create User")
    async def create_user(self, user_data: UserCreate) -> UserRead:
        try:
            new_user = await self.repository.create(user_data)
            return UserRead.model_validate(new_user)
        except UserAlreadyExistsError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    @monitor_async(operation_name="SERVICE: Get All Users")
    async def get_all_users(self, skip: int = 0, limit: int = 100) -> list[UserRead]:
        users = await self.repository.get_all(skip, limit)
        return [UserRead.model_validate(u) for u in users]

    @monitor_async(operation_name="SERVICE: Get User By ID")
    async def get_user_by_id(self, user_id: int) -> UserRead:
        user = await self.repository.get_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return UserRead.model_validate(user)

    @monitor_async(operation_name="SERVICE: Update User")
    async def update_user(self, user_id: int, user_data: UserUpdate) -> UserRead:
        try:
            updated_user = await self.repository.update(user_id, user_data)
            if updated_user is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
            return UserRead.model_validate(updated_user)
        except UserAlreadyExistsError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    @monitor_async(operation_name="SERVICE: Delete User")
    async def delete_user(self, user_id: int) -> bool:
        deleted = await self.repository.delete(user_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return deleted
