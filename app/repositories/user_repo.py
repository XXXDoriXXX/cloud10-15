from typing import List, Optional

from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging.decorators import monitor_async
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class UserAlreadyExistsError(Exception):

    pass


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    @monitor_async(operation_name="DB: Create User", log_args=False)
    async def create(self, user_data: UserCreate) -> User:

        db_user = User(**user_data.model_dump())
        try:
            self.session.add(db_user)
            await self.session.commit()
            await self.session.refresh(db_user)
            return db_user
        except IntegrityError as e:
            await self.session.rollback()

            raise UserAlreadyExistsError(f"User with email {user_data.email} already exists.") from e

    @monitor_async(operation_name="DB: Get All Users", log_args=False)
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        stmt = select(User).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    @monitor_async(operation_name="DB: Get User By ID", log_args=True)
    async def get_by_id(self, user_id: int) -> Optional[User]:
        return await self.session.get(User, user_id)

    @monitor_async(operation_name="DB: Update User", log_args=True)
    async def update(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        data = user_data.model_dump(exclude_unset=True)
        if not data:
            return await self.get_by_id(user_id)

        stmt = update(User).where(User.id == user_id).values(**data).returning(User)

        try:
            result = await self.session.execute(stmt)
            await self.session.commit()
            updated_user = result.scalars().first()
            return updated_user
        except IntegrityError as e:
            await self.session.rollback()
            raise UserAlreadyExistsError("Email conflict during update.") from e

    @monitor_async(operation_name="DB: Delete User", log_args=True)
    async def delete(self, user_id: int) -> bool:
        stmt = delete(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0
