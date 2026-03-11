from fastapi import FastAPI
from .db import init_db
from .routers.listings import router as listings_router
from .routers.areas import router as areas_router
from .routers.analytics import router as analytics_router
from .routers.official_stats import router as official_stats_router


app = FastAPI(
    title="Rental Insights API",
    version="1.0.0",
    description="A housing market and rental insights API with CRUD for listings and analytics endpoints."
)

@app.on_event("startup")
def on_startup():
    init_db()
    print("Rental Insights API started, databases initialized")

app.include_router(listings_router)
app.include_router(areas_router)
app.include_router(analytics_router)
app.include_router(official_stats_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"message": "Rental Insights API is running"}