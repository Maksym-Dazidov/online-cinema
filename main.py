from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.actor import router as actor_router
from app.api.genre import router as genre_router
from app.api.movie import router as movie_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(actor_router)
app.include_router(genre_router)
app.include_router(movie_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
