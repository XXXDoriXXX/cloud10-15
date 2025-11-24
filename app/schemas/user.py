from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None

class UserCreate(UserBase):
    pass

class UserUpdate(UserBase):
    email: EmailStr | None = None
    is_active: bool | None = None

class UserRead(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True