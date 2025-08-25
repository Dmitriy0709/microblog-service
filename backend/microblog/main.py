from fastapi import FastAPI
from microblog.routes import medias, tweets, users

app = FastAPI(title="Microblog API")

app.include_router(tweets.router)
app.include_router(users.router)
app.include_router(medias.router)
