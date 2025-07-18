from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from app.routers.websocket import router as websocket_router


app = FastAPI()

# TODO: secure websockets form hijacks (CRITICAL)

app.include_router(websocket_router, prefix="/ws")
