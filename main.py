from fastapi import FastAPI
import uvicorn

from authorization.auth import router

app = FastAPI()


app.include_router(router=router)