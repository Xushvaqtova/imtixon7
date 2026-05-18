from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..security import get_current_user
from .. import schemas, models

router = APIRouter(prefix="/recipes", tags=["Recipes"])

# Swagger UI-da qulofcha (Authorize) ishlashi va tokenni avtomatik tekshirish uchun
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


@router.post("/", response_model=schemas.RecipeOut, status_code=status.HTTP_201_CREATED)
def create_new_recipe(
        recipe: schemas.RecipeCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    # Yangi retsept obyektini yaratish va unga joriy foydalanuvchi ID-sini biriktirish
    db_recipe = models.Recipe(**recipe.model_dump(), owner_id=current_user.id)
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)
    return db_recipe


@router.get("/", response_model=List[schemas.RecipeOut])
def list_recipes(db: Session = Depends(get_db)):
    # Hech qanday filtrsiz, to'g'ridan-to'g'ri bazadagi barcha retseptlarni qaytaradi
    return db.query(models.Recipe).all()


@router.get("/fastest", response_model=schemas.RecipeOut)
def get_fastest_recipe(db: Session = Depends(get_db)):
    # cooking_time bo'yicha eng kichigini saralab, birinchi retseptni oladi
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

    # Faqat retsept egasi uni tahrirlay olishini tekshirish
    if recipe.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Sizda bu retseptni tahrirlash huquqi yo'q")

    # Faqat kiritilgan (o'zgartirilgan) maydonlarni yangilash
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

    # Faqat retsept egasi uni o'chira olishini tekshirish
    if recipe.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Sizda bu retseptni o'chirish huquqi yo'q")

    db.delete(recipe)
    db.commit()
    return None