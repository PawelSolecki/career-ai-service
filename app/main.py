from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.offer_routes import router as offer_router
from app.api.cv_routes import router as cv_router
import yaml
from pathlib import Path


def auto_resolve_yaml():
    try:
        import subprocess

        base_path = Path(__file__).parent.parent
        resolve_script = base_path / "resolve_yaml.py"

        if resolve_script.exists():
            subprocess.run(["python3", str(resolve_script)], cwd=base_path, check=True)
    except Exception as e:
        print(f"Could not auto-resolve YAML: {e}")


def load_openapi_spec():
    base_path = Path(__file__).parent.parent
    resolved_path = base_path / "resources" / "api" / "openapi-resolved.yaml"
    openapi_path = base_path / "resources" / "api" / "openapi.yaml"

    # Auto-resolve if needed (resolved file doesn't exist or is older)
    if not resolved_path.exists() or (
        openapi_path.exists()
        and resolved_path.stat().st_mtime < openapi_path.stat().st_mtime
    ):
        auto_resolve_yaml()

    if resolved_path.exists():
        with open(resolved_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return None


app = FastAPI(
    title="Career AI Service",
    description="API for analyzing job offers and extracting skill requirements",
    version="1.0.0",
)

# Override with YAML spec if available
openapi_spec = load_openapi_spec()
if openapi_spec:

    def custom_openapi():
        return openapi_spec

    app.openapi = custom_openapi

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://career-ai-service:8082",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(offer_router, prefix="/api/v1/offer", tags=["Job Offer Analysis"])
app.include_router(cv_router, prefix="/api/v1/cv", tags=["CV Analysis"])


@app.get("/openapi.json")
async def get_openapi():
    return app.openapi()


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8082)
