from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db_session
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.repositories.user_repo import UserRepository
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users (SQL CRUD)"])

def get_user_service(session: AsyncSession = Depends(get_db_session)):
    repo = UserRepository(session)
    return UserService(repo)

@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    service: UserService = Depends(get_user_service)
):
    return await service.create_user(user_data)

@router.get("/", response_model=list[UserRead])
async def read_users(
    skip: int = 0, limit: int = 100,
    service: UserService = Depends(get_user_service)
):

    return await service.get_all_users(skip, limit)

@router.get("/{user_id}", response_model=UserRead)
async def read_user(
    user_id: int,
    service: UserService = Depends(get_user_service)
):

    return await service.get_user_by_id(user_id)

@router.put("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    service: UserService = Depends(get_user_service)
):

    return await service.update_user(user_id, user_data)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    service: UserService = Depends(get_user_service)
):
    await service.delete_user(user_id)
    return