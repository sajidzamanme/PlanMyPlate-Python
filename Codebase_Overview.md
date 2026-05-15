# PlanMyPlate-Python Codebase Overview

A meal planning REST API built with **FastAPI** + **SQLAlchemy** + **MySQL**. Manages users, recipes, meal plans, grocery lists, inventory, and AI-powered recipe generation via Google Gemini.

---

## 1. Project Structure (All Files)

```
PlanMyPlate-Python/
├── .env                          # Database URL, JWT secret, Gemini key
├── .gitignore
├── API_DOCUMENTATION.md          # Full API reference (this is the companion doc)
├── Codebase_Overview.md          # ← You are here
├── README.md                     # Setup instructions
├── requirements.txt              # Python packages (FastAPI, SQLAlchemy, etc.)
├── plan_my_plate.sql             # Full DB schema: tables, indexes, foreign keys
├── entries.sql                   # Seed data: 50 recipes, 36 ingredients, etc.
├── uploads/                      # Uploaded image files
└── app/
    ├── main.py                   # FastAPI app creation, CORS, static files, router mount
    ├── api/
    │   ├── deps.py               # Dependency injection: get_db(), get_current_user()
    │   └── v1/
    │       ├── api.py            # Master router – includes all 12 endpoint groups
    │       └── endpoints/        # One file per resource group
    │           ├── admin.py
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
    │           ├── ai.py
    │           └── expiry.py
    ├── core/
    │   ├── config.py             # Settings class (reads .env)
    │   └── security.py           # JWT creation, bcrypt password hashing
    ├── crud/                     # Database operations (one file per resource)
    │   ├── base.py               # Generic CRUDBase<Model, Create, Update>
    │   ├── crud_user.py
    │   ├── crud_user_preferences.py
    │   ├── crud_ingredient.py
    │   ├── crud_recipe.py
    │   ├── crud_meal_plan.py
    │   ├── crud_grocery_list.py
    │   ├── crud_inventory.py
    │   ├── crud_expiry.py
    │   └── crud_reference.py
    ├── db/
    │   ├── base_class.py         # SQLAlchemy declarative Base with auto tablename
    │   └── session.py            # Engine + SessionLocal
    ├── models/                   # SQLAlchemy ORM models (7 files, 10+ tables)
    │   ├── user.py               # User, UserPreferences + 4 association tables
    │   ├── recipe.py             # Recipe, RecipeIngredient
    │   ├── ingredient.py         # Ingredient + ingredient_tag_map
    │   ├── meal_plan.py          # MealPlan, MealSlot
    │   ├── grocery.py            # GroceryList, GroceryListIngredient
    │   ├── inventory.py          # Inventory, InvItem
    │   └── reference.py          # Diet, Allergy, IngredientTag
    ├── schemas/                  # Pydantic v2 request/response DTOs
    │   ├── auth.py               # SignUpRequest, SignInRequest, AuthResponse, etc.
    │   ├── user.py               # UserCreate, UserUpdate, UserDto, UserPreferencesDto
    │   ├── ingredient.py         # Ingredient, IngredientCreate, IngredientQuantityDto
    │   ├── recipe.py             # RecipeCreateDto, RecipeResponse, RecipeIngredientDto
    │   ├── meal_plan.py          # MealPlanRequestDto, MealPlanResponse, MealSlotResponse
    │   ├── grocery.py            # GroceryListCreate, PurchaseRequestDto, UpdateItemDto
    │   ├── inventory.py          # InvItemCreateRequest, InvItemResponse, InventoryResponse
    │   ├── expiry.py             # ExpiryEntryRequest, ExpiryItemResponse, SoonToExpireResponse
    │   └── ai.py                 # AiRecipeRequestDto
    └── services/
        └── gemini_service.py     # Google Gemini AI integration (recipe + meal plan gen)
```

---

## 2. The 7-Layer Architecture

Each layer has a single responsibility. A request flows through them top-to-bottom, then the response bubbles back up.

