from sqlalchemy.orm import Session
from . import models, schemas, security


def create_user(db: Session, user: schemas.UserCreate):
    hashed_pwd = security.get_password_hash(user.password)
    db_user = models.User(username=user.username, email=user.email, hashed_password=hashed_pwd)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_recipe(db: Session, recipe: schemas.RecipeCreate, user_id: int):
    db_recipe = models.Recipe(**recipe.model_dump(), owner_id=user_id)
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)
    return db_recipe


def get_recipes(db: Session, search: Optional[str] = None, max_time: Optional[int] = None):
    query = db.query(models.Recipe)
    if search:
        query = query.filter(models.Recipe.title.ilike(f"%{search}%") | models.Recipe.description.ilike(f"%{search}%"))
    if max_time:
        query = query.filter(models.Recipe.cooking_time <= max_time)
    return query.all()


def get_fastest_recipe(db: Session):
    return db.query(models.Recipe).order_by(models.Recipe.cooking_time.asc()).first()