from fastapi import FastAPI
from sc_api import knowledge, tokens, users

app = FastAPI()

app.include_router(knowledge.router, prefix="/api")
app.include_router(tokens.router, prefix="/api")
app.include_router(users.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "SC API Root"}
