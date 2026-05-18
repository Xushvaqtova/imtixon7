from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)

    recipes = relationship("Recipe", back_populates="owner")


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
    cooking_time = Column(Integer)

    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="recipes")