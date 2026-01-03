from fastapi import FastAPI
import uvicorn

from ops import ops
from authorization import auth

app = FastAPI()


app.include_router(router=ops.router)
app.include_router(router=auth.router)