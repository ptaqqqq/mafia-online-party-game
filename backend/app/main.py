from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from app.routers.websocket import router as websocket_router


app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# TODO: secure websockets form hijacks (CRITICAL)

@app.get("/")
async def root():
    return {"message": "Mafia Online Backend is running!", "status": "ok"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "medic_role": "added"}

app.include_router(websocket_router, prefix="/ws")
