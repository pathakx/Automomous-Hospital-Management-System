from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
from app.config import settings
from app.database import engine, Base
from app.routes import auth, doctors, appointments, records, doctor_portal, chat
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs on application startup and shutdown.
    Creates upload directory if it does not exist.
    """
    # Create upload directory on startup
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    print(f"Upload directory ready: {settings.UPLOAD_DIR}")
    print(f"File storage mode: {settings.FILE_STORAGE}")
    print(f"Database connected: {settings.DATABASE_URL.split('@')[-1]}")
    yield
    # Cleanup on shutdown (if needed)
    print("Application shutting down.")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Hospital AI Chatbot Backend API",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Middleware
# Allows frontend (Next.js on port 3000) to call backend APIs
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",     # Next.js dev server
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Serve uploaded files as static files (local dev only)
if settings.FILE_STORAGE == "local":
    os.makedirs(os.path.join(settings.UPLOAD_DIR), exist_ok=True)
    app.mount(
        "/uploads",
        StaticFiles(directory="uploads"),
        name="uploads"
    )


# Health check endpoint
@app.get("/health", tags=["System"])
def health_check():
    """
    Health check endpoint.
    Returns system status. Used by monitoring tools and deployment checks.
    """
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "storage": settings.FILE_STORAGE
    }

# Include Routers
app.include_router(auth.router)
app.include_router(doctors.router)
app.include_router(appointments.router)
app.include_router(records.router)
app.include_router(doctor_portal.router)
app.include_router(chat.router)


# Root endpoint
@app.get("/", tags=["System"])
def root():
    return {
        "message": "Hospital AI Chatbot API",
        "docs": "/docs",
        "health": "/health"
    }