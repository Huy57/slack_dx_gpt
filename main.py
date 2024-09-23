from fastapi import FastAPI
from service import router as slack_router

app = FastAPI()

# Include API routers
app.include_router(slack_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "__main__:app",
        host="0.0.0.0",
        port=5000,
        # reload_dirs=reload_dirs,
        # reload=True,
    )

