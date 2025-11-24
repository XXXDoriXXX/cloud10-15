from sqlalchemy import select, update, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from fastapi import HTTPException


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_data: UserCreate) -> User:
        db_user = User(**user_data.model_dump())
        try:
            self.session.add(db_user)
            await self.session.commit()
            await self.session.refresh(db_user)
            return db_user
        except IntegrityError:
            await self.session.rollback()
            raise HTTPException(status_code=400, detail="User with this email already exists.")

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        stmt = select(User).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_id(self, user_id: int) -> User | None:
        return await self.session.get(User, user_id)

    async def update(self, user_id: int, user_data: UserUpdate) -> User | None:
        data = user_data.model_dump(exclude_unset=True)
        if not data:
            return await self.get_by_id(user_id)

        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(**data)
            .returning(User)
        )

        try:
            result = await self.session.execute(stmt)
            await self.session.commit()
            updated_user = result.scalars().first()
            return updated_user
        except IntegrityError:
            await self.session.rollback()
            raise HTTPException(status_code=400, detail="User with this email already exists.")

    async def delete(self, user_id: int) -> bool:
        stmt = delete(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0