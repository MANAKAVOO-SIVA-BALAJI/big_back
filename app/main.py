from fastapi import FastAPI

from .db import Base, engine
from . import models 
# Create tables
Base.metadata.create_all(bind=engine)
from .routes import router

app = FastAPI(title="MVP Backend")

app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=False)