```
Client (App/Browser)
    ↓  HTTP Request
┌─────────────────────────────────┐
│  1. main.py (Entry Point)       │  Creates FastAPI app, mounts routers
├─────────────────────────────────┤
│  2. api.py (Router Aggregator)  │  Includes 11 endpoint routers with prefixes
├─────────────────────────────────┤
│  3. Endpoints (Request Handlers)│  Receives HTTP, calls deps → crud/services
├─────────────────────────────────┤
│  4. Schemas (Pydantic DTOs)     │  Validates input, serializes output
├─────────────────────────────────┤
│  5. CRUD (DB Operations)        │  SQL queries via SQLAlchemy ORM
├─────────────────────────────────┤
│  6. Models (ORM Definitions)    │  Maps Python classes ↔ MySQL tables
├─────────────────────────────────┤
│  7. Database (MySQL)            │  Actual data storage
└─────────────────────────────────┘
    ↑  HTTP Response
Client (App/Browser)
```

### Layer Details

**Layer 1 — `app/main.py`**
- Creates the `FastAPI` app instance
- Configures CORS (all origins allowed)
- Mounts the `uploads/` directory for static file serving
- Includes the master API router at `/api` prefix
- Auto-creates all database tables on startup (`Base.metadata.create_all`)

**Layer 2 — `app/api/v1/api.py`**
- Creates a top-level `APIRouter`
- Includes 12 sub-routers, each with a URL prefix and tag group:
  | Router | Prefix | Tag |
  |--------|--------|-----|
  | auth | `/auth` | auth |
  | users | `/users` | users |
  | user_preferences | `/user-preferences` | user-preferences |
  | ingredients | `/ingredients` | ingredients |
  | recipes | `/recipes` | recipes |
  | meal_plans | `/meal-plans` | meal-plans |
  | grocery_lists | `/grocery-lists` | grocery-lists |
  | inventory | `/inventory` | inventory |
  | reference_data | `/reference-data` | reference-data |
  | files | `/files` | files |
  | ai | `/ai` | ai |
  | expiry | `/expiry` | expiry |
  | admin | `/admin` | admin |

**Layer 3 — Endpoints `app/api/v1/endpoints/*.py`**
- Each file defines a router with `@router.get()`, `@router.post()`, etc.
- Endpoints receive the HTTP request, call dependencies, then delegate to CRUD or Services
- Example pattern:
  ```python
  @router.get("/search", response_model=List[RecipeResponse])
  def search_recipes(
      *, db: Session = Depends(deps.get_db), name: str
  ) -> Any:
      return crud.recipe.search_by_name(db, name=name)
  ```

**Layer 4 — Schemas `app/schemas/*.py`**
- Define **request bodies** (what the client sends) and **response models** (what the API returns)
- Use Pydantic v2 with `Field(alias=...)` to map between API camelCase and Python snake_case
- Schema examples:
  - `SignUpRequest` validates email, password (min 8 chars), phone format, date of birth
  - `RecipeCreateDto` accepts ingredients as `List[RecipeIngredientDto]`
  - `MealPlanResponse` automatically nests `List[MealSlotResponse]` each containing a `RecipeResponse`

**Layer 5 — CRUD `app/crud/*.py`**
- Generic base class `CRUDBase<ModelType, CreateSchema, UpdateSchema>` provides:
  - `get(db, id)` — get by primary key
  - `get_multi(db, skip, limit)` — list with pagination
  - `create(db, obj_in)` — insert
  - `update(db, db_obj, obj_in)` — partial update (only provided fields)
  - `remove(db, id)` — delete
- Each resource extends CRUDBase with custom methods:
  ```python
  class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
      def get_by_email(self, db, *, email)
      def authenticate(self, db, *, identifier, password)
  ```

**Layer 6 — Models `app/models/*.py`**
- SQLAlchemy ORM classes mapping to MySQL tables
- Define columns, relationships, and association tables
- Auto-generate `__tablename__` from class name (e.g., class `Recipe` → table `recipe`)

**Layer 7 — Database**
- MySQL via XAMPP, connected via `pymysql` driver
- Connection string in `.env`: `DATABASE_URL=mysql+pymysql://root:@localhost:8050/plan_my_plate`

---

## 3. Naming Convention: camelCase ↔ snake_case

The API speaks **camelCase** (JSON), but Python/database uses **snake_case**. Pydantic handles the translation automatically:

```python
class RecipeResponse(BaseModel):
    recipeId: int = Field(alias="recipe_id")   # API returns recipeId
    prepTime: int  = Field(alias="prep_time")   # model attribute is prep_time
    imageUrl: str  = Field(alias="image_url")
    recipeIngredients: List[...] = Field(alias="recipe_ingredients")

    model_config = {"from_attributes": True, "populate_by_name": True}
```

