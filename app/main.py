from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.offer_routes import router as offer_router

app = FastAPI(
    title="Career AI Service",
    description="API for analyzing job offers and extracting skill requirements",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(offer_router, prefix="/api/v1", tags=["Job Offer Analysis"])


@app.get("/")
async def root():
    return {"message": "Career AI Service is running", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
