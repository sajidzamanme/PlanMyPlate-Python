from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.core.config import settings
from app.db.session import engine
from app.db.base_class import Base
import os

# Create tables
# In a real project, use Alembic for migrations.
# But for this migration task, creating all tables on startup is fine.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "REST API for the **PlanMyPlate** meal-planning mobile app. "
        "Manage users, recipes, meal plans, grocery lists, inventory, "
        "product expiry tracking, and AI-powered recipe generation via Google Gemini."
    ),
    version="1.1.0",
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "auth",             "description": "User registration, login, and password reset"},
        {"name": "users",            "description": "User profile management"},
        {"name": "user-preferences", "description": "Dietary preferences, allergies, and dislikes"},
        {"name": "ingredients",      "description": "Ingredient catalogue with price and tags"},
        {"name": "recipes",          "description": "Recipe CRUD, search, and calorie filtering"},
        {"name": "meal-plans",       "description": "Weekly meal plan creation and management"},
        {"name": "grocery-lists",    "description": "Grocery list management and purchase flow"},
        {"name": "inventory",        "description": "Pantry / inventory item tracking"},
        {
            "name": "expiry",
            "description": (
                "**Product Expiry System** — Add purchased products with expiry dates, "
                "list all tracked items, and fetch soon-to-expire items within a configurable "
                "day window (default 10 days). Designed for scheduled mobile calls. "
                "Uses the existing inventory; no separate table required."
            ),
        },
        {"name": "reference-data",   "description": "Static reference lists: diets, allergies, ingredient tags"},
        {"name": "files",            "description": "Image upload and static file serving"},
        {"name": "ai",               "description": "AI-powered recipe and meal plan generation via Google Gemini"},
    ],
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files (Uploads)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount(f"/{settings.UPLOAD_DIR}", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include API router
app.include_router(api_router, prefix=settings.API_PREFIX)

@app.get("/")
def root():
    return {"message": "Welcome to PlanMyPlate Python API"}

@app.get("/api/test")
def test():
    return "Hello from PlanMyPlate"