- **`from_attributes: True`** — allows creating the schema from a SQLAlchemy model object
- **`populate_by_name: True`** — allows constructing with either camelCase or snake_case names
- Clients always send/receive **camelCase**; internal Python code uses **snake_case**

---

## 4. Request Lifecycle (Trace a Real Example)

### Example: `POST /api/meal-plans/user/1/create` — Create a weekly meal plan with recipes

```
Step 1: FastAPI receives POST /api/meal-plans/user/1/create
Step 2: api.py matches prefix /meal-plans → routes to endpoints/meal_plans.py
Step 3: deps.get_db() creates a SQLAlchemy Session (DB connection from pool)
Step 4: deps.get_current_user() does:
          - Extracts JWT from Authorization: Bearer <token>
          - Decodes it using python-jose (verifies signature + expiry)
          - Looks up user by email from "sub" claim
          - Returns User model (or raises 403)
Step 5: MealPlanRequestDto validates the JSON body:
          - recipeIds: list of 21 recipe IDs
          - servingsMultipliers: optional list of 21 multipliers
          - duration: defaults to 7, startDate: optional
Step 6: Authorization check: userId != current_user.user_id → 403
Step 7: crud.meal_plan.create_with_recipes(db, user_id=1, dto=...):
          7a. Deactivates all existing "active" meal plans for this user
          7b. Deactivates all existing "active" grocery lists
          7c. Creates a new MealPlan row with status="active"
          7d. For each of the 21 recipe IDs:
              - Determines day number (i // 3 + 1) and meal type (0→Breakfast,1→Lunch,2→Dinner)
              - Creates a MealSlot row with the servings_multiplier
          7e. Commits to MySQL
Step 8: Back in the endpoint, aggregates all ingredients across recipes × multipliers:
          - For each recipe slot, multiplies ingredient quantities by servings_multiplier
          - Calls crud.grocery_list.add_ingredients_with_quantities() to build grocery list
Step 9: Returns MealPlanResponse → Pydantic auto-serializes ORM objects to JSON (camelCase)
```

### Example: `GET /api/recipes/search?name=chicken` (simpler, no auth)
```
FastAPI → endpoints/recipes.py → deps.get_db() → crud.recipe.search_by_name()
  → Recipe.name.ilike("%chicken%") → returns List[Recipe] → auto-serialized
```

---

## 5. Database Schema (All Tables)

### Users & Preferences
| Table | Key Columns | Relationships |
|-------|-------------|---------------|
| `users` | `user_id`, `first_name`, `last_name`, `email`, `password` (bcrypt hash), `phone`, `date_of_birth`, `reset_token` | → `user_preferences`, `meal_plan`, `grocery_list`, `inventory` |
| `user_preferences` | `pref_id`, `user_id`, `diet_id`, `budget` | → `users`, `diets`, M2M `ingredients` (allergens), M2M `ingredients` (dislikes) |
| `user_preferences_allergies` | `pref_id`, `ing_id` | Association table (allergens as ingredients) |
| `user_preferences_dislikes` | `pref_id`, `ing_id` | Association table |

### Reference Data
| Table | Columns |
|-------|---------|
| `diets` | `diet_id`, `diet_name` (Omnivore, Vegetarian, Vegan, ...) |
| `ingredient_tags` | `tag_id`, `tag_name` |
| `ingredient_tag_map` | `ing_id`, `tag_id` (M2M bridge) |

### Ingredients & Recipes
| Table | Key Columns | Relationships |
|-------|-------------|---------------|
| `ingredients` | `ing_id`, `name`, `price` | M2M `tags`, used in recipes/grocery/inventory |
| `recipe` | `recipe_id`, `name`, `description`, `calories`, `prep_time`, `cook_time`, `instructions`, `image_url` | → `recipe_ingredients` |
| `recipe_ingredients` | `id`, `recipe_id`, `ing_id`, `quantity`, `unit` | → `recipe`, `ingredients` |

### Meal Plans
| Table | Key Columns | Relationships |
|-------|-------------|---------------|
| `meal_plan` | `mp_id`, `user_id`, `start_date`, `duration`, `status` | → `users`, → `meal_slot` |
| `meal_slot` | `id`, `mp_id`, `recipe_id`, `slot_index`, `meal_type` (Breakfast/Lunch/Dinner), `day_number` (1-7), `servings_multiplier` | → `meal_plan`, → `recipe` |

