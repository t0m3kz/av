from fastapi import FastAPI
from spatium.api.device import router as device_router

app = FastAPI(
    title="Spatium",
    description="Network Configuration Analyzer (SSH-only API)",
    version="0.1.0",
)

# Only expose the device config API (SSH)
app.include_router(device_router)


@app.get("/")
async def root():
    return {
        "name": "Spatium",
        "version": "0.1.0",
        "description": "Network Configuration Analysis Platform (SSH-only API)",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
