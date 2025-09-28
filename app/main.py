from fastapi import FastAPI
from app.database.connection import engine, Base
from app.routers import auth, products

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Tienda Backend API",
    description="Backend para aplicación de inventario y compras",
    version="1.0.0"
)

app.include_router(auth.router)      
app.include_router(products.router)  

@app.get("/")
def read_root():
    return {"message": "¡Tienda Backend funcionando!", "status": "ready"}

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API funcionando correctamente"}

@app.get("/test-db")
def test_database():
    try:
        from app.database.connection import SessionLocal
        from sqlalchemy import text
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return {"database": "connected", "status": "ok"}
    except Exception as e:
        return {"database": "error", "message": str(e)}