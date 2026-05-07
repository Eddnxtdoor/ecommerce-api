from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.database import engine, Base
from app.routers import auth, products, orders

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="NXTDoor E-Commerce API",
    description="A REST API for browsing products and placing orders",
    version="1.0.0"
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again later."}
    )

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(orders.router)

@app.get("/")
def root():
    return {
        "message": "Welcome to the E-Commerce API",
        "docs": "/docs",
        "version": "1.0.0"
    }