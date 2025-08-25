from fastapi import FastAPI
from app.routes import tweets, users, medias
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(tweets.router)
app.include_router(users.router)
app.include_router(medias.router)
