# PlanMyPlate — Python Backend

A meal planning REST API built with **FastAPI** + **SQLAlchemy** + **MySQL (XAMPP)**. Provides endpoints for user management, recipes, meal plans, grocery lists, inventory tracking, and AI-powered recipe generation via Google Gemini.

---

## Prerequisites

- **Python 3.10+** — [Download](https://www.python.org/downloads/)
- **XAMPP** — [Download](https://www.apachefriends.org/) (for MySQL/MariaDB)
- **Git** (optional) — for cloning the repository

---

## Setup Instructions

### 1. Start XAMPP MySQL

1. Open **XAMPP Control Panel**
2. Start **MySQL** (make sure it runs on port **8050** — or adjust `.env` if your port differs)
3. Open **phpMyAdmin** at `http://localhost/phpmyadmin`

### 2. Create the Database

1. In phpMyAdmin, click **"New"** in the left sidebar
2. Enter database name: `plan_my_plate`
3. Set collation to `utf8mb4_general_ci`
4. Click **Create**

### 3. Import the Schema

1. Select the `plan_my_plate` database in phpMyAdmin
2. Click the **"Import"** tab
3. Click **"Choose File"** and select `plan_my_plate.sql` from the project root
4. Click **"Go"** to execute

This creates all the tables, indexes, primary keys, foreign key constraints, and required columns.

### 4. Import Seed Data

1. Still in the `plan_my_plate` database, click **"Import"** again
2. Click **"Choose File"** and select `entries.sql` from the project root
3. Click **"Go"** to execute

This populates the database with:
- 7 allergies (Peanuts, Milk, Eggs, Fish, Shellfish, Soy, Gluten)
- 7 diets (Omnivore, Vegetarian, Vegan, Pescatarian, Low Carb, High Protein, Diabetic Friendly)
- 8 ingredient tags
- 36 ingredients with prices
- 50 recipes with descriptions, instructions, and image URLs
- Recipe-ingredient mappings with quantities and units

### 5. Set Up Python Virtual Environment

```bash
# Navigate to the project directory
cd PlanMyPlate-Python

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 6. Install Dependencies

```bash
pip install -r requirements.txt
```

### 7. Configure Environment Variables

Edit the `.env` file in the project root:

```env
# Database Configuration
# Format: mysql+pymysql://username:password@host:port/database_name
# Default XAMPP: no password for root user
DATABASE_URL=mysql+pymysql://root:@localhost:8050/plan_my_plate

# JWT Configuration
JWT_SECRET=your_jwt_secret_here          # Change this to a strong random string
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440         # 24 hours

# Gemini AI Configuration (Optional — needed for AI features)
GEMINI_API_KEY=your_gemini_api_key_here

# App Configuration
API_PREFIX=/api
UPLOAD_DIR=uploads
```

> **Important:** 
> - Change the `DATABASE_URL` port if your XAMPP MySQL runs on a different port (default XAMPP port is `3306`, this project uses `8050`)
> - Replace `JWT_SECRET` with a strong random string for production
> - Get a Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey) if you want AI features

### 8. Run the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The server will start at: **http://localhost:8000**

---

## Accessing the API

| Resource | URL |
|----------|-----|
| **API Root** | http://localhost:8000 |
| **Swagger UI (Interactive Docs)** | http://localhost:8000/docs |
| **ReDoc (Alternative Docs)** | http://localhost:8000/redoc |
| **OpenAPI JSON** | http://localhost:8000/api/openapi.json |

### Quick Test

After starting the server, verify it's working:

```bash
curl http://localhost:8000
# Expected: {"message":"Welcome to PlanMyPlate Python API"}

curl http://localhost:8000/api/test
# Expected: "Hello from PlanMyPlate"

curl http://localhost:8000/api/recipes
# Expected: List of 50 recipes (if seed data was imported)
```

### Using Swagger UI

1. Go to `http://localhost:8000/docs`
2. To test authenticated endpoints:
   - First, create an account via `POST /api/auth/signup`
   - Click the **"Authorize"** button (🔒) at the top right
   - Enter your email as **username** and your password
   - Click **"Authorize"**
   - Now all authenticated endpoints will include the token automatically

---

## Project Structure

```
PlanMyPlate-Python/
├── .env                    # Environment variables
├── requirements.txt        # Python dependencies
├── plan_my_plate.sql       # Database schema (tables, indexes, FKs)
├── entries.sql             # Seed data (recipes, ingredients, etc.)
├── API_DOCUMENTATION.md    # Detailed API reference
├── uploads/                # Uploaded image files
└── app/
    ├── main.py             # FastAPI application entry point
    ├── api/
    │   ├── deps.py         # Dependency injection (DB session, auth)
    │   └── v1/
    │       ├── api.py      # Router aggregation
    │       └── endpoints/  # API endpoint handlers
    │           ├── auth.py
    │           ├── users.py
    │           ├── user_preferences.py
    │           ├── recipes.py
    │           ├── ingredients.py
    │           ├── meal_plans.py
    │           ├── grocery_lists.py
    │           ├── inventory.py
    │           ├── reference_data.py
    │           ├── files.py
    │           └── ai.py
    ├── core/
    │   ├── config.py       # Settings (loaded from .env)
    │   └── security.py     # JWT + password hashing
    ├── crud/               # Database operations (CRUD layer)
    ├── db/
    │   ├── base_class.py   # SQLAlchemy base model
    │   └── session.py      # Database engine & session
    ├── models/             # SQLAlchemy ORM models
    ├── schemas/            # Pydantic request/response schemas
    └── services/
        └── gemini_service.py  # Google Gemini AI integration
```

---

## API Overview

| Module | Endpoints | Auth Required |
|--------|-----------|---------------|
| **Auth** | signup, signin, token, forgot-password, reset-password | No |
| **Users** | CRUD operations on user profiles | Yes |
| **User Preferences** | Get/set dietary preferences, allergies, dislikes | Yes |
| **Recipes** | CRUD, search by name, filter by calories | No (public) |
| **Ingredients** | CRUD, search by name, filter by price | No (public) |
| **Meal Plans** | Create, manage weekly meal plans | Yes |
| **Grocery Lists** | Manage shopping lists, purchase items | Yes |
| **Inventory** | Track pantry items, add/remove/update | Yes |
| **Reference Data** | List diets, allergies, ingredients | No (public) |
| **Files** | Upload images | No |
| **AI** | Generate recipes, generate weekly meal plans | Yes |

For detailed endpoint documentation, see [API_DOCUMENTATION.md](API_DOCUMENTATION.md).

---

## Troubleshooting

### Common Issues

**"Can't connect to MySQL server"**
- Make sure XAMPP MySQL is running
- Check the port in `.env` matches your XAMPP MySQL port
- Default XAMPP port is `3306`; this project uses `8050`

**"Table 'plan_my_plate.xxx' doesn't exist"**
- Import `plan_my_plate.sql` before `entries.sql`
- Make sure you selected the correct database in phpMyAdmin before importing

**"ModuleNotFoundError"**
- Make sure the virtual environment is activated: `source venv/bin/activate`
- Run `pip install -r requirements.txt` again

**"bcrypt" or password-related errors**
- The project pins `bcrypt==4.0.1` for `passlib` compatibility
- Run: `pip install bcrypt==4.0.1`

**Gemini AI features not working**
- Set a valid `GEMINI_API_KEY` in `.env`
- Get one free from [Google AI Studio](https://aistudio.google.com/apikey)

---

## Tech Stack

- **Framework:** FastAPI
- **ORM:** SQLAlchemy 2.0
- **Database:** MySQL/MariaDB (via XAMPP)
- **Auth:** JWT (python-jose) + bcrypt (passlib)
- **AI:** Google Gemini API
- **Validation:** Pydantic v2

---
