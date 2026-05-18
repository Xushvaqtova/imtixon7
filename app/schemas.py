from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str


class RecipeCreate(BaseModel):
    title: str
    description: str
    cooking_time: int


class RecipeOut(BaseModel):
    id: int
    title: str
    description: str
    cooking_time: int

    class Config:
        orm_mode = True