### Grocery & Inventory
| Table | Key Columns | Relationships |
|-------|-------------|---------------|
| `grocery_list` | `list_id`, `user_id`, `date_created`, `status` | → `users`, → items |
| `grocery_list_ingredients` | `id`, `list_id`, `ing_id`, `quantity`, `unit` | → `grocery_list`, → `ingredients` |
| `inventory` | `inv_id`, `user_id`, `last_update` | → `users`, → items |
| `inv_item` | `item_id`, `inv_id`, `ing_id`, `quantity`, `unit`, `date_added`, `expiry_date` | → `inventory`, → `ingredients`. Index on `expiry_date` for fast expiry queries. |

---

## 6. Authentication Flow

### Sign Up
```
Client → POST /api/auth/signup { firstName, lastName, email, password, phone, dateOfBirth }
  → Validates all fields (password ≥ 8 chars, valid email, phone format, DOB in past)
  → Checks for duplicate email/phone → 400 if exists
  → Hashes password with bcrypt
  → Creates User row in database
  → Creates JWT with user email as "sub" claim, 24h expiry
  → Returns { access_token, email, firstName, lastName, userId, phone, dateOfBirth }
```

### Sign In
```
Client → POST /api/auth/signin { identifier (email or phone), password }
  → Looks up user by email or phone
  → Verifies password with bcrypt
  → Creates JWT
  → Returns { access_token, token_type, user info }
```

### Authenticated Request
```
Client → GET /api/users/me (Authorization: Bearer <JWT>)
  → deps.get_current_user():
      1. Extracts Bearer token from Authorization header
      2. Decodes with python-jose using JWT_SECRET + HS256
      3. Reads "sub" claim (user email)
      4. Looks up User by email in database
      5. Returns User object (or raises HTTP 403)
```

### Swagger UI Authorization
The Swagger UI Authorize button accepts a Bearer token directly. After signing in via `POST /api/auth/signin`, copy the `access_token` and paste it as `Bearer <token>`.

### Password Reset
```
Forgot: POST /api/auth/forgot-password { email }
  → Generates 4-digit numeric token, stores in user.reset_token with 1h expiry
  → Returns token (in production this would be emailed)

Reset:  POST /api/auth/reset-password { resetToken, newPassword }
  → Finds user by token
  → Checks expiry (timezone-aware comparison)
  → Hashes new password, clears token
```

---

## 7. CRUD Base Pattern Explained

The generic `CRUDBase` eliminates repetitive code:

```python
class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def get(self, db, id)                        # SELECT WHERE id = ?
    def get_multi(self, db, skip=0, limit=100)   # SELECT with OFFSET/LIMIT
    def create(self, db, *, obj_in)               # INSERT from schema
    def update(self, db, *, db_obj, obj_in)       # Partial UPDATE (only set fields)
    def remove(self, db, *, id)                   # DELETE
```

Resources extend this with resource-specific queries:

| CRUD Class | Extra Methods |
|------------|---------------|
| `CRUDUser` | `get_by_email()`, `get_by_phone()`, `authenticate()` |
| `CRUDIngredient` | `search_by_name()`, `filter_by_price()` |
| `CRUDRecipe` | `create_recipe()`, `update_recipe()`, `search_by_name()`, `filter_by_calories()` |
| `CRUDMealPlan` | `get_by_user_id()`, `get_weekly_plans()`, `create_simple()`, `create_with_recipes()`, `deactivate_active_plans()` |
| `CRUDGroceryList` | `get_by_user_id_and_status()`, `add_ingredients_with_quantities()`, `purchase_items()` |
| `CRUDInventory` | `get_by_user_id()`, `create_for_user()`, `add_item()`, `add_to_inventory()` |
| `CRUDExpiry` | `add_expiry_item()`, `update_expiry_item()`, `delete_expiry_item()`, `get_item_by_id()`, `get_all_expiry_items()`, `get_soon_to_expire()` |
| `CRUDUserPreferences` | `get_by_user_id()`, `create_or_update()` |
| `CRUDDiet` | `get_by_name()` |

---

## 8. Services Layer (Gemini AI)

