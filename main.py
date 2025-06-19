from fastapi import FastAPI
from spatium.api import device, deployment

app = FastAPI(
    title="Spatium",
    description="Network Configuration Analyzer and Digital Twin Platform",
    version="0.1.0"
)

# Include routers from API modules
app.include_router(device.router)
# app.include_router(analysis.router)
app.include_router(deployment.router)

@app.get("/")
async def root():
    return {
        "name": "Spatium",
        "version": "0.1.0",
        "description": "Network Configuration Analysis and Digital Twin Platform"
    }

@app.get("/about")
async def about():
    return {
        "name": "Spatium",
        "version": "0.1.0",
        "description": "Network Configuration Analysis and Digital Twin Platform",
        "author": "Spatium Team",
        "repository": "https://github.com/yourusername/spatium",
        "license": "MIT"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
