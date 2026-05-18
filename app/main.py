from fastapi import FastAPI
from .database import Base, engine
from .routers import auth, recipe

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Recipe Management API",
    version="1.0.0",
    description="Imtihon uchun rmasi"
)

app.include_router(auth.router)
app.include_router(recipe.router)

@app.get("/")
def root():
    return {"status": "Recipe API muvaffaqiyatli ishlamoqda!"}