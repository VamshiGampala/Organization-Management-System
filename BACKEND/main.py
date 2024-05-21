import models
from database import engine
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI,Request
from routers import user_module
import uvicorn

models.Base.metadata.create_all(bind=engine)
app = FastAPI(title='Organization Management System')
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

app.include_router(user_module.router)

if __name__ == "__main__":
    uvicorn.run(app,port=8000)


