from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..security import get_current_user
from .. import schemas, models

router = APIRouter(prefix="/recipes", tags=["Recipes"])

# Swagger UI-da qulofcha va avtomatik token ishlashi uchun
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


@router.post("/", response_model=schemas.RecipeOut, status_code=status.HTTP_201_CREATED)
def create_new_recipe(
        recipe: schemas.RecipeCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    db_recipe = models.Recipe(**recipe.model_dump(), owner_id=current_user.id)
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)
    return db_recipe


@router.get("/", response_model=List[schemas.RecipeOut])
def list_recipes(
        search: Optional[str] = Query(None, description="Retsept nomi yoki tavsifi bo'yicha qidirish"),
        max_time: Optional[int] = Query(None, description="Maksimal tayyor bo'lish vaqti (daqiqa)"),
        db: Session = Depends(get_db)
):
    # Asosiy so'rov: hamma retseptlarni olishga tayyor turadi
    query = db.query(models.Recipe)

    # Agar qidiruv so'zi kiritilsa, nomi yoki tavsifidan qidiradi
    if search:
        query = query.filter(
            (models.Recipe.title.ilike(f"%{search}%")) |
            (models.Recipe.description.ilike(f"%{search}%"))
        )

    # Agar maksimal vaqt kiritilsa, pishish vaqtini filterlaydi
    if max_time is not None:
        query = query.filter(models.Recipe.cooking_time <= max_time)

    # Hech narsa kiritilmasa (shunchaki Execute bosilsa) yuqoridagi if'larga kirmaydi
    # va bazadagi jami retseptlar ro'yxatini qaytaradi
    return query.all()


@router.get("/fastest", response_model=schemas.RecipeOut)
def get_fastest_recipe(db: Session = Depends(get_db)):
    # Eng tez pishadigan retseptni vaqt bo'yicha o'sib borish tartibida saralab, 1-sini oladi
    recipe = db.query(models.Recipe).order_by(models.Recipe.cooking_time.asc()).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Hech qanday retsept topilmadi")
    return recipe


@router.get("/{recipe_id}", response_model=schemas.RecipeOut)
def read_recipe(recipe_id: int, db: Session = Depends(get_db)):
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Retsept topilmadi")
    return recipe


@router.put("/{recipe_id}", response_model=schemas.RecipeOut)
def update_recipe(
        recipe_id: int,
        recipe_update: schemas.RecipeUpdate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Retsept topilmadi")
    if recipe.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Sizda bu retseptni tahrirlash huquqi yo'q")

    for key, value in recipe_update.model_dump(exclude_unset=True).items():
        setattr(recipe, key, value)

    db.commit()
    db.refresh(recipe)
    return recipe


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipe(
        recipe_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Retsept topilmadi")
    if recipe.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Sizda bu retseptni o'chirish huquqi yo'q")

    db.delete(recipe)
    db.commit()
    return None