`app/services/gemini_service.py` — integrates with Google Gemini (uses `gemini-2.5-flash`).

### How it works:
1. Builds a prompt describing what recipe/meal plan to generate
2. Includes database context (existing recipe names + ingredients) so AI can reuse them
3.   Sends prompt to Gemini API (model: `gemini-2.5-flash`)
4. Parses JSON from AI response
5. Creates/saves Recipe and Ingredient records in the database

### Two features:
- **`POST /api/ai/generate-recipe`** — single recipe with custom constraints (calories, cuisine, allergies, mood, max cooking time)
- **`POST /api/ai/generate-meal-plan`** — weekly plan (7 breakfasts + 7 lunches + 7 dinners), auto-creates grocery list

The AI auto-creates new ingredients if they don't exist in the database.

---

## 9. File Uploads

`POST /api/files/upload` — accepts `multipart/form-data` with a `file` field.

- Saves file to `uploads/` directory with a UUID-based filename
- Returns `{ "url": "http://localhost:8000/uploads/uuid-filename.jpg", "filename": "uuid-filename.jpg" }`
- The returned URL can be used as `imageUrl` when creating/updating recipes

Files are served statically via FastAPI's `StaticFiles` mount at `/uploads`.

---

## 10. Key Design Decisions

| Decision | Why |
|----------|-----|
| **FastAPI** | Auto-generated OpenAPI docs, Pydantic integration, async support, fast |
| **SQLAlchemy 2.0** | Mature ORM, migration support, raw SQL when needed |
| **MySQL (XAMPP)** | Local dev convenience, matches potential production DB |
| **JWT + bcrypt** | Stateless auth, no server-side sessions needed |
| **Pydantic v2 aliases** | API speaks camelCase (standard for JSON APIs), Python uses snake_case |
| **CRUD Base pattern** | Eliminates repetitive SELECT/INSERT/UPDATE/DELETE code |
| **21-slot meal plan** | 3 meals × 7 days; auto-assigned as Breakfast/Lunch/Dinner |
| **GEMINI_API_KEY optional** | AI features gracefully degrade if key not configured |

---

## 11. Quick Reference Map

| You want to... | Go to... |
|---|---|
| Add a new API endpoint | `app/api/v1/endpoints/new_file.py` |
| Change a database model | `app/models/` |
| Add a new database query | `app/crud/` |
| Change request/response format | `app/schemas/` |
| Modify AI prompts | `app/services/gemini_service.py` |
| Change JWT expiry or algorithm | `app/core/config.py` (or `.env`) |
| Change DB connection | `.env` → `DATABASE_URL` |
| Add seed data | `entries.sql` |
| Run a DB migration | Write a new `.sql` file in project root |
| Upload file handling | `app/api/v1/endpoints/files.py` |
| Auth logic (signup, login, token) | `app/api/v1/endpoints/auth.py` |
| Permission/access control | `app/api/deps.py` → `get_current_user()` |
| Expiry tracking logic | `app/crud/crud_expiry.py` |
| Expiry endpoints | `app/api/v1/endpoints/expiry.py` |

---

## 12. Tips for Beginners

- **All API field names use camelCase** (`recipeId`, `prepTime`). The code automatically maps them to snake_case for the database (`recipe_id`, `prep_time`). You don't need to worry about this — just use camelCase when calling the API.
- **Use `http://localhost:8000/docs`** (Swagger UI) to test every endpoint interactively — it shows schemas, lets you try requests, and handles auth tokens.
- **Use `access_token`** from auth responses in the `Authorization: Bearer <access_token>` header for authenticated requests.
- **Every authenticated endpoint** includes `current_user: User = Depends(deps.get_current_user)`. You don't need to pass user_id manually — the token identifies you.
- **Trace a simple flow** to understand the architecture: start with `POST /api/auth/signup` → follow it through `auth.py` → `crud_user.py` → `User` model → MySQL.
- **The CRUD layer is where SQL lives.** If you need a custom query (e.g., "find recipes with chicken"), add a method to the relevant CRUD file.
- **Don't modify `base.py`** (generic CRUD) unless you're changing how ALL resources work. Add custom methods to the specific CRUD file instead.

---

*This document is meant to help you understand the project architecture. For detailed endpoint documentation, see [API_DOCUMENTATION.md](API_DOCUMENTATION.md).*
