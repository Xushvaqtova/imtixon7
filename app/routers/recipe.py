from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import models, schemas, database

router = APIRouter(prefix="/recipes", tags=["Recipes"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
def create_recipe(recipe: schemas.RecipeCreate, db: Session = Depends(get_db)):
    new_recipe = models.Recipe(**recipe.dict())
    db.add(new_recipe)
    db.commit()
    db.refresh(new_recipe)
    return new_recipe


@router.get("/")
def get_recipes(db: Session = Depends(get_db)):
    return db.query(models.Recipe).all()


@router.get("/{id}")
def get_recipe(id: int, db: Session = Depends(get_db)):
    return db.query(models.Recipe).filter(models.Recipe.id == id).first()


@router.put("/{id}")
def update_recipe(id: int, recipe: schemas.RecipeCreate, db: Session = Depends(get_db)):
    db_recipe = db.query(models.Recipe).filter(models.Recipe.id == id).first()
    for key, value in recipe.dict().items():
        setattr(db_recipe, key, value)
    db.commit()
    return db_recipe


@router.delete("/{id}")
def delete_recipe(id: int, db: Session = Depends(get_db)):
    recipe = db.query(models.Recipe).filter(models.Recipe.id == id).first()
    db.delete(recipe)
    db.commit()
    return {"msg": "Deleted"}


@router.get("/search/")
def search(q: str, db: Session = Depends(get_db)):
    return db.query(models.Recipe).filter(models.Recipe.title.contains(q)).all()


@router.get("/fastest/")
def fastest(db: Session = Depends(get_db)):
    return db.query(models.Recipe).order_by(models.Recipe.cooking_time).first()


@router.get("/filter/")
def filter_time(max_time: int, db: Session = Depends(get_db)):
    return db.query(models.Recipe).filter(models.Recipe.cooking_time <= max_time).all()