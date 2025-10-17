"""
Main FastAPI application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import (
    users_router,
    products_router,
    orders_router,
    notifications_router
)

# Initialize FastAPI app
app = FastAPI(
    title="Marketplace API",
    description="API para marketplace completo con usuarios, productos, pedidos y notificaciones",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware (para que Flutter pueda conectarse)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción: especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
def health_check():
    """Endpoint para verificar que la API está funcionando"""
    return {
        "status": "ok",
        "message": "API is running",
        "version": "1.0.0"
    }

# Root endpoint
@app.get("/")
def root():
    """Endpoint raíz"""
    return {
        "message": "Welcome to Marketplace API",
        "docs": "/docs",
        "health": "/health"
    }

# Include all routers
app.include_router(users_router, prefix="/api")
app.include_router(products_router, prefix="/api")
app.include_router(orders_router, prefix="/api")
app.include_router(notifications_router, prefix="/api")

# Startup event
@app.on_event("startup")
async def startup_event():
    """Se ejecuta al iniciar la aplicación"""
    print("🚀 Marketplace API starting up...")
    print("📊 Database: becarios_db")
    print("🔗 API running on: http://localhost:8001")
    print("📚 Docs available at: http://localhost:8001/docs")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Se ejecuta al cerrar la aplicación"""
    print("👋 Marketplace API shutting down...")