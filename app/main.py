from fastapi import FastAPI

app = FastAPI(
    title="Rental Insights API",
    version="0.1.0",
    description="A housing market and rental insights API with CRUD for listings and analytics endpoints."
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"message": "Rental Insights API is running"}