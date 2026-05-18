from pydantic import BaseModel, EmailStr
from typing import Optional

# Auth tokenlar uchun
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# User sxemalari
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True

# Recipe sxemalari
class RecipeBase(BaseModel):
    title: str
    description: Optional[str] = None
    instructions: str
    cooking_time: int

class RecipeCreate(RecipeBase):
    pass

class RecipeUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    instructions: Optional[str] = None
    cooking_time: Optional[int] = None

class RecipeOut(RecipeBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True